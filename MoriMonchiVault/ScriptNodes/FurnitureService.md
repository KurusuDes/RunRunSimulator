---
tags: [script, furniture, service, placement]
---

# FurnitureService.cs

**Ruta:** `Systems/Furniture/FurnitureService.cs`

**Responsabilidad:** CRUD muebles: place, remove, rotate. Modifica `FurnitureRegistrySO`, dispara `GameEvents.OnFurnitureChanged()`. **S138:** Reconstruye ocupancy de grilla en Start() y OnFurnitureReloaded (reload escena olvida muebles).

## Métodos Principales

- `Place()` — Añade a registry
- `Remove()` — Borra de registry
- `Rotate()` — Actualiza rotación
- **S138:** `RebuildGridOccupancy()` — Recarga grilla con todas piezas de registry

## S138: Grid Rebuild

**Start() + OnFurnitureReloaded()**
```csharp
RebuildGridOccupancy();
ScheduleRebake();
```

**RebuildGridOccupancy()** — Clear grid, re-ocupar todas piezas:
```csharp
grid.Clear();
foreach (var piece in registry.GetAll().Values)
{
    var def = database.GetByID(piece.DefId);
    Vector2Int footprint = def != null ? def.Footprint : Vector2Int.one;
    grid.Occupy(new Vector2Int(piece.CellX, piece.CellY), footprint, piece.Rotation);
}
```

**Propósito:** Reload escena (CloudSyncService.OnWorldStateReloaded) restaura registry pero grilla estaba vacía. Ahora se repuebla automáticamente.

## Conexiones

- [[FurnitureRegistrySO]], [[PlacementGrid]], [[GameEvents]], [[FurnitureSpawner]]
