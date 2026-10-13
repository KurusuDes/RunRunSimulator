---
tags: [script, world, title, ai, wander]
---

# TitleWanderer.cs

**Ruta:** `World/Title/TitleWanderer.cs`

**Responsabilidad:** Comportamiento de paseo de una criatura decorativa del título. Alterna entre caminar a un punto aleatorio del NavMesh, quedarse quieta y hacer gestos, y a veces acercarse a otra criatura y mirarla mientras espera. No tiene estado de juego.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `agent` | `NavMeshAgent` (Required) | — | Movimiento |
| `locomotion` | `MonchiLocomotionAnimator` (Required) | — | Gestos (`PlayGesture`) |
| `idleSeconds` | `Vector2` | (2, 6) | Rango de espera entre paseos |
| `gestureChance` | `float` | 0.35 | Probabilidad de gesto al quedarse quieta |
| `approachChance` | `float` | 0.25 | Probabilidad de elegir acercarse a otra criatura |
| `approachDistance` | `float` | 1.6 | Distancia de parada junto a la otra criatura |
| `turnSpeed` | `float` | 180 | Grados por segundo al girar hacia el objetivo |
| `gestures` | `string[]` | Yes, No, Eat, Roar | Gestos posibles |

## Ciclo

1. `Init(center, radius)`: fija el centro y radio, velocidad aleatoria entre 0.8 y 1.4, arranca `Loop`.
2. `Loop` (tras un frame): toma la lista de otras criaturas del título.
3. Cada vuelta: con `approachChance` elige la criatura más cercana y un punto a `approachDistance` de ella; si no, un punto aleatorio dentro de `radius` del centro.
4. Camina y espera la llegada (`WaitArrival`, timeout 30 s).
5. Si no está acercándose, puede hacer un gesto (`gestureChance`).
6. Espera un tiempo aleatorio en `idleSeconds`; mientras se acerca a otra, gira hacia ella.

## Notas

- La lista de otras criaturas se toma una sola vez, en el primer frame del `Loop`. Las criaturas que aparezcan después no se conocen.
- Fallo de muestreo de NavMesh: se queda en la posición actual.

## Conexiones

- [[TitleDiorama]] — la instancia y llama `Init`
- [[MonchiLocomotionAnimator]] — `PlayGesture`
- [[NavMeshAgent]] — movimiento
