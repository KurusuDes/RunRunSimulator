---
tags: [script, ui, brawl, run, veil, uitk]
---

# BrawlRunVeil.cs

**Ruta:** `UI/BrawlRunVeil.cs`

**Responsabilidad:** Velo entre salas de la bajada Brawl. Al entrar en `Transition` llena el velo con la sala que viene (glifo, "Sala N de M", pips del tramo y cuántas faltan) y reproduce `onShow`. Al salir de `Transition` reproduce `onHide`. No tiene temporizador: la duración la marca el director con `BrawlRunRulesSO.VeilCoverSeconds`. Presentación pura.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento con `run-root` (Required) |
| `director` | `BrawlRunDirector` | Estado de la bajada (Required) |
| `glyphs` | `BrawlRoomGlyphsSO` | Glifos de sala (Required) |
| `onShow` | `MMF_Player` | Feedback al entrar en `Transition` |
| `onHide` | `MMF_Player` | Feedback al salir de `Transition` |

## Elementos UXML

`run-root`, `run-veil-glyph`, `run-veil-title`, `run-veil-pips`, `run-veil-left`. `TryBind()` no valida estos cuatro hijos.

## Contenido del Velo

- **Glifo:** `glyphs.For(room)` de la sala actual, con clase `run-glyph--foe` (combate), `run-glyph--heal` (muñecos) o `run-glyph--mineral` (minerales).
- **Título:** "Sala N de M", con N = sala actual + 1 y M = salas del tramo.
- **Pips:** `done` (antes del índice), `current` e `upcoming`.
- **Restantes:** "Última sala del tramo" (ninguna después de la actual), "Queda 1 más" o "Quedan N más".

## Flujo

- `OnEnable`: guarda el estado actual del director como `previousState`, suscribe `director.Changed` y bindea.
- `HandleChanged`: compara `previousState` con el estado nuevo. Entrar en `Transition` → `Fill(run)` y `onShow`. Salir de `Transition` → `onHide`. `previousState` se actualiza siempre, aunque el bind no esté listo.
- `OnDisable`: desuscribe y `Unbind()` (limpia los pips).

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlRunDirector]] — `Changed`, `State`, `Run`, `Active`; `Transition` es el único estado que abre el velo
- [[BrawlRun]] — `CurrentRoom`, `RoomIndex`, `Rooms`
- [[BrawlRoomGlyphsSO]] — glifo de la sala
- [[BrawlRoom]], [[BrawlEnums.cs]] — `BrawlRoomKind`
- [[BrawlRunRulesSO]] — `VeilCoverSeconds`, lo lee el director
- [[BrawlRunHud]] — comparte el documento `run-root`
- [[MMF_Player]] — feedbacks de entrada y salida

## Notas

- El velo aparece entre salas de un tramo y al aceptar un tramo nuevo. Al terminar un tramo el director pasa a `Planning` sin `Transition`, así que no hay velo.
- S146: nuevo.
