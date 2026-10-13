---
tags: [script, ui, store, panel]
---

# StorePanelUITK.cs

**Ruta:** `UI/StorePanelUITK.cs`

**Responsabilidad:** Panel de tienda con 8 pestañas: Expansiones (mejoras de tienda), WorldProps (herramientas), Consumables (comida y medicina), Creatures (cajas de criaturas), Decor (decoraciones de cría), Toys (juguetes), Orders (encargos del día, **S151**) y Goals (metas de progreso, **S152**). Renderiza las filas que arma `StoreRows` y ejecuta la compra vía `StoreManager`. Precio dinámico por día de juego; los descuentos se calculan con `ShopCatalogSO.IsDiscountActive(day)`.

**S131:** Cambió DateTime (UTC) → int day (GameClock.Instance.Day).
**S138:** las mejoras (ahora "Expansiones") se listan como filas con nivel actual y precio del siguiente nivel.
**S149:** sale la pestaña Furniture (muebles borrados); entran Expansions, Decor y Toys.
**S151:** entra la pestaña Orders.
**S152:** entra la pestaña Goals; la compra rechazada por bloqueo (`BuyResult.Locked`) muestra aviso.

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

## Comportamiento

- **Apertura:** `ResetAndRebuild()` pide `store.RestockIfNeeded()`, vuelve a la primera pestaña y reconstruye.
- **Navegación:** eje x cambia de pestaña; eje y mueve la selección entre filas; Submit compra la fila seleccionada.
- **Filas de solo lectura:** si `row.Buy == null` solo se dibuja el nombre y la recompensa (`store-row__price`). Lo usan Orders, Goals y las filas bloqueadas (S151/S152).
- **Estado vacío:** el texto `ui.store.empty.orders` aparece en Orders y `ui.store.empty` en el resto.
- **Resultado de compra:** `Success` reconstruye la lista; `OutOfStock`, `InsufficientFunds` y `AlreadyOwned` muestran un aviso 2.5 s. **(S152)** `Locked` muestra `ui.store.result.locked`.
- **Descuento:** tachado del precio base cuando `DiscountBase > 0` y el día es de descuento (no aplica si hay `PriceOverride`).

## Eventos

- Suscritos: `UIManager.OnPanelToggleRequested`, `UIManager.OnPanelSetRequested`, `GameEvents.OnInventoryChanged`, `GameEvents.OnInventoryReloaded` (solo refresca el saldo).

## Conexiones

- [[GameClock]] — `Day`
- [[ShopCatalogSO]] — listings de cada pestaña
- [[StoreManager]] — `BuyUpgrade`, `BuyDecor`, `BuyCreatureBox`, `BuyWorldProp`, `CreatureBoxPrice`, `RestockIfNeeded`
- [[StoreRows]] — `Collect()` por pestaña (genera `Row`)
- [[OrderBoardService]] — fuente de la pestaña Orders (S151)
- [[GoalService]] — fuente de la pestaña Goals (vía `StoreRows`, S152)
- [[Wallet]] — saldo de Dabloons
- [[GameEvents]] — refresco del saldo
- [[UIManager]] — ciclo del panel y navegación
