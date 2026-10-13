---
tags: [world, ai, agent, toys, composition]
---

# AgentToys.cs

**Ruta:** `World/AI/AgentToys.cs`

**Responsabilidad:** Colaborador de `MoriMochiAgent` (patron de composicion, no MonoBehaviour) que decide y ejecuta el juego con juguetes. **S151:** ya no tiene la máquina de modos monolítica: orquesta tres comportamientos (`IToyBehavior`) — `ToyPlayerPlay`, `ToyBuddyPlay` y `ToyFreePlay` — que comparten un `AgentToyMotor`. Elige cuál entra según lo que haya cerca y la prioridad fija. Gestiona la energía mínima, el cooldown, el afecto por juego y la reacción a golpes de juguete.

## Entrada (`TryEngage`, una vez por frame, prob. por segundo)

Requisitos: `toyTuning` presente; estado Idle o Roaming, o Reacting si hay una invitación del jugador (juguete lanzado o juguete en la mano del jugador a `NoticeRadius`); cooldown listo (salvo invitación del jugador); `AgentToyMotor.CanPlay()` (sin contenedor, no cría, no huevo, sin equipo de expedición); `Needs.Energy >= MinEnergy`.

- **Invitado** (juguete lanzado por el jugador, o cuerda llevada por otro monchi): probabilidad `FetchEngageChancePerSecond`. Si no, `EngageChancePerSecond`.
- Luego prueba **primero** `ToyPlayerPlay` (índice 0) y después los otros dos (`ToyBuddyPlay`, `ToyFreePlay`) en orden aleatorio.
- El primero que acepte queda como `active`.

## Ejecución

- `TickPlaying()` (estado Playing): suma `AffectPerSecond * dt` de afecto, refresca el boost del motor y ticka el comportamiento activo. Si el comportamiento termina, `active = null`.
- `TickAlways()`: si hay comportamiento activo y el estado ya no es Playing, lo limpia, quita el boost y arranca el cooldown.
- `ReactToHit(Toy, kicker)`: emote Molesto. Si hay comportamiento activo, se lo pasa. Si no, prueba cada comportamiento en orden hasta que uno acepte (hoy solo `ToyFreePlay` reacciona: persigue al que pateó).
- `Intent`: el del comportamiento activo; `Wandering` si no hay.
- `ResetForReuse()`: limpia el comportamiento activo y el motor.
- `Abort()`: si el comportamiento deja de estar activo, lo limpia y termina el motor con `completed = false`.

## Campos y dependencias

- Crea `AgentToyMotor` y los tres `IToyBehavior` en el constructor.
- Lee `AgentContext` (`Dna`, `State`) y `ToyTuningSO` (`MinEnergy`, `NoticeRadius`, `EngageChancePerSecond`, `FetchEngageChancePerSecond`, `AffectPerSecond`).
- Escribe `State` solo a través de los comportamientos (`motor.Enter()` pone `Playing`).

## Metodos Internos Relevantes

| Metodo | Quien lo llama | Descripcion |
|--------|----------------|-------------|
| `TryEngage()` | `MoriMochiAgent` (tick) | Evalua invitaciones y entra en comportamiento |
| `TickPlaying()` | `MoriMochiAgent` (tick, estado Playing) | Avanza el comportamiento activo |
| `TickAlways()` | `MoriMochiAgent` (cada frame) | Si salió de Playing, limpia y arranca cooldown |
| `ReactToHit(Toy, MoriMochiAgent)` | `MoriMochiAgent.ReactToToyHit` | Emote molesto y reacción de comportamientos |
| `ResetForReuse()` | Pool de agentes | Limpia todo el estado |
| `Intent` | `MoriMochiAgent` | Intención del comportamiento activo |

## Cambios S151

- Reemplaza la máquina de modos (GoToBall, Kicking, GoToCarry, Carrying, Chasing, Snatching) por tres comportamientos (`IToyBehavior`), cada uno con sus propios modos.
- Prioridad fija: `ToyPlayerPlay` primero; luego los otros dos en orden aleatorio.
- Invitación del jugador: permite entrar en `Reacting` y salta el cooldown.
- Energía mínima en la entrada (`Needs.Energy >= MinEnergy`).

## Conexiones

[[MoriMochiAgent]], [[AgentContext]], [[AgentToyMotor]], [[IToyBehavior]], [[ToyPlayerPlay]], [[ToyBuddyPlay]], [[ToyFreePlay]], [[Toy]], [[ToyTuningSO]], [[NeedsState]], [[ExpeditionTeam]], [[EmoteKind]], [[CreatureIntent]]
