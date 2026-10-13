---
tags: [script, ui, uitk, tutorial, hint]
---

# TutorialHintUITK.cs

**Ruta:** `UI/TutorialHintUITK.cs`

**Responsabilidad:** Pastilla de pista del tutorial. Muestra el texto del paso activo con su contador (`n/Total`), marca el paso con ✓ al completarse y la oculta al terminar el tutorial o mientras hay UI con foco. Solo presenta: el estado viene de los eventos estáticos de [[TutorialDirector]].

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Root de la pista |

## Elementos UXML

`hint-root` (contenedor, visible solo con tutorial activo y sin UI con foco), `hint-pill`, `hint-badge` (contador o ✓), `hint-text`.

Clases de estado: `hint--shown` (entrada), `hint--done` (paso cumplido), `hint--pop` (rebote de 140 ms).

## Comportamiento

- `StepChanged(index, total, textKey)`: guarda el paso, muestra la pastilla con `Loc.Tr(textKey)`.
- `StepCompleted()`: cambia el badge a ✓ con pop.
- `Finished()`: quita `hint--shown` y oculta tras 450 ms.
- `UIManager.OnUIFocusChanged`: oculta la pista mientras hay UI con foco.
- `Start()`: resuelve elementos; si el paso ya estaba activo, lo muestra.

## Suscripciones (OnEnable / OnDisable)

| Evento | Manejador |
|--------|-----------|
| `TutorialDirector.StepChanged` | `OnStepChanged` |
| `TutorialDirector.StepCompleted` | `OnStepCompleted` |
| `TutorialDirector.Finished` | `OnFinished` |
| `UIManager.OnUIFocusChanged` | `OnUIFocusChanged` |

## Conexiones

- [[TutorialDirector]] — fuente de los eventos
- [[TutorialStep]] — `TextKey` del paso
- [[UIManager]] — foco de UI
- [[UiPanels]] — `RootOf(document)`
- [[Loc]] — texto localizado
