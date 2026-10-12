---
tags: [script, data, customer]
---

# CustomerArchetypeSO.cs

**Ruta:** `Data/Customers/CustomerArchetypeSO.cs`

**Responsabilidad:** Define un arquetipo NPC único (persona en la tienda). `DisplayName`, `Icon`, `AgentPrefab`. Pesos de preferencia: `WeightBreed`, `WeightTier` (afectan valuación). Presupuesto (`BudgetMultiplier`, `BudgetMin`, `BudgetMax`). **S149:** Gusto (`Taste`, `TasteBonus`, `BuyWithoutMatchChance`, `TasteFromDisplayChance`) que alimenta `CustomerTaste.Roll`. Negociación con `RenegotiationTolerance`. Comportamiento: `MinInspections`, `MaxInspections`, `InspectionDuration`, `WaitTimeoutSeconds`.

## Campos S149 (gusto y presupuesto)

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `Taste` | `TasteKind` | None | Tipo de gusto: Role, Color o PartSet. None = sin preferencia |
| `TasteBonus` | float (0-2) | 0.35 | Bonificación cuando la criatura cumple el gusto |
| `BuyWithoutMatchChance` | float (0-1) | 0.3 | Probabilidad de comprar aunque la criatura no cumpla el gusto |
| `TasteFromDisplayChance` | float (0-1) | 0.6 | Probabilidad de copiar el gusto de una criatura en exhibición en vez de tirarlo al azar |
| `BudgetMultiplier` | float (≥ 0) | 1 | Escala del presupuesto |
| `BudgetMin`, `BudgetMax` | int | 20, 80 | Rango de presupuesto |

## Pesos (Reemplazados en S75)

- **WeightBreed** — Preferencia por criados más veces
- **WeightTier** — Preferencia por tiers altos
- **SIN:** WeightCombat (demolición del combate), WeightStats (S129)

## Cambios

- **S75:** Eliminado `WeightCombat`
- **S129:** Eliminado `WeightStats`
- **S149:** Agregados gusto (`Taste*`) y presupuesto (`Budget*`). Consumidos por `CustomerTaste` y `NpcAgent`.

## Vinculado a

- [[Index/06 - Customer System]]

**Conexiones:** [[ValuationHandler]], [[CustomerPricingSO]], [[CustomerTaste]], [[NpcAgent]]
