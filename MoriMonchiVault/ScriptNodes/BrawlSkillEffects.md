---
tags: [script, world, brawl, skills, router]
---

# BrawlSkillEffects.cs

**Ruta:** `World/Brawl/BrawlSkillEffects.cs`

**Responsabilidad:** Router singleton de ejecución de habilidades. Despacha `BrawlCast` a ejecutores estáticos (BrawlSkillOffense/Support) según familia. Helpers para construir hits, aplicar control, crear proyectiles y eventos VFX.

## Métodos Estáticos

| Método | Descripción |
|--------|-------------|
| `Execute(cast)` | Router: switch en `cast.Skill.Family` → llama ejecutor |
| `Hit(cast, victim, amount, knockDir, knockback)` | Construye `BrawlHit` con source + theme |
| `Control(skill, victim)` | Aplica slow/stun según skill |
| `NewShot(cast)` | Factory `BrawlShot` con owner, team, origin, dirección |
| `NewFx(kind, cast)` | Factory `BrawlFxEvent` con theme + team + source |
| `PlanarDir(from, to)` | Normaliza dirección XZ (ignorando Y) |

## Familias y Ejecutores

| Familia | Ejecutor | Tipo |
|---------|----------|------|
| Dash | `BrawlSkillOffense.Dash` | Embestida con damage paso a paso |
| Chain | `BrawlSkillOffense.Chain` | Rayo que salta; falloff daño |
| Cone | `BrawlSkillOffense.Cone` | Barrido cono |
| Shot | `BrawlSkillOffense.Shot` | Proyectil rebota/atraviesa/estalla |
| Nova | `BrawlSkillOffense.Nova` | Púas en todas direcciones |
| Homing | `BrawlSkillOffense.Homing` | Proyectiles que persiguen |
| Pull | `BrawlSkillSupport.Pull` | Atrae + taunt |
| Zone | `BrawlSkillSupport.Zone` | Área con demora/duración |
| Ward | `BrawlSkillSupport.Ward` | Escudo propio + aliado |
| Mend | `BrawlSkillSupport.Mend` | Curación dirección/área |

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Entrada:**
- [[BrawlSkillCaster]] → `Fire()` → `Execute(cast)`

**Salida:**
- [[BrawlSkillOffense]] — ejecución daño
- [[BrawlSkillSupport]] — ejecución apoyo
- [[BrawlFx]] — eventos visuales
- [[BrawlProjectile]] — disparo de proyectiles
- [[BrawlZone]] — spawn zonas

## Notas

- Router puro; sin lógica de física
- Hit construido con Source = Caster y FromSkill = true
- Helpers reduce duplicación entre Offense/Support
