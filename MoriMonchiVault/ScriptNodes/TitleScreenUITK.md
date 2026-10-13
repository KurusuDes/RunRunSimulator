---
tags: [script, ui, uitk, title, menu]
---

# TitleScreenUITK.cs

**Ruta:** `UI/TitleScreenUITK.cs`

**Responsabilidad:** Menú de la escena de título. Presenta el logo animado (letras por línea con entrada escalonada y oleaje), la tagline y los botones de entrada. Según el botón elegido sale a la tienda (continuar), abre confirmación y pide partida nueva, abre ajustes o cierra el juego. No persiste nada: la partida nueva la resuelve [[SceneFlow]] y [[StarterKitService]].

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Root del título |
| `settings` | `SettingsPanelUITK` | Panel de ajustes; se abre desde el botón de ajustes |

## Elementos UXML

`title-menu`, `title-confirm`, `title-logo`, `title-fade`, `title-version`, `title-tagline`, `title-confirm-text`, `title-continue`, `title-new`, `title-settings`, `title-quit`, `title-confirm-yes`, `title-confirm-no`.

## Botones

| Botón | Acción |
|-------|--------|
| Continuar | Fade de salida y `SceneFlow.GoToStore()` |
| Nueva partida | Muestra confirmación; "sí" → fade y `SceneFlow.RequestNewGame()` |
| Ajustes | Oculta el menú, `settings.Show()`; al cerrar (`Closed`) vuelve a mostrarlo |
| Salir | `EditorApplication.isPlaying = false` en editor, `Application.Quit()` en build |

Escape cierra la confirmación si está abierta. Mientras sale (`leaving`) desactiva los botones para evitar doble disparo.

## Animación de Entrada

- Logo "Mori" / "Monchis": una `Label` por letra, rotación aleatoria que se anula con la clase `title-letter--in`, escalonado de 50 ms.
- Después del logo, oleaje senoidal por letra en `WaveTick` cada 16 ms (`WaveAmplitude 6`, `WaveSpeed 3`).
- Tagline y botones deslizan con `title-slide--hidden` / `title-slide`; el botón continuar respira (`title-button--breathe`) cada 1300 ms.
- Salida: clase `title-fade--leave` y 450 ms antes de cargar la escena.

## Otros

- `Time.timeScale = 1` y cursor libre/visible en `Start`.
- Textos con `Loc.Tr("ui.title.*")`; versión con `Application.version`.

## Conexiones

- [[SceneFlow]] — `GoToStore`, `RequestNewGame`
- [[SettingsPanelUITK]] — panel de ajustes (`Show`, `Closed`)
- [[UiPanels]] — `RootOf(document)`
- [[Loc]] — textos
- [[StarterKitService]] — consume la bandera de partida nueva al entrar a la tienda
