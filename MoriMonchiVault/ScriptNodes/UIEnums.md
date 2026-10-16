---
tags: [enum, ui, state]
---

# UIEnums

**Ruta:** `Core/Enums/UIEnums.cs`

**Responsabilidad:** Enumeraciones para sistema de UI y estados del jugador. Contiene: `UIPanelType` (paneles con hueco en 4), `FocusPrompt` (qué ofrece el punto de mira, S161), `PlayerStateType` (3 estados de jugador).

**S128:** `Combat = 4` permanece **como hueco** (se borró todo combate RPS pero no se renumera). **S151:** `UIPanelType` gana `Pause = 10` y `Settings = 11`; `PlayerStateType` ya no tiene `Building` (modo construcción borrado con muebles en S149).

## Enumeraciones

### UIPanelType

| Valor | Descripción |
|-------|-------------|
| `None = 0` | No panel abierto |
| `CreatureGrid = 1` | Grilla de criaturas |
| `MorimonchiDetail = 2` | Ficha de criatura |
| `Breeding = 3` | Panel de cría |
| ~~`Combat = 4`~~ | **HUECO (S128):** demolición RPS, no renumera siguientes |
| `Storage = 5` | Almacén de props |
| `Store = 6` | Tienda de compras |
| `Transaction = 7` | Historial/transacciones |
| `Expedition = 8` | Selección de equipo |
| `ExpeditionReturn = 9` | Resultado al volver de la bajada (`ExpeditionReturnCardUITK`) |
| `Pause = 10` | **(S151)** Menú de pausa (`PauseMenuUITK`) |
| `Settings = 11` | **(S151)** Panel de ajustes (`SettingsPanelUITK`) |

### FocusPrompt

| Valor | Descripción |
|-------|-------------|
| `None = 0` | Nada que ofrecer |
| `Creature = 1` | MoriMochi acariciable o agarrable |
| `Interactable = 2` | Objeto con `IInteractable` |
| `Carrying = 3` | El jugador sostiene algo |
| `Item = 4` | Ítem activo del hotbar |

Lo publica [[PlayerFocusProbe]] y lo pinta [[FocusPromptUITK]] (S161).

### PlayerStateType

| Valor | Descripción |
|-------|-------------|
| `None = 0` | Estado inicial |
| `Exploring = 1` | Libre en tienda; permite navegación/interacción |
| `Menu = 2` | Abre/cierra paneles (no movimiento) |

## Uso

- **UIPanelType:** identifica qué panel está abierto; usado por `UIManager.OpenPanel()` para rutear entrada/lógica. Pause y Settings se piden también con `UIManager.RequestPanelSet`.
- **FocusPrompt:** aviso contextual de gameplay; no participa en la navegación de UI.
- **PlayerStateType:** constraints inputs (qué acciones permite cada estado)

## Cambios Históricos

**S95:** Combat = 4 agregado (Dragon RPS).
**S120:** Expedition = 8 agregado (panel bajada).
**S128:** Combat eliminado (RPS demolido); valor 4 queda como hueco, no se renumera (evita serialización breaks).
**S145:** ExpeditionReturn = 9 agregado (tarjeta de retorno de bajada; reemplaza el toast de InfoOverlay).
**S149:** `PlayerStateType.Building` eliminado (modo construcción de muebles borrado).
**S151:** Agregados `Pause = 10` y `Settings = 11`.
**S161:** `FocusPrompt` agregado (aviso contextual del foco).

## Nota de Diseño

El hueco en 4 es intencional. Renumerar causaría breakage de:
- Saves existentes con valores serializados
- Prefabs/escenas con referencias a índices

## Vinculado a

[[Index/05 - UI System]]

**Conexiones:** [[UIManager]], [[PlayerInputs]], [[ExpeditionPanelUITK]], [[ExpeditionReturnCardUITK]], [[PauseMenuUITK]], [[SettingsPanelUITK]], [[PlayerFocusProbe]] (S161), [[FocusPromptUITK]] (S161)
