---
tags: [script, ui, expedition, builder, uitk]
---

# ExpeditionCardBuilder.cs

**Ruta:** `UI/ExpeditionCardBuilder.cs`

**Responsabilidad:** Builder estático de la presentación del panel de bajada: tile de cada candidato, carta de cada integrante del equipo y slot vacío. Solo construye `VisualElement`; no guarda estado, no suscribe eventos y no escribe en `GameManager`. Lo llama `ExpeditionPanelUITK` en cada `Rebuild` y cada cambio de selección.

## Tipos Públicos

`Power` (readonly struct): `Theme` (`BrawlTheme`), `Role` (`BrawlSkillRole`), `Title`, `Locked`. Describe un poder de la carta.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `BuildTile(dna, ok, careGate)` | Tile de candidato. Si es apta (`ok`), muestra estado listo; si no, estado ocupado o no listo y la barra de la necesidad más débil (`CreatureAvailability.WeakestNeed`). No apta: clase `exp-card--off` |
| `BuildTeamCard(dna, profile)` | Carta de un integrante elegido con sus poderes (ala, cuerno, espalda) |
| `BuildEmptySlot()` | Slot vacío de la fila de equipo |
| `FillTeam(team, profiles, order, maxPick)` | Llena la fila de equipo con una carta por elegido y slots vacíos hasta `maxPick` |

Cambio S161: `BuildCard` pasó a `BuildTile`, y `FillTeam` recibe `order` y `maxPick` en lugar de la lista de elegidos.

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
- [[CreatureAvailability]], [[CareGateSO]] — aptitud y necesidad más débil
- [[NeedsDisplay]] — color y relleno de la barra
- [[MonchiPortraitUI]] — retrato de la tarjeta
- [[CreatureDNA]] — nombre, estado ocupado, necesidades
- [[Loc]] — textos `ui.expedition.*` y `ui.power.locked.*`

## Notas

- Estático y sin estado: cada llamada reemplaza el contenido del contenedor que recibe.
- Los nombres de los poderes salen de los SO de kit (`Title`, `Description`), no de `Loc`. La excepción es el poder bloqueado.
- S146: espalda bloqueada para formas no adultas, con el mismo criterio que la ficha y el HUD.
