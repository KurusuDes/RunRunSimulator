---
tags: [script, world, brawl, zone, effect]
---

# BrawlZone.cs

**Ruta:** `World/Brawl/BrawlZone.cs`

**Responsabilidad:** Zona de efecto pool singleton (Lana, Cristales, Malvaviscos, LomoLana). Demora antes de armarse; duración; tick periódico (daño/heal/slow/stun/knockback/pull). Follow owner o anclada. Detecta targets en radio cada tick.

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Spec` | `BrawlZoneSpec` | Configuración completa |
| `Center` | Vector3 | Centro actual |
| `Age` | float | Tiempo desde spawn |
| `Armed` | bool | `Age >= Delay` |
| `Delay01`, `Life01` | float | Progreso de demora/duración |

## BrawlZoneSpec

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Owner`, `Team` | Fighter, Enum | Lanzador y equipo |
| `Center`, `Radius` | Vector3, float | Posición y radio |
| `Delay`, `Duration` | float | Demora antes de armar, duración |
| `TickSeconds` | float | Intervalo de tick |
| `DamagePerTick`, `HealPerTick` | float | Efecto por tick |
| `Slow`, `SlowSeconds` | float | Slow aplicado |
| `StunSeconds`, `Knockback`, `Pull` | float | Status |
| `FollowOwner`, `HitOnArm` | bool | Follow lanzador o golpea al lanzar |
| `Theme` | `BrawlTheme` | Color VFX |

## Ciclo de Vida

1. `Spawn(spec)` → `Acquire()` → `Begin(spec)`
2. `Update()`:
   - Incrementa `age`
   - Si `FollowOwner`, actualiza `center = owner.Position`
   - Si `Armed` y `age >= lastTick + TickSeconds`, `Tick()`
3. `Tick()`:
   - Busca targets en radio
   - Aplica daño/heal/slow/stun/knock/pull
   - Emite VFX zone
4. Cuando `Life01 >= 1`, `Release()` al pool

## HitOnArm

- Si true: golpea al lanzar (sin demora), además del tick
- Si false: espera demora antes de primer tick

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Entrada:**
- [[BrawlSkillSupport]] → `Spawn()` en Zone skill

**Salida:**
- [[BrawlFighter]] → `TakeDamage()`, `Heal()`, Apply slow/stun/taunt/knock

**VFX:**
- [[BrawlFx]] → `Emit()` zone visuals

## Notas

- Pool singleton, reutilizable (no GC en combate)
- DefaultTickSeconds 0,5 s si skill no define
- PullMinDistance 0,1 m (mínimo para aplicar pull)
- Follow owner permite zonas móviles (ej: lluvia persigue caster)
- Scratch buffer para búsquedas (reutilizable, no GC)
