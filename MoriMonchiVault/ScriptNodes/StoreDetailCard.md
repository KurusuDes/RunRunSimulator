---
tags: [script, ui, store, detail, uitk]
---

# StoreDetailCard.cs

**Ruta:** `UI/StoreDetailCard.cs`

**Responsabilidad:** Ficha de detalle de la fila seleccionada en la tienda (columna derecha del PC). Muestra ícono, nombre, categoría, bloqueo por meta, hechos (nivel, precio con descuento tachado, stock) y el botón de compra con su estado. Clase no-MonoBehaviour: la crea `StorePanelUITK` sobre el root del documento (S161).

**Vinculado a:** [[Index/04 - Store & Transactions]], [[Index/05 - UI System]]

## Elementos UXML

`detail-content`, `detail-icon`, `detail-name`, `detail-category`, `detail-facts`, `detail-lock`, `detail-buy` (botón).

## Miembros Públicos

| Miembro | Descripción |
|---------|-------------|
| `BuyButton` (`Button`) | Botón de compra. `StorePanelUITK` se suscribe a su `clicked` |
| `StoreDetailCard(VisualElement root)` | Resuelve los elementos por nombre |
| `SetEmpty()` | Oculta el contenido y deshabilita el botón (sin fila seleccionada) |
| `Show(StoreRows.Tab tab, StoreRows.Row row, bool discountActive)` | Llena la ficha con la fila |

## Contenido de `Show`

- Ícono con `StoreTileView.ApplyIcon` (sprite de la fila o ícono por pestaña).
- Categoría con `StoreRows.TabLabel(tab)`.
- Bloqueo: `row.LockedBy` visible solo si no está vacío.
- Hechos (`BuildFacts`):
  - Solo lectura (`Buy == null`): recompensa con ícono de moneda.
  - Mejoras: nivel `ui.store.level` con `Upgrade.CurrentLevel`/`MaxLevel`.
  - Precio si no está al tope, con `StorePrice.Text`; si hay descuento, precio base tachado y clase `store-fact__value--sale`. Minerita usa ícono propio.
  - Stock si es un producto con `Shop` limitado: "agotado" (crítico), "quedan 2 o menos" (advertencia) o cuenta.
- Botón: "Máximo" si está al tope, "Comprar" si no; habilitado según `StorePrice.CanBuy`.

## Conexiones

- [[StoreRows]] — `Row` y `Tab`
- [[StoreTileView]] — `ApplyIcon`
- [[StorePrice]] — precio, descuento, tope y disponibilidad
- [[StorePanelUITK]] — dueño; crea la ficha y reenvía el clic de compra
- [[StoreManager]] — la compra la ejecuta el panel, no esta ficha
- [[Loc]] — textos `ui.store.*`

## Notas

- No compra ni persiste: solo presenta y expone el botón.
- Todos los textos de la ficha pasan por `Loc`.
