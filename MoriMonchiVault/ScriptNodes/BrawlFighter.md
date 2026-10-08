---
tags: [script, world, brawl, core, fighter, state]
---

# BrawlFighter.cs

**Ruta:** `World/Brawl/BrawlFighter.cs`

**Responsabilidad:** Núcleo de estado de combatiente: vida, escudo, velocidad, daño. Mantiene referencias a componentes (Motor, Wing, SkillCaster, Brain). Punto de unión de entrada de daño y curación. Emite eventos estáticos para inscripción de presentación. Aplica modificadores de estado (slow, stun, haste, boost, espinas, provocación). Registra combatientes en lista estática `BrawlFighter.All`.

## Estructura

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `visualizer` | `MonchiVisualizer` | Componente visual 3D |
| `motor` | `BrawlMotor` | Movimiento y patrones de desplazamiento |
| `wing` | `BrawlWing` | Ataque básico y movilidad |
| `caster` | `BrawlSkillCaster` | Habilidades (cuerno, espalda) |
| `brain` | `BrawlBrain` | IA autónoma |
| `bodyRadius`, `centerHeight` | float | Geometría de colisión |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `DNA` | `CreatureDNA` | Datos vivos (leer después de Bind) |
| `Team` | `ExpeditionTeam` | Player o Rival |
| `MaxHp`, `Hp`, `Hp01` | float | Vida y ratio |
| `Shield` | float | Escudo activo (decrece por tiempo) |
| `IsAlive` | bool | `Hp > 0` |
| `IsStunned` | bool | Aturdido; `SpeedMultiplier = 0` |
| `SpeedMultiplier` | float | `(1 - slow) × (1 + haste)`; 0 si aturdido |
| `DamageMultiplier` | float | `(1 + boost) × RoundDamageFactor` |
| `Position`, `Center` | Vector3 | Posición y centro de impacto |
| `Radius` | float | Radio de cuerpo |
| `Lift` | float | Altura de salto (set por Motor) |
| `WingKit`, `HornSkill`, `BackSkill` | SO | Kits y habilidades |
| `WingTheme`, `HornTheme`, `BackTheme` | `BrawlTheme` | Color e ícono de VFX |
| `DamageDealt`, `HealingDone`, `KOs` | float/int | Estadísticas de ronda |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Bind(dna, team, kits, tuning, parts, bank, fur)` | Inicialización completa; visualiza, carga habilidades, máxima vida |
| `Despawn()` | Retira de `All` |
| `TakeDamage(hit)` | Aplica daño (absorbe escudo primero), knockback, espinas, event |
| `Heal(amount, source)` | Restaura vida (limitado a máx) |
| `AddShield(amount, seconds)` | Escudo temporal |
| `ApplySlow/Stun/Haste/DamageBoost/Thorns/Taunt(...)` | Modifica estado; más fuerte gana |

## Eventos Estáticos

| Evento | Parámetros | Cuándo |
|--------|-----------|--------|
| `OnBound` | `BrawlFighter` | Al Bind; presentación puede inicializar |
| `OnDamaged` | `fighter, hit` | Después del daño |
| `OnHealed` | `fighter, amount, source` | Después de curar (real > 0,5) |
| `OnShielded` | `fighter, amount` | Al añadir escudo |
| `OnKnockedOut` | `fighter, attacker` | Cuando llega a 0 HP |
| `OnStatusApplied` | `fighter, kind, duration` | Status nuevo aplicado |

## Modadores de Estado

- **Shield:** Absorbe daño hasta expirar; no acumula, se queda con máximo.
- **Slow/Haste:** Modifican `SpeedMultiplier`; mantiene el más fuerte, extiende duración.
- **Stun:** Cancela Wing/Caster; `SpeedMultiplier = 0`.
- **Thorns:** Rebota daño en ataques melé enemigos.
- **Taunt:** Fuerza a blanco de cuerno/espalda.
- **Boost:** Amplifica daño saliente.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Componentes:**
- [[BrawlMotor]] — propulsor físico
- [[BrawlWing]] — ataque básico
- [[BrawlSkillCaster]] — habilidades
- [[BrawlBrain]] — toma de decisiones

**Datos:**
- [[CreatureDNA]] — estadísticas
- [[BrawlWingKitSO]], [[BrawlSkillSO]] — kit de combate
- [[BrawlTheme]] — tema VFX
- [[BrawlTuningSO]] — parámetros globales

**Presentación:**
- [[BrawlAnimator]] — anima estado
- [[BrawlBody]] — pulso y flash
- [[BrawlCamera]] — sigue e impulsiona

## Notas

- Lista estática `All` alimenta [[BrawlQuery]] para búsquedas espaciales.
- `RoundDamageFactor` escala daño global (rampa por KOs en [[BrawlMatch]]).
- `LastAttacker`/`LastHurtAt` para crédito de KO.
- `Frozen` pausar en gameplay (distinto de Stun).
