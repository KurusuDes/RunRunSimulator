---
tags: [script, ui]
---

# UIManager.cs

**Ruta:** `UI/UIManager.cs`

**Responsabilidad:** Hub de paneles + stack LIFO + router de input UI. Static event bus para UI-domain.

**Vinculado a:** [[Index/05 - UI System]]

**Conexiones:** [[UIInputs]], [[PanelTrigger]], [[CreatureGridUITK]], [[MorimonchiDetailInfoUITK]], [[StorePanelUITK]], [[PauseMenuUITK]] (S151), [[SettingsPanelUITK]] (S151), [[Interfaces]]

## Eventos estáticos (UI-domain)

| Evento | Payload | Quién lo pide / escucha |
|--------|---------|-------------------------|
| `OnPanelToggleRequested` / `RequestPanelToggle` | `UIPanelType` | Botones de cierre de paneles |
| `OnPanelSetRequested` / `RequestPanelSet` | `UIPanelType, bool` | Paneles que se abren o cierran a sí mismos |
| `OnCreatureSelected` / `SelectCreature` | `CreatureDNA, CreatureRegistrySO` | Grid → ficha de detalle |
| `OnUIFocusChanged` | `bool` | `PlayerController` y `PauseMenuUITK`: foco UI en el flanco 0↔1 |
| `OnPanelVisibilityChanged` | `UIPanelType, bool` | **(S151)** Avisa cada vez que un panel cambia de visibilidad. Lo escucha `PauseMenuUITK` |
| `OnNavigableRegistered` / `OnNavigableUnregistered` | panel, `IUINavigable` | Paneles que reciben navegación |

`Present` (static bool) es true mientras el componente está activo.

## Invariantes (S93)

- Eventos UI-domain viven aquí (`OnPanelToggleRequested`, `OnPanelSetRequested`, `OnCreatureSelected`, `OnUIFocusChanged`, etc.), separados de `GameEvents` (gameplay-only). Cada dominio tiene su bus.
- **Nunca** `SetActive(false)` a un GameObject con `UIDocument`: un documento inactivo pierde `rootVisualElement` y deja de actualizarse. Se togglea `display` del root en su lugar.
- `UIManager` es el **único** suscriptor de `UIInputs`: Navigate/Submit se despachan al panel top del stack; Cancel (ESC) popea el top. Los paneles cierran en orden inverso.
- `RouteCancel`: el panel top maneja el cancel internamente (cerrar sub-vista); solo si no lo consume se popea.
- `UpdateFocus`: dispara `OnUIFocusChanged` solo en el flanco 0↔1.
- `OnEnable` corre antes que `Start`, por eso `rootVisualElement` ya existen para ocultar paneles en `Start`.

## Cambios S151

- **Cancel sin paneles abiertos:** si el stack está vacío y el mapa de paneles tiene `UIPanelType.Pause`, `RouteCancel` abre el menú de pausa. Antes Cancel no hacía nada en ese caso.
- `OnPanelVisibilityChanged` se dispara en `TogglePanel` y `SetPanel`, tras actualizar el foco.
- Los paneles `Pause` y `Settings` se mapean en `panels` como cualquier otro.

## Conexiones

- [[UIInputs]] — fuente de Navigate, Submit y Cancel
- [[IUINavigable]] — interfaz de los paneles navegables
- [[UIPanelType]] — claves del mapa `panels`
- [[PlayerController]] — consume `OnUIFocusChanged`
- [[PauseMenuUITK]] — consume `OnPanelVisibilityChanged` y `OnUIFocusChanged`
