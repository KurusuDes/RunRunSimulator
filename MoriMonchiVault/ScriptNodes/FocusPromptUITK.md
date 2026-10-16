---
tags: [script, ui, uitk, hud, focus]
---

# FocusPromptUITK.cs

**Ruta:** `UI/FocusPromptUITK.cs`

**Responsabilidad:** Aviso contextual del HUD de gameplay: retícula (punto que pasa a anillo dorado al apuntar a algo usable) y bloque de prompt con rótulo (`IFocusLabel`) y filas de teclas (E Acariciar, Mantener E Agarrar, E Usar, E Soltar, Clic Lanzar, etc.). Es presentación pura: lee `PlayerFocusProbe` y reconstruye el contenido solo cuando cambia el prompt, el foco de UI, los ajustes o el idioma. Reemplaza la leyenda de teclas fija del overlay (S161).

**Vinculado a:** [[Index/05 - UI System]], [[Index/06 - Player & World]]

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento del HUD. Se resuelve con `UiPanels.RootOf` |

## Elementos UXML

- `crosshair`: retícula. Clase `crosshair--target` cuando el prompt es `Creature` o `Interactable`. Se oculta con UI abierta.
- `focus-prompt`: contenedor del aviso. Clase `focus-prompt--visible` cuando hay algo que mostrar.
- Dentro se crean en código: `focus-title`, `focus-detail` (si hay rótulo) y filas `focus-row` con `mm-hud-key` + `focus-key` y `focus-action`.

## Visibilidad

- El prompt se muestra si no hay UI con foco y (hay pista de tecla o hay rótulo).
- La pista de tecla exige `SettingsService.Current.ShowKeyHints` (el toggle de ajustes controla los avisos).
- Rótulo sin pista: se muestra igual (título y detalle del `IFocusLabel`).

## Filas por Prompt

| Prompt | Filas |
|--------|-------|
| `Creature` | E · `ui.focus.pet` / Mantener E · `ui.focus.grab` |
| `Interactable` | E · `ui.focus.use` |
| `Carrying` | E · `ui.focus.drop` / Clic · `ui.focus.throw` |
| `Item` | Clic · `ui.focus.useitem` / Mantener E · `ui.focus.throw` |

Las teclas con `Loc.Tr("ui.key.*")` salen de `Loc`.

## Flujo

- `OnEnable`: suscribe `PlayerFocusProbe.Changed`, `UIManager.OnUIFocusChanged`, `SettingsService.Changed` y `LocalizationSettings.SelectedLocaleChanged`; toma el estado actual y refresca.
- `Start`: resuelve la raíz del documento, `crosshair` y `focus-prompt`, y refresca.
- `Update`: si hay `titleLabel`, actualiza solo los textos del rótulo (el rótulo cambia sin cambiar el prompt, p. ej. el nivel de un suministro).
- `OnDisable`: desuscribe todo.

## Conexiones

- [[PlayerFocusProbe]] — `Changed`, `Current`, `CurrentLabel`
- [[IFocusLabel]] — `FocusTitle`, `FocusDetail`
- [[UIManager]] — `OnUIFocusChanged`
- [[SettingsService]], [[GameSettings]] — `ShowKeyHints`
- [[Loc]] — `Tr` para teclas y acciones
- [[UiPanels]] — `RootOf`
- [[FocusPrompt]] — `UIEnums.cs`

## Notas

- Si no encuentra el root del UXML, registra un warning y no hace nada.
- Textos de teclas y acciones pasan por `Loc` (claves `ui.focus.*`, `ui.key.*`).
