---
tags: [script, system, tutorial, singleton, onboarding]
---

# TutorialDirector.cs

**Ruta:** `Systems/Tutorial/TutorialDirector.cs`

**Responsabilidad:** Dirige el tutorial de onboarding. Mantiene el paso activo, detecta cuándo se cumple la señal de cada paso (movimiento, llegada, eventos de tienda, bajada), completa el paso con una pausa breve y avanza el progreso guardado en `WorldStateSO.TutorialStep`. Expone eventos estáticos para la pista (`TutorialHintUITK`) y la guía en el mundo (`TutorialGuide`).

## Singleton y Eventos Estáticos

- `TutorialDirector.Instance` asignado en `Awake`.
- `StepChanged(int index, int total, string textKey)` — paso activado.
- `StepCompleted()` — paso cumplido (antes de la pausa de avance).
- `Finished()` — tutorial terminado o saltado.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `steps` | `List<TutorialStep>` | vacía | Pasos en orden |
| `player` | `Transform` | — | Referencia al jugador para distancias |
| `cloudSync` | `CloudSyncService` | — | Espera a `StartupSyncDone` |
| `syncTimeoutSeconds` | `float` | 20 | Timeout de la espera |
| `moveDistance` | `float` | 3 | Distancia plana para `Moved` |

Constante: `CompleteDelaySeconds = 0.6f` (pausa realtime antes de avanzar).

## Estado Persistido

`WorldStateSO.TutorialStep` (entero, 1-based):

| Valor | Significado |
|-------|-------------|
| `<= 0` | Sin tutorial activo |
| `1..Total` | Paso `value - 1` activo |
| `> Total` | Tutorial terminado |

Al completar un paso se escribe `index + 2` (el siguiente). `Skip()` escribe `Total + 1`.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Active` | `activeIndex >= 0` |
| `Index`, `Total`, `Current` | Paso activo y conteo |
| `Skip()` | Marca el tutorial como terminado (botón "Saltar tutorial" del pausa) |

## Lógica

- **Boot:** espera `StartupSyncDone` (con timeout) y evalúa.
- **Evaluate:** lee el valor guardado. Si es `1` y el save ya tiene criaturas o departidas, lo considera save antiguo y salta el tutorial.
- **Activate:** los pasos `BoxOrdered` y `CreatureArrived` se saltan si ya hay criaturas vivas.
- **Update:** comprueba `Moved` y `ReachTarget` por distancia plana (XZ).
- **Complete(signal):** solo si coincide con el paso activo; dispara `StepCompleted`, espera 0.6 s realtime y avanza.

## Suscripciones (OnEnable / OnDisable)

| Evento | Efecto |
|--------|--------|
| `GameEvents.OnWorldStateReloaded` | `Evaluate()` |
| `GameEvents.OnWorldStateChanged` | `Evaluate()` si cambió `TutorialStep` |
| `GameEvents.OnCreatureBoxOrdered` | `Complete(BoxOrdered)` |
| `GameEvents.OnStationRefilled` | `Complete(FoodRefilled)` si es `Food` |
| `GameEvents.OnRegistryChanged` | `Complete(CreatureArrived)` si hay criaturas vivas |
| `GameEvents.OnExpeditionReturned` | `Complete(ExpeditionReturned)` |
| `UIManager.OnPanelVisibilityChanged` | `Complete(StorePanelOpened)` al abrir Store |

## Notas

- Lee `WorldStateSO` y `CreatureRegistrySO` a través de `GameManager.Instance` (no llega por el payload del evento). Punto a revisar frente a la regla de comunicación.
- Escribe el progreso con `SetValue()`, que dispara `GameEvents.WorldStateChanged` (persistencia por evento).

## Conexiones

- [[TutorialStep]] — datos de cada paso y `TutorialSignal`
- [[TutorialHintUITK]] — escucha `StepChanged`, `StepCompleted`, `Finished`
- [[TutorialGuide]] — escucha `StepChanged`, `StepCompleted`, `Finished`
- [[PauseMenuUITK]] — botón "Saltar tutorial" llama `Skip()` y consulta `Active`
- [[WorldStateSO]] — `TutorialStep`
- [[GameEvents]] — 6 suscripciones de gameplay
- [[UIManager]] — `OnPanelVisibilityChanged`
- [[CloudSyncService]] — `StartupSyncDone`
- [[GameManager]] — `WorldState`, `Registry`
