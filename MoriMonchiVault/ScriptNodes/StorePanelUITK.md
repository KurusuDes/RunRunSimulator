---
tags: [script, ui, store, panel]
---

# StorePanelUITK.cs

**Ruta:** `UI/StorePanelUITK.cs`

**Responsabilidad:** Panel de tienda (PC de la tienda) con 8 pestañas: Expansiones (mejoras de tienda), WorldProps (herramientas), Consumables (comida y medicina), Creatures (cajas de criaturas), Decor (decoraciones de cría), Toys (juguetes), Orders (encargos del día, **S151**) y Goals (metas de progreso, **S152**). Renderiza las tiles que arma `StoreTileView` a partir de las filas de `StoreRows`, muestra la fila seleccionada en la ficha `StoreDetailCard` y ejecuta la compra vía `StoreManager`. Precio dinámico por día de juego; los descuentos se calculan con `ShopCatalogSO.IsDiscountActive(day)`.

**S131:** Cambió DateTime (UTC) → int day (GameClock.Instance.Day).
**S138:** las mejoras (ahora "Expansiones") se listan como filas con nivel actual y precio del siguiente nivel.
**S149:** sale la pestaña Furniture (muebles borrados); entran Expansions, Decor y Toys.
**S151:** entra la pestaña Orders.
**S152:** entra la pestaña Goals; la compra rechazada por bloqueo (`BuyResult.Locked`) muestra aviso.
**S161:** overhaul visual: tiles con ícono y píldora de precio (`StoreTileView`), ficha de detalle con botón de compra (`StoreDetailCard`) y precio con descuento (`StorePrice`). La fila seleccionada usa la clase `store-tile--selected`.
**S162:** la ficha recibe `affordable` (`CanAfford`: saldo ≥ precio final, o fila sin compra ni tope) y el grid rellena con tiles vacías hasta completar las filas visibles (`StoreTileView.BuildEmpty`), con columnas calculadas por ancho.

## Pestañas

| Tab | Contenido | Notas |
|-----|-----------|-------|
| Expansions | Mejoras de tienda (`UpgradeListings`) | Click ejecuta `BuyUpgrade`; muestra "Nv x/y" y "Max" al tope. Bloqueadas por meta: fila de solo lectura (S152) |
| WorldProps | Herramientas (`WorldPropCategory.Tool`) | Compra con stock. Bloqueadas por meta: solo lectura (S152) |
| Consumables | Comida y medicina | Compra con stock. Bloqueadas por meta: solo lectura (S152) |
| Creatures | Cajas de criaturas (S137) | Precio dinámico vía `CreatureBoxPrice` |
| Decor | Decoraciones de cría (S149) | Precio fijo; nombre oculto hasta descubrirla |
| Toys | Juguetes (`WorldPropCategory.Toy`, S151) | Compra con stock |
| Orders | Encargos del día (`OrderBoardService`, S151) | Solo muestra el encargo y la recompensa; no hay botón de compra |
| Goals | Metas de progreso (`GoalService`, S152) | Solo lectura: título, progreso `n/Target` y recompensa con lo que abre |

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento de la tienda |
| `panel` | `UIPanelType` | Default `Store` |
| `store` | `StoreManager` | Compra, catálogo y restock. `Catalog` sale de aquí |

## Comportamiento

- **Apertura:** `ResetAndRebuild()` pide `store.RestockIfNeeded()`, vuelve a la primera pestaña y reconstruye.
- **Navegación:** eje x cambia de pestaña; eje y mueve la selección entre tiles; Submit compra la fila seleccionada.
- **Tiles:** clic simple selecciona; doble clic compra (`StoreTileView.Build`). Las tiles vacías de relleno no reciben clic.
- **Ficha:** `StoreDetailCard.Show` con la fila seleccionada, el descuento activo y `CanAfford(row)`; `SetEmpty` si no hay selección. El botón de compra de la ficha se suscribe a `BuySelected`.
- **Filas de solo lectura:** si `row.Buy == null` la tile muestra la recompensa (`Reward`). Lo usan Orders, Goals y las filas bloqueadas (S151/S152).
- **Estado vacío:** el texto `ui.store.empty.orders` aparece en Orders y `ui.store.empty` en el resto.
- **Resultado de compra:** `Success` reconstruye la lista; `OutOfStock`, `InsufficientFunds` y `AlreadyOwned` muestran un aviso 2.5 s. **(S152)** `Locked` muestra `ui.store.result.locked`.
- **Descuento:** tachado del precio base cuando `DiscountBase > 0` y el día es de descuento (no aplica si hay `PriceOverride`). Lo resuelve `StorePrice.Resolve`.

## Eventos

- Suscritos: `UIManager.OnPanelToggleRequested`, `UIManager.OnPanelSetRequested`, `GameEvents.OnInventoryChanged` (refresca el saldo), `GameEvents.OnInventoryReloaded` (solo refresca el saldo).

## Conexiones

- [[GameClock]] — `Day`
- [[ShopCatalogSO]] — listings de cada pestaña e `IsDiscountActive`
- [[StoreManager]] — `BuyUpgrade`, `BuyDecor`, `BuyCreatureBox`, `BuyWorldProp`, `CreatureBoxPrice`, `RestockIfNeeded`
- [[StoreRows]] — `Collect()` por pestaña (genera `Row`)
- [[StoreTileView]] (S161) — tiles, relleno vacío y clase de selección
- [[StoreDetailCard]] (S161) — ficha y botón de compra
- [[StorePrice]] (S161) — precio y descuento
- [[OrderBoardService]] — fuente de la pestaña Orders (S151)
- [[GoalService]] — fuente de la pestaña Goals (vía `StoreRows`, S152)
- [[Wallet]] — saldo de Dabloons
- [[GameEvents]] — refresco del saldo
- [[UIManager]] — ciclo del panel y navegación
