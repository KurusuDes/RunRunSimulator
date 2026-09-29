---
tags: [script, ui, store, panel]
---

# StorePanelUITK.cs

**Ruta:** `UI/StorePanelUITK.cs`

**Responsabilidad:** Panel de tienda (4 pestañas: Furniture/WorldProps/Consumables/Creatures). **S138:** Furniture tab ahora incluye mejoras (visualmente al final de muebles). Soporta Form en cajas de criaturas (Egg/Slime/Adult). Precio dinámico por día de juego. Descuentos via `IsDiscountActive(day)`.

**S131:** Cambió DateTime (UTC) → int day (GameClock.Instance.Day).

## Pestañas

| Tab | Contenido | Cambios |
|-----|-----------|---------|
| Furniture | Muebles + mejoras **(S138)** | Mejoras se listan al final de muebles; click dispara BuyUpgrade |
| WorldProps | Props/naturales | Sin cambios |
| Consumables | Items | Sin cambios |
| Creatures | Cajas de criaturas (S137) | Form especificado (Egg/Slime/Adult); precio dinámico via CreatureBoxPrice |

## Integración S138

**StoreRows.Collect(Tab.Furniture, ...)** ahora:
1. Itera `catalog.FurnitureListings` (muebles normales)
2. Itera `catalog.UpgradeListings` (mejoras) — sin Stock, con PriceOverride
3. Construye Row con `Buy = () => store.BuyUpgrade(upgrade)`

**Rendering:**
- Las mejoras se renderizan como filas adicionales con nivel actual + precio para siguiente nivel
- Click ejecuta BuyUpgrade (automático via Row.Buy)
- IsSoldOut: nunca (siempre disponibles); IsMaxed: si nivel >= MaxLevel

## Conexiones (S131 + S137 + S138)

- [[GameClock]] — Day (S131)
- [[ShopCatalogSO]] — Furniture/Items/CreatureBoxes/Upgrades (S138)
- [[StoreManager]] — BuyFurniture/BuyWorldProp/BuyCreatureBox/BuyUpgrade (S138)
- [[StoreRows]] — Collect() genera Row list (S138: con Upgrade field)
- [[Wallet]] — Balance display
- [[GameEvents]] — OnInventoryChanged/Reloaded refrescan UI

## Notas

- Descuentos módulo: `day % DiscountEveryDays == 0`
- FinalPrice dinámico en cada render
- Mejoras persisten en WorldStateSO automáticamente
- S138: UI neutral entre muebles y mejoras (ambos en Furniture tab)
