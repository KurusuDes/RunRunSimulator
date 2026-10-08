---
tags: [script, world, brawl, attack, basic]
---

# BrawlWing.cs

**Ruta:** `World/Brawl/BrawlWing.cs`

**Responsabilidad:** Ataque básico (6 tipos) + movilidad (5 tipos). Windup visual, recarga. Emite eventos antes de acción. Proyectiles pool (shotgun, sniper, boomerang, ráfaga de curación). Golpe melé en cono. Latigazo línea con slowdown. Comportamiento de combo melé (2 mordiscos en 0,12 s). Leap aterrizaje causa daño.

## Ataques

| Tipo | Proyectiles | Contacto |
|------|-------------|----------|
| **Melee** | No | Cono frontal, 2 golpes |
| **Whip** | No | Segmento línea + slow |
| **Shotgun** | Sí (5 spread) | Contacto directo |
| **Sniper** | Sí (1 puntería) | Alto daño, puntería predicitiva |
| **Burst** | Sí (3 dardos) | Ráfaga con homing a blanco/curación |
| **Boomerang** | Sí (pierce + vuelta) | Viaje ida-vuelta |

## Movilidades

| Tipo | Efecto |
|------|--------|
| **Leap** | Salto sobre blanco, daño de caída |
| **Sprint** | Haste 0,6 por duración |
| **Roll/Blink** | Dash directamente |
| **Hop** | Salto bajo |
| **Glide** | Salto alto |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `IsWindingUp` | bool | En anticipación (windup) |
| `Windup01` | float | Progreso 0-1 |
| `AttackReady` | bool | Recarga completada |
| `Attack01` | float | Progreso recarga 0-1 |
| `MobilityReady` | bool | Movilidad lista |
| `Mobility01` | float | Progreso movilidad 0-1 |
| `AimPoint`, `AimDir` | Vector3 | Objetivo y dirección |
| `AimHealing` | bool | True si curando aliado |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Init(fighter)` | Inicializar con kit; windup = 0; recarga aleatoria |
| `TryAttack(target)` | Intenta ataque (recarga, distancia, alianza); inicia windup o ejecuta |
| `TryMobility(desiredPoint)` | Intenta movilidad; valida rango |
| `Cancel()` | Detiene windup y combo |

## Eventos Estáticos

| Evento | Parámetros | Cuándo |
|--------|-----------|--------|
| `OnAttackFired` | `fighter, kit, aimPoint, healing` | Proyectil/golpe disparado |
| `OnMobilityUsed` | `fighter, mobilityKind` | Movilidad consumida |

## Windupys Bucle

1. `TryAttack()` → `windingUp = true`, `windupEndAt = now + kit.Windup`
2. Update → `windupTarget.Position` sigue el objetivo
3. `Time.time >= windupEndAt` → `Execute()`
4. Dispara proyectil(es), inicia combo si melé/ráfaga

## Puntería

- **Sniper/Shotgun/Burst:** Predicción de movimiento = `targetVelocity × (distancia / projectileSpeed)`
- **Melé/Latigazo:** Cono frontal del atacante
- **Boomerang:** Dirección del objetivo, Pierce + Spin

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Dueño:**
- [[BrawlFighter]] — propietario

**Entrada:**
- [[BrawlBrain]] — llama TryAttack/TryMobility
- [[BrawlMotor]] — recibe onLeapLanded callback

**Salida:**
- [[BrawlFx]] — emite Slash/Whip/Muzzle/Dash/Pulse/Land
- [[BrawlProjectile]] — pool de proyectiles
- [[BrawlQuery]] — búsqueda de enemigos en rango/cono

## Notas

- Combo activado por melé/ráfaga; bloqueado por otro ataque
- WaitForSeconds cacheadas (MeleeWait 0,12 s, BurstWait 0,09 s)
- LeapLandRadius 1,8 m; LeapLandKnockback 4
- Heal para Colibrí (ala W1); filtra aliados bajo 62 % vida
