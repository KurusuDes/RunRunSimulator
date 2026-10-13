---
tags: [script, world]
---

# WorldPropInstance.cs

**Ruta:** `World/Props/WorldPropInstance.cs`

**Responsabilidad:** Tag de identidad (I#) para props sueltos del mundo, y punto de entrada de recoger (`IInteractable` → `HotbarController.PickUp`). Guarda si el prop nació en runtime (para que `GameManager` lo recoja al cerrar) y si está en mano del jugador.

## Campos y propiedades

| Miembro | Tipo | Descripción |
|---------|------|-------------|
| `itemId` | string (ReadOnly, serializado) | ID del `ItemDefinitionSO` (I#). Se estampa al spawnear; serializado para que un prop colocado a mano en escena también tenga identidad |
| `ItemId` | string | Getter del `itemId` |
| `IsHeld` | bool (get/set público) | True mientras el prop está en la mano del jugador. Lo leen `BubbleMachine` (no emite si está en mano) y `Toy` (`IsHeldByPlayer`) |
| `SpawnedAtRuntime` | bool | True si lo configuró `Configure` (spawn en juego) |

## Métodos

| Método | Descripción |
|--------|-------------|
| `Configure(string id)` | Fija `itemId` y marca `SpawnedAtRuntime = true` |
| `Interact()` | `HotbarController.Instance.PickUp(this)`; avisa si no hay hotbar en escena |

## Conexiones

- [[HotbarController]] — recoge el prop (`PickUp`) y lo sostiene
- [[GameManager]] — `CollectLooseWorldProps` recoge los props sueltos con `SpawnedAtRuntime` al cerrar o pausar (S151: lee `IsHeld` y `ItemId`)
- [[Toy]] — `IsHeldByPlayer`, y los juguetes que son props también
- [[BubbleMachine]] — no emite mientras `IsHeld`
- [[Interfaces]] — `IInteractable`
- [[StorageContainer]]

**Vinculado a:** [[Index/06 - Player & World]]
