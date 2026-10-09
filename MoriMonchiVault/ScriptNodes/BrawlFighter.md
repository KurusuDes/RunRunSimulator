---
tags: [script, world, brawl, core, fighter, state]
---

# BrawlFighter.cs

**Ruta:** `World/Brawl/BrawlFighter.cs`

**Responsabilidad:** Núcleo de estado de combatiente: vida, escudo, velocidad, daño. Mantiene referencias a componentes (Motor, Wing, SkillCaster, Brain). Punto de unión de entrada de daño y curación. Emite eventos estáticos para inscripción de presentación. Aplica modificadores de estado (slow, stun, haste, boost, espinas, provocación). Registra combatientes en lista estática `BrawlFighter.All`. Recibe el poder y la vida de la bajada vía `Prime` y puede marcarse como muñeco (`Dummy`). `Bind` resuelve el kit y los temas con `BrawlKitProfile.Of`.

## Estructura

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `visualizer` | `MonchiVisualizer` | Componente visual 3D |
| `motor` | `BrawlMotor` | Movimiento y patrones de desplazamiento |
| `wing` | `BrawlWing` | Ataque básico y movilidad |
| `caster` | `BrawlSkillCaster` | Habilidades (cuerno, espalda) |
| `brain` | `BrawlBrain` | IA autónoma |
| `bodyRadius`, `centerHeight` | float | Geometría de colisión (defaults 0.65 y 0.8) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `DNA` | `CreatureDNA` | Datos vivos (leer después de Bind) |
| `Team` | `ExpeditionTeam` | Player o Rival |
| `DisplayName` | string | `CustomName` del DNA o nombre del GameObject |
| `BodyLabel` | string | Etiqueta de cuerpo desde `BrawlTuningSO.BodyFor` |
| `MaxHp`, `Hp`, `Hp01` | float | Vida y ratio |
| `Shield` | float | Escudo activo (decrece por tiempo) |
| `IsAlive` | bool | `Hp > 0` |
| `IsStunned` | bool | Aturdido; `SpeedMultiplier = 0` |
| `SpeedMultiplier` | float | `(1 - slow) × (1 + haste)`; 0 si aturdido |
| `DamageMultiplier` | float | `(1 + boost) × RoundDamageFactor × Power` |
| `Power` | float | Multiplicador de vida y daño puesto por `Prime` (1 por defecto) |
| `Dummy` | bool | Muñeco de sala de prueba; hace `Frozen` al combatiente |
| `Frozen` | bool | Get: `frozen \|\| Dummy`. Set: pausa de gameplay (distinto de Stun) |
| `Position`, `Center` | Vector3 | Posición y centro de impacto |
| `Radius` | float | Radio de cuerpo |
| `Lift` | float | Altura de salto (set por Motor) |
| `BaseSpeed` | float | `WingKit.MoveSpeed × body.SpeedMul` |
| `HealFactor`, `RoundDamageFactor` | float | Multiplicadores de curación y daño (muerte súbita, ramp de KO) |
| `Taunter` | BrawlFighter | Quien provoca, si el taunt está vigente |
| `WingKit`, `HornSkill`, `BackSkill` | SO | Kits y habilidades |
| `WingTheme`, `HornTheme`, `BackTheme` | `BrawlTheme` | Color e ícono de VFX |
| `DamageDealt`, `HealingDone`, `KOs` | float/int | Estadísticas de ronda |
| `LastAttacker`, `LastHurtAt` | BrawlFighter / float | Crédito de KO y última herida |

## Struct `BrawlHit`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Amount` | float | Daño o curación. `TakeDamage` lo reescribe a daño aplicado + absorbido |
| `Source` | BrawlFighter | Atacante (null si no hay) |
| `Point` | Vector3 | Punto de impacto (los floats de daño lo usan) |
| `KnockDir`, `Knockback` | Vector3, float | Dirección y magnitud del empuje |
| `Theme` | `BrawlTheme` | Tema VFX del golpe |
| `FromSkill` | bool | Viene de una habilidad |
| `Melee` | bool | Cuerpo a cuerpo; activa espinas |
| `IsDrain` | bool | Drenaje: no cuenta para `LastAttacker` ni `DamageDealt` |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Bind(dna, team, kits, tuning, parts, bank, fur)` | Inicialización completa: visualiza el DNA, resuelve kit y temas con `BrawlKitProfile.Of`, toma `MaxHp`, `BaseSpeed` y `BodyLabel` de `tuning.BodyFor(BodyShapeID)`, resetea estado, registra en `All` e inicia motor, ala, caster y brain. Resetea `Power = 1` y `Dummy = false` |
| `Prime(power, health01)` | Escala la vida máxima por `power` (mín 0,05) y fija la vida actual a `MaxHp × health01` (mín 1). Usado por la bajada |
| `Despawn()` | Retira de `All` |
| `TakeDamage(hit)` | Aplica daño (absorbe escudo primero), knockback, espinas, event |
| `Heal(amount, source)` | Restaura vida (limitado a máx) |
| `AddShield(amount, seconds)` | Escudo temporal |
| `ApplySlow/Stun/Haste/DamageBoost/Thorns/Taunt(...)` | Modifica estado; más fuerte gana |

## Eventos Estáticos

| Evento | Parámetros | Cuándo |
|--------|-----------|--------|
| `OnBound` | `BrawlFighter` | Al Bind; presentación puede inicializar |
| `OnDamaged` | `fighter, hit` | Después del daño (`hit.Amount` ya es el daño aplicado + absorbido) |
| `OnHealed` | `fighter, amount, source` | Después de curar (real > 0,5) |
| `OnShielded` | `fighter, amount` | Al añadir escudo |
| `OnKnockedOut` | `fighter, attacker` | Cuando llega a 0 HP |
| `OnStatusApplied` | `fighter, kind, duration` | Status nuevo aplicado |

## Modificadores de Estado

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
- [[BrawlKitProfile]] — resuelve kit, temas y rol desde el DNA
- [[BrawlTheme]] — tema VFX
- [[BrawlTuningSO]] — parámetros globales

**Presentación:**
- [[BrawlAnimator]] — anima estado
- [[BrawlBody]] — pulso y flash
- [[BrawlCamera]] — sigue e impulsiona
- [[BrawlHud]], [[BrawlOverheads]] — leen eventos y propiedades para cards y plates
- [[BrawlTrialRoom]] — escucha `OnDamaged` para medir daño en salas de prueba
- [[BrawlPropHit]] — escucha `OnDamaged` para el feedback del prop del muñeco

**Bajada Brawl:**
- [[BrawlRunDirector]] — llama `Prime` y marca `Dummy`; lee `Hp01` al terminar la sala
- [[BrawlTrialProps]] — lee `Team`, `Position` y `Visualizer` para colocar el prop del rival

## Notas

- Lista estática `All` alimenta [[BrawlQuery]] para búsquedas espaciales.
- `RoundDamageFactor` escala daño global (rampa por KOs en [[BrawlMatch]]).
- `LastAttacker`/`LastHurtAt` para crédito de KO.
- `Prime` multiplica `MaxHp` cada vez que se llama: no es idempotente. Hoy se llama una vez por spawn, porque `Bind` restaura `MaxHp` antes.
- `TakeDamage` reescribe `hit.Amount` a daño aplicado + absorbido (con tope de vida restante) antes de `OnDamaged`.
