---
tags: [script, ui, expedition, uitk]
---

# ExpeditionPanelUITK.cs

**Ruta:** `UI/ExpeditionPanelUITK.cs`

**Responsabilidad:** Panel UITK para elegir el elenco de la bajada. Lista las criaturas del registry como tarjetas (aptas primero, luego por salud), permite marcar hasta `maxPick` (3), muestra el estado de necesidades y el costo de bajada en el botón. "Bajar" se habilita con al menos una elegida, bloque nocturno y Dabloons suficientes. Al confirmar cierra el panel y pide la salida a `ExpeditionBridge`.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del panel (`UiPanels.RootOf`) |
| `panel` | `UIPanelType` | `Expedition` | Clave de registro en `UIManager` |
| `maxPick` | `int` | 3 | Máximo de criaturas elegidas |
| `careGate` | `CareGateSO` | — | Criterio para `CreatureAvailability.CanExplore` |

## Elementos UXML

- Textos y contenedores: `exp-title`, `exp-subtitle`, `exp-empty`, `exp-list` (ScrollView), `exp-close`, `exp-go`.
- Tarjetas: `exp-card` (+ `--off`, `--on`, `--focus`), `exp-card__icon`, `exp-card__name`, `exp-card__state`, `exp-card__bars`, `exp-card__bar-track` (+ `--weak`), `exp-card__bar-fill`.

## Comportamiento

- **Rebuild:** se llama en `Start`, al abrir el panel (`OnPanelSet` con show) y al alternar visibilidad. Excluye criaturas muertas o vendidas.
- **Orden:** aptas primero; luego salud descendente.
- **Tarjeta no apta:** clase `exp-card--off`, estado "ocupado" o "no listo", y la barra más débil resaltada.
- **Selección:** click o submit alterna la elección. No deja pasar de `maxPick` ni elegir no aptas.
- **Navegación:** `OnUINavigate` (eje x) mueve el foco; `OnUISubmit` alterna; `OnUICancel` devuelve false.
- **Botón Bajar:** texto `ui.expedition.go` (n, maxPick), con " · costo" si `BrawlRunRulesSO.Current.DescentCost > 0`. Habilitado si n ≥ 1, `ExpeditionOpen` y `Wallet.Balance(Dabloons) ≥ costo`.
- **Subtítulo:** `ui.expedition.subtitle` (maxPick) o `ui.expedition.night_only`.
- **Depart:** arma los IDs elegidos, cierra el panel con `UIManager.RequestPanelSet` y llama `ExpeditionBridge.RequestDeparture(ids)`.

## Horario

- `ExpeditionOpen` = `GameClock.Instance.Block.ExpeditionOpen` (true si no hay reloj).
- Escucha `GameEvents.OnDayBlockChanged` → `RefreshScheduleUI` (solo subtítulo y botón).
- La guarda de horario vive en el botón; `ExpeditionBridge.Depart` no la revalida.

## Vinculado a

- [[Index/23 - Arena Sandbox y Expedicion]]

## Conexiones

- [[ExpeditionBridge]] — `RequestDeparture`
- [[BrawlRunRulesSO]] — costo mostrado (`Current`)
- [[GameManager]] — `Registry`
- [[GameClock]] — `Block.ExpeditionOpen`
- [[GameEvents]] — `OnDayBlockChanged`
- [[UIManager]] — `OnPanelSetRequested`, `OnPanelToggleRequested`, `RegisterNavigable`, `UnregisterNavigable`, `RequestPanelSet`
- [[CreatureAvailability]], [[CareGateSO]] — aptitud y necesidad más débil
- [[MonchiPortraitUI]] — retrato de la tarjeta
- [[Wallet]] — `Balance(Dabloons)`
- [[UiPanels]] — `RootOf`, `ClampSelection`, `SetActiveIndex`

## Notas

- Se registra como navegable en `Start` y se desregistra en `OnDestroy`.
- Suscribe `UIManager.OnPanelSetRequested` / `OnPanelToggleRequested` en `OnEnable` y desuscribe en `OnDisable`.
- Solo lee `GameManager.Instance.Registry`; no persiste nada.
- La lista de tarjetas se reconstruye completa en cada `Rebuild`.
