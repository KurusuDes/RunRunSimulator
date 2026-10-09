---
tags: [script, data, brawl, run, struct]
---

# BrawlRoom.cs

**Ruta:** `Data/Brawl/BrawlRoom.cs`

**Responsabilidad:** Struct de una sala de la bajada Brawl: tipo (`BrawlRoomKind`) y cantidad de rivales. Solo data, sin comportamiento.

## Estructura

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Kind` | `BrawlRoomKind` | Combate, Muñecos o Minerales |
| `Rivals` | `int` | Rivales de la sala de combate (0 en salas de prueba) |

## Uso

- Generada por `BrawlRun.PlanNextTramo()`.
- Leída por `BrawlRunDirector` (al entrar y al resolver la sala) y `BrawlRunPanel` (un chip por sala).

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlRun]] — construye la lista de salas del tramo
- [[BrawlRunDirector]] — consume la sala actual
- [[BrawlRunPanel]] — dibuja un chip por sala
- [[BrawlEnums.cs]] — `BrawlRoomKind`

## Notas

- Struct sin lógica: el tipo de sala decide si el director usa rivales IA o muñecos con `BrawlTrialRoom`.
