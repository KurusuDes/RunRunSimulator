---
tags: [script, ui, presenter]
---

# DetailInfoTabPresenter.cs

**Ruta:** `UI/DetailInfoTabPresenter.cs`

**Responsabilidad:** Presenter UITK de la pestaña Info de la ficha de MoriMochi. Muestra las tres barras de necesidades (Health, Energy, Affect) con su porcentaje y la más débil resaltada, el badge de apta para explorar, el subtítulo (género · rol · elemento), el bloque de datos (estado, nacimiento, crianzas, batallas), el bloque de personalidad (nombre y descripción del rol), el rol de combate sugerido (píldora de `BrawlKitProfile`), las ranuras visuales de partes (izquierda: cuerno, espalda, ala; derecha: cara, cuerpo), y la lista de partes con el poder de su kit y el bloque de evolución de cada parte (vía `DetailEvolutionBlock`). La espalda bloqueada (forma no adulta) se muestra como bloque "bloqueado" en lugar del poder y sin evolución. Es presentación: no persiste. El cambio de tier pasa por `EvolutionService`.

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `database` | `CreatureDatabaseSO` | Acceso a las partes (cuerpo, cuerno, espalda, ala, cara) |
| `careGate` | `CareGateSO` | Umbral de necesidades para exploración |
| `kits` | `BrawlKitDatabaseSO` | Kits de combate por ID de parte |
| `evolutionBlock` | `DetailEvolutionBlock` | Bloques de evolución por parte y acción de evolución (S148) |
| `lastDna` | `CreatureDNA` | Último DNA renderizado; se usa como callback al terminar una evolución |
| `needHealthFill`, `needEnergyFill`, `needAffectFill` | `VisualElement` | Barras de relleno |
| `needHealthRow`, `needEnergyRow`, `needAffectRow` | `VisualElement` | Filas, para resaltar la necesidad más débil |
| `needHealthValue`, `needEnergyValue`, `needAffectValue` | `Label` | Porcentaje de cada necesidad (S160) |
| `exploreStatus` | `Label` | Badge "Apta" o "Bloqueada" |
| `subtitle` | `Label` | Género · rol · elemento (S160; reemplaza `identityLabel` y `roleElementLabel`) |
| `statState`, `statBorn`, `statBreeds`, `statBattles` | `Label` | Estado, nacimiento, crianzas (`BreedCount`) y batallas (`Battles`) (S160) |
| `personalityName`, `personalityDesc` | `Label` | Nombre del rol y su descripción (S160) |
| `combatRole`, `combatRoleTitle`, `combatRolePill` | `VisualElement`, `Label`, `VisualElement` | Bloque de rol de combate sugerido |
| `slotsLeft`, `slotsRight` | `VisualElement` | Ranuras visuales de partes: izquierda cuerno/espalda/ala, derecha cara/cuerpo (S160) |
| `partsContainer` | `VisualElement` | Contenedor dinámico de filas de partes |

Ya no existen `identityLabel`, `roleElementLabel` ni `progressionLabel` (S160).

## Métodos

| Método | Descripción |
|--------|-------------|
| `DetailInfoTabPresenter(root, database, careGate, kits, evolution, registry)` | Constructor: busca por nombre `need-*`, `need-*-fill`, `need-*-value`, `explore-status`, `combat-role*`, `subtitle`, `stat-*-value` (state, born, breeds, battles), `personality-name`, `personality-desc`, `slots-left`, `slots-right` y `parts`. Crea `DetailEvolutionBlock` con `Rebuild(lastDna)` como callback de cambio |
| `Rebuild(dna)` | Punto de entrada: guarda `lastDna` y actualiza todo el tab. Retorna si `dna` es null |
| `SetNeedBar(fill, valueLabel, need, value)` | Porcentaje en el label, ancho del relleno y clase de color (`exp-bar--good`, `--warn`, `--crit`) |
| `SetNeedHighlight(row, highlight)` | Clase `detail-need--blocked` en la fila de la necesidad más débil |
| `SetCombatRole(profile)` | Título `ui.detail.combatrole.suggested` y píldora con `BrawlRolePill.Build`. Visible solo si hay `kits` |
| `BuildSlots(dna)` | Limpia `slotsLeft` y `slotsRight`. Izquierda: Horn, Back, Wing. Derecha: Face, Body |
| `BuildSlot(slot, part)` | Ranura: caja `mm-slot detail-slot__box` con viñeta y marco (`mm-layer`), icono (`part.Icon` con clase `part-icon--horn/back/wing`, o color del set si no hay icono), etiqueta con el nombre del slot y nombre de la parte (`DataLoc.PartName`, o "—") |
| `BuildParts(dna, profile)` | Limpia el contenedor. Agrega primero la acción de evolución (si existe) y luego las filas: Body, Horn, Back (bloqueada si `BackLocked`, sin evolución) y Wing. La cara ya no tiene fila: vive en `BuildSlots` |
| `AddPartRow(slot, part, evolution)` | Fila con swatch y texto de la parte, sin bloque de poder. Si hay `evolution`, lo agrega junto al texto |
| `AddSkillRow(slot, part, skill, locked, evolution)` | Fila con el poder del `BrawlSkillSO`. Si `locked`, muestra el bloque bloqueado (`ui.power.locked.title` / `.desc`) sin anillo de rol |
| `AddWingRow(slot, part, wing, evolution)` | Fila con poder del ala; rol por `BrawlKitProfile.WingRole` |
| `AddPowerPartRow(..., evolution)` | Fila base: swatch, texto y, si hay rol o está bloqueada, bloque de poder (`part-power`; `part-power--locked` si aplica). Al final agrega el bloque de evolución si existe |
| `PartText(slot, part)` | Texto de fila: `Slot · Nombre` (nombre por `DataLoc.PartName`), o solo el slot si no hay parte |
| `BuildPartSwatch(part, ringRole)` | Swatch con anillo de rol (`mm-role-ring--…`), icono de parte o color del set |
| `SlotName(PartRole)` | Nombre localizado del slot (`ui.detail.slot.body/horn/back/wing/face`) |
| `RoleDesc(Role)` | Descripción localizada del rol (`ui.detail.roledesc.*`) |
| `Born(dna)` | Fecha de nacimiento en `dd/MM/yy` (hora local), o "—" si `BirthDate` es default |

## Textos de Fila de Parte

- Con parte: `Slot · Nombre` (vía `PartText`). El set se muestra con el color del swatch, no con texto.
- Sin parte: solo el nombre del slot.
- La fila no muestra tier ni rareza. El nivel de mejora aparece en el bloque de evolución de cada parte (pips y `Nivel X/Y`, vía `DetailEvolutionBlock`).

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
- [[CreatureDatabaseSO]], [[BodyPart]] — partes, sets, iconos
- [[DataLoc]] — nombres localizados de partes (S162)
- [[CreatureDNA]] — necesidades, género, rol, elemento, `BirthDate`, `BreedCount`, `Battles`, `Form`
- [[NeedsDisplay]] — color y relleno de barras
- [[CreatureAvailability]], [[CareGateSO]] — apta y necesidad más débil
- [[CreatureDisplay]] — `StateOf`
- [[LocEnumMaps]] — nombres de género, rol y elemento

## Notas

- El poder de cada parte sale del kit (`BrawlKitProfile`), no de un campo de la parte.
- Si no hay `careGate`, no se resalta ninguna necesidad ni se marca apta.
- S146: espalda bloqueada para formas no adultas. La fila muestra el bloque bloqueado en lugar del poder de la espalda.
- S148: cada parte adulta puede mostrar su bloque de evolución y la acción de evolución va arriba de las partes. Sin `evolution` asignado en `MorimonchiDetailInfoUITK`, ambos quedan ocultos.
- S160: rediseño de la ficha con el kit v2 de UI. Se eliminaron los labels `identity`, `role-element` y `progression`; se agregaron subtítulo, bloque de datos, bloque de personalidad y ranuras de partes. La cara sale de la lista de filas y pasa a `slots-right`. `PartLine` fue reemplazado por `PartText`. Las barras muestran porcentaje.
- S162: nombres de partes en ranuras y filas por `DataLoc.PartName` (loc de datos). Sin cambios en la estructura de la ficha.
