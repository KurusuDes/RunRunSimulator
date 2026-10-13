---
tags: [script, core, creatures, breeding, static]
---

# CreatureFrailty.cs

**Ruta:** `Core/CreatureFrailty.cs`

**Responsabilidad:** Regla pura de fragilidad de una criatura. Static, sin estado. Decide si un MoriMochi es "frágil" (salud en 0 o etapa Elder según la tabla de vida) y expone la penalización `Penalty` = 0.5 que aplica la crianza a esas criaturas. No persiste, no emite eventos.

## Campos publicos

| Campo | Valor | Descripcion |
|-------|-------|-------------|
| `Penalty` | 0.5f (const) | Factor de penalización para criaturas frágiles |

## Metodos publicos

| Metodo | Retorno | Descripcion |
|--------|---------|-------------|
| `IsFrail(CreatureDNA dna)` | `bool` | `true` si `dna.Needs.Health <= 0` o si la etapa de vida por edad (`GameClock.Instance.Day`) es `LifeStage.Elder` según `BreedingController.Instance.LifeStageTable` |

## Conexiones

- [[CreatureDNA]] — lee `Needs.Health` y `AgeDays(day)`
- [[BreedingController]] — provee `LifeStageTable`
- [[GameClock]] — provee el día actual
- [[NeedsState]] — fuente de la salud
