---
tags: [world, breeding, decor, interactable, slot]
---

# DecorSlot.cs

**Ruta:** `World/Breeding/DecorSlot.cs`

**Responsabilidad:** Ranura fisica de decoracion en un `BreedingContainer`. Implementa `IInteractable`. Cada interaccion devuelve la decoracion actual al inventario y toma la siguiente disponible del catalogo (orden de `BreedingDecorDatabaseSO`). Persiste el contenido en `WorldStateSO` y muestra el visual o un cubo tintado de fallback.

## Identidad

`SlotId = {owner.name}_{index}`. Es la clave de persistencia en `WorldStateSO.GetDecorSlot/SetDecorSlot`.

## Interaccion (`Interact`, solo Play)

1. Si hay decoracion, la devuelve al inventario (`AddDecor`) y arranca el ciclo desde la siguiente del catalogo.
2. Toma la primera decoracion del catalogo con stock (`TryTakeDecor`).
3. Si no habia nada y no hay nada que tomar, no hace nada.
4. Guarda en `WorldStateSO` y dispara `InventoryChanged` + `WorldStateChanged`. No persiste directamente.

## Visual (`Refresh`)

Destruye los hijos de `anchor` y spawnea `Prefab` o un cubo sin collider tintado con `_BaseColor`. La etiqueta muestra el nombre si `IsDiscovered(BredTotal)`, o `ui.store.decor.unknown`. Sin decoracion, `ui.decor.slot.empty`.

## Suscripciones

| Evento | Accion |
|--------|--------|
| `OnWorldStateChanged`, `OnWorldStateReloaded` | `Refresh()` |
| `LocalizationSettings.SelectedLocaleChanged` | `Refresh()` |

Se desuscribe en `OnDisable`.

## Referencias Serializadas

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `owner` | `BreedingContainer` | Si |
| `index` | `int` | No (Min 0) |
| `anchor` | `Transform` | No |
| `label` | `TextMeshPro` | No |

**Conexiones:** [[BreedingContainer]], [[BreedingController]] (`DecorDatabase`), [[BreedingDecorSO]], [[BreedingDecorDatabaseSO]], [[PlayerInventorySO]], [[WorldStateSO]], [[GameEvents]], [[IInteractable]], [[Loc]]
