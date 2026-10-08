---
tags: [script, world, brawl, camera, cinemachine]
---

# BrawlCamera.cs

**Ruta:** `World/Brawl/BrawlCamera.cs`

**Responsabilidad:** Cámara dinámica para Brawl con `CinemachineTargetGroup`. Sigue a 6 fighters; impulso (shake) en golpes pesados (≥1500 dmg), KOs, Last Stand. Ponderación de miembros desactivos (idle weight 0,12).

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `ended` | bool | Partida finalizada |
| `winner` | `ExpeditionTeam` | Ganador (Player/Rival) |

## Métodos Privados (Handlers)

| Handler | Entrada | Efecto |
|---------|---------|--------|
| `HandleRosterSpawned(fighters)` | Lista de fighters | Limpia targets; añade todos a TargetGroup |
| `HandleMatchEnded(winner)` | Winner team | Flag ended |
| `HandleDamaged(victim, hit)` | Fighter, hit | Boost acción; shake si ≥1500 dmg |
| `HandleKnockedOut(victim, killer)` | Fighter, fighter | Shake fuerte |
| `HandleLastStand(survivor)` | Fighter | Shake moderado |

## Cinemachine Setup

- `CinemachineTargetGroup` con miembro radio 1,6 m
- `CinemachineImpulseSource` para shakes
- Blend speed 2,5 s
- FOV range 18-50° (antes 32° limitaba zoom)
- FramingSize 0,6; idleWeight 0,12 (inactivos 12 % importancia)

## Impulsos (Shake)

| Evento | Condición | Fuerza |
|--------|-----------|--------|
| **Heavy Hit** | Daño ≥1500 | 0,25 |
| **KO** | Knockout | 0,6 |
| **Last Stand** | Último en pie | 0,45 |

- Gap mínimo 0,12 s entre impulsos (evita spam)
- Ignorar gap para KO (siempre shake)

## Action Boost

- Al daño/sanación: marca tiempo (actionSeconds 1,5 s)
- Miembros activos reciben peso > 1,0
- Inactivos (sin acción en 1,5 s) pesan 0,12

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Suscriptor:**
- [[BrawlMatch]] → OnRosterSpawned, OnMatchEnded
- [[BrawlFighter]] → OnDamaged, OnKnockedOut
- [[BrawlMatch]] → OnLastStand

**Componentes:**
- CinemachineTargetGroup (ref serializada)
- CinemachineImpulseSource (ref serializada)
- ObserverCamera (listener de impulsos)

## Notas

- Cámara no bloquea gameplay
- Smooth tracking de múltiples targets
- Impulsos independientes de simulación (Time.timeScale no afecta)
