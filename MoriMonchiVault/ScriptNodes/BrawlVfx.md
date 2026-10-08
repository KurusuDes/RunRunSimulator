---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlVfx.cs

**Ruta:** `World/Brawl/BrawlVfx.cs`

**Responsabilidad:** Orquestador central de VFX en arena. Enruta eventos de `BrawlFx.Emitted` a sub-sistemas especializados (iconos, líneas, destellos, impactos, lluvia, etc.). Maneja destellos de golpe en tierra con `CueDrawer` (templates de habilidades con relleno progresivo), anima piscinas de prefabs `HitFx`, `DustFx`, `KnockOutFx`. Escucha eventos de daño, curación, KO, inicio de casteo y movilidad para disparar VFX temáticos. Pure presentation: lee `BrawlTheme` y `BrawlTeamLook` para aplicar color de equipo (aliados saturados+grandes, rivales lavados en rojo).

**Campos principales:**
- `icons`, `lines`, `wards`, `swoosh`, `trails`, `impacts`, `rain`, `bubbles`, `vortex` — sub-sistemas de VFX especializados
- `cueMaterial`, `additiveMaterial` — materiales para `CueDrawer`
- Parámetros de timing: `slashSeconds`, `ringSeconds`, `pulseSeconds`, `pullSeconds`, `muzzleSeconds`
- Pool de prefabs (HitFx, DustFx, KnockOutFx) con límite `maxInstancesPerPrefab`

**Métodos principales:**
- `OnFx(BrawlFxEvent)` — enruta por `e.Kind`: Slash, Lightning, Beam, Whip, Burst, Ring, Pulse, Ward, Dash, Pull, Throw, Muzzle, Spawn, KnockOut, Land
- `OnDamaged(victim, hit)` — explosión de íconos proporcional a daño
- `OnHealed(target, amount, source)` — ráfaga verde creciente
- `OnKnockedOut(victim, killer)` — trifle de iconos + triple estela
- `OnCastStarted(caster, skill, aim)` — convergencia de íconos en caster durante windup
- `LateUpdate()` — anima flashes (sectores de barrido, anillos, discos pulsantes) con fade suave

**Notas:**
- El pool de prefabs rota si alcanza `maxInstancesPerPrefab` (evita instancia infinita)
- `CueDrawer.Configure()` inicializa materiales una sola vez
- Los aliados disparan +50% íconos por `AllyIconCountBoost` (lectura de equipo)
- Ground snap: muestrea NavMesh para colocar VFX al nivel del terreno
- Triple Burst en KnockOut: ala, cuerno, espalda del muerto

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlIconParticles]], [[BrawlLineFx]], [[BrawlWardFx]], [[BrawlSwooshFx]], [[BrawlTrailFx]], [[BrawlImpactFx]], [[BrawlRainFx]], [[BrawlBubbleFx]], [[BrawlVortexFx]], [[BrawlTeamLook]], [[BrawlFx]], [[BrawlFighter]], [[BrawlSkillCaster]], [[BrawlWing]], [[CueDrawer]]
