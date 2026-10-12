---
tags: [world, store, navmesh, rebake, events]
---

# NavMeshRebaker.cs

**Ruta:** `World/Store/NavMeshRebaker.cs`

**Responsabilidad:** Rehornea los `NavMeshSurface` de la tienda cuando cambia la geometria (expansiones abiertas). Es el unico que emite `NavMeshWillRebake` y `NavMeshRebaked`. Usa debounce de 0.4 s y una bandera `pending` para no solapar horneados: si llega otra peticion mientras hornea, la reagenda al terminar.

## Disparadores

| Evento / Momento | Accion |
|------------------|--------|
| `Start` | `ScheduleRebake()` |
| `GameEvents.OnWorldStateReloaded` | `ScheduleRebake()` |
| `GameEvents.OnShopZoneOpened` | `ScheduleRebake()` |
| Boton Odin `Rebake NavMesh` | `ScheduleRebake()` |

## Flujo

1. `ScheduleRebake`: si esta corriendo, marca `pending`. Si no, arranca la corrutina con debounce.
2. `RebakeRoutine`: emite `NavMeshWillRebake`, usa `UpdateNavMesh` si hay `navMeshData` o `BuildNavMesh` si no, espera las operaciones y emite `NavMeshRebaked`.
3. Al terminar, si `pending`, reagenda.

`OnDisable` detiene corrutinas y limpia banderas.

**Conexiones:** [[GameEvents]] (`OnWorldStateReloaded`, `OnShopZoneOpened`, `NavMeshWillRebake`, `NavMeshRebaked`), [[ShopZone]], [[WorldStateSO]], `NavMeshSurface` (Unity AI Navigation)
