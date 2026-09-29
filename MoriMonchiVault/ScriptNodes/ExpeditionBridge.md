---
tags: [script, system, expedition, bridge]
---

# ExpeditionBridge

**Ruta:** `Systems/Expedition/ExpeditionBridge.cs`

**Responsabilidad:** Componente MonoBehaviour en GameScene que orquesta transiciones tienda ↔ arena. Expone evento estático `OnDepartureRequested` y método `Depart()` para iniciar viaje con equipo elegido. Al retornar, espera startup cloud y aplica rewards: suma **Minerita** vía [[Wallet]], mata criaturas caídas vía [[CreatureLifecycle]], registra exploraciones y evoluciona slimes → adultos vía [[CreatureGrowth]] **(S137 NUEVO)**. **S128:** suma Minerita vía `Wallet.Add()` (puerta única). **S129:** matar criaturas es responsabilidad de `CreatureLifecycle`, no toca `Needs` ni stats. **S137:** recordar exploraciones para cada slime, desencadenar evolución si alcanza threshold.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|----------|
| `cloudSync` | `CloudSyncService` | Ref a sincronización (esperar StartupSyncDone) |
| `syncTimeoutSeconds` | `float` | Timeout máximo esperando cloud (default 20s) |
| `departFlushTimeout` | `float` | Timeout flush local antes de arena (default 5s) |
| `permadeathEnabled` | `bool` | Activar muerte permanente (S129) |

## Evento Estático

```csharp
public static event Action<IReadOnlyList<string>> OnDepartureRequested;
public static void RequestDeparture(IReadOnlyList<string> ids) => OnDepartureRequested?.Invoke(ids);
```

Disparado por `ExpeditionPanelUITK` al hacer clic "Ir" con IDs de criaturas. Llamado por AutoPlayer.Step7_Departure (S137).

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `void Depart()` | [Button] Dev; ejecuta Depart(null) |
| `void Depart(IReadOnlyList<string> ids)` | Inicia DepartRoutine: flush cloud (timeout), desbloquea cursor, dispara ExpeditionHandoff.GoToArena(ids) |

## Ciclo de Vida

### OnEnable/OnDisable

- OnEnable: suscribe a `OnDepartureRequested`
- OnDisable: desuscribe

### Start

Si `ExpeditionHandoff.HasResult`: inicia `ApplyResult()` coroutine.

### DepartRoutine

```
1. Si GameManager existe: FlushToCloudAsync() con timeout (5s)
2. Desbloquea cursor (visible=true, lockState=None)
3. ExpeditionHandoff.GoToArena(ids)
```

### ApplyResult (Coroutine, S129 + S137)

```
1. Esperar cloudSync.StartupSyncDone (max syncTimeoutSeconds)
2. TryConsumeResult() — lee ExpeditionResult, limpia flags
3. Minerita = 0 si result.Lost, else result.PlayerSecured
4. Si Minerita > 0: Wallet.Add(Currency.Minerita, material, "expedition")
   (un solo evento InventoryChanged automático)

5. Matar criaturas caídas (result.FallenIds, si permadeathEnabled):
   - Por cada id en FallenIds:
     - Si dna existe y viva: CreatureLifecycle.Kill(dna)
     (dispara OnCreatureDeparted + RegistryChanged)
   - Si resultado.Lost (perdió): matar también todos en result.TeamIds
   
6. NUEVO (S137): Registrar exploraciones y evolucionar slimes:
   - Consulta threshold: BreedingController.LifeStageTable.ExplorationsToEvolve (default 3)
   - Por cada id en result.TeamIds (vivos, no caídos):
     - Si no perdió: CreatureGrowth.RecordExploration(dna, toEvolve)
       - Incrementa dna.Explorations++
       - Si Explorations >= toEvolve: Form = Adult (retorna true)
     - Si evolucionó, agrega a lista evolvedDnas
   
7. Si hubo cambios: GameEvents.RegistryChanged(registry) (persistencia)
8. Por cada dna en evolvedDnas: GameEvents.CreatureFormChanged(dna) (re-arma visual)
9. Dispara GameEvents.ExpeditionReturned(expReturn) con summary
10. Debug.Log con piso, material, caídos, evolucionados
```

## Flujo Tienda ↔ Arena (S137 con ciclo de vida)

```
GameScene (Tienda)
  ↓ ExpeditionPanelUITK: elegir hasta 3 criaturas (solo slimes/adultos, no eggs)
  ↓ Botón "Ir"
ExpeditionBridge.RequestDeparture(ids)
  ↓ Depart(ids) → DepartRoutine
    Flush cloud + ExpeditionHandoff.GoToArena(ids)
  ↓ Scene Load
ArenaSandbox (Arena)
  ↓ ArenaRunDirector: ArenaRun(RunSeed, SelectedIds)
  ↓ Ciclo piso: juega → decide Continuar/Retirarse
  ↓ Retreat() → ExpeditionHandoff.ReturnToStore(result)
  ↓ Scene Load
GameScene (Tienda, Start)
  ↓ ApplyResult() coroutine
    Wallet.Add Minerita
    + CreatureLifecycle.Kill(FallenIds) si permadeath
    + CreatureGrowth.RecordExploration() (S137) + CreatureFormChanged para evolucionados (S137)
    + GameEvents.RegistryChanged (persistencia)
  ↓ GameEvents.ExpeditionReturned → UI actualiza
```

## Cambios S137

**ApplyResult() — Evolución de slimes (línea 108-134 NUEVO):**

```csharp
int evolved = 0;
var evolvedDnas = new List<CreatureDNA>();

if (registry != null && !result.Lost && result.TeamIds != null)
{
    int toEvolve = BreedingController.Instance != null && BreedingController.Instance.LifeStageTable != null
        ? BreedingController.Instance.LifeStageTable.ExplorationsToEvolve
        : 3;

    foreach (var id in result.TeamIds)
    {
        if (!registry.TryGet(id, out var dna) || dna == null || dna.IsDead) continue;
        if (result.FallenIds != null && result.FallenIds.Contains(id)) continue;

        bool wasSlime = dna.Form == MonchiForm.Slime;
        if (CreatureGrowth.RecordExploration(dna, toEvolve))
        {
            evolved++;
            evolvedDnas.Add(dna);
        }
        if (wasSlime) touched = true;
    }
}

if (touched) GameEvents.RegistryChanged(registry);

foreach (var dna in evolvedDnas) GameEvents.CreatureFormChanged(dna);
```

**Contexto:** Ciclo de vida S137: slimes ganados exploraciones en arena. Cuando alcanzan threshold (default 3), evolucionan a Adult. Este bloque:
- Consulta threshold de `LifeStageTable.ExplorationsToEvolve`
- Por cada miembro del equipo vivo (no caído, no muerto):
  - Si no perdió la expedición: llama `CreatureGrowth.RecordExploration()` 
  - Si retorna true (evolucionó), agrega a `evolvedDnas` para dispatch de evento
- Dispara `CreatureFormChanged` para cada evolucionado (MonchiVisualizer re-arma visual Slime → Adult)

**Impacto:**
- Slimes ahora progresan hacia adultos en expediciones
- Visual se re-arma automáticamente al retorno (Slime → Adult)
- Persistencia automática vía RegistryChanged

## Cambios S129

- **ELIMINADO:** Aplicar delta vida (`HealthById` removido de ExpeditionResult)
- **ELIMINADO:** Tocar `dna.Needs`
- **AGREGADO:** `CreatureLifecycle.Kill()` para cada ID en `result.FallenIds`
- **CAMBIO:** `ExpeditionResult.FallenIds` → lista de IDs muertos (antes era diccionario de deltas)
- **CAMBIO:** `ExpeditionResult.TeamIds` → nuevos, lista de IDs del equipo

## Invariantes S137

- Material anulado si `result.Lost`
- Criaturas caídas marcadas `IsDead` vía `CreatureLifecycle`
- Exploración solo se registra si equipo vive (no si resultado.Lost)
- Threshold consultado a `LifeStageTable.ExplorationsToEvolve` (default 3) para seguridad
- CreatureFormChanged disparado para CADA evolucionado (puede ser múltiples por expedición)
- Cargas todas criaturas caídas, no solo algunas
- Timeout cloud: evita bloqueos indefinidos
- Cursor desbloqueado al partir (herencia evitada)

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/24 - Puente Tienda-Arena]]
- [[Index/26 - Plan H0 - Bajada por pisos]] (S124)
- [[Index/09 - Active Context]] (S137: ciclo de vida)
- [[Index/28 - Cimientos y camino a Game Ready]]

**Conexiones:** 
- [[ExpeditionHandoff]], [[ExpeditionPanelUITK]] 
- [[CloudSyncService]], [[GameManager]], [[Wallet]]
- [[CreatureRegistrySO]], [[GameEvents]]
- [[InfoOverlayUITK]], [[ArenaRunDirector]]
- [[CreatureLifecycle]] (matar caídos)
- [[CreatureGrowth]] (S137: RecordExploration)
- [[BreedingController]] (S137: LifeStageTable.ExplorationsToEvolve)
- [[AutoPlayer]] (S137: llamador de RequestDeparture)
