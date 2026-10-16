---
tags: [script, ui, store, price, static]
---

# StorePrice.cs

**Ruta:** `UI/StorePrice.cs`

**Responsabilidad:** Utilidad estática de precio para las filas de la tienda. Resuelve el precio final, el precio base tachado cuando hay descuento activo, la moneda (Dabloons o Minerita), si la mejora está al tope y si la fila se puede comprar. No cambia saldos ni stock (S161).

**Vinculado a:** [[Index/04 - Store & Transactions]], [[Index/28 - Currency & Monetization]]

## Tipos

```csharp
public struct Info
{
    public int  Final;
    public int  Was;
    public bool Minerita;
    public bool Discounted => Was >= 0;
}
```

`Discounted` es verdadero solo si `Was` tiene valor (≥ 0).

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Resolve(StoreRows.Row row, bool discountActive)` | Devuelve `Info`. Hay descuento si la fila no tiene `PriceOverride`, el descuento del día está activo y `Shop.DiscountBase > 0`. `Final` = `PriceOverride` o `Shop.FinalPrice(discounted)`; `Was` = `Shop.BasePrice` si hay descuento; `Minerita` = la moneda del shop es Minerita |
| `Text(int amount, bool minerita)` | "N Minerita" o el texto localizado `ui.store.price` |
| `IsMaxed(StoreRows.Row row)` | Verdadero si la fila es una mejora en su nivel máximo |
| `CanBuy(StoreRows.Row row)` | Falso si no hay `Buy`; mejoras: no al tope; productos: sin `Shop` o con stock |

## Conexiones

- [[StoreRows]] — `Row`
- [[StoreShopData]] — `FinalPrice`, `BasePrice`, `DiscountBase`, `Currency`, `InStock`
- [[ShopUpgradeSO]] — `IsMaxed`, `CurrentLevel`
- [[Currency]] — enum de moneda
- [[StoreTileView]], [[StoreDetailCard]] — consumidores
- [[Loc]] — `ui.store.price`

## Notas

- Clase estática sin estado.
- El día del descuento lo decide `StorePanelUITK` con `ShopCatalogSO.IsDiscountActive(day)` y lo pasa como parámetro.
