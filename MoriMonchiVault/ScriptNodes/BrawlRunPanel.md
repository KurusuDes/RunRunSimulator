---
tags: [script, ui, brawl, run, uitk]
---

# BrawlRunPanel.cs

**Ruta:** `UI/BrawlRunPanel.cs`

**Responsabilidad:** Tarjeta central de la bajada Brawl (UITK), con dos vistas: planificación del tramo (`Planning`) y derrota (`Over`). Dibuja un chip por sala con el glifo de `BrawlRoomGlyphsSO`, la salud de cada MoriMochi y el botín expresado en Minerita (botín × `BrawlRunRulesSO.MineritaPerLoot`). No decide reglas ni persiste nada: lee `BrawlRunDirector` y reenvía los clicks. La pelea y el velo entre salas salieron a `BrawlRunHud` y `BrawlRunVeil` en S146.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento con el elemento `run-root` (Required) |
| `director` | `BrawlRunDirector` | Estado de la bajada (Required) |
| `glyphs` | `BrawlRoomGlyphsSO` | Glifos de los chips (Required; sin él no bindea) |

## Elementos UXML

`run-root`, `run-card-wrap`, `run-rooms`, `run-title`, `run-info`, `run-go`, `run-leave`. El label `run-minerita` se crea en código y se inserta antes de `run-info`.

## Comportamiento por Estado

La tarjeta solo se muestra si hay bajada activa, `Depth > 0` y el estado es `Planning` u `Over`. En `Fighting`, `RoomResult` y `Transition` queda oculta.

| Estado | Título | Línea Minerita | Línea de salud | Botón principal | Botón salir |
|--------|--------|----------------|----------------|-----------------|-------------|
| `Planning` | "Tramo N · K salas" | "Minerita: X" | Nombre y % de vida por MoriMochi | "Enfrentar tramo" | "Volver a la tienda" si es tramo 1 y Minerita 0; si no, "Salir con X Minerita" |
| `Over` | "Perdiste el combate" | "Se pierden X Minerita · te llevas Y" o "Sin botín que perder" | oculta | oculto | "Volver a la tienda" |

- **Chips:** uno por sala. Clase `run-room--done` (antes del índice), `--current` o `--upcoming`. El glifo (`run-room__glyph`) usa `glyphs.For(room)` y la clase `run-glyph--foe` (combate), `run-glyph--heal` (muñecos) o `run-glyph--mineral` (minerales).

## Flujo

- `OnEnable` suscribe `director.Changed` y prueba el bind; `OnDisable` desuscribe y limpia los chips.
- El bind es perezoso: `TryBind()` se reintenta hasta que el UXML y `glyphs` están listos.
- No tiene `Update`: solo redibuja cuando el director dispara `Changed`.
- Botón principal → `AcceptTramo()`, solo si el estado es `Planning`. Botón salir → `Leave()` (válido en `Planning` y `Over`).

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlRunDirector]] — `Changed`, `State`, `Run`, `Team`, `AcceptTramo`, `Leave`
- [[BrawlRun]] — `Rooms`, `RoomIndex`, `Depth`, `Material`, `MaterialLost`, `Health01`
- [[BrawlRunRulesSO]] — `MineritaPerLoot` vía `Current`
- [[BrawlRoomGlyphsSO]] — glifo de cada chip
- [[BrawlRoom]], [[BrawlEnums.cs]] — `BrawlRoomKind`
- [[BrawlRunHud]] y [[BrawlRunVeil]] — vistas de pelea y velo sobre el mismo `run-root`
- [[CreatureDNA]] — `CustomName`, `UniqueID`

## Notas

- Textos en español hardcodeados (no pasan por `Loc`), igual que `BrawlHud` y `BrawlRunHud`.
- S146: ya no tiene `trial`, ni iconos por tipo (`combatIcon`, `dummiesIcon`, `mineralsIcon`), ni muestra el estado `RoomResult`. El avance a la siguiente sala es automático.
