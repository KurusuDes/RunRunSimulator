---
tags: [script, core, handoff, expedition, time-scale]
---

# ExpeditionHandoff.cs

**Ruta:** `Core/ExpeditionHandoff.cs`

**Responsabilidad:** Puente estático entre la escena de tienda (`GameScene`) y la de arena (`BrawlDemo`). Lleva el elenco elegido y la semilla de la bajada al entrar, y el resultado al volver. Antes de cada cambio de escena restaura `timeScale` y `fixedDeltaTime` (S138).

**Vinculado a:**
- [[Index/23 - Arena Sandbox y Expedicion]]
- [[Index/32 - Demo Brawl 3v3 arcade]]

## Tipos

**`ExpeditionResult`** (resultado de la bajada): `Seed`, `Winner`, `PlayerSecured`, `RivalSecured`, `Floors`, `Lost`, `FallenIds`, `Fallen`, `TeamIds`.

**`ExpeditionReturn`** (payload de `GameEvents.ExpeditionReturned`): `Seed`, `Winner`, `PlayerSecured`, `RivalSecured`, `MineritaGained`, `Fallen`, `Floors`, `Lost`.

## Estado Estático

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `CameFromStore` | `bool` | Llegó desde la tienda; lo lee `BrawlRunDirector.Awake` |
| `HasResult` | `bool` | Hay resultado pendiente de consumir |
| `Result` | `ExpeditionResult` | Último resultado |
| `RunSeed` | `int` | Semilla de la bajada (`TickCount & 0x7fffffff` al bajar) |
| `SelectedIds` | `IReadOnlyList<string>` | Elenco elegido en el panel |
| `defaultFixedDeltaTime` | `float` | Capturado en `ResetState()` (S138) |

Constantes: `StoreScene = "GameScene"`, `ArenaScene = "BrawlDemo"`.

## Métodos

| Método | Descripción |
|--------|-------------|
| `GoToArena(ids)` | Copia los IDs, `CameFromStore = true`, `HasResult = false`, nueva `RunSeed`, `ResetTime()`, `LoadScene(ArenaScene)` |
| `ReturnToStore(result?)` | Con resultado: guarda `Result` y `HasResult = true`. Sin resultado: `CameFromStore = false`. Limpia IDs, `ResetTime()`, `LoadScene(StoreScene)` |
| `TryConsumeResult(out result)` | Devuelve el resultado y limpia `HasResult`, `CameFromStore` y los IDs |
| `ResetTime()` (privado) | `timeScale = 1`; restaura `fixedDeltaTime` (S138) |
| `ResetState()` (privado, `SubsystemRegistration`) | Limpia todo el estado y captura `fixedDeltaTime` |

## S138: Time Management

**ResetState():** captura `fixedDeltaTime` al arrancar.

**ResetTime():** antes de cambiar de escena.

```csharp
Time.timeScale = 1f;
if (defaultFixedDeltaTime > 0f) Time.fixedDeltaTime = defaultFixedDeltaTime;
```

La arena escala `timeScale` (4x). `MMTimeManager` multiplica `fixedDeltaTime` por ese factor, así que restaurar ambos evita física distorsionada al volver a la tienda.

## Conexiones

- [[ExpeditionBridge]] — `GoToArena`, `TryConsumeResult`, `ReturnToStore`
- [[BrawlRunDirector]] — lee `CameFromStore`, `RunSeed`, `SelectedIds`; vuelve con `ReturnToStore`
- [[ArenaRunDirector]], [[ArenaSandbox]] — consumidores de la bajada por pisos
- [[MMTimeManager]] — escala de tiempo afectada por `ResetTime`

## Notas

- `ReturnToStore` con resultado no toca `CameFromStore`; lo limpia `TryConsumeResult` al consumir el resultado.
- Sin IDs (`GoToArena(null)`) la arena no tiene equipo y el director vuelve a la tienda.
