---
tags: [script, ui, expedition, builder, uitk]
---

# ExpeditionCardBuilder.cs

**Ruta:** `UI/ExpeditionCardBuilder.cs`

**Responsabilidad:** Builder estático de la presentación del panel de bajada: tile de cada candidato, carta de cada integrante del equipo, fila de equipo con sus slots vacíos aviso de falta de apoyo. Solo construye `VisualElement`; no guarda estado, no suscribe eventos y no escribe en `GameManager`. Lo llama `ExpeditionPanelUITK` en cada `Rebuild` y cada cambio de selección.

## Tipos Públicos

`Power` (readonly struct): `Theme` (`BrawlTheme`), `Role` (`BrawlSkillRole`), `Title`, `Locked`. Describe un poder de la carta.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `BuildTile(dna, ok, careGate)` | Tile de candidato con retrato, check y nombre. Si es apta (`ok`), estado listo; si no, estado ocupado o no listo y la barra de la necesidad más débil (`CreatureAvailability.WeakestNeed`). No apta: clase `exp-tile--off` |
| `BuildTeamCard(dna, profile)` | Carta de un integrante elegido: retrato, nombre, píldora de rol y sus tres poderes (ala, cuerno, espalda) |
| `BuildEmptySlot()` | Slot vacío de la carta de equipo (hint `ui.expedition.slot.empty`) |
| `FillTeam(team, dnas, profiles, order, maxPick)` | Limpia `team` y lo llena: título, contador `order.Count / maxPick`, una fila por elegido (`BuildTeamRow`) y filas vacías hasta `maxPick`. Si hay elegidos y ninguno tiene rol de apoyo, agrega aviso `ui.expedition.nosupport` |

Cambio S161: `BuildCard` pasó a `BuildTile`, y `FillTeam` recibe `order` y `maxPick` en lugar de la lista de elegidos.
Cambio S162: `FillTeam` recibe `dnas` (la lista completa de candidatos, indexada por `order`) y arma filas de equipo con retrato, nombre y píldora, más el aviso de apoyo.

## Métodos Privados Relevantes

- `BuildTeamRow(dna, profile)` / `BuildTeamEmptyRow()` (S162): fila de equipo (retrato, nombre, píldora) y fila vacía con runas.
- `PowerAt(profile, slot)` / `SkillPower(theme, skill)`: arma el `Power` de cada columna.
- `BuildBar(need, value)`: barra de la necesidad más débil con tooltip de `ui.expedition.needs.*`.

## Poderes

- Slot 0: ala, con rol `BrawlKitProfile.WingRole`.
- Slot 1: cuerno (`BrawlSkillSO`).
- Slot 2: espalda (`BrawlSkillSO`). Si `BackLocked`, es un poder bloqueado: ícono con "?" (`exp-power__lock`) y textos de `ui.power.locked.*`.
- Ícono: `Theme.Icon` como fondo o `Theme.Color` si no hay ícono. Clase `mm-role-ring--{rol}`.
- Parte sin kit: poder vacío con rol Offense.

## Conexiones

- [[ExpeditionPanelUITK]] — único consumidor
- [[BrawlKitProfile]] — rol, temas, kits y `BackLocked` de cada poder
- [[BrawlTheme]], [[BrawlSkillSO]], [[BrawlWingKitSO]] — iconos, colores, títulos
- [[BrawlRolePill]] — píldora de rol de cada integrante
- [[CreatureAvailability]], [[CareGateSO]] — aptitud y necesidad más débil
- [[NeedsDisplay]] — color y relleno de la barra
- [[MonchiPortraitUI]] — retrato de la tarjeta
- [[CreatureDNA]] — nombre, estado ocupado, necesidades
- [[Loc]] — textos `ui.expedition.*` y `ui.power.locked.*`

## Notas

- Estático y sin estado: cada llamada reemplaza el contenido del contenedor que recibe.
- Los nombres de los poderes salen de los SO de kit (`Title`, `Description`) pasando por `BrawlLoc.Title` (S162), no de `Loc` directo. La excepción es el poder bloqueado.
- S146: espalda bloqueada para formas no adultas, con el mismo criterio que la ficha y el HUD.
- S162: la bajada muestra el equipo como filas (no como cartas grandes) y avisa si el equipo no tiene apoyo.
