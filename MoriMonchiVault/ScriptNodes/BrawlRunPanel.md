---
tags: [script, ui, brawl, run, uitk]
---

# BrawlRunPanel.cs

**Ruta:** `UI/BrawlRunPanel.cs`

**Responsabilidad:** Presentación UITK de la bajada Brawl. Muestra dos vistas sobre el mismo documento: una tira superior durante la pelea (tramo, sala, texto de la sala de prueba) y una tarjeta central entre salas (planificación, resultado, derrota). Dibuja un chip por sala (VS n, Muñecos, Minerales) con iconos. Expresa el botín en Minerita (botín × `BrawlRunRulesSO.MineritaPerLoot`). No decide reglas ni persiste nada: lee `BrawlRunDirector` y `BrawlTrialRoom` y reenvía los clicks.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento con el elemento `run-root` (Required) |
| `director` | `BrawlRunDirector` | Estado de la bajada (Required) |
| `trial` | `BrawlTrialRoom` | Estado de salas de prueba (opcional) |
| `combatIcon`, `dummiesIcon`, `mineralsIcon` | `Sprite` | Iconos de los chips; si falta, se usa la clase `run-room__icon--empty` |

## Elementos UXML (clases)

- Raíz y vistas: `run-root`, `run-strip`, `run-strip-rooms`, `run-strip-title`, `run-strip-trial`, `run-card`, `run-rooms`, `run-title`, `run-info`, `run-go`, `run-leave`.
- `run-minerita`: label creado en código e insertado antes de `run-info` (no está en el UXML).
- Chips: `run-room` (+ `--small`, `--done`, `--current`, `--upcoming`, `--vs0` a `--vs3`), `run-room__icons`, `run-room__icon`, `run-room__label`.

## Comportamiento por Estado

| Estado | Vista | Título | Botón principal | Botón salir |
|--------|-------|--------|-----------------|-------------|
| `Planning` | tarjeta | "Tramo N · K salas" | "Enfrentar tramo" | "Volver a la tienda" si tramo 1 y Minerita 0; si no, "Salir con X Minerita" |
| `Fighting` | tira | "Tramo N · Sala i/K" + chips | oculto | oculto |
| `RoomResult` | tarjeta | `LastRoomSummary` | "Ver el próximo tramo" o "Siguiente sala" | oculto |
| `Over` | tarjeta | "Perdiste el combate" | oculto | "Volver a la tienda" |

- **Tira de prueba:** "Muñecos · pegales para curar al equipo"; minerales sin empezar: "Minerales · pegale al cristal para empezar"; minerales en curso: "Minerales · +X Minerita". Solo reconstruye el texto cuando cambian si está activa, si empezó o el material. No muestra segundos (el cronómetro está en `BrawlHud`).
- **Tarjeta:** línea `run-minerita`: "Minerita: X" en `Planning` y `RoomResult`; en `Over`, "Se pierden X Minerita · te llevás Y" o "Sin botín que perder". Y una línea de salud por MoriMochi ("Nombre NN %") en `Planning` y `RoomResult`.
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
- [[BrawlRunRulesSO]] — `MineritaPerLoot` vía `Current`
- [[BrawlRoom]], [[BrawlEnums.cs]] — `BrawlRoomKind`
- [[BrawlTrialRoom]] — `Active`, `Started`, `Kind`, `Material`
- [[CreatureDNA]] — `CustomName`, `UniqueID`

## Notas

- Textos en español hardcodeados (no pasan por `Loc`), igual que `BrawlHud`.
- Las clases `run-room--vs0` se usan para salas no combate; los combates usan `vs1` a `vs3`.
- S145: el botín crudo (`Material`) ya no se muestra en la tarjeta; se muestra la Minerita equivalente.
