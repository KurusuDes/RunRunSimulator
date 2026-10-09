---
tags: [script, system, expedition, bridge, monetization]
---

# ExpeditionBridge.cs

**Ruta:** `Systems/Expedition/ExpeditionBridge.cs`

**Responsabilidad:** Orquestador de las transiciones tienda↔arena de la bajada. Cobra el costo de bajada en Dabloons, espera el flush a la nube antes de cambiar de escena y, al volver, aplica el resultado: Minerita por botín (tasa de `BrawlRunRulesSO`), bajas (si permadeath), evolución por exploración y el evento `ExpeditionReturned` con el payload completo para la tarjeta de retorno.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `cloudSync` | `CloudSyncService` | — | Espera `StartupSyncDone` al volver |
| `syncTimeoutSeconds` | `float` | 20 | Tope de espera de sync al volver |
| `departFlushTimeout` | `float` | 5 | Tope de espera del flush antes de bajar |
| `permadeathEnabled` | `bool` | false | Si true, mata caídos y, si se perdió, a todo el equipo |
| `runRules` | `BrawlRunRulesSO` | — | `DescentCost` (cobro), `MineritaPerLoot` (conversión al volver) y activación de `Current` |

## Eventos y Métodos

| Miembro | Descripción |
|---------|-------------|
| `OnDepartureRequested` (static) | `Action<IReadOnlyList<string>>`; lo dispara `RequestDeparture` |
| `RequestDeparture(ids)` (static) | Dispara el evento; lo llama `ExpeditionPanelUITK` |
| `Depart(ids)` | Cobra `DescentCost` con `Wallet.TrySpend(Dabloons)`. Si falla, avisa y no baja. Si pasa, inicia `DepartRoutine` |
| `Depart()` | Botón Odin "Salir de expedición" (solo en Play); llama `Depart(null)` |

## Flujo de Bajada (`DepartRoutine`)

1. Si existe `GameManager.Instance`, espera `FlushToCloudAsync()` hasta `departFlushTimeout` (tiempo unscaled).
2. Libera el cursor.
3. `ExpeditionHandoff.GoToArena(ids)`.

## Flujo de Vuelta (`ApplyResult`, desde `Start` si hay resultado)

1. Espera `cloudSync.StartupSyncDone` hasta `syncTimeoutSeconds`.
2. `TryConsumeResult`. Si no hay resultado, sale.
3. Tasa = `runRules.MineritaPerLoot` (si `runRules` falta, tasa 1 y warning). Material = `PlayerSecured` (ya descontada la pérdida de la derrota). `Minerita += material × tasa` con `Wallet.Add`.
4. Si `permadeathEnabled`: `CreatureLifecycle.Kill` a los `FallenIds`; si `Lost`, a todo `TeamIds`. IDs no encontrados o ya muertos se ignoran.
5. El equipo se arma con todos los DNA vivos de `TeamIds` (también caídos o en derrota). Si no hay derrota: `CreatureGrowth.RecordExploration` por cada miembro no caído. El umbral sale de `BreedingController.LifeStageTable.ExplorationsToEvolve` (3 si no hay tabla). Los que evolucionan van a `evolvedIds`; los que estaban en Slime marcan `touched`.
6. Si `touched`: `GameEvents.RegistryChanged(registry)`. Por cada evolucionado: `GameEvents.CreatureFormChanged(dna)`.
7. `GameEvents.ExpeditionReturned(ExpeditionReturn{...})` con `MineritaLost = MaterialLost × tasa`, `Team`, `EvolvedIds` y `ExplorationsToEvolve`.

## Notas

- El cobro del costo ocurre en `Depart`, antes del flush: si el flush falla, el costo ya está cobrado.
- `BrawlRunRulesSO.Current` se activa en `OnEnable` (tienda) y se desactiva en `OnDisable`, para que el panel pueda mostrar el costo antes de entrar a la arena.
- `Depart` no revisa el horario: esa guarda vive solo en el botón de `ExpeditionPanelUITK`.
- Con derrota, la Minerita se paga sobre el botín que quedó tras la pérdida.
- S145: la tasa de Minerita por botín ya no es un campo de este script (`mineritaPerMaterial` se quitó): vive en `BrawlRunRulesSO.MineritaPerLoot`.

## Conexiones

- [[ExpeditionHandoff]] — `GoToArena`, `TryConsumeResult`, `ReturnToStore`
- [[ExpeditionPanelUITK]] — llama `RequestDeparture`
- [[ExpeditionReturnCardUITK]] — consume `ExpeditionReturned` (tarjeta de resultado)
- [[BrawlRunDirector]] — vuelve con `ReturnToStore(run.ToResult())`
- [[BrawlRunRulesSO]] — `DescentCost`, `MineritaPerLoot`, `Activate`/`Deactivate`
- [[GameManager]] — `FlushToCloudAsync`, `Registry`
- [[CloudSyncService]] — `StartupSyncDone`
- [[Wallet]] — `TrySpend(Dabloons)`, `Add(Minerita)`
- [[CreatureLifecycle]], [[CreatureGrowth]], [[BreedingController]] — muerte, exploración, tabla de etapas
- [[GameEvents]] — `RegistryChanged`, `CreatureFormChanged`, `ExpeditionReturned`
