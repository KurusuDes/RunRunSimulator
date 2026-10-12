---
tags: [world, props, toy, rigidbody, ai]
---

# Toy.cs

**Ruta:** `World/Props/Toy.cs`

**Responsabilidad:** Juguete fisico de los MoriMonchis. Requiere `Rigidbody`. Puede ser una pelota (`ToyKind.Ball`, patada) o un objeto carriable (en la boca de un monchi). Expone su estado (`Holder`, `LastKicker`, `IsFree`, `IsHeldByPlayer`) para `AgentToys`. Registro estatico `All`.

## Metodos Publicos

| Metodo | Descripcion |
|--------|-------------|
| `TryAttach(MoriMochiAgent holder, Transform mouth)` | Pasa a kinematic, se parenta a la boca, colliders en trigger. Solo carriables y libres |
| `Detach(Vector3 velocity)` | Suelta con velocidad, reactiva fisica |
| `Kick(MoriMochiAgent kicker, Vector3 impulse)` | Impulso si esta libre. Guarda `LastKicker` |

## Golpes

`OnCollisionEnter`: si la velocidad relativa >= `hitSpeedThreshold` (2.5) y choca con un `MoriMochiAgent` distinto del ultimo que pateo, llama `agent.ReactToToyHit(this, LastKicker)`.

## Propiedades

| Propiedad | Descripcion |
|-----------|-------------|
| `Kind` | `ToyKind` (serializado) |
| `IsCarriable` | `Kind != Ball` |
| `Holder` | Monchi que lo lleva (null si no) |
| `IsHeldByPlayer` | `WorldPropInstance.IsHeld` |
| `IsFree` | Sin holder y no en mano del jugador |

## Eventos MMF

`onCarryStart`, `onCarryEnd`, `onKick`, `onHitCreature` (visual solo via MMFeedbacks, regla de juice).

**Conexiones:** [[AgentToys]] (usa todo), [[MoriMochiAgent]] (`ReactToToyHit`), [[HoseSpray]] (requiere un Toy), [[WorldPropInstance]], [[ToyKind]], [[ToyTuningSO]]
