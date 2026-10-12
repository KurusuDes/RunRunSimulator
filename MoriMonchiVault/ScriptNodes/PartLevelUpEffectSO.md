---
tags: [script, data, so, evolution, minerita]
---

# PartLevelUpEffectSO.cs

**Ruta:** `Data/Evolution/PartLevelUpEffectSO.cs`

**Responsabilidad:** Implementación de `EvolutionEffectSO` que sube de tier una parte del MoriMochi con Minerita. Candidatas: cuerpo, cuerno, espalda y ala; la cara no evoluciona. Sube solo las partes del tier más bajo que aún no llegaron al máximo de su kit. Si hay empate, elige una al azar.

**Asset:** `Create > MoriMonchi > Evolution > Part Level Up`

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `Kits` | `BrawlKitDatabaseSO` | — (`[Required]`) | Escalones de cada parte (`Upgrades`) |
| `CostPerLevel` | `List<int>` | `{30, 60, 100}` | Costo en Minerita según el tier de la candidata: subir desde tier 1 cuesta 30, desde 2 cuesta 60, desde 3 cuesta 100 |
| `BattlesPerEvolution` | `int` | 2 | Batallas por escalón de evolución |

## Reglas

| Regla | Cálculo |
|-------|---------|
| Elegible | `dna` no nulo, no muerto, no vendido, `Form == Adult` y `Kits` asignado |
| Candidatas | Partes con `TierOf(role) < MaxLevel(Kits.Upgrades(dna, role))`, filtradas al tier más bajo del conjunto |
| `CanApply` | Elegible, con candidatas y `dna.Battles >= RequiredBattles` |
| `RequiredBattles` | `BattlesPerEvolution × (suma de (tier − 1) de las 4 partes + 1)` |
| `Cost` | `CostPerLevel[clamp(tier de las candidatas − 1)]`; 0 si no hay candidatas |
| `Apply` | Elige una candidata al azar con `UnityEngine.Random`, `SetTier(role, tier + 1)` y devuelve la parte |

Ejemplo: con las 4 partes en tier 1 y `BattlesPerEvolution = 2`, la primera evolución exige 2 batallas. Después de una evolución (una parte en tier 2), la siguiente exige 4.

## Conexiones

- [[EvolutionEffectSO]] — clase base
- [[EvolutionService]] — llama `CanApply`, `Cost` y `Apply`
- [[DetailEvolutionBlock]] — llama `IsCandidate`, `Cost` y `RequiredBattles` para mostrar la ficha
- [[BrawlKitDatabaseSO]] — `Upgrades(dna, role)` entrega los escalones de cada parte
- [[BrawlUpgrades]] — `MaxLevel` define el tier máximo
- [[CreatureDNA]] — `TierOf`, `SetTier`, `Battles`, `Form`, `IsDead`, `IsSold`

## Notas

- `Kits` de este asset y `kits` de `MorimonchiDetailInfoUITK` (la ficha que muestra los escalones) son referencias separadas. Deben apuntar al mismo `BrawlKitDatabaseSO`; si difieren, la ficha puede mostrar un próximo escalón que el botón no puede aplicar.
- `Evolvable` y `Candidates` son estáticos. `FillCandidates` limpia la lista en cada llamada, así que `CanApply`, `IsCandidate`, `Cost` y `Apply` la recalculan y no dependen de estado previo.
- `Apply` usa `UnityEngine.Random` sin semilla: la parte elegida en un empate no es reproducible.
- El tier máximo depende de los escalones del kit: con 3 escalones llega a Tier4; una parte sin escalones nunca es candidata.
- Sin `Kits` asignado, `IsCandidate` da false en todas las partes y la ficha muestra "todas al máximo" en lugar de un error.
- `RequiredBattles` depende de la suma de tiers de las cuatro partes, no solo de la candidata.
