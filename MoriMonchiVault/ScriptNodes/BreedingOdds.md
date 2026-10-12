---
tags: [data, breeding, genetics, odds, inheritance]
---

# BreedingOdds.cs

**Ruta:** `Data/Breeding/BreedingOdds.cs`

**Responsabilidad:** Pesos efectivos de una cria. Parte de `InheritanceOddsTableSO` y suma los `BreedingModifier` (decoraciones y otras fuentes). Todos los pesos se clampean a 0 o mas. Roll elige el origen de cada rasgo (padre, abuelo, bisabuelo, mutacion o base) y `PickMotherSide` decide el lado materno o paterno.

## Metodos Publicos

| Metodo | Retorna | Descripcion |
|--------|---------|-------------|
| `From(InheritanceOddsTableSO table, IEnumerable<BreedingModifier> mods)` | `BreedingOdds` | Construye pesos desde la tabla y aplica deltas. Null-safe en mods |
| `Roll()` | `InheritanceOddsTableSO.Slot` | Tirada ponderada. Si el total es 0 devuelve Parent |
| `PickMotherSide()` | `bool` | Lado materno ponderado por `MotherSide` / `FatherSide` |

## Campos Publicos

`Parent`, `Grandparent`, `GreatGrandparent`, `Mutation`, `Base`, `MotherSide` (default 1), `FatherSide` (default 1).

**Conexiones:** [[InheritanceOddsTableSO]], [[BreedingModifier]], [[BreedingService]] (`From` con mods), [[BreedingController]] (expone `InheritanceOdds`), [[BreedingDecorSO]]
