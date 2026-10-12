---
tags: [data, breeding, genetics, struct]
---

# BreedingModifier.cs

**Ruta:** `Data/Breeding/BreedingModifier.cs`

**Responsabilidad:** Tipos de dato para modificar la tirada de herencia. Define el enum `BreedingStat` (pesos de linaje, mutacion, base y sesgo materno/paterno) y el struct serializable `BreedingModifier` (Stat + Delta). Sin logica: la aplicacion vive en `BreedingOdds.From`.

## Tipos

| Tipo | Descripcion |
|------|-------------|
| `BreedingStat` | `ParentWeight`, `GrandparentWeight`, `GreatGrandparentWeight`, `MutationWeight`, `BaseWeight`, `MotherBias`, `FatherBias` |
| `BreedingModifier` | `Stat` (BreedingStat) + `Delta` (float, suma al peso base) |

**Conexiones:** [[BreedingOdds]], [[BreedingDecorSO]], [[IncubationService]], [[BreedingService]]
