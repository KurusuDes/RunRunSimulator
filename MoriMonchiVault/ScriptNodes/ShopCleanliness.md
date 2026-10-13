---
tags: [script, systems, customers, cleanliness, static]
---

# ShopCleanliness.cs

**Ruta:** `Systems/Customers/ShopCleanliness.cs`

**Responsabilidad:** Calcula el multiplicador de limpieza de la tienda que afecta el precio que pagan los clientes. Static, sin estado. Suma suciedad de charcos (`Puddle.All`) y estaciones vacías (`StationSupply.All`) y la traduce a un multiplicador entre `DirtyMinMultiplier` y 1.

## Fórmula

- `dirt = Puddle.All.Count / MessForFullPenalty` + `emptyStations * EmptyStationPenalty`
- `Multiplier = 1 - (1 - DirtyMinMultiplier) * Clamp01(dirt)`
- `IsDirty` = `Multiplier < DirtyThoughtBelow` (dispara la queja del cliente)

## Metodos publicos

| Metodo | Retorno | Descripcion |
|--------|---------|-------------|
| `Multiplier(CustomerPricingSO pricing)` | `float` | Multiplicador de precio (1 = limpio) |
| `IsDirty(CustomerPricingSO pricing)` | `bool` | Si la tienda se ve sucia para el cliente |

## Conexiones

- [[CustomerPricingSO]] — parámetros (`MessForFullPenalty`, `EmptyStationPenalty`, `DirtyMinMultiplier`, `DirtyThoughtBelow`)
- [[Puddle]] — registro estático de charcos (lo llena [[MessEmitter]] con sus manchas, según el prefab)
- [[StationSupply]] — registro estático de estaciones con `IsEmpty`
- [[ValuationHandler]] — consume el multiplicador al tasar
- [[NpcAgent]] — guarda `ComplainedDirty` con `IsDirty` al elegir criatura; [[NpcThoughtTag]] y [[NpcDialogueBank]] lo usan para la queja
