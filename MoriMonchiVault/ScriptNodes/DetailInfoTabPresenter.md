---
tags: [script, ui, presenter]
---

# DetailInfoTabPresenter.cs

**Ruta:** `UI/DetailInfoTabPresenter.cs`

**Responsabilidad:** Presenter UITK de la pestaña Info de la ficha de MoriMochi. Muestra las tres barras de necesidades (Health, Energy, Affect) con la más débil resaltada, el badge de apta para explorar, la identidad (género, estado, nacimiento), rol y elemento, el rol de combate sugerido (píldora de `BrawlKitProfile`), las cinco partes genéticas con el poder de su kit, el bloque de evolución de cada parte (vía `DetailEvolutionBlock`) y el contador de crianzas. La espalda bloqueada (forma no adulta) se muestra como bloque "bloqueado" en lugar del poder y sin evolución. Es presentación: no persiste. El cambio de tier pasa por `EvolutionService`.

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `database` | `CreatureDatabaseSO` | Acceso a las partes (cuerpo, cuerno, espalda, ala, cara) |
| `careGate` | `CareGateSO` | Umbral de necesidades para exploración |
| `kits` | `BrawlKitDatabaseSO` | Kits de combate por ID de parte |
| `evolutionBlock` | `DetailEvolutionBlock` | Bloques de evolución por parte y acción de evolución (S148) |
| `needHealthFill`, `needEnergyFill`, `needAffectFill` | `VisualElement` | Barras de relleno |
| `needHealthRow`, `needEnergyRow`, `needAffectRow` | `VisualElement` | Filas, para resaltar la necesidad más débil |
| `exploreStatus` | `Label` | Badge "Apta" o "Bloqueada" |
| `identityLabel` | `Label` | Género, estado y nacimiento |
| `roleElementLabel` | `Label` | Rol + elemento + descripción del rol |
| `combatRole`, `combatRoleTitle`, `combatRolePill` | `VisualElement`, `Label`, `VisualElement` | Bloque de rol de combate sugerido |
| `partsContainer` | `VisualElement` | Contenedor dinámico de filas de partes |
| `progressionLabel` | `Label` | Contador de crianzas (`BreedCount`) |

## Métodos

| Método | Descripción |
|--------|-------------|
| `DetailInfoTabPresenter(root, database, careGate, kits, evolution, registry)` | Constructor: busca por nombre los elementos del tab (`need-*`, `explore-status`, `combat-role*`, `identity`, `role-element`, `parts`, `progression`) y crea `DetailEvolutionBlock` con `Rebuild(lastDna)` como callback de cambio |
| `Rebuild(dna)` | Punto de entrada: actualiza todo el tab. Retorna si `dna` es null |
| `SetNeedBar(fill, need, value)` | Ancho y clase de color (`good`, `warn`, `crit`) de la barra |
| `SetNeedHighlight(row, highlight)` | Clase `detail-need--blocked` en la fila de la necesidad más débil |
| `SetCombatRole(profile)` | Título `ui.detail.combatrole.suggested` y píldora con `BrawlRolePill.Build`. Visible solo si hay `kits` |
| `BuildParts(dna, profile)` | Limpia el contenedor. Agrega primero la acción de evolución (si existe) y luego las filas: Body, Horn, Back (bloqueada si `BackLocked`, sin evolución), Wing y Face (sin evolución) |
| `AddPartRow(slot, part, evolution)` | Fila con swatch y texto de la parte, sin bloque de poder. Si hay `evolution`, lo agrega junto al texto |
| `AddSkillRow(slot, part, skill, locked, evolution)` | Fila con el poder del `BrawlSkillSO`. Si `locked`, muestra el bloque bloqueado (`ui.power.locked.title` / `.desc`) sin anillo de rol |
| `AddWingRow(slot, part, wing, evolution)` | Fila con poder del ala; rol por `BrawlKitProfile.WingRole` |
| `AddPowerPartRow(..., evolution)` | Fila base: swatch, texto y, si hay rol o está bloqueada, bloque de poder (`part-power`; `part-power--locked` si aplica). Al final agrega el bloque de evolución si existe |
| `BuildPartSwatch(part, ringRole)` | Swatch con anillo de rol (`mm-role-ring--…`), icono de parte o color del set |

## Textos de Fila de Parte

- Con parte: `ui.detail.partrow` con slot, nombre, set y rareza (`LocEnumMaps.RarityName`).
- Sin parte: `ui.detail.partrow.empty` con el slot.
- La fila no muestra tier. El nivel de mejora aparece en el bloque de evolución de cada parte (pips y `Nivel X/Y`, vía `DetailEvolutionBlock`).

## Vinculado a

- [[Index/05 - UI System]]
- [[Index/28 - Cimientos y camino a Game Ready]]
- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[MorimonchiDetailInfoUITK]] — crea el presenter en `Wire()` y llama `Rebuild`
- [[DetailEvolutionBlock]] — bloques de evolución por parte y acción de evolución
- [[EvolutionEffectSO]] — efecto recibido en el constructor
- [[BrawlKitProfile]] — rol sugerido, poderes, temas y `BackLocked` por parte
- [[BrawlRolePill]] — píldora del rol sugerido
- [[BrawlKitDatabaseSO]] — kits por ID (para el perfil)
- [[CreatureDatabaseSO]], [[BodyPart]] — partes, sets, rareza
- [[CreatureDNA]] — necesidades, género, rol, elemento, `BirthDate`, `BreedCount`, `Form`
- [[NeedsDisplay]] — color y relleno de barras
- [[CreatureAvailability]], [[CareGateSO]] — apta y necesidad más débil
- [[CreatureDisplay]] — `StateOf`
- [[LocEnumMaps]] — nombres de género, rol, elemento y rareza

## Notas

- El poder de cada parte sale del kit (`BrawlKitProfile`), no de un campo de la parte.
- Si no hay `careGate`, no se resalta ninguna necesidad ni se marca apta.
- S146: espalda bloqueada para formas no adultas. La fila muestra el bloque bloqueado en lugar del poder de la espalda.
- S148: cada parte adulta puede mostrar su bloque de evolución y la acción de evolución va arriba de las partes. Sin `evolution` asignado en `MorimonchiDetailInfoUITK`, ambos quedan ocultos.
