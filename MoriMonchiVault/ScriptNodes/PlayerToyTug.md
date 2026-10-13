---
tags: [script, systems, player, toys, tug, singleton]
---

# PlayerToyTug.cs

**Ruta:** `Systems/Player/PlayerToyTug.cs`

**Responsabilidad:** Minijuego de tirón de juguete entre el jugador y un MoriMochi que está jalando el juguete que el jugador sostiene. Máquina de estados `Idle → Pulling → PlayerWon | CreatureWon`. El jugador suma progreso pulsando Interact; la criatura lo resta cada segundo. Termina por progreso (±1), por tiempo máximo, o por distancia/desactivación del puller.

## Estados

`TugState`: `Idle`, `Pulling`, `PlayerWon`, `CreatureWon`. `IsActive` = `Pulling`.

## Eventos (static)

| Evento | Payload | Cuándo |
|--------|---------|--------|
| `TugStarted` | — | Al iniciar el tirón |
| `TugChanged` | `float progress` (-1..1) | Al cambiar el progreso |
| `TugEnded` | `bool playerWon` | Al resolver |

## Campos y propiedades

- `[SerializeField] ToyTuningSO tuning` — usa `TugPressPower`, `TugMaxSeconds`, `TugRange`
- `Instance` (singleton), `State`, `Puller`, `Progress`, `IsActive`

## Metodos publicos

| Metodo | Descripción |
|--------|-------------|
| `TryBegin(MoriMochiAgent puller, float pullPerSecond)` | Arranca solo si está Idle, hay tuning y el jugador tiene un `Toy` transportable en la mano (`HotbarController`) |
| `Release(MoriMochiAgent puller)` | Suelta el tirón si el puller coincide |

## Invariantes

- `OnEnable` suscribe `PlayerInputs.InteractPressed`; `OnDisable` desuscribe y resetea.
- Si el puller se desactiva o se aleja más de `TugRange * 2`, el jugador gana.
- Mientras hay tirón activo, `PlayerController` ignora la tecla E (ver ese nodo).

## Conexiones

- [[ToyTuningSO]] — números del tirón
- [[ToyPlayerPlay]] — inicia el tirón (`TryBegin`) y lo suelta (`Release`) desde la criatura
- [[TugMeterHUD]] — escucha los 3 eventos para dibujar el medidor
- [[PlayerController]] — no procesa E mientras `IsActive`
- [[HotbarController]] — provee el objeto activo en mano
- [[Toy]] — `IsCarriable`
- [[PlayerInputs]] — Interact
