---
tags: [script, ui, expedition, uitk]
---

# ExpeditionPanelUITK.cs

**Ruta:** `UI/ExpeditionPanelUITK.cs`

**Responsabilidad:** Panel UITK para elegir el elenco de la bajada. Lista las criaturas del registry como tarjetas (aptas primero, luego por salud), permite marcar hasta `maxPick` (3) y muestra el detalle del MoriMochi enfocado (poderes de su kit y rol) y la fila del equipo elegido (con aviso si no hay Support). El costo de bajada aparece en el botón. "Bajar" se habilita con al menos una elegida, bloque nocturno y Dabloons suficientes. Al confirmar cierra el panel y pide la salida a `ExpeditionBridge`. Las tarjetas y el detalle los arma `ExpeditionCardBuilder`; el kit de cada criatura sale de `BrawlKitProfile.Of`.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del panel (`UiPanels.RootOf`) |
| `panel` | `UIPanelType` | `Expedition` | Clave de registro en `UIManager` |
| `maxPick` | `int` | 3 | Máximo de criaturas elegidas |
| `careGate` | `CareGateSO` | — | Criterio para `CreatureAvailability.CanExplore` |
| `database` | `CreatureDatabaseSO` | — | Partes para resolver el kit de cada criatura |
| `kits` | `BrawlKitDatabaseSO` | — | Kits de combate para el perfil de cada criatura |

## Elementos UXML

- Textos y contenedores: `exp-title`, `exp-subtitle`, `exp-empty`, `exp-list` (ScrollView), `exp-detail` (panel de detalle; oculto sin foco), `exp-team` (fila del equipo con aviso), `exp-close`, `exp-go`.
- Tarjetas (las arma `ExpeditionCardBuilder`): `exp-card` (+ `--off`, `--on`, `--focus`), `exp-card__icon`, `exp-card__name`, `exp-card__state`, `exp-card__bars`, `exp-card__bar-track` (+ `--weak`), `exp-card__bar-fill`, `exp-card__role`, `exp-card__powers`, `exp-power`.

## Comportamiento

- **Rebuild:** se llama en `Start`, al abrir el panel (`OnPanelSet` con show) y al alternar visibilidad. Excluye criaturas muertas o vendidas. Por cada criatura calcula `BrawlKitProfile.Of`, arma la tarjeta y guarda en listas paralelas (`cards`, `dnas`, `profiles`, `eligible`, `picked`).
- **Orden:** aptas primero; luego salud descendente.
- **Tarjeta no apta:** clase `exp-card--off`, estado "ocupado" o "no listo", y la barra más débil resaltada.
- **Tarjeta apta:** píldora de rol y tres iconos de poder (ala, cuerno, espalda).
- **Selección:** click o submit alterna la elección. No deja pasar de `maxPick` ni elegir no aptas. Tras cada cambio refresca el equipo.
- **Foco:** click y submit lo fijan; hover (`PointerEnter`) lo mueve sin scroll. El foco llena el detalle con `ExpeditionCardBuilder.FillDetail`.
- **Navegación:** `OnUINavigate` (eje x) mueve el foco; `OnUISubmit` alterna; `OnUICancel` devuelve false.
- **Equipo:** `ExpeditionCardBuilder.FillTeam` con los perfiles y las elecciones.
- **Botón Bajar:** texto `ui.expedition.go` (n, maxPick), con " · costo" si `BrawlRunRulesSO.Current.DescentCost > 0`. Habilitado si n ≥ 1, `ExpeditionOpen` y `Wallet.Balance(Dabloons) ≥ costo`.
- **Subtítulo:** `ui.expedition.subtitle` (maxPick) o `ui.expedition.night_only`.
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
- [[ExpeditionCardBuilder]] — tarjetas, detalle y fila de equipo
- [[BrawlKitProfile]] — perfil de combate por criatura
- [[BrawlKitDatabaseSO]], [[CreatureDatabaseSO]] — kits y partes del perfil
- [[BrawlRunRulesSO]] — costo mostrado (`Current`)
- [[GameManager]] — `Registry`
- [[GameClock]] — `Block.ExpeditionOpen`
- [[GameEvents]] — `OnDayBlockChanged`
- [[UIManager]] — `OnPanelSetRequested`, `OnPanelToggleRequested`, `RegisterNavigable`, `UnregisterNavigable`, `RequestPanelSet`
- [[CreatureAvailability]], [[CareGateSO]] — aptitud y necesidad más débil
- [[Wallet]] — `Balance(Dabloons)`
- [[UiPanels]] — `RootOf`, `ClampSelection`, `SetActiveIndex`

## Notas

- Se registra como navegable en `Start` y se desregistra en `OnDestroy`.
- Suscribe `UIManager.OnPanelSetRequested` / `OnPanelToggleRequested` en `OnEnable` y desuscribe en `OnDisable`.
- Solo lee `GameManager.Instance.Registry`; no persiste nada.
- La lista de tarjetas se reconstruye completa en cada `Rebuild`.
- S145: tarjetas, detalle y fila de equipo salieron de este script hacia `ExpeditionCardBuilder`; el perfil de cada criatura viene de `BrawlKitProfile`.
