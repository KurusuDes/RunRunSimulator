---
tags: [script, world, props]
---

# HotbarController.cs

**Ruta:** `World/Props/HotbarController.cs`

**Responsabilidad:** Hotbar de 6 slots en modo play. Pickup de `WorldPropInstance`, uso, throw, drop. Singleton `Instance` + eventos estáticos. Persiste slots en `PlayerInventorySO` (vía `SetHotbarSlot` / `GetHotbarSlot` / `ClearHotbarSlot`). Mantiene el visual en mano (`heldVisual`) para el slot activo, re-spawneado en load. S69: método `TryConsumeActiveFood() → bool` (si hotbar activo es Food, quita del slot, destruye visual en mano, emite `OnHotbarChanged` + `InventoryChanged`, NO dispara `OnItemUsed`). Consumo por `AgentBrain.TickHandFeed()` para comida de la mano. **S149:** `ActiveHeldObject` expone el visual en mano; `AgentToys` lo usa para detectar un juguete que el jugador sostiene (robo al jugador).

## Estructura

**Slots (0–5):**
- Almacenados en `PlayerInventorySO` (string[6], ids "I#" o null)
- Un slot activo (default 0)
- Visual en mano cuando ocupado (`heldVisual`, GameObject spawneado de prefab en `handAnchor`)

**Singleton:**
- `HotbarController.Instance` — acceso global
- Espera a que `GameManager.CurrentInventory` cargue; `OnInventoryReloaded` llama `EquipActive()` que re-spawnea el visual

## Propiedades Públicas

- `ActiveSlot` (int, read-only) — slot activo actual (0–5)
- `ActiveItemId` (string, read-only) — id "I#" del slot activo, null si vacío
- `ActiveHeldObject` (GameObject, read-only) — **(S149)** visual que el jugador tiene en la mano, null si no hay
- `HasActiveItem` (bool, read-only) — true si `ActiveItemId` no es null
- `IsOfferingFood` (bool, read-only) — true si slot activo contiene ítem con `ItemDefinitionSO.Category == WorldPropCategory.Food`

## Métodos Públicos

**Gestión de slot:**
- `ScrollActive(int dir)` — rueda del mouse; cambia slot activo con wrap-around (0→5, 5→0)
- `SetActiveSlot(int index)` — establece slot activo, re-spawnea el visual, emite `OnHotbarChanged`

**Pickup (tap E en prop suelto):**
- `PickUp(WorldPropInstance prop) → bool` — almacena id en primer slot libre (preferencia: slot activo), **destruye el GameObject del prop**, emite `InventoryChanged` + `OnHotbarChanged`. Retorna false si el hotbar está lleno.

**Uso:**
- `UseActive()` — emite `OnItemUsed` con id del slot activo. El efecto específico se conecta por listeners, **no aquí**.
- `TryConsumeActiveFood() → bool` — **S69, core food handFeed (verificado E2E en S70)**:
  1. Si `!IsOfferingFood`, retorna false
  2. Limpia slot activo (`ClearHotbarSlot`)
  3. Destruye `heldVisual`
  4. Emite `InventoryChanged` + `OnHotbarChanged`
  5. Retorna true
  6. **NO dispara** `OnItemUsed` (que es para equipo; food es consumo directo)

**Throw (hold E) / Drop (Q):**
- `ThrowActive(Vector3 force) → bool` — suelta item activo al mundo con impulso. Si tiene `IThrowable`, llama `OnThrow`; si no, aplica impulso al Rigidbody. Limpia slot y emite eventos. Retorna false si no hay item.
- `DropActive() → bool` — suelta item activo al mundo sin impulso. Si tiene `IThrowable`, llama `OnRelease`. Retorna false si no hay item.

## Eventos

**Estáticos (C#):**
- `OnHotbarChanged` (Action) — emitido tras cambio de contenido, slot activo, o pickup/drop
- `OnItemUsed` (Action<string>) — emitido al usar item (UseActive), transporta id "I#"

**Suscritos (OnEnable):**
- `GameEvents.OnInventoryReloaded` → `OnInventoryReloaded` (EquipActive + OnHotbarChanged)
- `PlayerInputs.HotbarScrolled` → `ScrollActive`
- `PlayerInputs.DropPressed` → `DropActive`

Se desuscribe en `OnDisable`.

## Campos Privados Significativos

- `activeSlot` (int) — slot actual (0–5)
- `heldVisual` (GameObject) — visual spawneado en mano, kinematic + colliders off mientras esté aquí
- `database` (ItemDatabaseSO, Required) — ref para lookups de definiciones
- `handAnchor` (Transform) — donde se spawneatea el visual en mano

## Ciclo de Vida

1. **Awake:** `Instance = this`
2. **OnEnable:** suscribe eventos (ver arriba)
3. **OnInventoryReloaded:** `EquipActive()` re-spawneatea el visual del slot activo, `OnHotbarChanged()`
4. **OnDisable:** desuscribe

## Persistencia

- Slots: `GameManager.CurrentInventory` (hotbar, persiste entre sesiones)
- Visual: re-spawneado en `OnInventoryReloaded`

## Notas de Implementación

- `FirstFreeSlot()` busca el preferido (slot activo si está vacío, si no el primer vacío, si no -1)
- `ReleaseActiveIntoWorld()` es helper compartido por throw y drop: limpia slot, despega visual y emite eventos
- `EquipActive()` es privada; spawneatea visual desde prefab y configura `WorldPropInstance.IsHeld`
- `HoldInHand()` / `ReleaseHeld()` son helpers para flip de Rigidbody y colliders
- `IsOfferingFood` es check barato (lookup id → def → Category == Food)
- `TryConsumeActiveFood()` es idempotente: sin comida activa devuelve false sin efectos

## Cambios S149

- Se expone `ActiveHeldObject` para `AgentToys` (robo de juguete al jugador).
- Acceso a slots vía `GetHotbarSlot` / `SetHotbarSlot` / `ClearHotbarSlot` del inventario (API renombrada en `PlayerInventorySO`).

## Cambios S93

- Referencia actualizada: `CurrentInventory` ahora accedida via `GameManager.CurrentInventory`.
- Método `GetByID()` para acceder a definiciones de ítems por ID.

## Vinculado a

[[Index/06 - Player & World]]

## Conexiones

[[WorldPropInstance]], [[ItemDefinitionSO]], [[ItemDatabaseSO]], [[PlayerInventorySO]], [[GameManager]], [[GameEvents]], [[PlayerInputs]], [[PlayerController]], [[AgentBrain]] (comida de la mano), [[AgentToys]] (juguete en mano), [[HotbarHUDUITK]], [[UIManager]]
