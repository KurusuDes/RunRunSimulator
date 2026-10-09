---
tags: [script, ui, brawl, run, uitk]
---

# BrawlRunPanel.cs

**Ruta:** `UI/BrawlRunPanel.cs`

**Responsabilidad:** Presentación UITK de la bajada Brawl. Muestra dos vistas sobre el mismo documento: una tira superior durante la pelea (tramo, sala, cronómetro de prueba) y una tarjeta central entre salas (planificación, resultado, derrota). Dibuja un chip por sala (VS n, Muñecos, Minerales) con iconos. No decide reglas ni persiste nada: lee `BrawlRunDirector` y `BrawlTrialRoom` y reenvía los clicks.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento con el elemento `run-root` (Required) |
| `director` | `BrawlRunDirector` | Estado de la bajada (Required) |
| `trial` | `BrawlTrialRoom` | Cronómetro y daño de salas de prueba (opcional) |
| `combatIcon`, `dummiesIcon`, `mineralsIcon` | `Sprite` | Iconos de los chips; si falta, se usa la clase `run-room__icon--empty` |

## Elementos UXML (clases)

- Raíz y vistas: `run-root`, `run-strip`, `run-strip-rooms`, `run-strip-title`, `run-strip-trial`, `run-card`, `run-rooms`, `run-title`, `run-info`, `run-go`, `run-leave`.
- Chips: `run-room` (+ `--small`, `--done`, `--current`, `--upcoming`, `--vs0` a `--vs3`), `run-room__icons`, `run-room__icon`, `run-room__label`.

## Comportamiento por Estado

| Estado | Vista | Título | Botón principal | Botón salir |
|--------|-------|--------|-----------------|-------------|
| `Planning` | tarjeta | "Tramo N · K salas" | "Enfrentar tramo" | "Volver a la tienda" si tramo 1 y botín 0; si no, "Salir con X de botín" |
| `Fighting` | tira | "Tramo N · Sala i/K" + chips | oculto | oculto |
| `RoomResult` | tarjeta | `LastRoomSummary` | "Ver el próximo tramo" o "Siguiente sala" | oculto |
| `Over` | tarjeta | "Perdiste el combate" | oculto | "Volver a la tienda" |

- **Tira de prueba:** "Minerales: N s · daño X" o "Muñecos: N s". Solo reconstruye el texto cuando cambian segundos o daño.
- **Tarjeta:** "Botín: X" y una línea de salud por MoriMochi ("Nombre NN %").
- **Chips:** combate → `max(1, rivales)` iconos de combate y etiqueta "VS n"; muñecos y minerales → un icono y etiqueta propia.
- Oculto si no hay bajada activa o `Depth == 0`.

## Flujo

- `OnEnable` suscribe `director.Changed` y prueba el bind; `OnDisable` desuscribe.
- El bind es perezoso: `TryBind()` se reintenta hasta que el UXML está listo.
- `Update` refresca la tira de prueba cada frame (solo redibuja al cambiar).
- Botón principal → `AcceptTramo()` en `Planning` o `NextRoom()` en `RoomResult`. Botón salir → `Leave()`.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlRunDirector]] — `Changed`, `State`, `Run`, `Team`, `LastRoomSummary`, `AcceptTramo`, `NextRoom`, `Leave`
- [[BrawlRun]] — `Rooms`, `RoomIndex`, `Depth`, `Material`, `MaterialLost`, `Health01`
- [[BrawlRoom]], [[BrawlEnums.cs]] — `BrawlRoomKind`
- [[BrawlTrialRoom]] — `TimeLeft`, `Damage`, `Kind`, `Active`
- [[CreatureDNA]] — `CustomName`, `UniqueID`

## Notas

- Textos en español hardcodeados (no pasan por `Loc`), igual que `BrawlHud`.
- Las clases `run-room--vs0` se usan para salas no combate; los combates usan `vs1` a `vs3`.
