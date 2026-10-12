---
tags: [script, genetics]
---

# CreatureGenerator

**Ruta:** `Core/CreatureGenerator.cs`

**Responsabilidad:** Generador estático de criaturas aleatorias. Crea `CreatureDNA` con 5 partes aleatorias (Body/Horn/Back/Wing/Face), color base aleatorio, color secundario derivado, FurType aleatorio, IsShiny roll y potenciales de partes (1-3). **S129:** Eliminada generación de stats base (removidos de DNA). **S149:** La elección de partes filtra con `PartPool.Rollable`: Horn, Back y Wing solo salen si tienen malla en `MonchiVisualBankSO`.

## Constantes

| Constante | Valor | Propósito |
|-----------|-------|----------|
| `PotentialMin` | 1 | Mínimo potencial de parte |
| `PotentialMax` | 10 | Máximo potencial de parte |
| `MintPotentialMax` | 3 | Máximo al generar (1-3 range) |

## Métodos Públicos

| Método | Retorna | Propósito |
|--------|---------|----------|
| `GenerateRandom(database, furDb)` | `CreatureDNA` | Genera 5 partes aleatorias (filtradas por `PartPool.Rollable`), colores, FurType, IsShiny, potenciales (1-3 range) |
| `RandomRole()` | `Role` | Role aleatorio (1/3) |
| `RandomElement()` | `Element` | Element aleatorio (1/4) |
| `RandomDial()` | `float` | `Random.Range(0.15f, 0.85f)` para diales (Sociability, Boldness) |
| `RandomMintPotential()` | `int` | Potencial aleatorio [1, 3] |

## GenerateRandom

Genera 5 partes aleatorias, colores derivados, FurType (`furDb.RollMintFurType()` si hay base, si no aleatorio del enum), IsShiny roll y potenciales de partes (1-3).

**Campos mutados:**
- BodyShapeID, HornID, BackID, WingID, FaceID (aleatorios, rolleables)
- BaseColor, SecondaryColor (derivados)
- FurType, IsShiny
- HornPotential, BackPotential, WingPotential (1-3)

**No incluye:** Gender, Element, Role, diales, nombre y Timestamp. `GameManager.MintCreature` los asigna después de generar. Tampoco incluye stats base (S129).

**Parte sin entrada:** si una base queda vacía, el ID queda `""` y se loguea warning.

## Cambios S129

- **ELIMINADO:** `RandomBaseStats()` (stats base removidos de CreatureDNA)
- **ELIMINADO:** Generación de Constitution/Attack/Speed/Defense/Luck/Evasion
- **MANTIENE:** Generación de potenciales de partes (1-3 range para evolución HC)

## Cambios S149

- `Pick` usa `PartPool.Rollable` como filtro (`GetRandomPart(where: ...)`). Antes tomaba cualquier parte.

## Vinculado a

[[Index/02 - Genetics & Breeding]]
[[Index/28 - Cimientos y camino a Game Ready]]

**Conexiones:** [[CreatureDNA]], [[CreatureDatabaseSO]], [[GameManager]], [[ColorGenetics]], [[BreedingService]], [[PartPool]], [[MonchiVisualBankSO]]
