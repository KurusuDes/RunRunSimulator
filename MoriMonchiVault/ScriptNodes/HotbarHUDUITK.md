---
tags: [script, ui]
---

# HotbarHUDUITK.cs

**Ruta:** `UI/HotbarHUDUITK.cs`

**Responsabilidad:** HUD del hotbar. Overlay permanente en gameplay, no navegable. Muestra los slots del inventario con el ícono del ítem (`ItemDefinitionSO.Icon`) y el nombre. Toma el inventario del payload de `OnInventoryReloaded` y de `GameManager.CurrentInventory` al habilitarse. **S93:** usa `UiPanels.RootOf()` para resolver el root.

**Vinculado a:** [[Index/05 - UI System]]

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento del hotbar |
| `database` | `ItemDatabaseSO` | Definiciones de ítems para resolver ícono y nombre |

## Estado Privado

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `slotRoots` | `List<VisualElement>` | Raíces de cada slot |
| `slotIcons` | `List<VisualElement>` | Ícono de cada slot (fondo) |
| `slotNames` | `List<Label>` | Nombre de cada slot |
| `built` | `bool` | Slots ya construidos |
| `inventory` | `PlayerInventorySO` | Inventario en uso |

## Métodos

| Método | Descripción |
|--------|-------------|
| `OnEnable` / `OnDisable` | Suscribe y desuscribe `GameEvents.OnInventoryReloaded` y `HotbarController.OnHotbarChanged` (→ `Refresh`) |
| `Start()` | Resuelve el root y construye los slots |
| `OnInventoryReloaded(inv)` | Guarda el inventario y refresca |
| `BuildSlots()` | Crea los slots una sola vez |
| `Refresh()` | Pinta cada slot con el ítem de su posición: si `Icon` existe, lo usa como fondo y limpia el nombre; si no, limpia el fondo y muestra el nombre (`DataLoc.ItemName`). Marca `hotbar-slot--active` en el slot de `HotbarController.ActiveSlot` |

## Visual (S161)

Receta estilo FarmingLife con el kit de Synty: caja marrón, runas de fondo, tecla abajo del slot, marco dorado en el slot activo y fondo al 30 %. Los íconos son renderizados de los prefabs de cada ítem (`Skin/Icons/Items/`).

## Conexiones

- [[HotbarController]] — ítem activo y uso
- [[ItemDatabaseSO]], [[ItemDefinitionSO]] — ícono y nombre por ítem
- [[PlayerInventorySO]] — inventario
- [[UiPanels]] — `RootOf`
- [[GameManager]] — `CurrentInventory`
- [[GameEvents]] — `OnInventoryReloaded`
- [[StoragePanelUITK]] — muestra una copia del hotbar dentro del almacén

## Notas

- S162: sincronizado con el código: el HUD se refresca también por `HotbarController.OnHotbarChanged` (ítem activo y slots) y muestra el nombre del ítem cuando no tiene ícono.
