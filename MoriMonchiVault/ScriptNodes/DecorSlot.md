---
tags: [world, breeding, decor, interactable, slot]
---

# DecorSlot.cs

**Ruta:** `World/Breeding/DecorSlot.cs`

**Responsabilidad:** Ranura física de decoración en un `BreedingContainer`. Implementa `IInteractable` e `IFocusLabel` (S161). Cada interacción devuelve la decoración actual al inventario y toma la siguiente disponible del catálogo (orden de `BreedingDecorDatabaseSO`). Persiste el contenido en `WorldStateSO` y muestra el visual o un cubo tintado de fallback.

## Identidad

`SlotId = {owner.name}_{index}`. Es la clave de persistencia en `WorldStateSO.GetDecorSlot/SetDecorSlot`.

## Interacción (`Interact`, solo Play)

1. Si hay decoración, la devuelve al inventario (`AddDecor`) y arranca el ciclo desde la siguiente del catálogo.
2. Toma la primera decoración del catálogo con stock (`TryTakeDecor`).
3. Si no había nada y no hay nada que tomar, no hace nada.
4. Guarda en `WorldStateSO` y dispara `InventoryChanged` + `WorldStateChanged`. No persiste directamente.

## Visual (`Refresh`)

Destruye los hijos de `anchor` (o del propio transform) y spawnea `Prefab` de la decoración o un cubo sin collider tintado con `_BaseColor`. Sin decoración no spawnea nada.

## Rótulo de Foco (S161)

Ya no hay etiqueta TMP flotante (se quitó el campo `label` y las etiquetas de decoraciones en prefabs y escena). El rótulo sale por `IFocusLabel`:

| Miembro | Valor |
|---------|-------|
| `FocusTitle` | `ui.decor.slot.empty` si no hay decoración; el nombre si `IsDiscovered(BredTotal)`; si no, `ui.store.decor.unknown` |
| `FocusDetail` | `null` |

Lo consume [[PlayerFocusProbe]] y lo pinta [[FocusPromptUITK]].

## Suscripciones

| Evento | Acción |
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

**Conexiones:** [[BreedingContainer]], [[BreedingController]] (`DecorDatabase`), [[BreedingDecorSO]], [[BreedingDecorDatabaseSO]], [[PlayerInventorySO]], [[WorldStateSO]], [[GameEvents]], [[IInteractable]], [[IFocusLabel]] (S161), [[Loc]]
