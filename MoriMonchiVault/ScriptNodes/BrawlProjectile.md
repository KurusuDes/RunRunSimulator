---
tags: [script, world, brawl, projectile, pool]
---

# BrawlProjectile.cs

**Ruta:** `World/Brawl/BrawlProjectile.cs`

**Responsabilidad:** Proyectil pool singleton (shotgun, sniper, boomerang, ráfaga). Física: movimiento línea, lob parabólico, homing tracking, rebote, pierce, spin. Detecta impacto; no daña dos veces. Trail renderer con VFX team look.

## Tipos de Proyectil

| Tipo | Movimiento | Rebote | Pierce |
|------|-----------|--------|--------|
| **Normal** | Línea | No | No |
| **Bounce** | Línea + rebote | Sí | No |
| **Pierce** | Línea | No | Sí |
| **Lob** | Parábola | No | No |
| **Boomerang** | Línea → vuelta | Sí | Sí |
| **Homing** | Tracking curva | Sí | No |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Shot` | `BrawlShot` | Datos de disparo |
| `Active` | IReadOnlyList | Proyectiles vivos |

## Métodos Estáticos

| Método | Descripción |
|--------|-------------|
| `Fire(shot)` | Adquiere del pool, lanza |
| `ClearAll()` | Limpia pool (reset escena) |

## Ciclo de Vida

1. `Fire(shot)` → `Acquire()` → `Launch(shot)`
2. `Update()` → `StepMotion()`:
   - **Línea:** Movimiento directo + rebotes/pierce
   - **Lob:** Interpolación parabólica (arc)
   - **Homing:** Tracking hacia blanco + turn speed
3. Detección colisión contra `BrawlFighter` en ruta
4. Impacto → `TakeDamage()` + efectos + VFX
5. Fin de vida (range, boomerang timeout) → `Release()` al pool

## Homing

- Turn speed ° por segundo
- Re-adquiere blanco si muere
- Velocidad de persecución > velocidad blanco

## Spin

- Proyectil rota (visual); Spin ° por segundo
- Aplicado a SpriteRenderer del sprite

## VFX

- **Sprite ícono billboard** del tema con color team look
- **Halo aditivo** para proyectiles aliados (GlowScale 2,2, GlowAlpha 0,55)
- **Trail renderer** con gradiente (plain o comet signature)
- **Pulso brillo** en glow (pulsHz 8 Hz)

## Parámetros SO

| Parámetro | Uso |
|-----------|-----|
| `Damage`, `Heal` | Impacto |
| `Knockback` | Fuerza knock |
| `Speed` | Velocidad línea/lob |
| `Range` | Distancia máxima |
| `Bounces` | Rebotes permitidos |
| `Lob`, `LobTarget`, `LobSeconds` | Parábola |
| `Pierce`, `Boomerang` | Especiales |
| `Homing`, `HomingTurn` | Tracking |
| `SpriteSize` | Escala ícono |

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Entrada:**
- [[BrawlWing]] → `Fire()` shotgun/sniper/boomerang/ráfaga
- [[BrawlSkillOffense]] → `Fire()` skills (Shot, Nova, Homing)

**Impacto:**
- [[BrawlFighter]] → `TakeDamage()`, `Heal()`

**VFX:**
- [[BrawlProjectileTrail]] → trail setup
- [[BrawlTeamLook]] → color wash

## Notas

- Pool singleton, reutilizable (no GC en combate)
- Struck set previene doble-impacto
- BoomerangMaxSeconds 4 s (timeout)
- GlowSprite aditivo para proyectiles aliados (visibilidad)
- S142: 431 líneas (sobre tope ~400); si crece, partir visual en BrawlProjectileVisuals
