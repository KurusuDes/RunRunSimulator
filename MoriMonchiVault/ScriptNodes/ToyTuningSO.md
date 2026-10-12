---
tags: [data, world, toys, tuning, scriptableobject]
---

# ToyTuningSO.cs

**Ruta:** `Data/World/ToyTuningSO.cs`

**Responsabilidad:** Ajustes de juguetes para los MoriMonchis. Un solo SO con los numeros de todo el ciclo de juego: enganche, pelota, llevar en la boca, robo entre monchis y robo al jugador. Sin logica. Lo lee `AgentToys` a traves de `MoriMochiAgent.toyTuning`.

## Grupos de Campos

| Grupo | Campos clave |
|-------|--------------|
| Enganche | `NoticeRadius` 8, `EngageChancePerSecond` 0.25, `MinEnergy` 30, `Cooldown` 12, `AffectPerSecond` 1.5 |
| Pelota | `KickRange` 0.9, `KickForce` 2.5, `KickUp` 0.6, `KicksMin` 2, `KicksMax` 5 |
| Llevar en la boca | `CarryDurationMin` 5, `CarryDurationMax` 9, `CarrySpeedMultiplier` 1.4, `WanderRadius` 5, `MouthOffset` |
| Robo entre monchis | `StealRange` 0.8, `StealChance` 0.5, `ChaseDuration` 5, `ChaseSpeedMultiplier` 1.5 |
| Robo al jugador | `SnatchRange` 1.3, `SnatchChancePerSecond` 0.08 |

Los valores entre parentesis son los defaults del campo en codigo.

**Conexiones:** [[AgentToys]], [[MoriMochiAgent]] (`toyTuning`), [[Toy]]
