---
tags: [script, store, data, catalog]
---

# ShopCatalogSO.cs

**Ruta:** `Systems/Store/ShopCatalogSO.cs`

**Responsabilidad:** Catálogo unificado: descuentos + restock schedule por día de juego. Expone listings de props del mundo, cajas de criaturas, mejoras (S138) y decoraciones de cría (S149). S131: API cambió DateTime → int day (GameClock.Instance.Day). **S149:** Se retiran los listings de muebles. Se agrega `RequiresExpansion` en props, `decorListings` y la exportación/importación de stock a `WorldStateSO`. Métodos: IsDiscountActive(int day), FinalPrice(StoreShopData, int day), NeedsRestock(int day), RestockAll(int day), ExportStock(), ImportStock().

## Clases Internas

### ItemListing (props del mundo)
```csharp
[Serializable]
public class ItemListing
{
    [Required, AssetsOnly] public ItemDefinitionSO Item;
    public StoreShopData Shop;
    [AssetsOnly] public ShopUpgradeSO RequiresExpansion;   // S149
}
```

### CreatureBoxListing
```csharp
[Serializable]
public class CreatureBoxListing
{
    [Required, AssetsOnly] public CreatureBoxSO Box;
    public StoreShopData Shop;
}
```

## Propiedades Públicas

| Propiedad | Retorna | Descripción |
|-----------|---------|-------------|
| `ItemListings` | `IReadOnlyList<ItemListing>` | Props del mundo |
| `CreatureBoxListings` | `IReadOnlyList<CreatureBoxListing>` | Cajas de criaturas |
| `UpgradeListings` | `IReadOnlyList<ShopUpgradeSO>` | **(S138)** Mejoras compradas con Dabloons. Sin stock ni restock |
| `DecorListings` | `IReadOnlyList<BreedingDecorSO>` | **(S149)** Decoraciones de cría. Stock ilimitado |
| `LastRestockDay` | int | **(S149)** Día del último restock (`NonSerialized`, se persiste vía WorldState) |
| `RestockEveryDays` | int | Intervalo restock (default 3) |
| `DiscountEveryDays` | int | Intervalo descuento (default 7; 0=nunca) |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `IsDiscountActive(int day)` | `bool` | `day % DiscountEveryDays == 0` (módulo) |
| `FinalPrice(StoreShopData shop, int day)` | `int` | Precio + descuento según IsDiscountActive(day) |
| `NeedsRestock(int day)` | `bool` | `lastRestockDay <= 0 \|\| day - lastRestockDay >= RestockEveryDays` |
| `RestockAll(int day)` | `void` | Recarga stock de props y cajas; guarda lastRestockDay. Decoraciones y mejoras no entran |
| `ExportStock()` | `Dictionary<string, int>` | **(S149)** Stock actual de props y cajas (sin los de stock ilimitado) |
| `ImportStock(stock, restockDay)` | `void` | **(S149)** Carga stock guardado; si falta un ID, repone al máximo |

## Cambios S149

- **Retirado:** `FurnitureListing` y su lista de muebles.
- **Agregado:** `RequiresExpansion` en `ItemListing` (un prop puede exigir una expansión abierta).
- **Agregado:** `decorListings` y `DecorListings`.
- **Agregado:** `ExportStock` / `ImportStock` / `LastRestockDay`. `StoreManager` los usa para persistir stock en `WorldStateSO`.

## Cambios S138

**Nuevo campo:**
```csharp
[Title("Shop upgrades for sale")]
[SerializeField] private List<ShopUpgradeSO> upgradeListings = new List<ShopUpgradeSO>();
```

Mejoras no tienen stock (no consumen), ni restock schedule. Cada mejora rastrea su nivel en `WorldStateSO.UpgradeLevel(id)`.

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

**Conexiones:** [[StoreShopData]], [[ItemDefinitionSO]], [[CreatureBoxSO]], [[ShopUpgradeSO]], [[BreedingDecorSO]], [[StoreManager]], [[WorldStateSO]], [[GameClock]]
