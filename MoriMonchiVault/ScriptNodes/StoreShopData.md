---
tags: [script, store, data, listing]
---

# StoreShopData.cs

**Ruta:** `Systems/Store/StoreShopData.cs`

**Responsabilidad:** Datos de un listing individual: precio, moneda, descuento, stock, tags, filtro tipo. **S138:** Campo `Currency` (default Dabloons); cada listing cobra en su moneda.

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `BasePrice` | int | Precio base |
| `Currency` | Currency | **(S138 NUEVO)** Moneda (Dabloons/Minerita) — cada listing elige su moneda |
| `DiscountBase` | float | Fracción descuento (0.2 = 20% off) |
| `CurrentStock` | int | Stock disponible (decrementado) |
| `MaxStock` | int | Stock máximo (recarga) |
| `TypeFilter` | StoreItemTypeFilter | Categoría (furniture/prop/consumable) |
| `Tags` | string[] | Etiquetas visuales (nuevo/oferta/limitado) |

## Métodos

- `FinalPrice(bool discountActive)` → BasePrice con descuento
- `IsUnlimited` → MaxStock < 0
- `InStock` → disponible
- `Restock()` → restaura a MaxStock
- `TryConsume()` → decrementa stock

## S138: Multi-Moneda

Cada listing en catálogo especifica su Currency. Muebles cobran Minerita (S138), items/cajas cobran Dabloons según contexto.

**Ejemplo:**
- Furniture: Currency.Minerita
- CreatureBox: Currency.Dabloons
- Upgrade: (no tiene StoreShopData; manejado por ShopUpgradeSO)

## Conexiones

- [[ShopCatalogSO]], [[StoreManager]], [[StorePanelUITK]], [[Wallet]]
