---
tags: [world, ai, agent, toys, composition]
---

# AgentToys.cs

**Ruta:** `World/AI/AgentToys.cs`

**Responsabilidad:** Colaborador de `MoriMochiAgent` (patron de composicion, no MonoBehaviour) que decide y ejecuta el juego con juguetes. Maquina de modos: GoToBall, Kicking, GoToCarry, Carrying, Chasing, Snatching. Tambien gestiona el robo entre monchis, el robo al jugador y el cooldown.

## Prioridad de `TryEngage` (una vez por frame, probabilidad por segundo)

1. Robar un juguete ya cargado por otro monchi en `NoticeRadius` (Chasing).
2. Juguete libre en rango: pelota = GoToBall (patear), carriable = GoToCarry (llevar en la boca).
3. Juguete que el jugador sostiene en la mano a rango de `NoticeRadius` = Snatching.

Requisitos de entrada: estado Idle o Roaming, cooldown vencido, no criar ni ser huevo, sin equipo de expedicion, `Needs.Energy` >= `MinEnergy`.

## Comportamiento

- Patear: 2 a 5 patadas con ruido angular de 25 grados (`Toy.Kick`).
- Llevar: duracion aleatoria, velocidad x`CarrySpeedMultiplier`, punto de paseo dentro de `WanderRadius`.
- Perder el juguete ante un ladron: emote Molesto y persecucion.
- Afecto: suma `AffectPerSecond` mientras juega.
- Al terminar (`End`) suelta el juguete, aplica cooldown y pide roam.

## Metodos Internos Relevantes

| Metodo | Quien lo llama | Descripcion |
|--------|----------------|-------------|
| `TryEngage()` | `MoriMochiAgent` (tick) | Evalua y entra en modo |
| `TickPlaying()` | `MoriMochiAgent` (tick, estado Playing) | Avanza el modo activo |
| `ReactToHit(Toy, MoriMochiAgent)` | `MoriMochiAgent.ReactToToyHit` | Reaccion a un golpe de juguete: molesto y persecucion al que pateo |
| `TickAlways()` | `MoriMochiAgent` (cada frame) | Si salio de Playing, suelta el juguete y limpia |
| `DropToy()` | Varios | Suelta el juguete si lo lleva |
| `ResetForReuse()` | Pool de agentes | Limpia todo el estado |
| `Intent` | `MoriMochiAgent` | Mapea modo a `CreatureIntent` (Playing, Wandering, Approaching) |

## Dependencias de Estado

Lee `AgentContext` (`Dna`, `CurrentContainer`, `IsBreeding`, `State`, `Body`, `Agent`, `Player`). Escribe `State = Playing` y `SpeedMultiplier`/`SpeedBoostUntil`.

**Conexiones:** [[MoriMochiAgent]], [[AgentContext]], [[Toy]], [[ToyTuningSO]], [[HotbarController]] (`ActiveHeldObject`, `DropActive`), [[NeedsState]], [[ExpeditionTeam]], [[EmoteKind]]
