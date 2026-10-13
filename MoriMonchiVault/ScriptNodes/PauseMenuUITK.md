---
tags: [script, ui, uitk, pause, input]
---

# PauseMenuUITK.cs

**Ruta:** `UI/PauseMenuUITK.cs`

**Responsabilidad:** Menú de pausa (Escape). Abre/cierra el panel `UIPanelType.Pause`, congela el juego con `Time.timeScale = 0`, libera el cursor, abre el panel de ajustes desde el menú y ofrece "Salir" (hace flush a la nube y cierra la app o sale del Play). Respeta el stack de paneles de `UIManager`: si hay otro panel abierto, Escape pide cerrarlo en vez de pausar.

## Comportamiento

- `Escape` es un `InputAction` propio (`<Keyboard>/escape`), no pasa por `PlayerInputs`. Se habilita solo si no hay UI con foco (`UIManager.Present` / `uiFocused`).
- Abrir pausa guarda cursor previo; cerrar lo restaura.
- Ajustes: oculta el menú, muestra `SettingsPanelUITK`; al cerrar (`Closed`) vuelve a mostrar el menú si seguía pausado.
- Salir: `GameManager.Instance.FlushToCloudAsync()` y luego `Application.Quit` (o `EditorApplication.isPlaying = false` en editor).
- Si el panel de pausa lo abre `UIManager` (Cancel con stack vacío), el menú se muestra igual por `OnPanelVisibilityChanged`.

## Campos serializados

- `document` (`UIDocument`), `settings` (`SettingsPanelUITK`)

## Eventos suscritos

- `UIManager.OnPanelVisibilityChanged`, `UIManager.OnUIFocusChanged`
- `SettingsPanelUITK.Closed`

## Conexiones

- [[UIManager]] — stack de paneles y foco
- [[UiPanels]] — `RootOf(document)`
- [[SettingsPanelUITK]] — submenú de ajustes
- [[GameManager]] — `FlushToCloudAsync` (salida)
