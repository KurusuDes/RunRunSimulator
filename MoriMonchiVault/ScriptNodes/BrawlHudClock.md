---
tags: [script, ui, brawl, hud, clock]
---

# BrawlHudClock.cs

**Ruta:** `UI/BrawlHudClock.cs`

**Responsabilidad:** Reloj y control de velocidad del HUD Brawl, extraídos de `BrawlHud`. Es una clase plana (no MonoBehaviour) que crea y maneja `BrawlHud`: muestra el cronómetro de la partida o de la sala de prueba (con `+m:ss` en muerte súbita) y resalta el botón de velocidad activo (1x, 2x, 4x). No cambia el estado de la partida: solo lee `BrawlMatch`, `BrawlTrialRoom` y `ArenaClockControl`.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `BrawlHudClock(clock, trial)` | Constructor. `clock` puede ser null (sin botones de velocidad) |
| `Bind(root)` | Busca el label `brawl-timer` y los botones `brawl-speed-1`, `brawl-speed-2`, `brawl-speed-4`. Sin `clock`, los oculta. Con `clock`, cada click llama `clock.Set(valor)` |
| `Unbind()` | Desuscribe los clicks y suelta las referencias |
| `Refresh(match)` | Actualiza el tiempo (`RefreshTime`) y la velocidad activa (`RefreshSpeed`) |

## Comportamiento

- **Sala de prueba activa:** muestra `trial.TimeLeft` redondeado hacia arriba.
- **Muerte súbita:** muestra `+m:ss` con los segundos transcurridos y clase `brawl-timer--sudden`. También aplica si la partida terminó por tiempo (`Ended` con `TimeLeft <= 0`).
- **Partida normal:** muestra `match.TimeLeft` redondeado hacia arriba.
- **Velocidad:** resalta (`brawl-btn--on`) el botón cuyo valor coincide con `ArenaClockControl.Speed`.
- Solo reescribe el texto cuando cambian los segundos y solo reclasifica cuando cambia la velocidad.

## Conexiones

- [[BrawlHud]] — crea la instancia en `TryBind`, la une en `Bind`, la suelta en `Unbind` y la refresca en `Update`
- [[ArenaClockControl]] — `Set` y `Speed` (velocidad de la arena)
- [[BrawlTrialRoom]] — `Active` y `TimeLeft` de la sala de prueba
- [[BrawlMatch]] — `Phase`, `TimeLeft`, `SuddenDeathElapsed`
- [[BrawlMatchPhase]] — `BrawlEnums.cs`

## Notas

- Los botones de velocidad son herramienta de desarrollo: si no hay `ArenaClockControl`, quedan ocultos.
- Textos de tiempo sin localizar (formato numérico).
