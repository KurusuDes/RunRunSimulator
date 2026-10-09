---
tags: [script, ui, presenter]
---

# DetailInfoTabPresenter.cs

**Ruta:** `UI/DetailInfoTabPresenter.cs`

**Responsabilidad:** Presenter UITK de la pestaña Info de la ficha de MoriMochi. Muestra las tres barras de necesidades (Health, Energy, Affect) con la más débil resaltada, el badge de apta para explorar, la identidad (género, estado, nacimiento), rol y elemento, el rol de combate sugerido (píldora de `BrawlKitProfile`), las cinco partes genéticas con el poder de su kit y el contador de crianzas. La espalda bloqueada (forma no adulta) se muestra como bloque "bloqueado" en lugar del poder. Es presentación pura: no escribe fuera de su root ni persiste.

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `database` | `CreatureDatabaseSO` | Acceso a las partes (cuerpo, cuerno, espalda, ala, cara) |
| `careGate` | `CareGateSO` | Umbral de necesidades para exploración |
| `kits` | `BrawlKitDatabaseSO` | Kits de combate por ID de parte |
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
| `DetailInfoTabPresenter(root, database, careGate, kits)` | Constructor: busca por nombre los elementos del tab (`need-*`, `explore-status`, `combat-role*`, `identity`, `role-element`, `parts`, `progression`) |
| `Rebuild(dna)` | Punto de entrada: actualiza todo el tab. Retorna si `dna` es null |
| `SetNeedBar(fill, need, value)` | Ancho y clase de color (`good`, `warn`, `crit`) de la barra |
| `SetNeedHighlight(row, highlight)` | Clase `detail-need--blocked` en la fila de la necesidad más débil |
| `SetCombatRole(profile)` | Título `ui.detail.combatrole.suggested` y píldora con `BrawlRolePill.Build`. Visible solo si hay `kits` |
| `BuildParts(dna, profile)` | Limpia el contenedor y agrega: Body (`AddPartRow`), Horn (`AddSkillRow`), Back (`AddSkillRow` con `BackLocked`), Wing (`AddWingRow`), Face (`AddPartRow`) |
| `AddPartRow(slot, part)` | Fila con swatch y texto de la parte, sin bloque de poder |
| `AddSkillRow(slot, part, skill, locked)` | Fila con el poder del `BrawlSkillSO`. Si `locked`, muestra el bloque bloqueado (`ui.power.locked.title` / `.desc`) sin anillo de rol |
| `AddWingRow(slot, part, wing)` | Fila con poder del ala; rol por `BrawlKitProfile.WingRole` |
| `AddPowerPartRow(...)` | Fila base: swatch, texto y, si hay rol o está bloqueada, bloque de poder (`part-power`; `part-power--locked` si aplica) |
| `BuildPartSwatch(part, ringRole)` | Swatch con anillo de rol (`mm-role-ring--…`), icono de parte o color del set |

## Textos de Fila de Parte

- Con parte: `ui.detail.partrow` con slot, nombre, set y rareza (`LocEnumMaps.RarityName`).
- Sin parte: `ui.detail.partrow.empty` con el slot.
- No hay tier ni potencial en este código: la fila muestra nombre, set y rareza.

## Vinculado a

- [[Index/05 - UI System]]
- [[Index/28 - Cimientos y camino a Game Ready]]
- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[MorimonchiDetailInfoUITK]] — crea el presenter en `Wire()` y llama `Rebuild`
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
