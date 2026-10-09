---
tags: [script, world, brawl, run, trial, feedback, mmfeedbacks]
---

# BrawlPropHit.cs

**Ruta:** `World/Brawl/BrawlPropHit.cs`

**Responsabilidad:** Dispara el feedback de golpe (`MMF_Player`) del prop de sala de prueba cuando su dueño recibe daño. Va en el prefab del muñeco o mineral. Es presentación: el juice vive en el `MMF_Player` del prefab, no en código.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `onHit` | `MMF_Player` | Feedback que se reproduce en cada golpe al dueño |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Bind(BrawlFighter fighter)` | Fija el dueño cuyo daño escucha. Lo llama `BrawlTrialProps` al instanciar el prop |

## Eventos

| Evento | Manejador | Descripción |
|--------|-----------|-------------|
| `BrawlFighter.OnDamaged` (static) | `HandleDamaged` | Si la víctima es el dueño y hay `onHit`, llama `PlayFeedbacks()` |

Suscribe en `OnEnable` y desuscribe en `OnDisable`.

## Conexiones

- [[BrawlTrialProps]] — instancia el prop y llama `Bind`
- [[BrawlFighter]] — evento `OnDamaged`
- [[BrawlTrialRoom]] — la sala de prueba que contiene el prop
- Feedback: `MMF_Player` (MoreMountains Feedbacks), regla de VFX solo con MMFeedbacks

## Notas

- El filtro es por víctima: todos los props escuchan el mismo evento estático y solo reaccionan al suyo.
