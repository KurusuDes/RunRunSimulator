---
tags: [script, world, brawl, skills, abilities]
---

# BrawlSkillCaster.cs

**Ruta:** `World/Brawl/BrawlSkillCaster.cs`

**Responsabilidad:** Orquestación de 2 habilidades (cuerno, espalda). Maneja cooldown, windup, tracking de blanco durante casteo. Dispara a través de [[BrawlSkillEffects]]. Enraíza durante casteo si skill lo requiere. Interruple deja 50 % cooldown.

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `readyAt[2]` | float[] | Tiempo ready para slot 0 (cuerno), 1 (espalda) |
| `casting` | bool | En casteo |
| `castSlot` | int | 0 o 1; -1 si no |
| `castSkill` | `BrawlSkillSO` | Skill actual |
| `castStart`, `castEnd` | float | Ventana windup |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Count` | int | Siempre 2 (dos slots) |
| `IsCasting` | bool | En casteo activo |
| `CastSlot` | int | Slot siendo casteado; -1 sino |
| `CastSkill` | `BrawlSkillSO` | Skill en casteo |
| `Cast01` | float | Progreso windup 0-1 |
| `AimPoint`, `AimDir` | Vector3 | Objetivo y dirección |
| `CastTarget` | `BrawlFighter` | Blanco seguido |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Init(owner)` | Inicializar; cargar cooldowns iniciales |
| `Skill(slot)` | Retorna skill en slot (0 cuerno, 1 espalda) |
| `Theme(slot)` | Retorna theme para VFX |
| `IsReady(slot)` | True si no en cooldown y no casteando este slot |
| `Charge01(slot)` | Progreso del cooldown 0-1 |
| `TryCast(slot, target, aimPoint)` | Intenta casteo; retorna éxito |
| `Refill()` | Resetea todos los cooldowns a ahora (Last Stand) |
| `Interrupt()` | Cancela casteo; aplica penalización cooldown ×0,5 |

## Flujo de Casteo

1. `TryCast(slot, target, aimPoint)` → valida (ready, vivo, no aturdido, no forzado)
2. `casting = true`; `castStart = now`; `castEnd = now + skill.Windup`
3. Si `skill.Windup <= 0`, ejecutar inmediatamente
4. Update → si `skill.TracksTarget`, actualizar `AimPoint/AimDir` hacia blanco
5. Cuando `Time.time >= castEnd`, `Fire()`
6. `Fire()` → crea `BrawlCast`, delega a [[BrawlSkillEffects]]

## Tracking

- Activo si `skill.TracksTarget` y > 0,15 s restante
- No aplica en zona (EnemyCluster)
- Sigue blanco si vivo

## Eventos Estáticos

| Evento | Parámetros | Cuándo |
|--------|-----------|--------|
| `OnCastStarted` | `fighter, skill, aimPoint` | Al iniciar casteo |
| `OnCastFired` | `fighter, skill, aimPoint` | Al completar casteo |

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Dueño:**
- [[BrawlFighter]] — propietario

**Entrada:**
- [[BrawlBrain]] — llama TryCast
- [[BrawlMotor]], [[BrawlWing]] — bloquean casteo si IsForced/IsWindingUp

**Salida:**
- [[BrawlSkillEffects]] — ejecuta skill
- [[BrawlSkillJudge]] — juzga si querer

## Notas

- FirstDelay en SO para inicial delay distinto
- TrackCutoffSeconds 0,15 s (deja de seguir blanco dentro de último 0,15 s)
- InterruptCooldownFactor 0,5 (mitad del cooldown si interrumpido por stun)
- RootWhileCasting del SO determina raíz durante casteo
