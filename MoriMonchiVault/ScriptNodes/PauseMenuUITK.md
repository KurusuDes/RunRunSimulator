---
tags: [script, ui, uitk, pause, input]
---

# PauseMenuUITK.cs

**Ruta:** `UI/PauseMenuUITK.cs`

**Responsabilidad:** Menú de pausa (Escape). Abre/cierra el panel `UIPanelType.Pause`, congela el juego con `Time.timeScale = 0`, libera el cursor, abre el panel de ajustes desde el menú, ofrece "Saltar tutorial" (solo mientras el tutorial está activo) y "Volver al título" (flush a la nube y `SceneFlow.GoToTitle()`), y "Salir" (flush a la nube y cierra la app o sale del Play). Respeta el stack de paneles de `UIManager`: si hay otro panel abierto, Escape pide cerrarlo en vez de pausar.

## Comportamiento

- `Escape` es un `InputAction` propio (`<Keyboard>/escape`), no pasa por `PlayerInputs`. Se habilita solo si no hay UI con foco (`UIManager.Present` / `uiFocused`).
- Abrir pausa guarda cursor previo; cerrar lo restaura.
- Ajustes: oculta el menú, muestra `SettingsPanelUITK`; al cerrar (`Closed`) vuelve a mostrar el menú si seguía pausado.
- **Saltar tutorial (S152):** botón `pause-skiptutorial`, visible solo si `TutorialDirector.Instance.Active`. Al pulsar llama `TutorialDirector.Skip()` y vuelve a evaluar la visibilidad.
- **Volver al título (S152):** botón `pause-totitle`. Desactiva botones, espera `GameManager.Instance.FlushToCloudAsync()`, cierra la pausa y llama `SceneFlow.GoToTitle()`.
- Salir: `GameManager.Instance.FlushToCloudAsync()` y luego `Application.Quit` (o `EditorApplication.isPlaying = false` en editor).
- Si el panel de pausa lo abre `UIManager` (Cancel con stack vacío), el menú se muestra igual por `OnPanelVisibilityChanged`.
- Los textos y la visibilidad de "Saltar tutorial" se refrescan al abrir la pausa (`RefreshTexts`).

## Campos serializados

- `document` (`UIDocument`), `settings` (`SettingsPanelUITK`)

## Elementos UXML

`pause-title`, `pause-resume`, `pause-settings`, `pause-skiptutorial` (S152), `pause-totitle`, `pause-quit`.

## Eventos suscritos

- `UIManager.OnPanelVisibilityChanged`, `UIManager.OnUIFocusChanged`
- `SettingsPanelUITK.Closed`

## Conexiones

- [[UIManager]] — stack de paneles y foco
- [[UiPanels]] — `RootOf(document)`
- [[SettingsPanelUITK]] — submenú de ajustes
- [[GameManager]] — `FlushToCloudAsync` (salida y volver al título)
- [[SceneFlow]] — `GoToTitle()` (S152)
- [[TutorialDirector]] — `Active`, `Skip()` (S152)
