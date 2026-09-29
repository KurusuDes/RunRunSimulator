---
tags: [script, store, data, catalog]
---

# ShopCatalogSO.cs

**Ruta:** `Systems/Store/ShopCatalogSO.cs`

**Responsabilidad:** Catálogo unificado: descuentos + restock schedule por día de juego. Expone 4 tipos de listings: Furniture, WorldProps, Creature Boxes, y Upgrades (S138). S131: API cambió DateTime → int day (GameClock.Instance.Day). Métodos: IsDiscountActive(int day), FinalPrice(StoreShopData, int day), NeedsRestock(int day), RestockAll(int day).

## Clases Internas

### FurnitureListing
```csharp
public class FurnitureListing
{
    [Required, AssetsOnly] public FurnitureDefinitionSO Furniture;
    public StoreShopData Shop;
}
```

### ItemListing
```csharp
public class ItemListing
{
    [Required, AssetsOnly] public ItemDefinitionSO Item;
    public StoreShopData Shop;
}
```

### CreatureBoxListing
```csharp
public class CreatureBoxListing
{
    [Required, AssetsOnly] public CreatureBoxSO Box;
    public StoreShopData Shop;
}
```

## Propiedades Públicas

| Propiedad | Retorna | Descripción |
|-----------|---------|-------------|
| `FurnitureListings` | `IReadOnlyList<FurnitureListing>` | Muebles |
| `ItemListings` | `IReadOnlyList<ItemListing>` | Props |
| `CreatureBoxListings` | `IReadOnlyList<CreatureBoxListing>` | Cajas de criaturas |
| `UpgradeListings` | `IReadOnlyList<ShopUpgradeSO>` | **(S138)** Mejoras compradas con Dabloons |
| `RestockEveryDays` | int | Intervalo restock (default 3) |
| `DiscountEveryDays` | int | Intervalo descuento (default 7; 0=nunca) |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `IsDiscountActive(int day)` | `bool` | `day % DiscountEveryDays == 0` (módulo) |
| `FinalPrice(StoreShopData shop, int day)` | `int` | Precio + descuento según IsDiscountActive(day) |
| `NeedsRestock(int day)` | `bool` | `lastRestockDay <= 0 \|\| day - lastRestockDay >= RestockEveryDays` |
| `RestockAll(int day)` | `void` | Recarga stock todas listings; guarda lastRestockDay |

## Cambios S138

**Nuevo campo:**
```csharp
[Title("Shop upgrades for sale")]
[SerializeField] private List<ShopUpgradeSO> upgradeListings = new List<ShopUpgradeSO>();
```

**Nueva propiedad:**
```csharp
public IReadOnlyList<ShopUpgradeSO> UpgradeListings => upgradeListings;
```

Mejoras no tienen stock (no consumen), ni restock schedule. Cada mejora rastrean su nivel en `WorldStateSO.UpgradeLevel(id)`.

## Dev Button

```csharp
[Button("Force Restock All (DEV)")]
private void DevForceRestock()
{
    int day = GameClock.Instance != null ? GameClock.Instance.Day : 1;
    RestockAll(day);
}
```

## Vinculado a

- [[Index/28 - Currency & Monetization]]
- [[Index/04 - Store & Transactions]]

**Conexiones:** [[StoreShopData]], [[FurnitureDefinitionSO]], [[ItemDefinitionSO]], [[CreatureBoxSO]], [[ShopUpgradeSO]], [[StoreManager]], [[GameClock]]
