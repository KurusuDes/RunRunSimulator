---
tags: [script, ui, uitk, toys, tug, hud]
---

# TugMeterHUD.cs

**Ruta:** `UI/TugMeterHUD.cs`

**Responsabilidad:** Medidor HUD del tirón de juguete. Escucha los eventos de `PlayerToyTug` y dibuja una barra bidireccional (de -1 a 1 se mapea a 0-100 %), con clase "perdiendo" cuando el progreso es negativo, y un mensaje de resultado que se oculta a los 800 ms. Solo presenta: no decide nada.

## Comportamiento

- `TugStarted`: muestra el medidor con texto "mash" y fill 50 %.
- `TugChanged(progress)`: actualiza el fill; clase `tug-meter--losing` si `progress < 0`.
- `TugEnded(playerWon)`: texto ganado/perdido y oculta tras 800 ms (`ResultHideMs`).

## Claves de localización

`ui.toy.tug.mash`, `ui.toy.tug.won`, `ui.toy.tug.lost`.

## Conexiones

- [[PlayerToyTug]] — eventos `TugStarted`, `TugChanged`, `TugEnded`
- [[UiPanels]] — `RootOf(document)`
