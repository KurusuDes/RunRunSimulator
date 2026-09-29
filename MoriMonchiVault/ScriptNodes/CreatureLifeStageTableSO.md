---
tags: [script, genetics]
---

# CreatureLifeStageTableSO.cs

**Ruta:** `Data/Breeding/CreatureLifeStageTableSO.cs`

**Responsabilidad:** ScriptableObject que mapea edad en días (`AgeDays`) a etapa de vida visible (`LifeStage`). `GetStage(ageDays)` devuelve la etapa más alta cuyo threshold se haya alcanzado. `Label(stage)` retorna string localizado (S68: ahora via `LocEnumMaps.LifeStageName(stage)`). Expone `ExplorationsToEvolve` **(S137 NUEVO)** — threshold de exploraciones para que slime evolucione a Adult. Display-only — nunca parte del string genético. Referenciado por `BreedingController` (único owner), leído por `NameTag` via `BreedingController.Instance.LifeStageTable`, consultado por `ExpeditionBridge` (S137).

## Cambios S137

**Nuevo campo y propiedad:**
```csharp
[Title("Evolution")]
[MinValue(1)]
[SerializeField]
private int explorationsToEvolve = 3;

public int ExplorationsToEvolve => explorationsToEvolve;
```

**Propósito:** Threshold de exploraciones (expediciones completadas como slime) para evolucionar a Adult. Default 3.

**Consumidor:** `ExpeditionBridge.ApplyResult()` consulta `BreedingController.Instance.LifeStageTable.ExplorationsToEvolve` para determinar cuándo un slime evoluciona (S137).

## Datos

- Dictionary `entryDayThreshold` — mapea `LifeStage` → edad (días) en que se entra en esa etapa
- Default: Newborn (0d), Child (1d), Teen (3d), Adult (7d), Elder (20d)
- Botón `SeedDefaults()` reestablece valores default (Odin, solo editor)
- **S137 NUEVO:** `explorationsToEvolve` (default 3) — exploraciones para Slime → Adult

## Métodos públicos

- `GetStage(int ageDays) → LifeStage` — devuelve la LifeStage más alta alcanzada (búsqueda lineal por threshold)
- `Label(LifeStage stage) → string` — traduce etapa a string localizado (S68)
- **S137 NUEVO:** `ExplorationsToEvolve` → propiedad getter (int)

## Ciclo de Vida S137

**Age-based staging (LifeStage):**
- Newborn (0d), Child (1d), Teen (3d), Adult (7d), Elder (20d)
- Independiente de Form (Egg/Slime/Adult)
- Usado por UI: NameTag muestra "Newborn Egg", "Child Slime", "Elder Adult", etc.

**Exploration-based evolution (MonchiForm):**
- Slime con Explorations < threshold: no evoluciona
- Slime con Explorations >= threshold: Form → Adult (vía CreatureGrowth.RecordExploration)
- ExpeditionBridge consulta `ExplorationsToEvolve` para decidir evolución

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/09 - Active Context]] (S137: ciclo de vida, threshold)
- [[Index/14 - Localization]]

## Conexiones

- [[BreedingController]] (propietario, getter)
- [[NameTag]] (LifeStage para edad visual)
- [[LocEnumMaps]], [[Loc]] (localización de etapa)
- [[ExpeditionBridge]] (S137: ExplorationsToEvolve)
- [[CreatureGrowth]] (S137: RecordExploration usa threshold)
- Enums (`Core/Enums/`, S93) (LifeStage)
