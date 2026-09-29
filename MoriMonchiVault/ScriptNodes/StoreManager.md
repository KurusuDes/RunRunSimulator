---
tags: [script, store, transactions]
---

# StoreManager

**Ruta:** `Systems/Store/StoreManager.cs`

**Responsabilidad:** Orquestador de compras. Valida saldo vía [[Wallet]], stock, ownership. Muta inventario y dispara eventos. Crea `DeliveryBox` para entregas (props y cajas de criaturas). S137: `BuyCreatureBox()` ahora instancia criaturas con Form especificado (Egg/Slime/Adult via CreatureBoxSO). **S128:** ahora valida saldo con `Wallet.Balance()` y cobra con `Wallet.TrySpend()` (puerta única); orden de operaciones fija: comprueba saldo → concede mueble/prop → cobra al final (un solo evento de persistencia). **S130:** añade `BuyCreatureBox()` con flujo idéntico a props. **S137:** cajas de huevos (Form=Egg) son el entry point del ciclo de vida.

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `BuyFurniture(FurnitureDefinitionSO def, StoreShopData shop)` | `BuyResult` | Compra mueble; valida stock/saldo/ownership, añade al inventario, cobra |
| `BuyWorldProp(ItemDefinitionSO def, StoreShopData shop)` | `BuyResult` | Compra prop; instancia `DeliveryBox`, spawna en punto, cobra |
| `BuyCreatureBox(CreatureBoxSO box, StoreShopData shop)` | `BuyResult` | **(S137)** Compra caja de criaturas con Form especificado; instancia `DeliveryBox`, configura caja, cobra. DeliveryBox mintea criaturas con Form=box.Form |
| `CreatureBoxPrice(CreatureBoxSO box, StoreShopData shop)` | `int` | **(S137)** Calcula precio de caja de criaturas |
| `RestockIfNeeded()` | `void` | Comprueba schedule en catálogo, recarga si aplica |

## BuyResult (enum)

- `Success` — transacción completada
- `OutOfStock` — no hay en stock o sistema no disponible
- `AlreadyOwned` — mueble ya poseído (furniture solo)
- `InsufficientFunds` — saldo insuficiente

## Flujo BuyCreatureBox (S130 + S137)

```
1. Valida args (box, shop)
2. Valida stock (shop.InStock)
3. Valida inventario no-nulo
4. Calcula precio via CreatureBoxPrice()
5. Cobra primero (BuyResult si insuficiente)
6. TryConsume stock
7. Instancia DeliveryBox via SpawnDeliveryBox()
8. Configure(box) — box contiene Form (S137)
9. Si price == 0: dispara InventoryChanged manualmente
```

**Invariante S137:** DeliveryBox.Interact() mintea criaturas con `dna.Form = box.Form`. Kit inicial contiene cajas Form=Egg (5 gratuitas).

## Referencias

| Referencia | Tipo | Uso |
|-----------|------|-----|
| `catalog` | `ShopCatalogSO` | Catálogo, precios finales, cálculo restock |
| `deliveryBoxPrefab` | `DeliveryBox` (prefab) | Instancia para props + cajas de criaturas |
| `deliverySpawnPoint` | `Transform` | Punto de spawn de cajas |

## Integración S137

- Ciclo de vida: cajas de huevos gratis en kit inicial. Kit inicial (S137) contiene 1 caja creatorBox con Form=Egg y Count=5.
- AutoPlayer.Step2_BuyEggBox() filtra cajas por Form=Egg y precio=0

## Integración S128

- **Acceso a saldo:** `Wallet.Balance(Currency)` (no directo a SO)
- **Gasto:** `Wallet.TrySpend()` (registra en log, dispara evento automático)
- **Reembolsos:** `Wallet.Add()` si error post-gasto

## Vinculado a

- [[Index/04 - Store & Transactions]]
- [[Index/02 - Genetics & Breeding]] (S137: ciclo de vida)
- [[Index/09 - Active Context]] (S137: kit inicial)
- [[Index/28 - Cimientos y camino a Game Ready]] (§3 · two currencies)

**Conexiones:** [[Wallet]], [[GameManager]], [[PlayerInventorySO]], [[ShopCatalogSO]], [[StoreShopData]], [[DeliveryBox]], [[CreatureBoxSO]], [[StorePanelUITK]], [[GameEvents]]
