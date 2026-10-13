---
tags: [script, systems, store, orders, singleton]
---

# OrderBoardService.cs

**Ruta:** `Systems/Store/OrderBoardService.cs`

**Responsabilidad:** Tablero de encargos diarios de la tienda. Genera 3 `ShopOrder` por día (mezcla de sets de partes y roles, sin repetir), los guarda en `WorldStateSO.Orders` y completa uno cuando un cliente vendido cumple su gusto (paga dabloons). Dueño de la lógica de encargos; no persiste por sí mismo (lo hace `GameManager` al recibir `WorldStateChanged`).

## Reglas

- `OrdersPerDay` = 3, intentos máximos = 40.
- Recompensas: rol 15, set 20 dabloons.
- Se re-tira solo si `WorldState.OrdersDay != day`.
- Mitad de tiradas sets de partes (si hay sets disponibles en Horns/Backs/Wings), mitad roles.
- Un encargo se completa si `ToTaste(db).Match(dna, db) >= 1`. Se quita de la lista, se acredita con `Wallet.Add(Dabloons, Reward, "order")`.

## Eventos que escucha

| Evento | Acción |
|--------|--------|
| `OnWorldStateReloaded` | Re-tira si el día cambió |
| `OnDayStarted` | Re-tira |
| `OnCustomerSold` | Intenta completar un encargo |

## Eventos que emite

- `GameEvents.WorldStateChanged(world)` — tras re-tirar o completar (GameManager persiste)
- `GameEvents.OrderCompleted(order)` — tras pagar la recompensa; lo escucha `InfoOverlayUITK` para el toast

## Propiedades

- `Instance` (singleton), `Active` (lista de encargos del día o vacía si no hay mundo)

## Conexiones

- [[WorldStateSO]] — `Orders`, `OrdersDay`
- [[ShopOrder]] — modelo
- [[CreatureDatabaseSO]] — sets y roles disponibles
- [[GameManager]] — `WorldState`, `Database`
- [[GameEvents]] — `OnWorldStateReloaded`, `OnDayStarted`, `OnCustomerSold`, `WorldStateChanged`, `OrderCompleted`
- [[Wallet]] — acredita la recompensa
- [[StoreRows]] — pestaña Orders de la tienda lee `Active`
- [[InfoOverlayUITK]] — toast de encargo completado
