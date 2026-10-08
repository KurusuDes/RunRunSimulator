---
tags: [script, world, brawl, animation, presentation]
---

# BrawlAnimator.cs

**Ruta:** `World/Brawl/BrawlAnimator.cs`

**Responsabilidad:** Animador de Brawl. Locomotión (Idle/Walk/Run/Fly) según velocidad. Impacto (Damage state). Casteo (Roar). Victoria (Jump/Roar alternado). Transiciones suaves (CrossFade). Micro-congelado (Animator.speed = 0) en golpes pesados.

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `dead` | bool | KO permanente |
| `victory` | bool | Ganador celebrando |

## Estados Animator

| Estado | Condición |
|--------|-----------|
| `Idle` | Quieto |
| `Walk` | Movimiento lento (< 2,6 m/s) |
| `Run` | Movimiento rápido (≥ 2,6 m/s) |
| `Fly` | Hover permanente (ala Colibrí W1) |
| `Sick` | Muerto/KO |
| `Damage` | Recibe golpe; transición rápida |
| `Die` | Muerte (raro; final KO) |
| `Jump`, `Roar` | Celebración victoria |

## Micro-Congelado (Hit Stop)

Pausa animador en golpes:
- **Light:** Damage < 600 dm (no freeze)
- **Medium:** 600-1500 dm → Animator.speed = 0, 0,05 s
- **Heavy:** ≥1500 dm → Animator.speed = 0, 0,1 s

Simula impacto física (ejecución del motor sin animación).

## Velocidad Locomotión

- **Walk threshold:** 0,2 m/s
- **Run threshold:** 2,6 m/s
- **Blending:** CrossFade 0,15 s (acciones), 0,06 s (rápidas)

## Victoria

Alternada Jump/Roar cada 1,2 s mientras `victory = true`.

## Mood (Estado emocional)

- **Scared (< 30 % HP):** Mood asustado
- **Healing:** Mood curación (1 s)
- **Normal:** DNA mood base

Mostrado vía `MonchiVisualizer.SetMood()`.

## Eventos Suscritos

| Evento | Handler |
|--------|---------|
| `BrawlFighter.OnBound` | `HandleBound()` — copia animator ref |
| `BrawlFighter.OnDamaged` | `HandleDamaged()` — play Damage, micro freeze |
| `BrawlFighter.OnHealed` | `HandleHealed()` — mood curación |
| `BrawlFighter.OnKnockedOut` | `HandleKnockedOut()` — dead = true, play Sick |
| `BrawlWing.OnAttackFired` | `HandleAttackFired()` — lock locomotión breve |
| `BrawlSkillCaster.OnCastStarted` | `HandleCastStarted()` — play Roar |
| `BrawlSkillCaster.OnCastFired` | `HandleCastFired()` — lock locomotión |
| `BrawlMatch.OnMatchEnded` | `HandleMatchEnded()` — victory = true |

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Dueño:**
- [[BrawlFighter]] — propietario
- [[MonchiVisualizer]] — animator + SetMood

**Entrada:**
- [[BrawlMotor]] → velocidad en Update
- Eventos de BrawlFighter/Wing/Caster/Match

## Notas

- Animator cacheado por fighter para rápida búsqueda
- HasStateCache previene búsqueda IsName cara en cada frame
- FireLockSeconds 0,3 s (Whip, disparos)
- CastFireLockSeconds 0,35 s (skills)
- DamageLockSeconds 0,25 s (impacto)
- VictoryInterval 1,2 s alternancia
