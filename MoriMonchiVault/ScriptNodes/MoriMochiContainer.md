---
tags: [script, world, container, anchor]
---

# MoriMochiContainer.cs

**Ruta:** `World/Containers/MoriMochiContainer.cs`

**Responsabilidad:** Corral base con BoxCollider trigger. Admite criaturas en vuelo (lanzadas al interior) hasta `Capacity`. Si el corral no acepta a la criatura o está lleno, la rebota hacia afuera. Lleva el censo de ocupantes y marca la ubicación (`LocationKey` / `LocationSlot`) en el DNA. **S138:** `protected virtual int Capacity` permite subclases overridear (StoreContainer suma upgrade bonus). `TryReclaim` valida `Accepts(agent)` antes de confinar.

## Campos Principales

| Campo | Tipo | Propósito |
|-------|------|----------|
| `area` | BoxCollider | Trigger del corral (interior). Se toma del propio objeto si está vacío |
| `anchorKey` | string | Clave del lugar (`name` por defecto). Se registra en `AnchorRegistry` |
| `capacity` | int (Min 1, default 2) | Máximo de ocupantes base |
| `bounceOut` | float (default 5) | Impulso horizontal de rebote cuando no entra |
| `bounceUp` | float (default 4) | Impulso vertical del rebote |

## Propiedades

| Propiedad | Retorna | Descripción |
|-----------|---------|-------------|
| `Center` | Vector3 | Centro del trigger |
| `InteriorBounds` | Bounds | Bounds del trigger |
| `Capacity` | int (virtual) | **(S138)** Retorna `capacity`. StoreContainer lo suma con el bonus de mejora |
| `IsFull` | bool | `occupants.Count >= Capacity` |
| `Occupants` | `IReadOnlyList<MoriMochiAgent>` | Censo |
| `AnchorKey` | string | Clave del lugar |
| `OccupantInfos` | `List<OccupantInfo>` | Vista para la tabla de Odin (nombre, género, rol) |

## Admisión (solo en vuelo)

`OnTriggerEnter` / `OnTriggerStay` solo consideran agentes con `IsAirborne` (lanzados).

- Si `Accepts(agent)` es false → `BounceOut`.
- Si está lleno → `BounceOut`.
- Si no → `Admit`: reclama al agente, marca `LocationKey = anchorKey` y `LocationSlot = -1`, y dispara `RegistryChanged`.
- Si `Claim` falla (por ejemplo el piso no tiene área de cría horneada) → warning y no entra.

## Métodos

| Método | Descripción |
|--------|-------------|
| `AnchorPosition(int slot)` | Centro (virtual, duck typing) |
| `TryReclaim(agent, slot)` | `Accepts(agent) && Claim(agent)` |
| `Accepts(agent)` (virtual) | Por defecto true. Subclases lo filtran |
| `Claim(agent)` (protected) | `agent.EnterConfinement(this)` y lo agrega al censo |
| `Release(agent)` (virtual) | Saca del censo y limpia `LocationKey` / `LocationSlot` del DNA si coinciden |
| `DetachOccupant(agent)` | Quita del censo sin tocar DNA |
| `SetAnchorKey(key)` | Asigna y registra la clave |

## Subclases

- **BreedingContainer:** `Accepts` solo Adult. Ver [[BreedingContainer]].
- **IncubatorContainer:** `Accepts` solo Egg.
- **StoreContainer:** `Accepts` Form != Egg. `Capacity` suma `upgrade.CurrentBonus`.

## Cambios S149

- Sin cambios de contrato. La validación de admisión (`Accepts` antes de `IsFull`) queda explícita en `OnTriggerEnter`.

## Cambios S138

- `Capacity` pasa a `protected virtual`.
- `TryReclaim` comprueba `Accepts` primero.

## Conexiones

- [[AnchorRegistry]]
- [[BreedingContainer]], [[IncubatorContainer]], [[StoreContainer]]
- [[MoriMochiAgent]] (`IsAirborne`, `EnterConfinement`, `Knock`)
- [[CreatureDNA]] (`LocationKey`, `LocationSlot`)
- [[GameEvents]] (`RegistryChanged`)
