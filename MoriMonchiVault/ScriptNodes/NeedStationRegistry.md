---
tags: [script, world, needs, registry, static]
---

# NeedStationRegistry.cs

**Ruta:** `World/Needs/NeedStationRegistry.cs`

**Responsabilidad:** Índice estático en runtime de las estaciones de necesidad. Lo llenan `NeedStation` al activarse y lo vacían al desactivarse. Lo consulta `AgentBrain` para buscar la estación más cercana de un tipo de necesidad.

## Métodos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Register(NeedStation s)` | `void` | Agrega si no está |
| `Unregister(NeedStation s)` | `void` | Quita |
| `AnyOfType(NeedType type)` | `bool` | ¿Hay alguna estación de ese tipo? (sin mirar disponibilidad) |
| `GetClosest(Vector3 from, NeedType type, bool onlyAvailable = true)` | `NeedStation` | Estación más cercana del tipo, por posición de uso. Con `onlyAvailable` descarta las llenas o vacías |

**Nota:** es una clase `static`, no tiene singleton `Instance`.

## Vinculado a

- [[Index/06 - Player & World]]

## Conexiones

[[NeedStation]], [[AgentBrain]], [[MoriMochiAgent]], [[Feeder]], [[PlayZone]], [[RestZone]]
