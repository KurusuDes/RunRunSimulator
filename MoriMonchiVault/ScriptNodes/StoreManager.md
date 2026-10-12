---
tags: [script, store, transactions, manager]
---

# StoreManager.cs

**Ruta:** `Systems/Store/StoreManager.cs`

**Responsabilidad:** Orquestador de compras. Valida saldo vía `Wallet`, stock y ownership. Muta inventario y dispara eventos. Crea `DeliveryBox` para entregas (props, cajas de criaturas, regalo del tío). **S138:** añade `BuyUpgrade()` + `CreatureBoxPrice()`. **S149:** se retira `BuyFurniture`; se agregan `GiftCreatureBox()` (regalo sin cobro, lo usa `UncleRescueService`) y `BuyDecor()`; el stock de la tienda se persiste en `WorldStateSO` y se reabastece al empezar un día. Flujo invariante: comprueba saldo → aplica → cobra → un evento de persistencia.

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `BuyWorldProp(ItemDefinitionSO def, StoreShopData shop)` | `BuyResult` | Instancia DeliveryBox, configura prop, cobra. Persiste stock si consume |
| `BuyCreatureBox(CreatureBoxSO box, StoreShopData shop)` | `BuyResult` | **(S137)** Instancia DeliveryBox con criaturas Form=box.Form, cobra |
| `GiftCreatureBox(CreatureBoxSO box)` | `bool` | **(S149)** Entrega una caja sin cobrar ni tocar stock. Lo llama `UncleRescueService` |
| `BuyUpgrade(ShopUpgradeSO upgrade)` | `BuyResult` | **(S138)** Valida nivel < max, deduce Dabloons, eleva nivel en WorldState, dispara evento |
| `BuyDecor(BreedingDecorSO decor)` | `BuyResult` | **(S149)** Cobra en Dabloons y suma la decoración al inventario. Stock ilimitado |
| `CreatureBoxPrice(CreatureBoxSO box, StoreShopData shop)` | `int` | **(S138)** Precio de caja; 0 si `box.FreeWhileNoCreatures` y no hay criaturas vivas |
| `RestockIfNeeded()` | `void` | **(S149)** Reabastece si toca según `ShopCatalogSO.NeedsRestock` y persiste |

## BuyResult (enum)

- `Success` — transacción completa
- `OutOfStock` — sin stock o sistema no disponible
- `AlreadyOwned` — mejora maxeada (solo upgrades)
- `InsufficientFunds` — saldo insuficiente

## Suscripciones (OnEnable / OnDisable)

| Evento | Handler | Efecto |
|--------|---------|--------|
| `GameEvents.OnDayStarted` | `OnDayStarted` | `RestockIfNeeded()` |
| `GameEvents.OnWorldStateReloaded` | `OnWorldStateReloaded` | `catalog.ImportStock(world.ShopStock, world.LastRestockDay)`; restock si toca |

## Persistencia del stock (S149)

`PersistStock()` copia `catalog.ExportStock()` y `LastRestockDay` a `WorldStateSO`, y dispara `GameEvents.WorldStateChanged`. Lo llaman `BuyWorldProp`, `BuyCreatureBox` (solo si consumió stock) y `RestockIfNeeded`.

## BuyUpgrade (S138)

```csharp
public BuyResult BuyUpgrade(ShopUpgradeSO upgrade)
{
    var world = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
    if (upgrade == null || world == null) return BuyResult.OutOfStock;

    int level = world.UpgradeLevel(upgrade.Id);
    if (upgrade.IsMaxed(level)) return BuyResult.AlreadyOwned;

    int price = upgrade.PriceFor(level);
    if (price > 0 && !Wallet.TrySpend(Currency.Dabloons, price, "upgrade")) 
        return BuyResult.InsufficientFunds;

    world.SetUpgradeLevel(upgrade.Id, level + 1);
    GameEvents.WorldStateChanged(world);
    return BuyResult.Success;
}
```

**Flujo:** Lee nivel actual (WorldState.UpgradeLevel) → comprueba max → deduce Dabloons → eleva nivel → dispara WorldStateChanged (persistencia automática vía GameManager).

## CreatureBoxPrice (S138)

Cajas gratuitas mientras el jugador no tenga criaturas vivas (onboarding). Si `box.FreeWhileNoCreatures` y no hay criaturas vivas (`!IsDead && !IsSold`), devuelve 0. Si no, `catalog.FinalPrice(shop, Today)`. El kit inicial ya no depende de esto (S149).

## Entrega (SpawnDeliveryBox)

Instancia `deliveryBoxPrefab` en `deliverySpawnPoint`. Si el prefab no tiene `DeliveryBox`, destruye la instancia, reembolsa el precio y repone el stock.

## Referencias Serializadas

| Referencia | Tipo | Uso |
|-----------|------|-----|
| `catalog` | `ShopCatalogSO` | Precios, restock, stock |
| `deliveryBoxPrefab` | `DeliveryBox` | Instancia para props + cajas |
| `deliverySpawnPoint` | `Transform` | Punto spawn |

## Integración S138 / S149

- AutoPlayer.Step16_Upgrade() itera `catalog.UpgradeListings`, filtra no-maxeados, llama `BuyUpgrade()`
- Mejoras persisten en WorldStateSO automáticamente vía GameEvents.WorldStateChanged
- `ShopZone` lee el nivel de la mejora para abrir o cerrar zonas
- `UncleRescueService` llama `GiftCreatureBox`

## Vinculado a

- [[Index/28 - Currency & Monetization]]
- [[Index/04 - Store & Transactions]]
- [[Index/02 - Genetics & Breeding]] (ciclo de vida cajas)

**Conexiones:** [[Wallet]], [[GameManager]], [[PlayerInventorySO]], [[ShopCatalogSO]], [[DeliveryBox]], [[CreatureBoxSO]], [[ShopUpgradeSO]], [[BreedingDecorSO]], [[WorldStateSO]], [[GameEvents]], [[UncleRescueService]], [[ShopZone]]
