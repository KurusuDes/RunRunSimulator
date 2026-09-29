---
tags: [script, ui, store, data, rows]
---

# StoreRows.cs

**Ruta:** `UI/StoreRows.cs`

**Responsabilidad:** Utilidad estática: convierte catálogo en rows de UI. **S138:** Furniture tab ahora incluye mejoras con `Upgrade` field. Abstracción agnóstica de presentación.

## Enumeraciones

### Tab

```csharp
enum Tab { Furniture, WorldProps, Consumables, Creatures }
```

## Structs Públicos

### Row (S138)

```csharp
public struct Row
{
    public string          Name;            // Display name
    public StoreShopData   Shop;            // Stock, precio (null para mejoras)
    public Func<BuyResult> Buy;             // Lambda compra
    public int?            PriceOverride;   // **(S138)** Precio para mejoras
    public ShopUpgradeSO   Upgrade;         // **(S138)** Referencia si es mejora
}
```

**Cambios S138:**
- `PriceOverride` — precio fijo (para mejoras sin Stock)
- `Upgrade` — referencia a ShopUpgradeSO si es mejora

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `TabLabel(Tab tab)` | `string` | Etiqueta localizada |
| `Collect(Tab tab, ShopCatalogSO catalog, StoreManager store, List<Row> rows)` | `void` | Popula rows de tab activa |

## Lógica Collect

**Furniture tab (S138):**
1. Itera `catalog.FurnitureListings` (muebles)
   - Row: Shop + Buy → BuyFurniture
2. Itera `catalog.UpgradeListings` (mejoras)
   - Row: Upgrade + PriceOverride + Buy → BuyUpgrade
   - Sin Shop (no tiene stock)
   - `PriceOverride = upgrade.PriceFor(upgrade.CurrentLevel)`

**Creatures tab (S137):**
- Itera `catalog.CreatureBoxListings` (cajas)
- Row: Box + Shop + Buy → BuyCreatureBox
- `PriceOverride = store.CreatureBoxPrice(box, shop)` (maneja gratis onboarding)

**WorldProps / Consumables:**
- Itera `catalog.ItemListings` con filtro categoría

## Integración S138

**StorePanelUITK.BuildRows()** → llama `StoreRows.Collect(Tab.Furniture, ...)` 
- UI itera rows, renderiza tanto muebles como mejoras
- Ejecuta `row.Buy()` en click
- Usa `row.PriceOverride` si existe, sino `row.Shop.Price`

## Invariantes S138

- Mejoras solo en tab Furniture
- Mejoras sin Stock (no consumen)
- Row.Upgrade ≠ null ⟹ Row.Shop = null
- Row.PriceOverride = precio para siguiente nivel

## Vinculado a

- [[Index/28 - Currency & Monetization]]
- [[Index/04 - Store & Transactions]]

**Conexiones:** [[StorePanelUITK]], [[StoreManager]], [[ShopCatalogSO]], [[ShopUpgradeSO]], [[CreatureBoxSO]]
