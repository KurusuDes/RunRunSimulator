---
tags: [script, ui, store, data, rows]
---

# StoreRows.cs

**Ruta:** `UI/StoreRows.cs`

**Responsabilidad:** Utilidad estática: convierte el catálogo en rows de UI. Abstracción agnóstica de presentación. **S138:** la pestaña de mejoras con `Upgrade` field. **S149:** las pestañas cambian: sale Furniture y entran Expansions (mejoras), Decor (decoraciones de cría) y Toys (juguetes). **S151:** entra la pestaña Orders (encargos del día) y `Row` gana el campo `Reward` para filas de solo lectura.

## Enumeraciones

### Tab

```csharp
public enum Tab { Expansions, WorldProps, Consumables, Creatures, Decor, Toys, Orders }
```

**S149:** `Furniture` reemplazado por `Expansions`. **S151:** `Orders` al final. Las etiquetas salen de `Loc` (`ui.store.tab.*`).

## Structs Públicos

### Row

```csharp
public struct Row
{
    public string          Name;            // Display name
    public string          Reward;          // S151: texto de recompensa (filas de solo lectura, Orders)
    public StoreShopData   Shop;            // Stock, precio (null para mejoras, decoraciones, encargos)
    public Func<BuyResult> Buy;             // Lambda compra (null en filas de solo lectura)
    public int?            PriceOverride;   // Precio fijo (mejoras, decoraciones, cajas)
    public ShopUpgradeSO   Upgrade;         // Referencia si es mejora
}
```

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `TabLabel(Tab tab)` | `string` | Etiqueta localizada |
| `Collect(Tab tab, ShopCatalogSO catalog, StoreManager store, List<Row> rows)` | `void` | Popula rows de tab activa |

## Lógica Collect

**Orders (S151):**
1. Lee `OrderBoardService.Instance.Active` (no usa catálogo ni `store`).
2. Row: `Name = order.Describe()`, `Reward = "+{Reward}"`, sin `Buy` ni `Shop`.

**Expansions (S138, renombrada S149):**
1. Itera `catalog.UpgradeListings`.
2. Row: Upgrade + `PriceOverride = upgrade.PriceFor(upgrade.CurrentLevel)` + Buy → `BuyUpgrade`. Sin Shop (no tiene stock).

**Decor (S149):**
1. Itera `catalog.DecorListings`.
2. El nombre se oculta (`ui.store.decor.unknown`) hasta que `WorldState.BredTotal` cumple `DiscoverAtBreeds`.
3. Si el jugador ya tiene unidades, agrega el contador `×N` al nombre (`inventory.DecorCount`).
4. Row: `PriceOverride = decor.Price` + Buy → `BuyDecor`. Sin Shop (stock ilimitado).

**Creatures (S137):**
- Itera `catalog.CreatureBoxListings`.
- Row: Box + Shop + Buy → `BuyCreatureBox`.
- `PriceOverride = store.CreatureBoxPrice(box, shop)` (maneja gratis onboarding).

**WorldProps / Consumables / Toys:**
- Itera `catalog.ItemListings` y filtra por `WorldPropCategory`: WorldProps = Tool, Toys = Toy, Consumables = Food o Medicine.
- **S149:** un listing con `RequiresExpansion` solo aparece si esa expansión tiene nivel >= 1.
- Row: Shop + Buy → `BuyWorldProp`.

## Integración

**StorePanelUITK** llama `Collect` por pestaña; la UI renderiza el row, ejecuta `row.Buy()` al click y usa `row.PriceOverride` si existe, o `row.Shop.Price` en caso contrario. Si `Buy` es null, la fila es de solo lectura (recompensa de encargo).

## Invariantes

- Mejoras solo en la pestaña Expansions.
- Mejoras y decoraciones sin Stock (no consumen).
- `Row.Upgrade != null` implica `Row.Shop == null`.
- `Row.PriceOverride` es el precio actual de la mejora (siguiente nivel) o el precio fijo de la decoración.
- Orders no tiene `Buy`: la recompensa la paga `OrderBoardService` al venderle al cliente correcto.

## Vinculado a

- [[Index/28 - Currency & Monetization]]
- [[Index/04 - Store & Transactions]]

**Conexiones:** [[StorePanelUITK]], [[StoreManager]], [[ShopCatalogSO]], [[ShopUpgradeSO]], [[CreatureBoxSO]], [[BreedingDecorSO]], [[WorldPropCategory]], [[WorldStateSO]], [[PlayerInventorySO]], [[OrderBoardService]] (S151), [[ShopOrder]] (S151), [[Loc]]
