---
tags: [script, inventory, world-props]
---

# ItemDefinitionSO

**Ruta:** `Data/Items/ItemDefinitionSO.cs`

**Responsabilidad:** Definición de world prop (objeto tangible): ID, nombre, categoría, prefab 3D e ícono de hotbar. ID estampado por `ItemDatabaseSO.SyncIds()`, nunca editado aquí. Precio NO vive aquí; se define en `StoreShopData`.

**S128:** Campo `Trigger` (ItemTriggerKind) eliminado (consumo automático no implementado en combate desmontado).

## Campos Públicos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Id` | string (ReadOnly) | ID único "I#", estampado por ItemDatabaseSO.SyncIds() |
| `DisplayName` | string | Nombre visible |
| `Category` | WorldPropCategory | Tipo: Tool, Food, Medicine |
| `Prefab` | GameObject | Prefab 3D spawneado. Debe llevar `WorldPropInstance` |
| `Icon` | Sprite (S161) | Ícono de la hotbar (`PreviewField`). Se renderiza desde el prefab y vive en `Skin/Icons/Items/` |

## Categorías (WorldPropCategory)

- **Tool:** objeto que habilita acciones (broom)
- **Food:** objeto consumible (snack)
- **Medicine:** objeto curativo

## Cambios S161

**Agregado:** campo `Icon` (Sprite) para la hotbar estilo FarmingLife. `HotbarHUDUITK` lo pinta como fondo del slot.

## Cambios S128

**Eliminado:** campo `Trigger` (ItemTriggerKind enum). Consumo automático de items no fue implementado en combate desmontado.

## Historial

**S75:** `Trigger` agregado (anticipado para combate automático).
**S128:** Trigger eliminado (limpieza RPS).

## Vinculado a

[[Index/06 - Player & World]]

**Conexiones:** [[ItemDatabaseSO]], [[WorldPropInstance]], [[PlayerInventorySO]], [[StoreManager]], [[HotbarHUDUITK]]
