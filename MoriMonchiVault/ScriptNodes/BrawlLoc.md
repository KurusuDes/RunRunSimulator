---
tags: [script, systems, localization, brawl]
---

# BrawlLoc.cs

**Ruta:** `Systems/Localization/BrawlLoc.cs`

**Responsabilidad:** Utilidad estática que resuelve textos localizados de la demo Brawl. Si la clave no existe en `Loc`, usa el texto de respaldo del ScriptableObject (fallback). No guarda estado.

## Métodos Públicos

| Método | Retorna | Clave | Fallback |
|--------|---------|-------|----------|
| `Title(BrawlSkillSO s)` | `string` | `brawl.skill.{name}.title` | `s.Title` |
| `Description(BrawlSkillSO s)` | `string` | `brawl.skill.{name}.desc` | `s.Description` |
| `Title(BrawlWingKitSO w)` | `string` | `brawl.wing.{name}.title` | `w.Title` |
| `Description(BrawlWingKitSO w)` | `string` | `brawl.wing.{name}.desc` | `w.Description` |
| `Body(string bodyId, string fallback)` | `string` | `brawl.body.{bodyId}` | `fallback` |
| `Posture(string stance, string bond)` | `string` | `brawl.stance.{stance}` + `brawl.bond.{bond}` | (concatena con " · ") |

## Conexiones

**Entrada:** [[Loc]] (`Loc.Tr`), BrawlSkillSO, BrawlWingKitSO.

**Consumidores:** `BrawlOverheads` (título del skill en la burbuja de cast). Los HUD de Brawl leen textos de `Loc` directamente.

## Invariantes

- Clave que devuelve la misma cadena (no encontrada) → se usa el fallback.
- Argumento null → cadena vacía.
- Sin estado ni suscripciones.
