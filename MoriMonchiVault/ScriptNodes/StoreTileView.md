---
tags: [script, ui, store, tile, uitk, static]
---

# StoreTileView.cs

**Ruta:** `UI/StoreTileView.cs`

**Responsabilidad:** Constructor estático de las tiles de la tienda (ranura con ícono, nombre y píldora de precio o estado). Un clic selecciona la fila y un doble clic la compra. Aplica el ícono de la fila o el ícono de la pestaña cuando la fila no trae sprite (S161).

**Vinculado a:** [[Index/04 - Store & Transactions]], [[Index/05 - UI System]]

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `IconClass(StoreRows.Tab tab)` | Clase `store-icon--{pestaña}` en minúsculas |
| `ApplyIcon(VisualElement el, StoreRows.Tab tab, Sprite sprite)` | Quita las clases de ícono de todas las pestañas. Con sprite, lo pone como `backgroundImage`; sin sprite, limpia el fondo y agrega la clase de la pestaña |
| `Build(Tab tab, Row row, bool discountActive, Action onSelect, Action onBuy)` | Crea la tile: `store-tile` > `mm-slot` > `store-icon`, nombre `store-tile__name` y píldora. Click con `clickCount >= 2` → `onBuy`; si no → `onSelect` |
| `BuildEmpty()` | Tile de relleno (`store-tile--empty`) con runas, sin picking, para completar la grilla visible |

## Píldora (`BuildPill`)

| Estado de la fila | Texto | Clase |
|-------------------|-------|-------|
| Bloqueada (`LockedBy`) | `ui.store.locked.short` ("Bloqueado", sin dos puntos) | `store-tile--locked` en la tile + `store-tile__tag` |
| Solo lectura (`Buy == null`) | `Reward` | `store-price__now` |
| Mejora al tope | "Máximo" | `store-tile__tag` |
| Precio | `StorePrice.Text` | `store-price__now--sale` si hay descuento, si no `store-price__now`; `--minerita` si es Minerita |
| Sin stock | — | `store-tile--soldout` en la tile |

## Conexiones

- [[StorePanelUITK]] — construye las tiles y les pasa los callbacks
- [[StoreDetailCard]] — usa `ApplyIcon` en la ficha
- [[StorePrice]] — precio, descuento y disponibilidad
- [[StoreRows]] — `Row`, `Tab`
- [[Loc]] — `ui.store.locked.short`, `ui.store.max`

## Notas

- Clase estática sin estado ni suscripciones: los eventos de clic viven en la tile creada.
- Los `pickingMode` de los hijos están en `Ignore` para que el clic llegue a la tile.
- S162: la píldora de bloqueo usa la clave `ui.store.locked.short` (antes el texto completo de la meta quedaba en la ficha) y `BuildEmpty` queda documentado como constructor público.
