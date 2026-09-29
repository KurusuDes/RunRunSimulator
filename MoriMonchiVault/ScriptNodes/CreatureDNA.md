---
tags: [data, genetics, serializable, timestamp]
---

# CreatureDNA.cs

**Ruta:** `Data/Genetics/CreatureDNA.cs`

**Responsabilidad:** Dato genética + estado MoriMochi. **S138:** `Stamp()` garantiza Timestamp estrictamente creciente vía static lastStamp.

## S138: Strict Monotonic Timestamp

**Campos estáticos:**
```csharp
private static long lastStamp;
```

**Stamp() — línea 82:**
```csharp
Timestamp = Math.Max(now.Ticks, lastStamp + 1);
lastStamp = Timestamp;
```

**Propósito:** Evita colisiones de UniqueID (que usa Timestamp). Si dos criaturas se crean en mismo tick, asegura Timestamp2 = Timestamp1 + 1.

**Garantía:** Timestamp siempre creciente, nunca igual (salvo races de CPU, que Math.Max previene).

## Ciclo de Vida (S137)

- **Egg:** Form=Egg, Explorations=0 (recién puesto por breeding)
- **Slime:** Form=Slime, Explorations=0 (eclosionado)
- **Adult:** Form=Adult, Explorations≥3 (evolucionado tras expediciones)

## UniqueID

```csharp
public string UniqueID => Timestamp > 0 ? $"{ToStringID()}-{Timestamp}" : "";
```

Immutable, determinístico por Timestamp monotónico.

## Conexiones

- [[CreatureRegistrySO]], [[BreedingService]], [[CreatureGrowth]], [[GameManager]]
