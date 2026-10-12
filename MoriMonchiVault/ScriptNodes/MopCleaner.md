---
tags: [world, props, mop, cleaning, hotbar]
---

# MopCleaner.cs

**Ruta:** `World/Props/MopCleaner.cs`

**Responsabilidad:** Limpia charcos con la fregona. Se suscribe al evento estatico `HotbarController.OnItemUsed`. Si el item usado es la fregona (`mopItem.Id`), limpia todos los `Puddle` dentro de `radius` desde un punto `forwardOffset` delante del jugador.

## Parametros

| Campo | Default | Descripcion |
|-------|---------|-------------|
| `player` | Transform (requerido) | Ancla del area de limpieza |
| `mopItem` | `ItemDefinitionSO` (requerido) | Item que dispara la limpieza |
| `radius` | 1.6 | Radio planar |
| `forwardOffset` | 1 | Desplazamiento adelante del jugador |

## Flujo

Filtra por distancia planar al centro, guarda en un buffer reutilizable y llama `Clean()` a cada charco. Registra la cantidad en `Debug.Log`.

**Conexiones:** [[HotbarController]] (`OnItemUsed`, evento estatico), [[Puddle]], [[ItemDefinitionSO]], [[PlayerController]] (ancla del jugador)
