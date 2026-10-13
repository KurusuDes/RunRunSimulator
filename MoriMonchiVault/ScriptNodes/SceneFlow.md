---
tags: [script, core, scene, flow, static]
---

# SceneFlow.cs

**Ruta:** `Core/SceneFlow.cs`

**Responsabilidad:** Dueño único de los nombres de escena del juego y de su carga. Antes de cada cambio de escena restaura `timeScale` y `fixedDeltaTime` (la arena escala el tiempo). Además guarda la bandera de "partida nueva" pedida desde el título. Clase estática, sin estado de escena.

## Constantes

| Constante | Valor | Escena |
|-----------|-------|--------|
| `TitleScene` | `"Title"` | Menú de título |
| `StoreScene` | `"GameScene"` | Tienda (escena base del juego) |
| `ArenaScene` | `"BrawlDemo"` | Arena de bajada |

## Estado Estático

| Campo | Descripción |
|-------|-------------|
| `defaultFixedDeltaTime` | Capturado en `ResetState()` al arrancar |
| `newGameRequested` | Bandera de partida nueva; se consume una sola vez |

## Métodos

| Método | Descripción |
|--------|-------------|
| `Load(string scene)` | `ResetTime()` + `SceneManager.LoadScene(scene)` |
| `GoToTitle()`, `GoToStore()`, `GoToArena()` | Atajos a `Load` con la constante de escena |
| `RequestNewGame()` | Marca la bandera y va a la tienda |
| `ConsumeNewGameRequest()` | Devuelve la bandera y la limpia |
| `ResetTime()` (privado) | `timeScale = 1`; restaura `fixedDeltaTime` si fue capturado |
| `ResetState()` (privado, `SubsystemRegistration`) | Limpia la bandera y captura `fixedDeltaTime` |

## Flujo de Partida Nueva (S152)

1. Título: botón "nueva partida" → confirmación → `RequestNewGame()`.
2. Entra a `StoreScene` con la bandera encendida.
3. `StarterKitService` llama `ConsumeNewGameRequest()`; si es `true`, espera `CloudSyncService.ResetProgressAsync()` y después aplica el kit.

## Historial

**S138:** `ResetTime()` y la captura de `fixedDeltaTime` vivían en `ExpeditionHandoff`.
**S152:** Nombres de escena y `ResetTime()` pasan a `SceneFlow`; `ExpeditionHandoff` delega en `GoToArena()` / `GoToStore()`.

## Conexiones

- [[ExpeditionHandoff]] — delega la carga de escena en `GoToArena()` y `GoToStore()`
- [[AutoPlayer]] — compara la escena activa con `ArenaScene` y `StoreScene`
- [[TitleScreenUITK]] — `GoToStore()` (continuar) y `RequestNewGame()` (nueva)
- [[PauseMenuUITK]] — `GoToTitle()`
- [[StarterKitService]] — `ConsumeNewGameRequest()`
