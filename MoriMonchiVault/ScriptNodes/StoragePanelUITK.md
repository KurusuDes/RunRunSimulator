---
tags: [script, ui]
---

# StoragePanelUITK.cs

**Ruta:** `UI/StoragePanelUITK.cs`

**Responsabilidad:** Panel de almacenamiento (cofre) con dos grillas: el inventario de ítems guardados y el hotbar. Retira ítems del almacén (`Eject`) con navegación `IUINavigable`. Toma el inventario del payload de `OnInventoryReloaded` y de `GameManager.CurrentInventory` al habilitarse. **S93:** usa `UiPanels.ClampSelection()` y `UiPanels.SetActiveIndex()`.

**Vinculado a:** [[Index/05 - UI System]]

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del panel |
| `panel` | `UIPanelType` | `Storage` | Clave de registro en `UIManager` |
| `database` | `ItemDatabaseSO` | — | Definiciones de ítems para íconos y nombres |

## Tipo Interno

`SlotView`: `Root`, `Icon` (`VisualElement`), `Name` y `Count` (`Label`). Representa una celda de cualquiera de las dos grillas.

## Elementos UXML

`grid` (ScrollView de inventario), `hotbar` (contenedor de la copia del hotbar), `subtitle`, `close-button`. Títulos y leyendas se localizan por nombre: `title`, `section-box`, `section-hotbar`, `prompt-move`, `prompt-take`, `prompt-close`.

## Estado Privado

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `filledSlots` | `List<VisualElement>` | Celdas con ítems |
| `slotIds` | `List<string>` | ID del ítem por celda |
| `selectedIndex` | `int` | Celda seleccionada (-1 si ninguna) |
| `inventory` | `PlayerInventorySO` | Inventario en uso |

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `OnEnable` / `OnDisable` | Suscribe y desuscribe `GameEvents.OnInventoryChanged`, `GameEvents.OnInventoryReloaded` (→ `Rebuild`) y `HotbarController.OnHotbarChanged` (→ `RebuildHotbar`) |
| `Start` / `OnDestroy` | Resuelve elementos, cablea el cierre y registra o desregistra la navegación |
| `OnUINavigate(dir)` | Mueve la selección entre celdas |
| `OnUISubmit()` | Saca el ítem seleccionado (`EjectSelected`) |
| `OnUICancel()` | Devuelve false |
| `Rebuild(inv)` / `RebuildFromInventory()` | Reconstruye todo desde el inventario |
| `RebuildGrid()` | Arma las celdas del cofre |
| `RebuildHotbar()` | Arma la copia del hotbar dentro del almacén |
| `Fill(view, id, count)` | Pinta una celda con ícono, nombre y cantidad |
| `Eject(id)` / `EjectSelected()` | Mueve un ítem del almacén al inventario del jugador |
| `Select(idx)` | Cambia la selección |
| `WireChrome()` / `OnCloseClicked()` | Botón de cierre vía `UIManager.RequestPanelToggle(panel)` |

## Conexiones

- [[UIManager]] — ciclo del panel y navegación
- [[StorageContainer]] — contenedor de almacenamiento
- [[PlayerInventorySO]] — inventario
- [[ItemDatabaseSO]], [[ItemDefinitionSO]] — ícono y nombre
- [[HotbarHUDUITK]] — mismo criterio visual para la copia del hotbar
- [[UiPanels]] — `ClampSelection`, `SetActiveIndex`

## Notas

- S161: el almacén es un cofre de dos grillas (inventario y hotbar), con el kit de Synty.
- S162: el cierre se resuelve por `close-button` y la copia del hotbar por `hotbar`; el hotbar del almacén se refresca también por `HotbarController.OnHotbarChanged`.
- Probar el inventario en Play escribe el save real: usar un save de prueba.
