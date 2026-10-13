---
tags: [script, world, tutorial, guide, navmesh, visual]
---

# TutorialGuide.cs

**Ruta:** `World/Tutorial/TutorialGuide.cs`

**Responsabilidad:** Dibuja en el mundo la guía del paso del tutorial: una línea punteada animada por el NavMesh desde el jugador hasta el objetivo del paso, y un disco con anillos en el destino. Solo visual; la lógica del paso vive en [[TutorialDirector]]. El juice se hace con `CueDrawer` (Shapes), sin MMFeedbacks.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `player` | `Transform` (Required) | — | Origen de la guía |
| `cueMaterial` | `Material` (Required) | — | Material de cue |
| `additiveMaterial` | `Material` (Required) | — | Material aditivo |
| `lineColor` | `Color` | ámbar, alfa 0.9 | Color de la línea |
| `targetColor` | `Color` | ámbar claro, alfa 0.9 | Color del destino |
| `lineWidth` | `float` | 0.12 | Grosor |
| `dashLength`, `dashGap` | `float` | 0.35, 0.25 | Patrón punteado |
| `flowSpeed` | `float` | 1.2 | Velocidad de avance de los guiones |
| `repathInterval` | `float` | 0.25 | Intervalo de recálculo de ruta |
| `floorOffset` | `float` | 0.05 | Elevación sobre el piso |

Constantes: 8 subdivisiones Catmull-Rom por tramo; fade de entrada 0.4 s, salida 0.3 s; fade de inicio 1 m, de fin 0.6 m.

## Comportamiento

- `StepChanged`: visible solo si hay paso activo y `Target` no es null; reinicia el fade de cambio.
- `StepCompleted` y `Finished`: se oculta.
- `LateUpdate` (tiempo unscaled):
  - Actualiza posición y radio del destino.
  - Recalcula la ruta cada `repathInterval` con `NavMesh.CalculatePath` (si falla, usa una línea recta).
  - Suaviza la ruta con Catmull-Rom y dibuja tramos con `CueDrawer.DashedSegment`, con fade en cabeza y cola.
  - Si el jugador ya está dentro del radio, no dibuja la línea.
  - Dibuja el destino con `CueDrawer.Disc`, `DashedRing` y `Ring` pulsante.
- Antes de dibujar guarda y restaura `CueDrawer.AlphaScale` y `CueDrawer.DrawBehind`.

## Suscripciones (OnEnable / OnDisable)

| Evento | Manejador |
|--------|-----------|
| `TutorialDirector.StepChanged` | `OnStepChanged` |
| `TutorialDirector.StepCompleted` | `OnStepCompleted` |
| `TutorialDirector.Finished` | `OnFinished` |

## Conexiones

- [[TutorialDirector]] — fuente de pasos y eventos
- [[TutorialStep]] — `Target` y `Radius` del paso
- [[CueDrawer]] — dibujo de líneas, discos y anillos
- [[NavMesh]] — ruta hacia el destino
