---
tags: [script, data, brawl, run, glyph, scriptable-object]
---

# BrawlRoomGlyphsSO.cs

**Ruta:** `Data/Brawl/BrawlRoomGlyphsSO.cs`

**Responsabilidad:** ScriptableObject con los glifos de sala de la bajada Brawl, estilo Another Door: tres calaveras (una por número de rivales), muñecos y minerales. `For(room)` devuelve el sprite de una sala. Es data pura: sin estado, sin eventos y sin UI.

Menú de creación: `MoriMonchi/Brawl/Room Glyphs`.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `skull1`, `skull2`, `skull3` | `Sprite` | Calavera de combate con 1, 2 o 3+ rivales |
| `mineral` | `Sprite` | Sala de minerales |
| `heal` | `Sprite` | Sala de muñecos (curación) |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Sprite For(BrawlRoom room)` | `Dummies` → `heal`; `Minerals` → `mineral`; combate → calavera según `Mathf.Clamp(room.Rivals, 1, 3)` |

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlRoom]] — `Kind` y `Rivals` deciden el glifo
- [[BrawlEnums.cs]] — `BrawlRoomKind`
- [[BrawlRunPanel]] — glifo de cada chip de sala en la tarjeta
- [[BrawlRunVeil]] — glifo de la sala que viene, en el velo

## Notas

- Un combate con 0 rivales cae en la calavera 1. Las salas de prueba no usan calavera.
- Las clases de color (`run-glyph--foe`, `run-glyph--heal`, `run-glyph--mineral`) las aplican `BrawlRunPanel` y `BrawlRunVeil`, no este SO.
- S146: nuevo.
