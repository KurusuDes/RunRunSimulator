---
tags: [script, world, brawl, movement, physics]
---

# BrawlMotor.cs

**Ruta:** `World/Brawl/BrawlMotor.cs`

**Responsabilidad:** Orquestación NavMesh + fuerzas (knockback, dash, leap). Maneja rotación suave hacia objetivo o dirección. Calcula velocidad alisada. Estados de movimiento: MoveTo (patrulla), Dash (línea con callback), Leap (parábola + altura). Knockback decae exponencialmente. LookAt opcional para girar sin movimiento.

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Velocity` | Vector3 | Velocidad planar alisada (LateUpdate) |
| `IsDashing` | bool | En despliegue de embestida |
| `IsLeaping` | bool | En vuelo parabólico |
| `IsForced` | bool | `IsDashing \| IsLeaping` (bloquea navío) |
| `Rooted` | bool | Raíz (skill de casteo) |
| `LookAt` | Vector3? | Punto para girar hacia él |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Init(owner)` | Configurar NavMeshAgent, estado inicial |
| `Warp(position)` | Teletransporte instantáneo |
| `MoveTo(point)` | Establece destino (con retraso de 0,15 s); cancela si > 1 m |
| `Stop()` | Limpia destino y camino |
| `Dash(dir, dist, seconds, onStep, onEnd)` | Embestida línea; callback en cada step, final |
| `Leap(target, seconds, height, onLand)` | Salto parabólico; warp a NavMesh destino, callback al aterrizaje |
| `Knock(dir, strength)` | Acumula knockback; decae cada frame |
| `Halt()` | Detiene todo (dash, leap, knock, dest, look) |

## Comportamiento de Movimiento

**NavMesh:**
- Agent deshabilitado durante dash/leap (agent.Move manual)
- Rotación manual (no updateRotation)
- Frenado automático
- Aceleración 40 m/s², parada 0,2 m

**Ruta:**
- Retrazo mínimo 0,15 s entre recálculos
- Reprueba si > 1 m de distancia

**Dash:**
- Empuja directo linear (agent.Move)
- OnStep invocada cada frame durante duración
- Knockback aplica solo si no está forzado (dash/leap)

**Leap:**
- Interpolación suave (SmoothStep) del arco
- Altura = 4 × leapHeight × t × (1 - t) en `owner.Lift`
- Clamp a NavMesh con SamplePosition + Raycast
- OnLand invocada al llegar

**Knockback:**
- Suma vectores; decae exponencialmente (knockDecay = 6 por defecto)
- Se detiene en < 0,05 m/s

## Giro Suave

- Hacia `LookAt` si presente, sino hacia `Velocity`, sino hacia dirección dash
- Velocidad angular 720°/s por defecto
- Brújula planar (Y = 0)

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Dueño:**
- [[BrawlFighter]] — propietario

**Entrada:**
- [[BrawlBrain]] — establece MoveTo
- [[BrawlWing]] — callback onLeapLanded (daño de impacto)
- [[BrawlSkillOffense]] — Dash para Ariete

**VFX:**
- [[BrawlFx]] — emite Land (landing particles)

## Notas

- NavMeshAgent gestionado en Awake (GetComponent fallback)
- Velocidad calculada en LateUpdate (alisada con factor 25)
- MinForcedSeconds 0,05 s garantiza duración mínima de dash/leap
- Sin Jump controller; Lift es puro visual (modifica y en ModelRoot)
