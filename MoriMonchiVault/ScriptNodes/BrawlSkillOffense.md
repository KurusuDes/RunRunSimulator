---
tags: [script, world, brawl, skills, damage]
---

# BrawlSkillOffense.cs

**Ruta:** `World/Brawl/BrawlSkillOffense.cs`

**Responsabilidad:** Ejecutores estáticos de habilidades ofensivas (6 familias). Damage, knockback, control (slow/stun). Dash paso a paso, Chain salta con falloff, Cone barrido, Shot proyectil, Nova radial, Homing perseguidor.

## Ejecutores Públicos

| Ejecutor | Entrada | Salida |
|----------|---------|--------|
| `Dash(cast)` | BrawlCast | Motor.Dash + daño paso a paso |
| `Chain(cast)` | BrawlCast | Rayo BrawlFx + saltos damage |
| `Cone(cast)` | BrawlCast | Barrido cono, damage + control |
| `Shot(cast)` | BrawlCast | Proyectil único rebota/atraviesa |
| `Nova(cast)` | BrawlCast | Púas radiales |
| `Homing(cast)` | BrawlCast | Proyectiles fan con tracking |

## Familias de Damage

- **Dash:** Embestida en línea; daño a cada foe en ruta (Ariete, Carnero, etc.)
- **Chain:** Rayo que salta entre rivales; falloff 0,8× por salto
- **Cone:** Barrido frontal (360° giro posible); aturde + slow si aplica
- **Shot:** Proyectil fuerte; rebota/atraviesa/estalla según SO
- **Nova:** Púas en todas direcciones; anillo de impacto visual
- **Homing:** Ráfaga que persigue blanco; usado por Cometitas

## Búsquedas

Usa [[BrawlQuery]] para:
- `FoesWithin(position, radius, team, buffer)` — enemigos en radio
- `InCone(origin, dir, range, halfAngle, target)` — dentro de cono
- `OnSegment(start, end, radius, target)` — sobre segmento (latigazo)

## Control Aplicado

- `Slow` (fracción de vel., segundos)
- `Stun` (segundos absolutos)
- Aplicado por `BrawlSkillEffects.Control()`

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Entrada:**
- [[BrawlSkillEffects]] → `Execute(cast)` → routing

**Salida:**
- [[BrawlFighter]] → `TakeDamage()`, `ApplySlow()`, `ApplyStun()`
- [[BrawlMotor]] → `Motor.Dash()` para Dash
- [[BrawlFx]] → `Emit()` eventos visuales
- [[BrawlProjectile]] → `Fire()` proyectiles
- [[BrawlQuery]] — búsquedas de targets

## Notas

- DashFallbackSeconds 0,35 s si skill.Duration no definido
- ChainFalloff 0,8 (80% daño remanente por salto)
- NovaProjectileRadius 0,4 m; NovaRingRadius 1,5 m
- HomingFanStep 25° (distribución abanico)
- ShotSpin 360° por segundo
