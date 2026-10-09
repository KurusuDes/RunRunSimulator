---
tags: [script, ui, brawl, run, hud, uitk]
---

# BrawlRunHud.cs

**Ruta:** `UI/BrawlRunHud.cs`

**Responsabilidad:** HUD de la bajada Brawl durante la pelea. Muestra en la tira superior cuántas salas faltan del tramo (texto y pips), la mochila de Minerita y la etiqueta de la sala de prueba activa (muñecos o minerales). Es visible en `Fighting` y `RoomResult`. Al cerrar una sala con botín dispara el feedback `onLoot` y actualiza la mochila con retardo. Es presentación pura: lee `BrawlRunDirector` y `BrawlTrialRoom`, no decide reglas.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento con `run-root` (Required) |
| `director` | `BrawlRunDirector` | Estado de la bajada (Required) |
| `trial` | `BrawlTrialRoom` | Sala de prueba activa (opcional) |
| `onLoot` | `MMF_Player` | Feedback al sumar botín (VFX por MMFeedbacks) |
| `countDelay` | `float` | Segundos (mín. 0; default 0,75) entre el feedback y la actualización de la mochila |

## Elementos UXML

`run-root`, `run-hud`, `run-left-pips`, `run-bag-count`, `run-left-text`, `run-trial`. `TryBind()` exige los cinco hijos (`run-hud`, `run-left-pips`, `run-bag-count`, `run-left-text`, `run-trial`) y no bindea si falta alguno.

## Comportamiento por Estado

| Estado | `run-hud` | Texto de salas | Pips | Etiqueta de prueba |
|--------|-----------|----------------|------|--------------------|
| `Fighting` | visible | "Faltan N salas", "Falta 1 sala" o "Última sala" (salas que quedan sin contar la actual) | `done` (antes del índice), `current` (índice actual), `upcoming` | visible si la sala de prueba está activa |
| `RoomResult` | visible | Mismo texto, contando las salas que faltan por jugar | `done` y `upcoming`, sin `current` | oculta |
| Otros | oculto | — | — | oculta |

- **Etiqueta de prueba** (solo en `Fighting` con `trial.Active`): muñecos → "Muñecos · pégales para curar al equipo"; minerales sin empezar → "Minerales · pégale al cristal para empezar"; minerales en curso → "Minerales · +X Minerita".
- **Mochila:** valor = `Material × MineritaPerLoot`. Si llega botín nuevo (`RoomResult` con `LastRoomLoot > 0` y valor distinto del mostrado), dispara `onLoot` y, tras `countDelay`, actualiza el número (`ApplyLoot`). Mientras espera, `lootPending` evita reprogramar. En los demás casos fija el valor directo.

## Flujo

- `OnEnable`: suscribe `director.Changed` y bindea. `OnDisable`: desuscribe y `Unbind()` (pausa el schedule pendiente y limpia los pips).
- `HandleChanged` → `TryBind` + `Refresh`.
- `Update` (cada frame): `TryBind` + `RefreshTrial`. La etiqueta de prueba solo se redibuja si cambian activa, empezada o material.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlRunDirector]] — `Changed`, `State`, `Run`, `Active`, `LastRoomLoot`
- [[BrawlRun]] — `Rooms`, `RoomIndex`, `Depth`, `Material`
- [[BrawlTrialRoom]] — `Active`, `Started`, `Kind`, `Material`
- [[BrawlRunRulesSO]] — `MineritaPerLoot` vía `Current`
- [[BrawlRunPanel]] — tarjeta de planificación y derrota (la tira de pelea ya no vive ahí)
- [[BrawlRunVeil]] — velo entre salas, comparte `run-root`
- [[BrawlEnums.cs]] — `BrawlRunState`, `BrawlRoomKind`

## Notas

- Textos en español hardcodeados (no pasan por `Loc`), como en `BrawlHud`.
- No tiene reglas propias: todo lo que muestra sale de `BrawlRun` y del director.
- S146: nuevo. Reemplaza la tira de pelea que tenía `BrawlRunPanel`.
