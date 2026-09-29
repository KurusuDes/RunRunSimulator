---
tags: [script, world, expedition, data-loading, utility]
---

# ArenaCastSource.cs

**Ruta:** `World/Expedition/ArenaCastSource.cs`

**Responsabilidad:** Utilidad estática: carga elenco local. **S138:** `AliveOrdered()` excluye Form==Egg.

## Métodos

- `LoadLocal()` — Carga save local, deserializa, filtra vivos
- `Pick(pool, count, seed)` — Fisher-Yates shuffle seeded

## S138: Egg Filter

**AliveOrdered() — línea 50:**
```csharp
if (dna != null && !dna.IsDead && dna.Form != MonchiForm.Egg) 
    result.Add(dna);
```

**Propósito:** Arena solo permite Slime/Adult. Huevos no pueden explorar (no son exploradores).

## Flujo

1. LoadLocal() → AliveOrdered() → lista de Slime/Adult vivos
2. Pick() → muestrea N con seed determinística

## Conexiones

- [[SaveSystem]], [[ArenaCastPlanner]], [[CreatureDNA]], [[RegistryData]]
