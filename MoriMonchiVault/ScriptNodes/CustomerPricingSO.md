---
tags: [script, data, customer]
---

# CustomerPricingSO.cs

**Ruta:** `Data/Customers/CustomerPricingSO.cs`

**Responsabilidad:** SO que centraliza parámetros de valuación de MoriMochis y de descuido de la tienda. `BasePricePerTier` (dict Tier→int), multiplicadores (`BreedCountMultiplier`, `TierMultiplier`, `RarityBonusPerLevel`, `ShinyMultiplier`, rango de cuidado), penalización por suciedad (**S151**) y `RenegotiationStep`. Se edita inline en el inspector (`[InlineEditor]`). **S75:** Sin `CombatWinrateMultiplier`. **S129:** Sin `StatsMultiplier`. **S149:** Agregados `RarityBonusPerLevel`, `ShinyMultiplier`, `CareMinMultiplier` y `CareMaxMultiplier`.

## Campos

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `BasePricePerTier` | `Dictionary<Tier, int>` (`[OdinSerialize]`) | Vacío | Precio base por tier. Se llena con el botón `Seed Defaults` |
| `BreedCountMultiplier` | float (≥ 0) | 2 | Multiplicador por cantidad de crianzas |
| `TierMultiplier` | float (≥ 0) | 5 | Multiplicador por tier |
| `RarityBonusPerLevel` | float (≥ 0) | 6 | Bono por nivel de rareza (S149) |
| `ShinyMultiplier` | float (≥ 1) | 1.5 | Multiplicador si la criatura es brillante (S149) |
| `CareMinMultiplier` | float (0-1) | 0.8 | Piso del multiplicador por cuidado (necesidades) (S149) |
| `CareMaxMultiplier` | float (≥ 1) | 1.2 | Techo del multiplicador por cuidado (S149) |
| `DirtyMinMultiplier` | float (0-1) | 0.75 | **(S151)** Multiplicador mínimo de la tienda sucia (`ShopCleanliness`) |
| `MessForFullPenalty` | float (≥ 1) | 12 | **(S151)** Cantidad de charcos que da penalización total |
| `EmptyStationPenalty` | float (0-1) | 0.15 | **(S151)** Suciedad que suma cada estación de suministro vacía |
| `DirtyThoughtBelow` | float (0-1) | 0.92 | **(S151)** Por debajo de este multiplicador el cliente piensa "está sucio" |
| `RenegotiationStep` | float (0-1) | 0.20 | Paso de renegociación |

## Botón Seed Defaults

Llena `BasePricePerTier` solo si está vacío: Tier1 = 20, Tier2 = 50, Tier3 = 120, Tier4 = 250. No sobrescribe valores existentes.

## Cambios

- **S75:** Eliminado `CombatWinrateMultiplier`
- **S129:** Eliminado `StatsMultiplier`
- **S149:** Agregados `RarityBonusPerLevel`, `ShinyMultiplier`, `CareMinMultiplier`, `CareMaxMultiplier`
- **S151:** Agregado bloque "Descuido de la tienda" (`DirtyMinMultiplier`, `MessForFullPenalty`, `EmptyStationPenalty`, `DirtyThoughtBelow`)
- **MANTIENE:** BasePricePerTier, BreedCountMultiplier, TierMultiplier, RenegotiationStep

## Vinculado a

- [[Index/06 - Customer System]]

**Conexiones:** [[ValuationHandler]], [[ShopCleanliness]] (S151), [[CustomerArchetypeSO]], [[CreatureEnums]] (`Tier`)
