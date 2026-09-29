---
tags: [script, world, container, anchor]
---

# MoriMochiContainer.cs

**Ruta:** `World/Containers/MoriMochiContainer.cs`

**Responsabilidad:** Corral base con BoxCollider trigger. Acepta criaturas hasta capacity. **S138:** `protected virtual int Capacity` permite subclases overridear (StoreContainer suma upgrade bonus). TryReclaim ahora valida `Accepts(agent)` antes de confinar.

## Campos Principales

| Campo | Tipo | Propósito |
|-------|------|----------|
| `area` | BoxCollider | Trigger del corral |
| `anchorKey` | string | Clave lugar ("x_y" o nombre) |
| `capacity` | int | Máximo ocupantes (base) |
| `occupants` | List<MoriMochiAgent> | Censo |

## Propiedades S138

| Propiedad | Retorna | Descripción |
|-----------|---------|-------------|
| `Capacity` | int (virtual) | **(S138)** `protected virtual`, retorna `capacity`. StoreContainer overridea: `base.Capacity + upgrade.CurrentBonus` |
| `IsFull` | bool | `occupants.Count >= Capacity` |
| `AnchorKey` | string | Clave del lugar |
| `AnchorPosition(slot)` | Vector3 | Centro (duck-typing) |
| `TryReclaim(agent, slot)` | bool | **(S138)** `Accepts(agent) && Claim(agent)` — valida Form primero |

## Métodos S138

```csharp
protected virtual int Capacity => capacity;

public virtual bool TryReclaim(MoriMochiAgent agent, int slot) 
    => Accepts(agent) && Claim(agent);
```

**Cambio:** TryReclaim ahora comprueba `Accepts()` (Form filter) antes de reclamar.

## Subclases

- **BreedingContainer:** Accepts solo Adult
- **IncubatorContainer:** Accepts solo Egg
- **StoreContainer:** Accepts Form != Egg; Capacity += upgrade.CurrentBonus

## Conexiones

- [[AnchorRegistry]], [[BreedingContainer]], [[IncubatorContainer]], [[StoreContainer]], [[FurnitureSpawner]]
