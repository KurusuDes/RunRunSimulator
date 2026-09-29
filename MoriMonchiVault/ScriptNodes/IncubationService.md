---
tags: [script, breeding-system, local-incubation]
---

# IncubationService

**Ruta:** `Systems/Breeding/IncubationService.cs` (renombrado de AsyncBreedingService en S131)

**Responsabilidad:** Gestor de cría local síncrona (sin Cloud Code). Reemplaza la arquitectura async de CloudCode por flujo local. Métodos públicos: `StartBreeding(motherID, fatherID)` (marca padres como Breeding, deduce energía, fija BreedReadyAt), `TryHatch(motherID, fatherID)` (verifica listo, deduce Minerita, hatcha vía BreedingService.Breed), `TryHatchEgg(CreatureDNA egg)` **(S137 NUEVO)** (intenta eclosionar huevo suelto), `IsReady(mother)`, `HatchCostFor()`. Dispara `GameEvents.RegistryChanged()` y `GameEvents.CreatureFormChanged()` (S137) para persistencia. Resuelve `registry` y `database` desde `GameManager.Instance` en Awake.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|----------|
| `energyCostPerParent` | float | Energía deducida al iniciar cría (default 20). `NeedsState.SpendEnergy()` |
| `status` | string | Display (ReadOnly, debug status message) |

## Métodos Públicos

| Método | Firma | Retorna | Descripción |
|--------|-------|---------|-------------|
| `StartBreeding` | `(string motherID, string fatherID)` | `bool` | Inicia cría local: marca BusyState=Breeding, deduce energía, fija BreedReadyAt = TotalMinutes + BreedDurationMinutes. Retorna true si ok. |
| `TryHatch` | `(string motherID, string fatherID)` | `HatchResult` | Verifica si listo (IsReady), deduce Minerita via HatchCost, hatcha. Retorna Hatched/NotReady/InsufficientMinerita/Invalid. |
| `TryHatchEgg` | `(CreatureDNA egg)` | `HatchResult` | **(S137 NUEVO)** Intenta eclosionar huevo suelto (no acoplado a breeding pair). Valida Form==Egg, deduce EggHatchCost via Wallet.TrySpend, llama CreatureGrowth.Hatch, dispara RegistryChanged + CreatureFormChanged. Retorna Hatched/InsufficientMinerita/Invalid. |
| `CancelBreeding` | `(string motherID, string fatherID)` | `void` | Cancela cría: limpia BusyState, BreedReadyAt, BreedPartnerID en ambos. |
| `CancelAllBreeding` | `()` | `void` | Cancela todas las crías activas (BusyState==Breeding). |
| `IsReady` | `(CreatureDNA mother)` | `bool` | ¿BreedReadyAt > 0 AND GameClock.TotalMinutes >= BreedReadyAt? |
| `HatchCostFor` | `(string motherID, string fatherID)` | `int` | Devuelve costo Minerita para ecloer (consultado a InheritanceOddsTableSO). |
| `EggHatchCost` | `(property)` | `int` | **(S137 NUEVO)** Getter → `odds != null ? odds.HatchCostBase : 10` (costo fijo para eclosionar un huevo suelto). |

## Ciclo de StartBreeding

1. Valida que GameClock esté cargado (Loaded==true)
2. Valida padres: ambos existen, libres (CreatureAvailability.IsFree), genders correctos (Female/Male), no superaron MaxBreedCount
3. Deduce energía: `mother.Needs.SpendEnergy(energyCostPerParent)` + `father.Needs...`
4. Fija timers: `BreedReadyAt = GameClock.Instance.TotalMinutes + odds.BreedDurationMinutes`
5. Marca busy: `BusyState = BusyReason.Breeding` + `BreedPartnerID = partnerId`
6. Dispara `GameEvents.RegistryChanged(registry)` → persistencia automática
7. Retorna true

## Ciclo de TryHatch

1. Valida padres existen
2. Verifica IsReady(mother) → si no, retorna NotReady
3. Deduce Minerita: `Wallet.TrySpend(Currency.Minerita, cost, "hatch")` → si falla, retorna InsufficientMinerita
4. Llama `HatchLocally(motherID, fatherID)`:
   - Limpia BusyState en ambos (ClearBreedState)
   - Llama `BreedingService.Breed(motherID, fatherID, registry, database, odds)` → CreatureDNA hijo
   - Asigna nombre: `child.CustomName = CreatureNameBank.GetRandomName()`
   - Estampa: `child.Stamp()` (timestamp = now)
   - Fija BirthDay: `child.BirthDay = GameClock.Instance.Day`
   - Asigna Form=Egg: `CreatureGrowth.Lay(child)` → Form=Egg, Explorations=0
   - Registra: `registry.Register(child)`
   - Agrega a ChildrenIDs en ambos padres
   - Dispara `GameEvents.BreedingCompleted(m, f, child)` + `GameEvents.RegistryChanged(registry)` + `GameEvents.CreatureFormChanged(child)` (S137)
5. Retorna Hatched

## Ciclo de TryHatchEgg (S137 NUEVO)

1. Valida: egg != null, !egg.IsDead, egg.Form == MonchiForm.Egg → si falla, retorna Invalid
2. Consulta costo: `int cost = EggHatchCost`
3. Intenta gastar: `Wallet.TrySpend(Currency.Minerita, cost, "hatch-egg")` → si falla, retorna InsufficientMinerita
4. Cambia forma: `CreatureGrowth.Hatch(egg)` → egg.Form = Slime, egg.Explorations = 0
5. Fija BirthDay: `egg.BirthDay = GameClock.Instance != null ? GameClock.Instance.Day : 1`
6. Dispara eventos:
   - `GameEvents.RegistryChanged(registry)` → persistencia
   - `GameEvents.CreatureFormChanged(egg)` → MonchiVisualizer reconstruye visual (Egg → Slime)
7. Retorna Hatched

**Diferencia vs TryHatch:**
- TryHatch: cría + eclosión de huevo de padres (HatchCost consulta a tabla de herencia)
- TryHatchEgg: eclosión de huevo suelto (EggHatchCost es base fijo)
- Ambos disparan CreatureFormChanged (S137)

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
}
```

Reutilizado en StartBreeding cleanup y TryHatch cleanup.

## Cambios S137

**TryHatchEgg() — NUEVO (línea 100-124):**
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

**EggHatchCost — NUEVA propiedad (línea 91-98):**
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
- [[GameEvents]] — dispara RegistryChanged, BreedingCompleted, CreatureFormChanged (S137)
- [[GameManager]] — proporciona registry, database
- [[Wallet]] — deduce Minerita en TryHatch / TryHatchEgg
- [[NeedsState]] — deduce energía en StartBreeding

## Conexiones

**Entrada:**
- Inyectado en BreedingController
- Métodos llamados desde BreedingContainer UI, IncubatorContainer (S137), y dev console
- Eventos GameEvents.OnExpeditionReturned pueden triggerar CancelAllBreeding

**Salida:**
- `GameEvents.RegistryChanged()` → persistencia
- `GameEvents.BreedingCompleted()` → notificaciones
- `GameEvents.CreatureFormChanged()` (S137) → re-armado visual
- Mutaciones en CreatureDNA (BusyState, BreedReadyAt, ChildrenIDs, Form, Explorations)

## Notas (S137 HC-4 + Ciclo de Vida)

- **Timing:** BreedReadyAt usa TotalMinutes absoluto (evita edge cases de rollover de día). Comparación simple `TotalMinutes >= BreedReadyAt`.
- **Energía vs Minerita:** StartBreeding deduce energía (recurso abundante), TryHatch/TryHatchEgg deducen Minerita (scarcity mecánica). Separación clara de costos.
- **Sin rollback:** Si HatchLocally falla parcialmente (e.g., Registry.Register falla), padres ya están limpios. Regla: cleanup antes de operación destructiva.
- **Null-safe:** Si odds==null, log error y return (no crasha).
- **MaxBreedCount:** Constante en BreedingService (típicamente 2-3). Cumple con "muerte permanente" — generaciones limitadas.
- **TryHatchEgg S137:** Desacoplado de breeding pair. Huevos sueltos del registro se eclosionan con costo fijo (EggHatchCost).
- **CreatureFormChanged S137:** Disparado en TryHatch (Lay) y TryHatchEgg (Hatch), indica cambio de visual.
