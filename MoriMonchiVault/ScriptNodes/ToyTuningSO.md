---
tags: [data, world, toys, tuning, scriptableobject]
---

# ToyTuningSO.cs

**Ruta:** `Data/World/ToyTuningSO.cs`

**Responsabilidad:** Ajustes de juguetes para los MoriMonchis. Un solo SO con los numeros de todo el ciclo de juego: enganche, pelota, llevar en la boca, robo entre monchis, robo al jugador, traer, tironeo con el jugador, pilla-pilla, cuerda entre monchis, peluche y burbujas. Sin logica. Lo leen `AgentToys` (vía `MoriMochiAgent.toyTuning`), `AgentToyMotor`, `ToyFreePlay`, `ToyBuddyPlay`, `ToyPlayerPlay` y `PlayerToyTug`.

## Grupos de Campos

| Grupo | Campos clave |
|-------|--------------|
| Enganche | `NoticeRadius` 8, `EngageChancePerSecond` 0.25, `MinEnergy` 30, `Cooldown` 12, `AffectPerSecond` 1.5 |
| Pelota | `KickRange` 0.9, `KickForce` 2.5, `KickUp` 0.6, `KicksMin` 2, `KicksMax` 5 |
| Llevar en la boca | `CarryDurationMin` 5, `CarryDurationMax` 9, `CarrySpeedMultiplier` 1.4, `WanderRadius` 5, `MouthOffset` (0, 0.55, 0.45) |
| Robo entre monchis | `StealRange` 0.8, `StealChance` 0.5, `ChaseDuration` 5, `ChaseSpeedMultiplier` 1.5 |
| Robo al jugador | `SnatchRange` 1.3, `SnatchChancePerSecond` 0.08 |
| Traer (S151) | `FetchEngageChancePerSecond` 2, `FetchAffect` 8, `FetchDropRange` 1.4 |
| Tironeo con el jugador (S151) | `TugRange` 1.6, `TugPressPower` 0.12, `TugPullPerSecond` 0.3, `TugBoldnessPull` 0.25, `TugMaxSeconds` 8, `TugWinAffect` 10 |
| Pilla-pilla (S151) | `TeaseDuration` 8, `TeaseKeepAway` 3, `TeaseSpeedMultiplier` 1.5, `CaughtAffect` 6 |
| Cuerda entre monchis (S151) | `RopeTugChance` 0.7, `RopeTugMin` 2, `RopeTugMax` 5, `RopeTugAffect` 4 |
| Peluche (S151) | `HugChancePerSecond` 0.5 (sin uso), `HugDurationMin` 6, `HugDurationMax` 10, `HugAffectPerSecond` 3 |
| Burbujas (S151) | `PopRange` 0.9, `PopsMax` 4, `PopAffect` 2 |

Los valores entre parentesis son los defaults del campo en codigo.

## Notas

- `HugChancePerSecond` está declarado pero no lo lee ningún script. La elección de peluche usa una probabilidad fija de 0.5 en `ToyBuddyPlay` (`PlushEngageChance`).
- `MinEnergy` lo consume `AgentToys` como umbral de energía para jugar. Los sociales usan `SocialTuningSO.MinEnergyToPlay`, un campo distinto.

## Conexiones

[[AgentToys]], [[AgentToyMotor]], [[ToyFreePlay]], [[ToyBuddyPlay]], [[ToyPlayerPlay]], [[PlayerToyTug]], [[MoriMochiAgent]] (`toyTuning`), [[Toy]]
