---
tags: [systems, player, rescue, gift, softlock]
---

# UncleRescueService.cs

**Ruta:** `Systems/Player/UncleRescueService.cs`

**Responsabilidad:** Rescate anti-bloqueo. Si el jugador queda "soft-blocked" (no tiene criaturas vivas que no sean huevos, y ademas no puede pagar la eclosion), el tio manda una caja de criaturas (`giftBox`) via `StoreManager.GiftCreatureBox`. Recalcula en `LateUpdate` solo cuando llega un evento marcado como sucio, y solo tras el sync de arranque.

## Logica de Bloqueo (`IsSoftBlocked`)

1. Sin criaturas que hayan salido (`registry.Departed` vacio) = no bloqueado.
2. Si hay criatura viva que no es Egg = no bloqueado.
3. Sin huevos vivos = bloqueado.
4. Con huevos: bloqueado si `Minerita` < costo de eclosion (`BreedingController.InheritanceOdds.HatchCostBase`, fallback 10).

## Eventos Suscritos

| Evento | Efecto |
|--------|--------|
| `OnRegistryChanged`, `OnRegistryReloaded` | Marca dirty |
| `OnInventoryChanged`, `OnInventoryReloaded` | Marca dirty |
| `OnCreatureDeparted` | Marca dirty |

## Metodos Publicos

| Metodo | Descripcion |
|--------|-------------|
| `IsSoftBlocked()` | Evalua el bloqueo (lectura pura) |
| `ForceCall()` | Envia el regalo sin evaluar (boton Odin) |

## Flujo de Envio

`SendGift()` llama `StoreManager.GiftCreatureBox(giftBox)`. Si devuelve true, marca `giftSent` y dispara `GameEvents.RescueGiftSent(giftBox)`. `giftSent` se resetea cuando deja de estar bloqueado, para permitir un nuevo rescate.

## Referencias Serializadas

| Campo | Tipo |
|-------|------|
| `store` | `StoreManager` |
| `giftBox` | `CreatureBoxSO` |
| `cloudSync` | `CloudSyncService` |

**Conexiones:** [[StoreManager]], [[CreatureBoxSO]], [[CloudSyncService]], [[BreedingController]], [[GameEvents]] (`OnRescueGiftSent`), [[InfoOverlayUITK]] (muestra el aviso), [[AdminDevConsole]]
