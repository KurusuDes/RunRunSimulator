---
tags: [script, breeding-system, local-incubation]
---

# IncubationService

**Ruta:** `Systems/Breeding/IncubationService.cs` (renombrado de AsyncBreedingService en S131)

**Responsabilidad:** Gestor de cría local síncrona (sin Cloud Code). Métodos públicos: `StartBreeding(motherID, fatherID, decorIds)` (marca padres como Breeding, deduce energía, fija BreedReadyAt y guarda decoraciones), `TryHatch(motherID, fatherID)` (verifica listo, deduce Minerita, hatcha vía BreedingService.Breed), `TryHatchEgg(CreatureDNA egg)` **(S137)** (intenta eclosionar huevo suelto), `IsReady(mother)`, `HatchCostFor()`. Dispara `GameEvents.RegistryChanged()` y `GameEvents.CreatureFormChanged()` (S137) para persistencia. Resuelve `registry` y `database` desde `GameManager.Instance` en Awake.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|----------|
| `energyCostPerParent` | float (Min 0) | Energía deducida a cada padre al iniciar cría (default 20). `NeedsState.SpendEnergy()` |
| `status` | string | Display (ReadOnly, debug status message) |

## Métodos Públicos

| Método | Firma | Retorna | Descripción |
|--------|-------|---------|-------------|
| `StartBreeding` | `(string motherID, string fatherID, IReadOnlyList<string> decorIds = null)` | `bool` | Inicia cría local: marca BusyState=Breeding, deduce energía, fija BreedReadyAt = TotalMinutes + `BreedDurationMinutes`, guarda `decorIds` en `BreedDecorIDs` de la madre. Retorna true si ok. |
| `TryHatch` | `(string motherID, string fatherID)` | `HatchResult` | Verifica si listo (IsReady), deduce Minerita via HatchCost, hatcha. Retorna Hatched/NotReady/InsufficientMinerita/Invalid. |
| `TryHatchEgg` | `(CreatureDNA egg)` | `HatchResult` | **(S137)** Intenta eclosionar huevo suelto (no acoplado a breeding pair). Valida Form==Egg, deduce EggHatchCost via Wallet.TrySpend, llama CreatureGrowth.Hatch, dispara RegistryChanged + CreatureFormChanged. Retorna Hatched/InsufficientMinerita/Invalid. |
| `CancelBreeding` | `(string motherID, string fatherID)` | `void` | Cancela cría: limpia BusyState, BreedReadyAt, BreedPartnerID y BreedDecorIDs en ambos. |
| `CancelAllBreeding` | `()` | `void` | Cancela todas las crías activas (BusyState==Breeding). |
| `IsReady` | `(CreatureDNA mother)` | `bool` | ¿BreedReadyAt > 0 AND GameClock.TotalMinutes >= BreedReadyAt? |
| `HatchCostFor` | `(string motherID, string fatherID)` | `int` | Devuelve costo Minerita para eclosionar (consultado a InheritanceOddsTableSO). 0 si no hay tabla. |
| `EggHatchCost` | `(property)` | `int` | **(S137)** Getter → `odds != null ? odds.HatchCostBase : 10` (costo fijo para eclosionar un huevo suelto). |

## Ciclo de StartBreeding

1. Valida que GameClock esté cargado (Loaded==true)
2. Valida padres (`ValidateParents`): existen, libres (`CreatureAvailability.IsFree`), genders correctos (Female/Male), no superaron `MaxBreedCount`
3. Valida que haya tabla de odds (`BreedingController.InheritanceOdds`)
4. Marca busy: `BusyState = BusyReason.Breeding` en ambos
5. Deduce energía: `mother.Needs.SpendEnergy(energyCostPerParent)` + `father.Needs...`
6. Fija timers: `BreedReadyAt = GameClock.Instance.TotalMinutes + odds.BreedDurationMinutes` (mismo valor en ambos)
7. Fija `BreedPartnerID` cruzado y copia `decorIds` a `BreedDecorIDs` de la madre (S149)
8. Dispara `GameEvents.RegistryChanged(registry)` → persistencia automática
9. Retorna true

## Ciclo de TryHatch

1. Valida padres existen
2. Verifica IsReady(mother) → si no, retorna NotReady
3. Valida tabla de odds
4. Deduce Minerita: `Wallet.TrySpend(Currency.Minerita, cost, "hatch")` → si falla, retorna InsufficientMinerita
5. Llama `HatchLocally(motherID, fatherID)`
6. Retorna Hatched

## HatchLocally (S149, ajustado S151)

1. Lee `BreedDecorIDs` de la madre y limpia el estado de cría en ambos padres (`ClearBreedState`).
2. Resuelve cada ID de decoración a `BreedingDecorSO` consultando `BreedingController.DecorDatabase` (`Get(id)`). S151: ya no convierte a `BreedingModifier` aquí; la lista de `BreedingDecorSO` va directo a `BreedingService.Breed`.
3. Llama `BreedingService.Breed(motherID, fatherID, registry, database, odds, decors)` → CreatureDNA hijo. Si devuelve null, actualiza `status` y dispara `RegistryChanged`.
4. Asigna nombre (`CreatureNameBank.GetRandomName()`), `Stamp()` y `BirthDay` = día actual de GameClock.
5. Llama `CreatureGrowth.Hatch(child)` y lo registra en el registry.
6. Agrega el ID del hijo a `ChildrenIDs` de ambos padres.
7. Dispara `GameEvents.BreedingCompleted(m, f, child)` y `GameEvents.RegistryChanged(registry)`.
8. **(S149)** Suma 1 a `WorldStateSO.BredTotal` y dispara `GameEvents.WorldStateChanged(world)`. Este total desbloquea decoraciones (`BreedingDecorSO.IsDiscovered`).

## Ciclo de TryHatchEgg (S137)

1. Valida: egg != null, !egg.IsDead, egg.Form == MonchiForm.Egg → si falla, retorna Invalid
2. Consulta costo: `int cost = EggHatchCost`
3. Intenta gastar: `Wallet.TrySpend(Currency.Minerita, cost, "hatch-egg")` → si falla, retorna InsufficientMinerita
4. Cambia forma: `CreatureGrowth.Hatch(egg)`
5. Fija BirthDay: `egg.BirthDay = GameClock.Instance != null ? GameClock.Instance.Day : 1`
6. Dispara eventos:
   - `GameEvents.RegistryChanged(registry)` → persistencia
   - `GameEvents.CreatureFormChanged(egg)` → MonchiVisualizer reconstruye visual
7. Retorna Hatched

**Diferencia vs TryHatch:**
- TryHatch: cría + eclosión de huevo de padres (HatchCost consulta a tabla de herencia)
- TryHatchEgg: eclosión de huevo suelto (EggHatchCost es base fijo)
- Ambos disparan CreatureFormChanged (S137) solo en TryHatchEgg; `HatchLocally` no dispara FormChanged

## ValidateParents

Checks:
- Existen en registry
- CreatureAvailability.IsFree() (no en expedición, no ocupados)
- Mother es Female, Father es Male
- Ambos < MaxBreedCount (constante en BreedingService)

Retorna false + LogError si algo falla.

## HatchResult Enum

```csharp
public enum HatchResult
{
    Hatched              = 0,
    NotReady             = 1,
    InsufficientMinerita = 2,
    Invalid              = 3,
}
```

Definido en CreatureEnums (introducido S131).

## ClearBreedState (static privado)

```csharp
private static void ClearBreedState(CreatureDNA dna)
{
    dna.BusyState      = BusyReason.None;
    dna.BreedReadyAt   = 0;
    dna.BreedPartnerID = "";
    dna.BreedDecorIDs  = new List<string>();   // S149
}
```

Reutilizado en StartBreeding cleanup, CancelBreeding, CancelAllBreeding y HatchLocally.

## Cambios S151

- `HatchLocally` pasa `List<BreedingDecorSO>` a `BreedingService.Breed` (antes convertía a `BreedingModifier`). Las decoraciones acreditan cada parte en `CreatureDNA.Origins`.

## Cambios S149

- `StartBreeding` acepta `decorIds` y los guarda en `BreedDecorIDs` de la madre.
- `HatchLocally` aplica las decoraciones a la tirada de herencia.
- `HatchLocally` incrementa `WorldStateSO.BredTotal` y dispara `WorldStateChanged`.
- `ClearBreedState` limpia `BreedDecorIDs`.

## Cambios S137

**TryHatchEgg() — NUEVO:**
```csharp
public HatchResult TryHatchEgg(CreatureDNA egg)
{
    if (egg == null || egg.IsDead || egg.Form != MonchiForm.Egg)
        return HatchResult.Invalid;

    int cost = EggHatchCost;
    if (!Wallet.TrySpend(Currency.Minerita, cost, "hatch-egg"))
        return HatchResult.InsufficientMinerita;

    CreatureGrowth.Hatch(egg);
    egg.BirthDay = GameClock.Instance != null ? GameClock.Instance.Day : 1;
    GameEvents.RegistryChanged(registry);
    GameEvents.CreatureFormChanged(egg);
    return HatchResult.Hatched;
}
```

**EggHatchCost — NUEVA propiedad:**
```csharp
public int EggHatchCost
{
    get
    {
        var odds = BreedingController.Instance != null ? BreedingController.Instance.InheritanceOdds : null;
        return odds != null ? odds.HatchCostBase : 10;
    }
}
```

**Contexto:** En S137, huevos se ponen como criaturas en el registro (no dependen de padres específicos). La incubadora los eclosiona de uno en uno. TryHatchEgg es el nuevo flow para eso.

## Cambios S131

**Renombrado:** AsyncBreedingService → IncubationService (cambio de paradigma).

**Arquitectura antes (S130 y anteriores):**
- AsyncBreedingService llamaba Cloud Code endpoints
- Cría async + server-side egg incubation
- Cliente solo consultaba estado

**Arquitectura ahora (S131 HC-4):**
- IncubationService es local síncrono
- StartBreeding inicia localmente (padres marcados, energía deducida)
- Huevo espera BreedReadyAt (tiempo real de GameClock)
- TryHatch hatcha localmente vía BreedingService.Breed
- Sin Cloud Code, sin buzón de estado, sin async Task

**Persistencia:**
- BreedingCompleted y RegistryChanged disparan SaveSystem.SaveDatabase via GameManager
- World state (GameClock.Day/MinuteOfDay) persiste vía WorldStateChanged → SaveWorldState

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/09 - Active Context]] (S137: ciclo de vida, huevos)
- [[BreedingController]] — API wrapper (StartBreeding, TryHatch, TryHatchEgg, etc.)
- [[BreedingService]] — lógica de herencia (método static Breed)
- [[GameClock]] — lee TotalMinutes para BreedReadyAt
- [[CreatureRegistrySO]] — acceso a padres/hijos
- [[CreatureDatabaseSO]] — resolución de partes
- [[InheritanceOddsTableSO]] — odds + HatchCost
- [[GameEvents]] — dispara RegistryChanged, BreedingCompleted, CreatureFormChanged (S137), WorldStateChanged (S149)
- [[GameManager]] — proporciona registry, database
- [[Wallet]] — deduce Minerita en TryHatch / TryHatchEgg
- [[NeedsState]] — deduce energía en StartBreeding
- [[BreedingDecorDatabaseSO]], [[BreedingDecorSO]] — decoraciones que modifican la herencia (S149)
- [[WorldStateSO]] — `BredTotal` (S149)

## Conexiones

**Entrada:**
- Inyectado en BreedingController
- Métodos llamados desde BreedingContainer UI, IncubatorContainer (S137), y dev console
- Eventos GameEvents.OnExpeditionReturned pueden triggerar CancelAllBreeding

**Salida:**
- `GameEvents.RegistryChanged()` → persistencia
- `GameEvents.BreedingCompleted()` → notificaciones
- `GameEvents.CreatureFormChanged()` (S137) → re-armado visual
- `GameEvents.WorldStateChanged()` (S149) → persistencia de `BredTotal`
- Mutaciones en CreatureDNA (BusyState, BreedReadyAt, BreedDecorIDs, ChildrenIDs, Form, Explorations)

## Notas (S137 HC-4 + Ciclo de Vida)

- **Timing:** BreedReadyAt usa TotalMinutes absoluto (evita edge cases de rollover de día). Comparación simple `TotalMinutes >= BreedReadyAt`.
- **Energía vs Minerita:** StartBreeding deduce energía (recurso abundante), TryHatch/TryHatchEgg deducen Minerita (scarcity mecánica). Separación clara de costos.
- **Sin rollback:** Si HatchLocally falla parcialmente (e.g., Registry.Register falla), padres ya están limpios. Regla: cleanup antes de operación destructiva.
- **Null-safe:** Si odds==null, log error y return (no crasha).
- **MaxBreedCount:** Constante en BreedingService (4). Cumple con "muerte permanente" — generaciones limitadas.
- **TryHatchEgg S137:** Desacoplado de breeding pair. Huevos sueltos del registro se eclosionan con costo fijo (EggHatchCost).
- **Decoraciones S149:** Solo la madre guarda `BreedDecorIDs`; el cruce las consume en `HatchLocally`.
