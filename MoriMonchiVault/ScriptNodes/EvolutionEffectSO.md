---
tags: [script, data, so, evolution, abstract]
---

# EvolutionEffectSO.cs

**Ruta:** `Data/Evolution/EvolutionEffectSO.cs`

**Responsabilidad:** Contrato abstracto de un efecto de evolución de partes. Es un `SerializedScriptableObject` (Odin) con nombre y descripción, y cinco métodos que cada implementación define: si puede aplicarse, cuánto cuesta, cuántas batallas exige, si una parte es candidata y cómo aplica el cambio. Solo decide reglas sobre el `CreatureDNA`: no cobra, no muestra nada y no persiste.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `DisplayName` | string | Nombre legible del efecto |
| `Description` | string | Texto del efecto (`[TextArea]`) |

## Contrato

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `CanApply(dna)` | bool | Puede aplicarse ahora: elegible, con candidata y con batallas suficientes |
| `Cost(dna)` | int | Minerita a cobrar |
| `RequiredBattles(dna)` | int | Batallas acumuladas exigidas |
| `IsCandidate(dna, role)` | bool | Si la parte `role` es la que subiría |
| `Apply(dna)` | `PartRole?` | Aplica el cambio y devuelve la parte afectada; `null` si no se pudo |

El cobro y el aviso de cambio no viven aquí: los hace `EvolutionService.Evolve`.

## Conexiones

- [[PartLevelUpEffectSO]] — implementación concreta (hoy la única)
- [[EvolutionService]] — llama `CanApply`, `Cost` y `Apply`
- [[DetailEvolutionBlock]] — llama `IsCandidate`, `Cost`, `RequiredBattles` y `CanApply` para la ficha
- [[DetailInfoTabPresenter]] — recibe el efecto en el constructor y lo pasa a `DetailEvolutionBlock`
- [[MorimonchiDetailInfoUITK]] — campo serializado `evolution`, asignado en el inspector
- [[CreatureDNA]] — dato sobre el que operan los métodos

## Notas

- Clase abstracta: una nueva variante hereda de aquí e implementa los cinco métodos.
