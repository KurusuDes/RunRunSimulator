---
tags: [script, world, brawl, vfx, presentation, hud]
---

# BrawlTelegraphs.cs

**Ruta:** `World/Brawl/BrawlTelegraphs.cs`

**Responsabilidad:** Dibuja plantillas de golpes en tierra (telegrafías) en tiempo real usando `CueDrawer`. Cada frame itera `BrawlFighter.All`, dibuja disco de base del luchador, e hilachas conos/cápsulas/áreas de ataque según lo que esté en casteo. Si hay ala en windup, dibuja plantilla del ala (melé cono, latigazo cápsula, sniper láser, escopeta cono). Si hay habilidad en casteo, dibuja plantilla de skill (dash/shot cápsula, chain área+enlace punteado, cono, nova área, homing área, pull área con anillo punteado, zona área, ward/mend área). Dibuja zonas activas con relleno + borde punteado giratorio. **Línea de mira punteada (verde si es curación)** del lanzador al blanco durante casteo.

**Campos principales:**
- `cueMaterial`, `additiveMaterial` — materiales para CueDrawer
- `tuning` — SO con colores de equipo
- Parámetros de espesor/alpha: `baseRadius`, `fillAlpha`, `edgeAlpha`, `edgeThickness`, `laserThickness`, `targetLineThickness`
- Parámetros de zona: `zoneFillAlpha`, `zoneEdgeAlpha`, `zoneDashCount`, `zoneSpinSpeed`

**Métodos principales:**
- `LateUpdate()` — itera fighters vivos, dibuja base + wing si windingUp + cast si isCasting; itera zonas activas
- `DrawBase(pos, team)` — disco + anillo del color del equipo
- `DrawWing(f, pos, team)` — enruta por `kit.Attack`: Melee cono, Whip cápsula, Sniper láser, Shotgun cono
- `DrawCast(f, pos, team)` — enruta por `s.Family`: Dash/Shot, Chain, Cone, Nova, Homing, Pull, Zone, Ward/Mend
- `DrawTargetLine(from, to, color)` — línea punteada que corre animada hacia el blanco
- `DrawZone(zone)` — discos + anillos punteados giratorios para demora y duración

**Notas:**
- Línea de mira del ala a `wing.AimPoint`, proyectada al suelo del caster
- En Chain, dibuja enlace punteado al blanco más próximo
- La línea de mira es **verde** (`HealLineColor`) si `wing.AimHealing`
- Las zonas sin armar (retardo) muestran dos anillos: uno que se llena, otro que se encoge
- Las zonas armadas tienen borde punteado giratorio a velocidad `zoneSpinSpeed`

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlFighter]], [[BrawlWing]], [[BrawlSkillCaster]], [[BrawlZone]], [[CueDrawer]], [[BrawlTeamLook]]
