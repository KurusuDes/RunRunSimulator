---
tags: [world, props, toy, rigidbody, ai]
---

# Toy.cs

**Ruta:** `World/Props/Toy.cs`

**Responsabilidad:** Juguete físico de los MoriMonchis. Requiere `Rigidbody`. Puede ser una pelota (`ToyKind.Ball`, patada) o un objeto carriable (en la boca de un monchi, o en la mano del jugador). Expone su estado (`Holder`, `TuggedBy`, `LastKicker`, `ThrownByPlayer`, `IsFree`, `IsHeldByPlayer`, `HomeArea`) para `AgentToys` y sus comportamientos. Registro estático `All`. **S151:** juguetes carriables incluyen `Rope` y `Plush` (además de Chew, Hose, Mop); memoria de lanzamiento del jugador; tirón por otro monchi (`TuggedBy`); vuelta a casa si queda fuera de su zona; `TryAttach` admite pelotas cuando el llamador lo permite.

## Metodos Publicos

| Metodo | Descripcion |
|--------|-------------|
| `TryAttach(MoriMochiAgent holder, Transform mouth, bool allowAnyKind = false)` | Pasa a kinematic, se parenta a la boca, colliders en trigger. Acepta carriables libres; con `allowAnyKind` también pelotas (S151, lo usa `ToyPlayerPlay` para traer). Limpia `ThrownByPlayer` |
| `Detach(Vector3 velocity)` | Suelta con velocidad, reactiva física. Limpia `TuggedBy` |
| `Kick(MoriMochiAgent kicker, Vector3 impulse)` | Impulso si es pelota y está libre. Guarda `LastKicker` |
| `SetTugger(MoriMochiAgent)` / `ClearTugger(MoriMochiAgent)` | **(S151)** Un monchi tira del juguete (cuerda). Dispara `onTug` al empezar |

## Golpes

`OnCollisionEnter`: si es pelota, la velocidad relativa >= `hitSpeedThreshold` (2.5) y choca con un `MoriMochiAgent` distinto del ultimo que pateo, llama `agent.ReactToToyHit(this, LastKicker)`.

## Vuelta a casa (S151)

Cada frame, si el juguete está libre, sin holder ni en la mano del jugador, y fuera de su `HomeArea` (`ToyPlayArea.Nearest`) y quieto, cuenta el tiempo. A los `returnHomeAfterSeconds` (25 s) lo teletransporta a un punto aleatorio de la zona y dispara `onReturnHome`.

## Memoria de lanzamiento (S151)

`TrackThrown`: si el jugador soltaba el objeto en su mano, queda `ThrownByPlayer = true` durante `thrownMemorySeconds` (20 s) o hasta que alguien lo agarre. Los monchis lo usan para ir a buscarlo (traer).

## Propiedades

| Propiedad | Descripcion |
|-----------|-------------|
| `Kind` | `ToyKind` (serializado) |
| `IsKickable` | `Kind == Ball` (S151) |
| `IsCarriable` | Chew, Hose, Mop, Rope o Plush (S151: antes solo `Kind != Ball`) |
| `ThrownByPlayer` | Lanzado por el jugador y dentro de la memoria (S151) |
| `TuggedBy` | Monchi que tira de la cuerda, si hay (S151) |
| `Holder` | Monchi que lo lleva (null si no) |
| `LastKicker` | Último monchi que lo pateó |
| `IsHeldByPlayer` | `WorldPropInstance.IsHeld` |
| `IsFree` | Sin holder y no en mano del jugador |
| `HomeArea` | `ToyPlayArea.Nearest(position)` (S151) |

## Eventos MMF

`onCarryStart`, `onCarryEnd`, `onKick`, `onHitCreature`, `onReturnHome` y `onTug` (S151). Visual solo via MMFeedbacks (regla de juice).

## Conexiones

[[AgentToys]], [[AgentToyMotor]], [[ToyFreePlay]], [[ToyBuddyPlay]], [[ToyPlayerPlay]] (usan todo), [[ToyPlayArea]] (zona de juego, S151), [[MoriMochiAgent]] (`ReactToToyHit`), [[MessEmitter]] (deja manchas al moverse, S151), [[HoseSpray]] (requiere un Toy), [[WorldPropInstance]], [[ToyKind]], [[ToyTuningSO]]
