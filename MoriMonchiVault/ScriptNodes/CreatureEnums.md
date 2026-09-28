---
tags: [enum, creature, core, expedition]
---

# CreatureEnums.cs

**Ruta:** `Core/Enums/CreatureEnums.cs`

**Responsabilidad:** Enumeraciones centrales de comportamiento, estado y forma de MoriMonchi. CreatureGender, LifeStage, MonchiMood, Tier, BusyReason, HatchResult, NeedType, CreatureCondition, CreatureIntent (30 valores), ProximityReaction, EmoteKind, SocialInteractionKind, MonchiForm (S135).

**S131:** Agregado HatchResult para flujo de cría local.
**S135:** Agregado MonchiForm para soportar Egg/Slime/Adult.

## Enumeraciones Principales

| Enum | Valores | Descripción |
|------|---------|-------------|
| `CreatureGender` | Unknown, Male, Female | Sexo de la criatura |
| `LifeStage` | Newborn, Child, Teen, Adult, Elder | Etapa de vida |
| `MonchiMood` | 12 valores (Neutral - KO) | Estado emocional/físico |
| `Tier` | Tier1, Tier2, Tier3 | Nivel de rareza/poder |
| `BusyReason` | None, Breeding, Sold | Razón de ocupación |
| `NeedType` | Health, Energy, Affect | Tipos de necesidad básica |
| `CreatureCondition` | Healthy, InNeed, Sick | Condición de salud |
| `HatchResult` | Hatched, NotReady, InsufficientMinerita, Invalid | Resultado de eclosión (S131) |
| `ProximityReaction` | Ignore, Flee, Approach, Follow, Retreat | Reacción a otros |
| `EmoteKind` | 6 valores (Curioso - Zzz) | Tipo de emote visual |
| `SocialInteractionKind` | PlayChase, SleepTogether, GremlinFight | Interacción social |
| `MonchiForm` | Adult (0), Egg (1), Slime (2) | Forma del MoriMochi (S135) |

## CreatureIntent (30 valores)

```
0:  Idle              5: Retreating     10: Playing       15: Chasing       20: Losing       25: Guarding
1:  Wandering         6: SeekingFood    11: Held          16: SleepTogether  21: Clashing      26: Hunting
2:  Following         7: SeekingRest    12: Tumbling      17: Fighting       22: Dazed         27: Taunting
3:  Approaching       8: SeekingPlay    13: Socializing   18: Collecting     23: Carrying      28: Exploring
4:  Fleeing           9: Eating         14: (reserved)    19: Taking         24: Securing      29: Reporting
```

### Cambios por Sesión

**S97-S103:** Collecting, Taking, Losing, Clashing, Dazed, Carrying, Securing, Guarding, Hunting, Taunting, Exploring, Reporting
**S103:** Exploring (28) = scout viajando; Reporting (29) = scout reportando veta

## MonchiForm (S135)

| Forma | Valor | Descripción | Mallas |
|-------|-------|-------------|--------|
| `Adult` | 0 | Forma adulta estándar | partMeshes |
| `Egg` | 1 | Forma de huevo (incubación) | eggPartMeshes |
| `Slime` | 2 | Forma de slime (alternativa) | slimePartMeshes |

**Uso:**
- `MonchiVisualBankSO.GetPartMesh(id, form)` → retorna prefab según forma
- Permite misma genética (DNA) con visuales distintos por ciclo de vida
- S135: Registración dinámica de formas via `MonchiPartRegistrar.RegisterAll()`

## HatchResult (S131)

```csharp
public enum HatchResult
{
    Hatched              = 0,
    NotReady             = 1,
    InsufficientMinerita = 2,
    Invalid              = 3,
}
```

| Resultado | Significado | Acción UI |
|-----------|-------------|-----------|
| **Hatched** | Eclosión exitosa | Animar hatching, mostrar criatura |
| **NotReady** | Incubación no finalizada | Toast + mostrar tiempo faltante |
| **InsufficientMinerita** | Cartera insuficiente | Toast + mostrar costo |
| **Invalid** | Estado corrupto | Toast error + log |

## MonchiMood (12 valores)

Neutral, Feliz, Triste, Dolor, Enojado, Dormido, Enfermo, Mareado, Asustado, Amoroso, Emocionado, KO

Usado por: `MonchiMoodDriver`, `MonchiVisualizer` (swap face materials), UI badges.

## Cambios S135

**MonchiForm agregado:**
```csharp
public enum MonchiForm
{
    Adult = 0,
    Egg   = 1,
    Slime = 2
}
```

Propósito: Diferenciar forma visual del MoriMochi para soporte de ciclos de vida e incubadora.

## Vinculado a

- [[Index/23 - Arena Sandbox & Expedicion (S102-S103)]]
- [[Index/02 - Genetics & Breeding]]

## Conexiones

[[MonchiVisualBankSO]], [[IncubationService]], [[MonchiMoodDriver]], [[MonchiPartRegistrar]], [[CreatureDNA]]
