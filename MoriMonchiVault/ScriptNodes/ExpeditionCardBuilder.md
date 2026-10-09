---
tags: [script, ui, expedition, builder, uitk]
---

# ExpeditionCardBuilder.cs

**Ruta:** `UI/ExpeditionCardBuilder.cs`

**Responsabilidad:** Builder estático de la presentación del panel de expedición: tarjeta de cada MoriMochi, panel de detalle del enfocado y fila de equipo elegido. Solo construye `VisualElement`; no guarda estado, no suscribe eventos y no escribe en `GameManager`. Lo llama `ExpeditionPanelUITK` en cada `Rebuild`, cada cambio de foco y cada cambio de selección.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `BuildCard(dna, ok, profile, careGate)` | Tarjeta `exp-card` con retrato, nombre y marca `✓`. Si es apta (`ok`): píldora de rol y tres iconos de poder (ala, cuerno, espalda). Si no: estado (`ui.expedition.busy` o `ui.expedition.notready`) y barra de la necesidad más débil (`CreatureAvailability.WeakestNeed`). No apta: clase `exp-card--off` |
| `FillDetail(detail, dna, profile)` | Limpia el contenedor y lo llena: nombre, píldora de rol y tres filas de poder (icono, título, descripción) |
| `FillTeam(team, profiles, picked)` | Fila `exp-team` con una píldora por elegido. Si hay elegidos y ninguno tiene `Support`, agrega el aviso `ui.expedition.nosupport`. Visibilidad oculta si no hay elegidos |

## Poderes

- Slot 0: ala, con rol `BrawlKitProfile.WingRole`.
- Slot 1: cuerno (`BrawlSkillSO`).
- Slot 2: espalda (`BrawlSkillSO`). Si `BackLocked`, es un poder bloqueado: icono con clase `exp-power--locked` y "?" (`exp-power__lock`), título y descripción `ui.power.locked.title` / `ui.power.locked.desc`, sin anillo de rol. Aplica en la tarjeta y en el detalle.
- Icono: `Theme.Icon` como fondo o `Theme.Color` si no hay icono. Clase `mm-role-ring--{rol}`.
- Parte sin kit: poder vacío con rol Offense.
- En el detalle, la fila bloqueada no lleva clase de color de rol en el título.

## Conexiones

- [[ExpeditionPanelUITK]] — único consumidor
- [[BrawlKitProfile]] — rol, temas, kits y `BackLocked` de cada poder
- [[BrawlRolePill]] — píldora de rol
- [[BrawlTheme]], [[BrawlSkillSO]], [[BrawlWingKitSO]] — iconos, colores, títulos y descripciones
- [[CreatureAvailability]], [[CareGateSO]] — aptitud y necesidad más débil
- [[NeedsDisplay]] — color y relleno de la barra
- [[MonchiPortraitUI]] — retrato de la tarjeta
- [[CreatureDNA]] — nombre, estado ocupado, necesidades
- [[Loc]] — textos `ui.expedition.*` y `ui.power.locked.*`

## Notas

- Estático y sin estado: cada llamada reemplaza el contenido del contenedor que recibe.
- Los nombres de los poderes salen de los SO de kit (`Title`, `Description`), no de `Loc`. La excepción es el poder bloqueado, que sale de `Loc`.
- S146: espalda bloqueada para formas no adultas, con el mismo criterio que la ficha y el HUD.
