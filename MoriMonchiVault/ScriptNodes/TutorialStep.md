---
tags: [script, data, tutorial, struct]
---

# TutorialStep.cs

**Ruta:** `Data/Tutorial/TutorialStep.cs`

**Responsabilidad:** Datos puros de un paso del tutorial. Contiene el struct `TutorialStep` y el enum `TutorialSignal` (qué evento completa el paso). Sin lógica: la ejecución la hace [[TutorialDirector]].

## Enum `TutorialSignal`

| Valor | Cuándo completa el paso |
|-------|-------------------------|
| `Moved` | El jugador se aleja `moveDistance` del punto de inicio del paso |
| `ReachTarget` | El jugador entra al `Radius` de `Target` |
| `StorePanelOpened` | Se abre el panel de tienda |
| `BoxOrdered` | Se encarga una caja de criatura (`GameEvents.OnCreatureBoxOrdered`) |
| `CreatureArrived` | Hay al menos una criatura viva en el registro |
| `FoodRefilled` | Se rellena una estación de comida (`GameEvents.OnStationRefilled`) |
| `ExpeditionReturned` | Vuelve una bajada a la tienda |

## Struct `TutorialStep` (`[Serializable]`)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `TextKey` | `string` | Clave de `Loc` del texto de la pista |
| `Signal` | `TutorialSignal` | Señal que completa el paso |
| `Target` | `Transform` | Punto de destino (solo para `ReachTarget`; también guía a `TutorialGuide`) |
| `Radius` | `float` | Radio de llegada en el plano XZ |

## Conexiones

- [[TutorialDirector]] — lista de pasos (`steps`) y evaluación de la señal
- [[TutorialHintUITK]] — muestra `TextKey` del paso activo
- [[TutorialGuide]] — dibuja la guía hacia `Target` y `Radius`
