---
tags: [script, core, handoff, expedition, time-scale]
---

# ExpeditionHandoff.cs

**Ruta:** `Core/ExpeditionHandoff.cs`

**Responsabilidad:** Puente estático entre la escena de tienda y la de arena. Lleva el elenco elegido y la semilla de la bajada al entrar, y el resultado al volver. La carga de escena y el reset de tiempo los hace [[SceneFlow]] (S152); este archivo solo guarda datos de la bajada.

**Vinculado a:**
- [[Index/23 - Arena Sandbox y Expedicion]]
- [[Index/32 - Demo Brawl 3v3 arcade]]

## Tipos

**`ExpeditionResult`** (resultado de la bajada, lo arma `BrawlRun.ToResult()`): `Seed`, `Winner`, `PlayerSecured`, `MaterialLost`, `RivalSecured`, `Floors`, `Lost`, `FallenIds`, `Fallen`, `TeamIds`, `Combats`.

**`ExpeditionReturn`** (payload de `GameEvents.ExpeditionReturned`): `Seed`, `Winner`, `PlayerSecured`, `RivalSecured`, `MineritaGained`, `MineritaLost`, `Fallen`, `Floors`, `Lost`, `Team` (`List<CreatureDNA>`), `EvolvedIds` (`List<string>`), `ExplorationsToEvolve` (`int`).

## Estado Estático

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `CameFromStore` | `bool` | Llegó desde la tienda; lo lee `BrawlRunDirector.Awake` |
| `HasResult` | `bool` | Hay resultado pendiente de consumir |
| `Result` | `ExpeditionResult` | Último resultado |
| `RunSeed` | `int` | Semilla de la bajada (`TickCount & 0x7fffffff` al bajar) |
| `SelectedIds` | `IReadOnlyList<string>` | Elenco elegido en el panel |

`ResetState()` (`SubsystemRegistration`) limpia todo el estado al arrancar.

## Métodos

| Método | Descripción |
|--------|-------------|
| `GoToArena(ids)` | Copia los IDs, `CameFromStore = true`, `HasResult = false`, nueva `RunSeed`, `SceneFlow.GoToArena()` |
| `ReturnToStore(result?)` | Con resultado: guarda `Result` y `HasResult = true`. Sin resultado: `CameFromStore = false`. Limpia IDs y `SceneFlow.GoToStore()` |
| `TryConsumeResult(out result)` | Devuelve el resultado y limpia `HasResult`, `CameFromStore` y los IDs |

## Time Management (movido a SceneFlow)

S138: `ResetTime()` y la captura de `fixedDeltaTime` vivían aquí. **S152:** pasaron a [[SceneFlow]], que restaura `timeScale` y `fixedDeltaTime` antes de cada carga de escena.

La arena escala `timeScale` (4x). `MMTimeManager` multiplica `fixedDeltaTime` por ese factor, así que restaurar ambos evita física distorsionada al volver a la tienda.

## Conexiones

- [[SceneFlow]] — nombres de escena, carga y reset de tiempo (S152)
- [[ExpeditionBridge]] — `GoToArena`, `TryConsumeResult`, `ReturnToStore`; arma `ExpeditionReturn` al volver
- [[BrawlRun]] — `ToResult()` produce el `ExpeditionResult`
- [[BrawlRunDirector]] — lee `CameFromStore`, `RunSeed`, `SelectedIds`; vuelve con `ReturnToStore`
- [[ExpeditionReturnCardUITK]] — consume el payload `ExpeditionReturn` completo
- [[ArenaRunDirector]], [[ArenaSandbox]] — consumidores de la bajada por pisos
- [[MMTimeManager]] — escala de tiempo afectada por el reset de `SceneFlow`

## Notas

- `ReturnToStore` con resultado no toca `CameFromStore`; lo limpia `TryConsumeResult` al consumir el resultado.
- Sin IDs (`GoToArena(null)`) la arena no tiene equipo y el director vuelve a la tienda.
- S145: `ExpeditionResult` suma `MaterialLost` y `ExpeditionReturn` suma `MineritaLost`, `Team`, `EvolvedIds` y `ExplorationsToEvolve`. El toast de retorno de `InfoOverlayUITK` ya no existe: la tarjeta lee el payload entero.
- S148: `ExpeditionResult` suma `Combats` (combates resueltos en la bajada). `ExpeditionBridge` lo suma a `CreatureDNA.Battles` de cada MoriMochi del equipo.
- S152: sin constantes de escena ni `ResetTime` propios; los nombres viven en `SceneFlow`.
