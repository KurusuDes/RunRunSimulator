---
tags: [data, genetics, serializable, timestamp]
---

# CreatureDNA.cs

**Ruta:** `Data/Genetics/CreatureDNA.cs`

**Responsabilidad:** Dato genética + estado MoriMochi. Guarda las partes elegidas, sus tiers de mejora (S148), los potenciales de cuerno, espalda y ala, las exploraciones y batallas acumuladas, el estado de vida (muerto, vendido, ocupado) y el estado de cría y ubicación. **S138:** `Stamp()` garantiza Timestamp estrictamente creciente vía static lastStamp.

## S148: Tiers de Partes

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `BodyTier` | `Tier` | Tier1 | Nivel de mejora del cuerpo |
| `HornTier` | `Tier` | Tier1 | Nivel de mejora del cuerno |
| `BackTier` | `Tier` | Tier1 | Nivel de mejora de la espalda |
| `WingTier` | `Tier` | Tier1 | Nivel de mejora del ala |

- `TierOf(role)` lee el tier de Body, Horn, Back o Wing. Cualquier otro rol devuelve Tier1.
- `SetTier(role, tier)` escribe el tier de esas cuatro partes. Otros roles no hacen nada.
- El tier se pasa como `level` a `BrawlUpgrades.Upgraded` y `BrawlUpgrades.Body` al armar el combatiente en `BrawlFighter.Bind`.
- Lo sube `PartLevelUpEffectSO` mediante `EvolutionService`.

## Batallas y Exploraciones

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Explorations` | int | Exploraciones acumuladas (evolución de etapa) |
| `Battles` | int | Combates de bajada acumulados. `ExpeditionBridge` suma `Combats` de cada run al equipo. Es el requisito de `PartLevelUpEffectSO` |

## Potenciales

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `HornPotential`, `BackPotential`, `WingPotential` | int | 1 | `CreatureGenerator` los genera entre 1 y 3. `BreedingService` los hereda promediando padres y madres (1 a 10) |

## Estado de Vida

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `IsDead` | bool | Muerte permanente |
| `Form` | `MonchiForm` | Adult por defecto; Egg o Slime según ciclo de vida |
| `BusyState` | `BusyReason` | `IsBusy` y `IsSold` se derivan de este campo |
| `Needs` | `NeedsState` | Salud, energía y afecto |

## Cría y Ubicación

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `BreedReadyAt` | long | Minuto total de juego (`GameClock.TotalMinutes`) en que la cría queda lista. 0 = no hay cría en curso. Lo compara `IncubationService.IsReady` |
| `BreedPartnerID` | string | ID de la pareja de la cría en curso |
| `BreedDecorIDs` | `List<string>` | Decoraciones (`BreedingDecorSO.Id`) de la cría en curso. Se convierten en `BreedingModifier` al eclosionar |
| `LocationKey`, `LocationSlot` | string, int | Dónde está físicamente la criatura (corral y slot de cría). `LocationSlot` = -1 si no tiene |
| `BirthDay`, `AgeDays(today)` | int | Día de nacimiento y edad calculada |

## S138: Strict Monotonic Timestamp

**Campos estáticos:**
```csharp
private static long lastStamp;
```

**Stamp():**
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
- [[CreatureGenerator]] — genera los potenciales iniciales
- [[ExpeditionBridge]] — suma `Battles` y `Explorations`
- [[PartLevelUpEffectSO]] — lee `Battles`, `TierOf` y `Form`; escribe el tier con `SetTier`
- [[BrawlUpgrades]], [[BrawlFighter]] — leen los tiers para armar el combatiente
- [[BreedingDecorSO]], [[BreedingOdds]], [[IncubationService]] — `BreedDecorIDs` alimenta los modificadores de herencia
- [[BreedingContainer]], [[DecorSlot]] — `LocationKey` y `LocationSlot` ubican a la criatura
