---
tags: [script, enum, core]
---

# BrawlEnums.cs

**Ruta:** `Core/Enums/BrawlEnums.cs`

**Responsabilidad:** Enumeraciones de batalla 3v3 arcade y de la bajada Brawl. Clasifican ataque, movilidad, locomoción, familia de habilidad, rol, target, fase, intención, estado, tipo de VFX, firmas visuales, tipo de sala y estado de la bajada.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Enumeraciones

| Enum | Valores | Descripción |
|------|---------|-------------|
| `BrawlAttackKind` | Melee, Whip, Shotgun, Sniper, Burst, Boomerang | Tipo de ataque básico del ala. Determina patrón de proyectil, spread, velocidad. |
| `BrawlMobilityKind` | Leap, Sprint, Roll, Hop, Blink, Glide | Tipo de movimiento de escape/enganche del ala. |
| `BrawlLocomotion` | Ground, Hover | Locomoción del ala: Ground (navmesh) o Hover (libre en 3D). |
| `BrawlSkillFamily` | Dash, Chain, Cone, Shot, Nova, Homing, Pull, Zone, Ward, Mend | Familia de habilidad (cuerno/espalda). Define geometría y efecto. |
| `BrawlSkillRole` | Offense, Control, Support, Tank | Rol de habilidad para IA (influye decisión de casting) y para el rol sugerido de `BrawlKitProfile`. |
| `BrawlSkillTarget` | Enemy, EnemyCluster, Self, LowestAlly, AlliesAround | Tipo de target para habilidad. Valida selección del lanzador. |
| `BrawlMatchPhase` | Idle, Countdown, Fight, SuddenDeath, Ended | Fase de partida. Controla HUD, VFX, comportamiento y el cronómetro de salas de prueba. |
| `BrawlIntent` | Idle, Engage, Kite, Hunt, Protect, Heal, Retreat, Cast | Intención del cerebro (BrawlBrain). Mostrada en HUD card. |
| `BrawlStatusKind` | Slow, Stun, Haste, Boost, Thorns, Taunt, Shield | Estados activos en criatura (buffs/debuffs). |
| `BrawlFxKind` | Slash, Lightning, Beam, Whip, Burst, Ring, Pulse, Ward, Dash, Pull, Throw, Muzzle, Spawn, KnockOut, Land | Tipo de efecto visual por familia de habilidad. |
| `BrawlSignature` | None, Rainbow, Storm, Cloud, Comet, Lure, Plates | Firma visual especial de partes estrella. Réplicas en VFX, rayos, etc. |
| `BrawlRoomKind` | Combat, Dummies, Minerals | Tipo de sala de la bajada: combate contra rivales o sala de prueba (muñecos / minerales). |
| `BrawlRunState` | Planning, Fighting, RoomResult, Over, Transition | Estado de la bajada (`BrawlRunDirector`). Decide qué vista muestra cada HUD: `BrawlRunPanel` en `Planning` y `Over`; `BrawlRunVeil` en `Transition`; `BrawlRunHud` en `Fighting` y `RoomResult`. |

## Dependencias

**Entrada:**
- Usadas en `BrawlWingKitSO` (Attack, Locomotion, Mobility)
- Usadas en `BrawlSkillSO` (Family, Role, Target, Signature)
- Usadas en `BrawlKitProfile` (BrawlSkillRole) para el rol sugerido
- Usadas en `BrawlMatch` (BrawlMatchPhase) y `BrawlTrialRoom` (BrawlMatchPhase, BrawlRoomKind)
- Usadas en `BrawlFighter`/`BrawlBrain` (BrawlIntent, BrawlLocomotion)
- Usadas en `BrawlRoom`, `BrawlRun`, `BrawlRunDirector`, `BrawlRunPanel`, `BrawlRunHud`, `BrawlRunVeil` y `BrawlRoomGlyphsSO` (BrawlRoomKind, BrawlRunState)

**Salida:**
- Ninguna (puramente definitorio)

## Notas

- Todas las enumeraciones son estáticas (no cambian en runtime).
- Se usan como índices de lookup en dictionaries y switch statements.
- BrawlSignature permite identificación visual (rainbow rayo, tormenta relámpago, etc.).
- BrawlIntent es legible en HUD card para feedback de IA.
- S144: se agregan `BrawlRoomKind` y `BrawlRunState` para la bajada Brawl (run de salas).
- S146: `BrawlRunState` suma `Transition` (velo entre salas). Las vistas de la bajada se reparten entre `BrawlRunPanel`, `BrawlRunHud` y `BrawlRunVeil`.
