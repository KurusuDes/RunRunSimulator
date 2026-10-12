---
tags: [script, ui, evolution, presenter]
---

# DetailEvolutionBlock.cs

**Ruta:** `UI/DetailEvolutionBlock.cs`

**Responsabilidad:** Construye los elementos UITK de evolución de la ficha: el bloque de cada parte (nivel con pips, escalones ya aplicados y próximo escalón o "al máximo") y la acción de evolución (resultado de la última evolución, XP de batallas y botón con costo). Clase plana, no `MonoBehaviour`, creada por `DetailInfoTabPresenter`. No cobra ni cambia datos: delega en `EvolutionService`.

**Vinculado a:** [[Index/05 - UI System]], [[Index/32 - Demo Brawl 3v3 arcade]]

## Métodos Públicos

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `DetailEvolutionBlock(kits, effect, registry, onChanged)` | — | Constructor. `registry` es una `Func` y `onChanged` una `Action` |
| `Build(dna, role, family)` | `VisualElement` | Bloque `part-evo` de una parte. Null si falta kit o efecto, si el DNA no es adulto o si la parte no tiene escalones |
| `BuildAction(dna)` | `VisualElement` | Bloque `evo-action`. Null si falta kit o efecto, o si el DNA es huevo |

`family` (`BrawlSkillFamily?`) solo se usa para el texto de `Count` en cuerno y espalda. Cuerpo y ala pasan null.

## Bloque por Parte (`Build`)

- Pips: `max − 1`, uno por escalón; se encienden los ya aplicados. Texto `ui.evo.level` con `Nivel X/Y`.
- Escalones ya aplicados (`ui.evo.done`), descritos con `BrawlUpgradeText.Describe`.
- Si el nivel es menor que el máximo y la parte es candidata: clase `part-evo--candidate` y próximo escalón (`ui.evo.next`).
- Si la parte está en el máximo: `ui.evo.max`.
- Clase `part-evo--fresh` si esta parte acaba de evolucionar en esta ficha.

## Acción (`BuildAction`)

- Forma no adulta (Slime): solo pista `ui.evo.needsadult`.
- Resultado de la última evolución de este MoriMochi (`ui.evo.result`), si existe.
- Sin candidatas: `ui.evo.allmax`.
- Con candidatas: XP (`dna.Battles` sobre `RequiredBattles`, `ui.evo.xp`), botón con el costo (`ui.evo.action`) habilitado si `CanApply` y saldo de Minerita mayor o igual al costo. Pista `ui.evo.needbattles` si faltan batallas o `ui.evo.action.hint` si no.

## Flujo al evolucionar (`Evolve`)

1. Llama `EvolutionService.Evolve(dna, effect, registry())`.
2. Si subió, toma el escalón recién aplicado (índice `tier − 2`) y guarda `resultId`, `resultRole` y `resultText`.
3. Llama `onChanged`. `DetailInfoTabPresenter` lo conecta a `Rebuild` de la ficha.

## Estado

| Campo | Descripción |
|-------|-------------|
| `resultId` | `UniqueID` del MoriMochi de la última evolución |
| `resultRole`, `resultText` | Parte y texto del escalón aplicado |

El resultado vive en la instancia del bloque, mientras viva el panel. No se persiste. `HasResult` lo compara con el `UniqueID` del DNA mostrado, así que solo aparece para ese MoriMochi.

## Conexiones

- [[EvolutionService]] — ejecuta la evolución
- [[EvolutionEffectSO]] — `IsCandidate`, `Cost`, `RequiredBattles`, `CanApply`
- [[BrawlKitDatabaseSO]] — escalones por parte (`Upgrades`) y familia de habilidad (`Skill`)
- [[BrawlUpgradeText]] — texto de cada escalón
- [[DetailInfoTabPresenter]] — crea el bloque y lo conecta a `Rebuild`
- [[CreatureDNA]] — `TierOf`, `Battles`, `Form`, `UniqueID`
- [[Wallet]] — saldo de Minerita para habilitar el botón
