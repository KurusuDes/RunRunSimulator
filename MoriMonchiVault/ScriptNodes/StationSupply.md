---
tags: [world, needs, station, supply, interactable]
---

# StationSupply.cs

**Ruta:** `World/Needs/StationSupply.cs`

**Responsabilidad:** Reserva consumible de una estación de necesidades (comida, agua o limpieza). Tiene nivel 0 a `max`, se rellena al interactuar y se consume cuando un MoriMonchi usa la estación. Persiste el nivel por `gameObject.name` en `WorldStateSO`, solo cuando cambia de decena (bucket de 10 puntos), para no escribir en cada tick. **S152:** al rellenarse dispara `GameEvents.StationRefilled(kind)`, que usa el tutorial. **S161:** implementa `IFocusLabel`; el porcentaje del suministro sale como rótulo de foco en lugar de la etiqueta TMP del mundo.

## Tipos (`SupplyKind`)

| Kind | Consumo | Empty |
|------|---------|-------|
| Food / Water | Factor 1 si hay nivel, 0 si no | Si nivel <= 0 |
| Clean | Factor 1 si `Level01 >= dirtyThreshold`, si no 0.5 | Nunca |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Consume(float needPoints)` | `float` (0 a 1) | Gasta `needPoints * usePerPoint` y devuelve el factor de eficacia |
| `Refill(float amount)` | `void` | Suma nivel (sin persistir si no cambia de decena) |
| `Interact()` | `void` | Rellena a `max`, persiste, dispara `GameEvents.StationRefilled(kind)` (S152) y feedback `onRefill` |
| `Level01`, `IsEmpty`, `Kind` | propiedades | Lectura de estado |
| `static All` | `IReadOnlyList<StationSupply>` | Registro para `HoseSpray` y otros |

## Rótulo de Foco (S161)

| Miembro | Valor |
|---------|-------|
| `FocusTitle` | Texto localizado según el tipo (`ui.station.food`, `ui.station.water`, `ui.station.clean`) con el porcentaje de `Level01` |
| `FocusDetail` | `null` |

Lo consume [[PlayerFocusProbe]] y lo pinta [[FocusPromptUITK]].

## Persistencia y Eventos

- `Persist()` llama `WorldStateSO.SetStationLevel` y dispara `GameEvents.WorldStateChanged`.
- `OnWorldStateReloaded` relee el nivel guardado (`TryGetStationLevel`).
- **(S152)** `Interact()` dispara `GameEvents.StationRefilled(kind)` después de persistir; `TutorialDirector` lo usa para el paso de comida (`FoodRefilled`).
- `onRefill` y `onEmpty` son `MMF_Player`.

**Conexiones:** [[NeedStation]] (consume via `Consume`), [[HoseSpray]] (rellena agua), [[WorldStateSO]], [[GameEvents]], [[GameManager]], [[NeedStationRegistry]], [[TutorialDirector]] (S152), [[IFocusLabel]] (S161), [[PlayerFocusProbe]] (S161)
