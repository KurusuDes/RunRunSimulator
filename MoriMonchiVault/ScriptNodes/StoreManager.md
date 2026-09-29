---
tags: [script, store, transactions, manager]
---

# StoreManager.cs

**Ruta:** `Systems/Store/StoreManager.cs`

**Responsabilidad:** Orquestador de compras. Valida saldo vía `Wallet`, stock, ownership. Muta inventario, dispara eventos. Crea `DeliveryBox` para entregas (props, cajas de criaturas). **S138:** añade `BuyUpgrade()` + `CreatureBoxPrice()`. Flujo invariante: comprueba saldo → aplica → cobra → un evento de persistencia.

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `BuyFurniture(FurnitureDefinitionSO def, StoreShopData shop)` | `BuyResult` | Valida stock/saldo/ownership, añade inventario, cobra |
| `BuyWorldProp(ItemDefinitionSO def, StoreShopData shop)` | `BuyResult` | Instancia DeliveryBox, configura prop, cobra |
| `BuyCreatureBox(CreatureBoxSO box, StoreShopData shop)` | `BuyResult` | **(S137)** Instancia DeliveryBox con criaturas Form=box.Form, cobra |
| `BuyUpgrade(ShopUpgradeSO upgrade)` | `BuyResult` | **(S138)** Valida nivel < max, deduce Dabloons, eleva nivel en WorldState, dispara evento |
| `CreatureBoxPrice(CreatureBoxSO box, StoreShopData shop)` | `int` | **(S138)** Precio de caja; 0 si `box.FreeWhileNoCreatures` y no hay criaturas vivas |

## BuyResult (enum)

- `Success` — transacción completa
- `OutOfStock` — sin stock o sistema no disponible
- `AlreadyOwned` — mueble ya poseído (solo furniture) ó mejora maxeada (solo upgrades)
- `InsufficientFunds` — saldo insuficiente

## BuyUpgrade (S138) — Nueva API

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

## CreatureBoxPrice (S138) — Nueva Lógica

```csharp
public int CreatureBoxPrice(CreatureBoxSO box, StoreShopData shop)
{
    if (box != null && box.FreeWhileNoCreatures)
    {
        var registry = GameManager.Instance?.Registry;
        if (registry == null) return catalog.FinalPrice(shop, Today);

        bool hasLivingCreature = false;
        foreach (var dna in registry.GetAll().Values)
        {
            if (dna.IsDead || dna.IsSold) continue;
            hasLivingCreature = true;
            break;
        }
        if (!hasLivingCreature) return 0;
    }
    return catalog.FinalPrice(shop, Today);
}
```

**Propósito:** Cajas gratuitas mientras el jugador no tenga criaturas vivas (onboarding). Kit inicial usa esto.

## Referencias Serializadas

| Referencia | Tipo | Uso |
|-----------|------|-----|
| `catalog` | `ShopCatalogSO` | Precios, restock |
| `deliveryBoxPrefab` | `DeliveryBox` | Instancia para props + cajas |
| `deliverySpawnPoint` | `Transform` | Punto spawn |

## Integración S138

- AutoPlayer.Step16_Upgrade() itera `catalog.UpgradeListings`, filtra no-maxeados, llama `BuyUpgrade()`
- Mejoras persisten en WorldStateSO automáticamente vía GameEvents.WorldStateChanged

## Vinculado a

- [[Index/28 - Currency & Monetization]]
- [[Index/04 - Store & Transactions]]
- [[Index/02 - Genetics & Breeding]] (ciclo de vida cajas)

**Conexiones:** [[Wallet]], [[GameManager]], [[PlayerInventorySO]], [[ShopCatalogSO]], [[DeliveryBox]], [[CreatureBoxSO]], [[ShopUpgradeSO]], [[GameEvents]]
