---
tags: [script, ui, expedition, uitk]
---

# ExpeditionPanelUITK.cs

**Ruta:** `UI/ExpeditionPanelUITK.cs`

**Responsabilidad:** Panel UITK para elegir el elenco de la bajada. Muestra una tira de candidatos (aptas primero, luego por salud), permite marcar hasta 3 y muestra el equipo elegido como cartas (`ExpeditionCardBuilder.BuildTeamCard`) con slots vacíos. El costo de bajada aparece en el botón. "Bajar" se habilita con al menos una elegida, bloque nocturno y Dabloons suficientes. Al confirmar cierra el panel y pide la salida a `ExpeditionBridge`.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del panel (`UiPanels.RootOf`) |
| `panel` | `UIPanelType` | `Expedition` | Clave de registro en `UIManager` |
| `careGate` | `CareGateSO` | — | Criterio para `CreatureAvailability.CanExplore` |
| `database` | `CreatureDatabaseSO` | — | Partes para resolver el kit de cada criatura |
| `kits` | `BrawlKitDatabaseSO` | — | Kits de combate para el perfil de cada criatura |

## Elementos UXML

- `exp-title`, `exp-subtitle`, `exp-empty`, `exp-list` (ScrollView de candidatos), `exp-team` (fila de equipo), `exp-close`, `exp-go`.
- Tarjetas de candidatos: `exp-card` (+ `--off`, `--on`, `--focus`) armadas por `ExpeditionCardBuilder.BuildTile`.

## Comportamiento

- **Rebuild:** se llama en `Start`, al abrir el panel (`OnPanelSet` con show) y al alternar visibilidad. Excluye criaturas muertas o vendidas. Por cada criatura calcula `BrawlKitProfile.Of` y guarda en listas paralelas (`cards`, `dnas`, `profiles`, `eligible`, `picked`, `order`).
- **Orden:** aptas primero; luego salud descendente.
- **Selección:** click o submit alterna la elección. No deja pasar del máximo ni elegir no aptas. Tras cada cambio refresca el equipo (`RefreshTeam`).
- **Foco:** `SetFocus` / `HoverAt` mueven el resaltado; hover no hace scroll.
- **Navegación:** `OnUINavigate` (eje x) mueve el foco; `OnUISubmit` alterna; `OnUICancel` devuelve false.
- **Botón Bajar** (`UpdateGoButton`): texto `ui.expedition.go` (n, máximo), con " · costo" si `BrawlRunRulesSO.Current.DescentCost > 0`. Habilitado si n ≥ 1, `ExpeditionOpen` y `Wallet.Balance(Dabloons) ≥ costo`.
- **Subtítulo:** `ui.expedition.subtitle` (máximo) o `ui.expedition.night_only`.
- **Depart:** arma los IDs elegidos, cierra el panel con `UIManager.RequestPanelSet` y llama `ExpeditionBridge.RequestDeparture(ids)`.

## Horario

- `ExpeditionOpen` = `GameClock.Instance.Block.ExpeditionOpen` (true si no hay reloj).
- Escucha `GameEvents.OnDayBlockChanged` → `RefreshScheduleUI` (solo subtítulo y botón).
- La guarda de horario vive en el botón; `ExpeditionBridge.Depart` no la revalida.

## Vinculado a

- [[Index/23 - Arena Sandbox y Expedicion]]
- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[ExpeditionBridge]] — `RequestDeparture`
- [[ExpeditionCardBuilder]] — tiles, cartas de equipo y slots vacíos
- [[BrawlKitProfile]] — perfil de combate por criatura
- [[BrawlKitDatabaseSO]], [[CreatureDatabaseSO]] — kits y partes del perfil
- [[BrawlRunRulesSO]] — costo mostrado (`Current`)
- [[GameManager]] — `Registry`
- [[GameClock]] — `Block.ExpeditionOpen`
- [[GameEvents]] — `OnDayBlockChanged`
- [[UIManager]] — `OnPanelSetRequested`, `OnPanelToggleRequested`, `RegisterNavigable`, `UnregisterNavigable`, `RequestPanelSet`
- [[CreatureAvailability]], [[CareGateSO]] — aptitud
- [[Wallet]] — `Balance(Dabloons)`
- [[UiPanels]] — `RootOf`, `ClampSelection`, `SetActiveIndex`

## Notas

- Se registra como navegable en `Start` y se desregistra en `OnDestroy`.
- Suscribe `UIManager.OnPanelSetRequested` / `OnPanelToggleRequested` en `OnEnable` y desuscribe en `OnDisable`.
- Solo lee `GameManager.Instance.Registry`; no persiste nada.
- La lista de tarjetas se reconstruye completa en cada `Rebuild`.
- S145: las tarjetas y la fila de equipo salieron hacia `ExpeditionCardBuilder`; el perfil de cada criatura viene de `BrawlKitProfile`.
- S161: el detalle lateral del enfocado salió del panel; el equipo se muestra como 3 cartas con slots vacíos y los candidatos en tira.
