---
tags: [script, data, customer]
---

# CustomerPricingSO.cs

**Ruta:** `Data/Customers/CustomerPricingSO.cs`

**Responsabilidad:** SO que centraliza parámetros de valuación de MoriMochis. `BasePricePerTier` (dict Tier→int), multiplicadores (`BreedCountMultiplier`, `TierMultiplier`, `RarityBonusPerLevel`, `ShinyMultiplier`, rango de cuidado) y `RenegotiationStep`. Se edita inline en el inspector (`[InlineEditor]`). **S75:** Sin `CombatWinrateMultiplier` (demolición del combate). **S129:** Sin `StatsMultiplier`. **S149:** Agregados `RarityBonusPerLevel`, `ShinyMultiplier`, `CareMinMultiplier` y `CareMaxMultiplier`.

## Campos

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `BasePricePerTier` | `Dictionary<Tier, int>` (`[OdinSerialize]`) | Vacío | Precio base por tier. Se llena con el botón `Seed Defaults` |
| `BreedCountMultiplier` | float (≥ 0) | 2 | Multiplicador por cantidad de crianzas |
| `TierMultiplier` | float (≥ 0) | 5 | Multiplicador por tier |
| `RarityBonusPerLevel` | float (≥ 0) | 6 | **(S149)** Bono por nivel de rareza |
| `ShinyMultiplier` | float (≥ 1) | 1.5 | **(S149)** Multiplicador si la criatura es brillante |
| `CareMinMultiplier` | float (0-1) | 0.8 | **(S149)** Piso del multiplicador por cuidado (necesidades) |
| `CareMaxMultiplier` | float (≥ 1) | 1.2 | **(S149)** Techo del multiplicador por cuidado |
| `RenegotiationStep` | float (0-1) | 0,20 | Paso de renegociación |

## Botón Seed Defaults

Llena `BasePricePerTier` solo si está vacío: Tier1 = 20, Tier2 = 50, Tier3 = 120, Tier4 = 250. No sobrescribe valores existentes.

## Cambios

- **S75:** Eliminado `CombatWinrateMultiplier`
- **S129:** Eliminado `StatsMultiplier`
- **S149:** Agregados `RarityBonusPerLevel`, `ShinyMultiplier`, `CareMinMultiplier`, `CareMaxMultiplier`
- **MANTIENE:** BasePricePerTier, BreedCountMultiplier, TierMultiplier, RenegotiationStep

## Vinculado a

- [[Index/06 - Customer System]]

**Conexiones:** [[ValuationHandler]], [[CustomerArchetypeSO]], [[CreatureEnums]] (`Tier`)
