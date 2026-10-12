---
tags: [script, world, npc, core, queue]
---

# NpcAgent.cs

**Ruta:** `World/Npc/NpcAgent.cs`

**Responsabilidad:** Cliente NPC de la tienda: recorre exhibiciones, elige una criatura según su gusto y su presupuesto, hace fila, negocia y compra (o se va). **S138:** `TickQueueing` mide la distancia al slot en plano XZ (antes 3D; el offset Y=0.83 impedía llegar). **S149:** el cliente tiene gusto (`CustomerTaste`) y presupuesto; la elección y la oferta inicial se calculan con ambos. Sus áreas caminables salen de la lista `walkableAreaNames`.

## Estado de Cliente (S149)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Taste` | `CustomerTaste` | Gusto tirado en `Initialize` (rol, color o set de partes) |
| `Budget` | int | Presupuesto tirado entre `BudgetMin` y `BudgetMax` del arquetipo |
| `PickMatch` | float | Cumplimiento del gusto de la criatura elegida |
| `InitialOffer` / `CurrentOffer` | int | Oferta inicial (valuación con `tasteMatch`) y la vigente |
| `TargetMM` | `CreatureDNA` | Criatura elegida |
| `Reason` | `LeaveReason` | Por qué se va |
| `HasCounteredOnce` | bool | Ya usó contraoferta |
| `State` | `NpcState` | Estado actual |

## Estados (`NpcState`)

Spawned, Wandering, InspectingDisplay, ApproachingRegister, Queueing, WaitingAtRegister, Negotiating, Leaving.

## Razones de salida (`LeaveReason`)

None, Purchased, Outbid (otro cliente compró la criatura), QueueFull.

## Inicialización (Initialize)

1. Arquetipo, nombre aleatorio (`NpcNameBank`), exhibiciones, caja y controlador.
2. `ApplyWalkableAreas()`: máscara de `walkableAreaNames` (default ShopFrontDesk y Outside; si no existe ninguna, sin restricción).
3. `ApplyInstanceVariation()`: velocidad, giro y aceleración ±`moveVariation`; `avoidancePriority` en `avoidancePriorityRange`; `ReactionDelay` en `reactionDelayRange`.
4. Inspecciones: entre `MinInspections` y `MaxInspections`.
5. Presupuesto: entre `BudgetMin` y `BudgetMax`.
6. `Taste = CustomerTaste.Roll(archetype, criaturas en exhibición libres, Database)`.

## Elección de criatura (BestPickFromContainer)

- Tope: `Budget * 1.2`.
- Por cada criatura libre de la exhibición: `match = Taste.Match(dna, db)`; `price = Valuation.Estimate(dna, archetype, pricing, match)`.
- Si el gusto es None o `match >= 1`, la más cara dentro del tope es la mejor.
- Si no hay mejor match, con probabilidad `BuyWithoutMatchChance` elige la más barata.
- Sin elección: vuelve a Wandering o sale si ya no le quedan inspecciones.

## Fila y compra

- `TickApproachingRegister` pide un slot en la caja (`CashRegister.TryReserveSlot`). Si no hay, sale por `QueueFull`.
- `TickQueueing` avanza hasta el slot con distancia XZ (S138). Al llegar al frente pasa a `WaitingAtRegister`.
- `WaitingAtRegister` sale tras `WaitTimeoutSeconds`.
- `AcceptCurrentOffer()`: `Wallet.Add(Dabloons, CurrentOffer)`, `CreatureLifecycle.Adopt(TargetMM)` y `GameEvents.CustomerSold`.
- `TryCounterOffer()`: una sola contraoferta según `NegotiationFlow`.

## Eventos

**Suscritos:** `GameEvents.OnCustomerSold` (`OnSomeoneSold`). Si otro cliente compra la misma criatura, este sale con `Outbid`.

**Emitidos:** `GameEvents.CustomerSold`.

## Tuning (inspector)

- `arriveDistance` (0.5, Min 0.1)
- `walkableAreaNames` (lista de áreas NavMesh; dropdown del editor)
- `moveVariation` (0.15), `avoidancePriorityRange` (30-70), `reactionDelayRange` (0.2-1.2 s)

## Vinculado a

- [[Index/06 - Customer System]]

## Conexiones

**Clientes y valuación:** [[CustomerArchetypeSO]], [[CustomerTaste]], [[ValuationHandler]], [[CustomerPricingSO]], [[NegotiationFlow]], [[CustomerService]]

**Tienda:** [[StoreContainer]] (exhibiciones), [[CashRegister]] (caja y fila), [[NpcController]] (spawn y despawn), [[NpcThoughtTag]] (burbuja)

**Sistemas:** [[CreatureLifecycle]] (`Adopt`), [[Wallet]], [[GameEvents]], [[NpcNameBank]], [[CreatureDNA]], [[CreatureAvailability]]
