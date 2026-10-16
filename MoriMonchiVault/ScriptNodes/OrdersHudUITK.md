---
tags: [script, ui, uitk, hud, orders]
---

# OrdersHudUITK.cs

**Ruta:** `UI/OrdersHudUITK.cs`

**Responsabilidad:** Bloque "encargos del día" del HUD (arriba a la izquierda). Lista los encargos activos de `OrderBoardService` con su descripción y recompensa en Dabloons. Se oculta si no hay encargos o si hay UI con foco. Presentación pura: no escribe en el tablero ni paga recompensas (S161).

**Vinculado a:** [[Index/05 - UI System]], [[Index/32 - Demo Brawl 3v3 arcade]]

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento del HUD. Se resuelve con `UiPanels.RootOf` |

## Elementos UXML

- `orders`: bloque completo (`display` none / flex).
- `orders-title`: título localizado (`ui.orders.hud.title`).
- `orders-list`: contenedor de filas.
- Filas creadas en código: `orders-row` con `orders-bullet`, `orders-text` (`ShopOrder.Describe()`) y `orders-reward` con `orders-reward__amount` (`+Reward`) y `orders-reward__coin`.

## Eventos Suscritos (OnEnable / OnDisable)

| Evento | Handler | Efecto |
|--------|---------|--------|
| `GameEvents.OnWorldStateChanged` / `OnWorldStateReloaded` | `HandleWorldState` | Refresca |
| `GameEvents.OnDayStarted` | `HandleDayStarted` | Refresca (tablero nuevo del día) |
| `GameEvents.OnOrderCompleted` | `HandleOrderCompleted` | Refresca (quita el encargo cumplido) |
| `UIManager.OnUIFocusChanged` | `HandleUIFocus` | Oculta con UI abierta |
| `LocalizationSettings.SelectedLocaleChanged` | `HandleLocaleChanged` | Refresca textos |

`Start` resuelve los elementos y refresca.

## Conexiones

- [[OrderBoardService]] — `Instance.Active` (fuente de los encargos)
- [[ShopOrder]] — `Describe()`, `Reward`
- [[GameEvents]] — eventos de la tabla
- [[UIManager]] — foco de UI
- [[UiPanels]] — `RootOf`
- [[Loc]] — `Tr`

## Notas

- Sin `Find*`: el tablero se lee por su singleton de servicio.
- Textos de la UI pasan por `Loc`; la descripción del encargo sale de `ShopOrder.Describe()`.
