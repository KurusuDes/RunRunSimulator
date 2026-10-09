---
tags: [script, world, brawl, run, trial, props]
---

# BrawlTrialProps.cs

**Ruta:** `World/Brawl/BrawlTrialProps.cs`

**Responsabilidad:** Coloca el prop de la sala de prueba (muñeco o mineral) sobre cada rival cuando empieza la sala. Al recibir `BrawlTrialRoom.Began`, apaga los renderers del rival, instancia el prop como hijo del rival y lo orienta hacia el centro del equipo jugador. Es presentación: no decide reglas ni daño.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `match` | `BrawlMatch` | — | Partida con los fighters (Required) |
| `trial` | `BrawlTrialRoom` | — | Sala de prueba que avisa el inicio y el tipo (Required) |
| `dummyProp` | `GameObject` | — | Prefab para salas de muñecos |
| `mineralProp` | `GameObject` | — | Prefab para salas de minerales |
| `propScale` | `float` | 1 | Escala del prop (mínimo 0,1) |

## Comportamiento

- **Suscripción:** `trial.Began` en `OnEnable`; desuscribe en `OnDisable`.
- **Elección del prefab:** `Dummies` usa `dummyProp`; cualquier otro tipo usa `mineralProp`. Si es null, no hace nada.
- **Centro del equipo:** promedio de las posiciones de los fighters `Player` de la partida.
- **Por cada rival:** pone `enabled = false` en todos los `Renderer` bajo `Visualizer`, instancia el prop como hijo del rival con posición y rotación locales en cero y escala `propScale`, y lo gira en yaw hacia el centro del equipo.
- Si el prop trae un `BrawlPropHit`, llama `Bind(rival)` para que reaccione a sus golpes.

## Conexiones

- [[BrawlTrialRoom]] — `Began` y `Kind`
- [[BrawlMatch]] — `Fighters`
- [[BrawlFighter]] — `Team`, `Position`, `Visualizer`
- [[BrawlPropHit]] — `Bind` del hit feedback del prop
- [[BrawlRunDirector]] — dispara el inicio de la sala por `trial.Begin`

## Notas

- Este script no restaura los renderers del rival al terminar la sala; el prop queda como hijo del rival.
- Los rivales de sala de prueba son `Dummy` (ver [[BrawlFighter]]): el prop reemplaza su malla visible.
