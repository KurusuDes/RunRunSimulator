---
tags: [script, ui, store]
---

# StorePanelUITK

**Ruta:** `UI/StorePanelUITK.cs`

**Responsabilidad:** Panel de tienda (4 pestañas: Furniture/WorldProps/Consumables/Creatures). S137: Soporta compra de cajas de criaturas con Form específico (Egg/Slime/Adult). S131: Precio por día de juego (descuentos dinámicos via `ShopCatalogSO.IsDiscountActive(day)` + `FinalPrice(shop, day)`). Reemplazó `GameManager.Now` (UTC) → `GameClock.Instance.Day` (día de juego).

## Cambio S131

**Cálculo de precio dinámico:**
```csharp
int today = GameClock.Instance?.Day ?? 1;
int price = ShopCatalogSO.Instance.FinalPrice(shop, today);
priceLabel.text = price.ToString();
```

**Descuentos módulo:**
- `IsDiscountActive(day)` → `day % DiscountEveryDays == 0`
- `FinalPrice(shop, day)` → aplica descuento si activo

## Cambios S137

**Creatures tab:** Ahora muestra cajas de criaturas con Form. AutoPlayer.Step2_BuyEggBox filtra cajas gratis (precio=0) con Form=Egg.

## Integración S137

- Ciclo de vida: cajas de huevos gratis en kit inicial. UI filtra por disponibilidad.
- StarterKitService aplica kit inicial al detectar partida nueva.

## Conexiones (S131 + S137)

- [[GameClock]] — proporciona Day (S131)
- [[ShopCatalogSO]] — cálculo de precio
- [[StoreManager]] — llamadas BuyFurniture/BuyCreatureBox (S137)
- [[StoreRows]] — Collect(Tab, catalog, store, rows)
- [[CreatureBoxSO]] — cajas con Form (S137)

## Notas

- Sin GameManager.Now (UTC).
- Descuentos dinámicos cada N días (S131).
- Form en CreatureBoxSO permite filtrar por tipo de criatura (S137).
