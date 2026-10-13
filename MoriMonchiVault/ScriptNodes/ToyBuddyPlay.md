---
tags: [script, world, ai, toys, social, internal]
---

# ToyBuddyPlay.cs

**Ruta:** `World/AI/ToyBuddyPlay.cs`

**Responsabilidad:** Comportamiento de juego entre MoriMonchis. Una criatura elige uno de tres juegos según lo que tenga cerca: tirar de una cuerda que lleva otro monchi (y, si gana, llevarse la cuerda), ir por un peluche libre y abrazarlo, o perseguir y reventar burbujas. Registra interacciones sociales en `SocialGraphService`. Clase `internal` que implementa `IToyBehavior`.

## Modos (`BuddyMode`)

`None`, `GoToRope`, `Tugging`, `CarryAway`, `GoToPlush`, `CarryPlush`, `Hugging`, `Bubbles`.

## Juegos

| Juego | Elegibilidad en `TryEngage` | Resultado |
|-------|----------------------------|-----------|
| Cuerda | Cuerda llevada por otro monchi dentro de `NoticeRadius`, prob. `RopeTugChance` | Tirón durante `RopeTugMin..Max`. Gana por bold (`BoldnessTugBias`). Si gana, lleva la cuerda `CarryDuration`. Ambos reciben `RopeTugAffect`. Registra `PlayChase` |
| Peluche | Peluche libre, prob. 0.5 (`PlushEngageChance`) | Lo lleva al centro de cercanía, abraza `HugDuration`, `HugAffectPerSecond` por segundo, al final registra `SleepTogether` con vecinos a 2.5 m |
| Burbujas | Burbuja no explotada dentro de `NoticeRadius` | Persigue, explota con `PopRange`, `PopAffect`, hasta `PopsMax` pops. Registra `PlayChase` con quienes reclamaron la burbuja |

## Reglas

- `ReactToHit` siempre devuelve `false` (no reacciona a golpes).
- `Intent`: Playing en tirón, carga y abrazo; Playing en burbujas tras el primer pop, Approaching antes.
- `Clear()` suelta el juguete y limpia el tirón (`ClearTugger`).
- Constantes de feel fijas en código (p.ej. `TugEngageFactor` 1.5, `TugBreakFactor` 3, `MinCarryTime` 0.5 s).

## Conexiones

- [[IToyBehavior]] — implementa
- [[AgentToyMotor]] — motor compartido
- [[AgentToys]] — orquestador
- [[ToyTuningSO]] — rangos y afectos
- [[Toy]] — `Kind` (Rope/Plush), `TuggedBy`, `SetTugger`/`ClearTugger`
- [[Bubble]] — `Claim`, `Pop`, `Popped`, `Bubble.All`
- [[SocialGraphService]] — `RecordInteraction` con `SocialInteractionKind`
- [[NeedsState]] — `AddAffect`
