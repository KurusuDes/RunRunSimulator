---
tags: [script, world, npc, core, queue]
---

# NpcAgent.cs

**Ruta:** `World/Npc/NpcAgent.cs`

**Responsabilidad:** Cliente NPC en tienda: navega estantes, espera fila, negocia, compra. **S138:** TickQueueing mide distancia al slot en plano XZ (antes 3D, offset Y=0.83 impedía llegar).

## S138: Queue Distance Fix

**TickQueueing() — líneas 230-232:**
```csharp
Vector3 toSlot = reservedQueueSlot - transform.position;
toSlot.y = 0f;  // Normaliza a plano horizontal (XZ)
float dist = toSlot.magnitude;
```

**Cambio:** Antes usaba 3D (includes Y), offset vertical 0.83 hacía imposible llegar. Ahora solo cuenta distancia XZ (plano suelo).

**Propósito:** NPC llega a caja cuando distancia XZ < arriveDistance.

## Métodos

- `Initialize()` — Setup inicial
- `AcceptCurrentOffer()` — Compra vía CreatureLifecycle.Adopt()
- `TickQueueing()` — Mantiene posición en fila (S138: distancia XZ)

## Enums

- `NpcState`: Spawned, Wandering, InspectingDisplay, ApproachingRegister, Queueing, WaitingAtRegister, Negotiating, Leaving
- `LeaveReason`: None, Purchased, Outbid, QueueFull

## Conexiones

- [[CashRegister]], [[StoreContainer]], [[CreatureLifecycle]], [[NpcNameBank]]
