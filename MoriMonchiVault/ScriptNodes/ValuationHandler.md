---
tags: [script, system, customer]
---

# ValuationHandler.cs

**Ruta:** `Systems/Customers/ValuationHandler.cs`

**Responsabilidad:** Clase pura que calcula el precio de un MoriMochi. API: `Estimate(CreatureDNA, CustomerArchetypeSO, CustomerPricingSO, float tasteMatch = 0f)`. **S149:** Suma además rareza de partes, aplica multiplicador de brillo, multiplicador de cuidado según necesidades y bonificación de gusto. **S151:** aplica el multiplicador de limpieza de la tienda (`ShopCleanliness`) antes del gusto. **S75:** Sin term de combat winrate (demolición del combate). **S129:** Sin term de stats (eliminados de DNA).

## Factores de Precio

Orden de cálculo:

1. **Base por tier:** suma de `BasePricePerTier` de Body, Horn, Back y Wing.
2. **Breed count:** `BreedCount * WeightBreed * BreedCountMultiplier`.
3. **Tier bonus:** suma de tiers * `WeightTier * TierMultiplier`.
4. **Rarity (S149):** niveles de rareza de Horn, Back y Wing * `RarityBonusPerLevel`.
5. **Shiny (S149):** si `IsShiny`, objetivo * `ShinyMultiplier`.
6. **Cuidado (S149):** `Health + Energy + Affect` (0-100 cada uno) normalizado a 0-1, interpolado entre `CareMinMultiplier` y `CareMaxMultiplier`.
7. **Limpieza (S151):** objetivo * `ShopCleanliness.Multiplier(pricing)` (1 = tienda limpia; baja con charcos y estaciones vacías).
8. **Gusto (S149):** si hay arquetipo, objetivo * (1 + `TasteBonus` * `tasteMatch`).
9. **Presupuesto:** resultado * `BudgetMultiplier` del arquetipo, redondeado y sin negativos.

## Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `dna` | `CreatureDNA` | Criatura a valorar. Null devuelve 0 |
| `archetype` | `CustomerArchetypeSO` | Pesos y gusto. Null usa pesos 1 y sin gusto |
| `pricing` | `CustomerPricingSO` | Tablas y multiplicadores. Null devuelve 0 |
| `tasteMatch` | float (0-1) | **(S149)** Resultado de `CustomerTaste.Match`. Default 0 |

## Cambios Históricos

- **S75:** Eliminado término de combat winrate (demolición del combate)
- **S129:** Eliminado término de stats (Constitution, Attack, Speed, Defense, Luck, Evasion borrados de DNA)
- **S149:** Agregados rareza, brillo, cuidado, gusto y el parámetro `tasteMatch`. Rareza se lee del `BodyPartDatabase` de `GameManager.Database`.
- **S151:** Agregado multiplicador de limpieza de la tienda (`ShopCleanliness`).

## Vinculado a

[[Index/06 - Customer System]]
[[Index/28 - Cimientos y camino a Game Ready]]

**Conexiones:** [[CustomerPricingSO]], [[CustomerArchetypeSO]], [[CustomerTaste]], [[CreatureDNA]], [[NeedsState]], [[NpcAgent]], [[ShopCleanliness]] (S151)
