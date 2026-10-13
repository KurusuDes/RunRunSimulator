---
tags: [world, needs, station, supply, interactable]
---

# StationSupply.cs

**Ruta:** `World/Needs/StationSupply.cs`

**Responsabilidad:** Reserva consumible de una estacion de necesidades (comida, agua o limpieza). Tiene nivel 0 a `max`, se rellena al interactuar y se consume cuando un monchi usa la estacion. Persiste el nivel por `gameObject.name` en `WorldStateSO`, solo cuando cambia de decena (bucket de 10 puntos), para no escribir en cada tick. **S152:** al rellenarse dispara `GameEvents.StationRefilled(kind)`, que usa el tutorial.

## Tipos (`SupplyKind`)

| Kind | Consumo | Empty |
|------|---------|-------|
| Food / Water | Factor 1 si hay nivel, 0 si no | Si nivel <= 0 |
| Clean | Factor 1 si `Level01 >= dirtyThreshold`, si no 0.5 | Nunca |

## Metodos Publicos

| Metodo | Retorna | Descripcion |
|--------|---------|-------------|
| `Consume(float needPoints)` | `float` (0 a 1) | Gasta `needPoints * usePerPoint` y devuelve el factor de eficacia |
| `Refill(float amount)` | `void` | Suma nivel (sin persistir si no cambia de decena) |
| `Interact()` | `void` | Rellena a `max`, persiste, dispara `GameEvents.StationRefilled(kind)` (S152) y feedback `onRefill` |
| `Level01`, `IsEmpty`, `Kind` | propiedades | Lectura de estado |
| `static All` | `IReadOnlyList<StationSupply>` | Registro para `HoseSpray` y otros |

## Persistencia y Eventos

- `Persist()` llama `WorldStateSO.SetStationLevel` y dispara `GameEvents.WorldStateChanged`.
- `OnWorldStateReloaded` relee el nivel guardado (`TryGetStationLevel`).
- **(S152)** `Interact()` dispara `GameEvents.StationRefilled(kind)` después de persistir; `TutorialDirector` lo usa para el paso de comida (`FoodRefilled`).
- Label localizada (`ui.station.food/water/clean`) con porcentaje y color rojo, amarillo, verde segun `Level01`.
- `onRefill` y `onEmpty` son `MMF_Player`.

**Conexiones:** [[NeedStation]] (consume via `Consume`), [[HoseSpray]] (rellena agua), [[WorldStateSO]], [[GameEvents]], [[GameManager]], [[NeedStationRegistry]], [[TutorialDirector]] (S152)
