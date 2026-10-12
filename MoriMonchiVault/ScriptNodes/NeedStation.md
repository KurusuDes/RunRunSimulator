---
tags: [script, world, needs, station]
---

# NeedStation.cs

**Ruta:** `World/Needs/NeedStation.cs`

**Responsabilidad:** Estación abstracta de restauración de necesidades. Tiene varios puntos de uso (slots) y un ritmo de llenado. Se auto-registra en `NeedStationRegistry` al activarse. Las subclases fijan el tipo de necesidad (`Need`: Health para Feeder, Energy para RestZone, Affect para PlayZone). **S149:** la estación consume reservas de `StationSupply` del mismo GameObject: sin reserva no hay disponibilidad ni restauración.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `usePoints` | `List<Transform>` | vacío | Puntos donde se para el monchi (un slot por punto). Vacío = un slot en el transform |
| `fillPerSecond` | float (Min 0) | 25 | Puntos de necesidad restaurados por segundo de uso |

## Propiedades

| Propiedad | Descripción |
|-----------|-------------|
| `Need` (abstract) | `NeedType` que cubre la estación |
| `UsePosition` | Posición del primer punto de uso no nulo |
| `IsAvailable` | False si la reserva está vacía (`StationSupply.IsEmpty`) o si todos los slots están ocupados |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `TryReserve(agent, from, areaMask, sampleRadius, out usePos)` | `bool` | Reserva el slot libre y alcanzable más cercano. Re-entrante: si el agente ya tiene slot, lo reusa |
| `Release(agent)` | `void` | Libera el slot del agente |
| `Refill(NeedsState needs, float dt)` | `bool` | Consume `fillPerSecond * dt` de la reserva y restaura la necesidad al factor de la reserva. Devuelve true si la reserva está vacía o la necesidad llegó a 100 |

## Llenado con reserva (S149)

`Refill` pide `amount = fillPerSecond * dt` a `StationSupply.Consume(amount)`. Ese valor devuelve un factor (0 a 1) que escala lo restaurado:
- Comida y agua: factor 1 si hay reserva, 0 si no.
- Limpieza (Clean): factor 1 con reserva suficiente, 0.5 bajo `dirtyThreshold`.

Si el factor es 0, la estación termina el uso.

## Invariantes

- Capacidad = cantidad de puntos de uso (slots). Cada agente reserva el slot libre y alcanzable más cercano y lo conserva hasta terminar o ser interrumpido.
- Sin puntos de uso, existe un slot implícito en el transform.
- `TryReserve` es re-entrante.

## Vinculado a

- [[Index/06 - Player & World]]

## Conexiones

- [[NeedStationRegistry]] (registro estático)
- [[StationSupply]] (reserva consumible, S149)
- [[Feeder]], [[PlayZone]], [[RestZone]] (subclases)
- [[MoriMochiAgent]], [[AgentBrain]] (`TryReserve`, `Refill`, `Release`)
- [[NeedsState]] (`Restore`, `Get`)
