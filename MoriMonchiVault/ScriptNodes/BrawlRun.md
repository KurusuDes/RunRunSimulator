---
tags: [script, data, brawl, run, state]
---

# BrawlRun.cs

**Ruta:** `Data/Brawl/BrawlRun.cs`

**Responsabilidad:** Modelo de datos de una bajada Brawl (run). Estado puro, sin MonoBehaviour: tramo y sala actuales, botín (`Material`), derrota, y salud por MoriMochi entre salas. Genera tramos de forma determinista a partir de la semilla. No toca escena, UI ni persistencia.

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `BaseSeed` | `int` | Semilla raíz de la bajada (viene de `ExpeditionHandoff.RunSeed`) |
| `TeamIds` | `IReadOnlyList<string>` | IDs del equipo, sin vacíos (copia en el constructor) |
| `Depth` | `int` | Tramo actual (0 antes de `PlanNextTramo`) |
| `Rooms` | `IReadOnlyList<BrawlRoom>` | Salas del tramo actual |
| `RoomIndex` | `int` | Índice de la sala actual |
| `CurrentRoom` | `BrawlRoom` | Sala en `RoomIndex` (con clamp; default si no hay salas) |
| `TramoDone` | `bool` | `RoomIndex >= Rooms.Count` |
| `RivalPower` | `float` | `rules.RivalPower(Depth)` |
| `Material` | `int` | Botín acumulado |
| `MaterialLost` | `int` | Botín perdido en la derrota: `ceil(Material × LossFraction)` |
| `Lost` | `bool` | Derrota definitiva de la bajada |
| `RoomsCleared` | `int` | Salas superadas |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `PlanNextTramo()` | Si no hay derrota: `Depth++`, `RoomIndex = 0`, regenera `Rooms` con RNG sembrado por `FloorSeedOf(BaseSeed, 1000 + Depth)` |
| `RoomSeed()` | Semilla de la sala: `ArenaRun.FloorSeedOf(BaseSeed, Depth × 16 + RoomIndex)` |
| `Health01(id)` | Vida 0-1 guardada del MoriMochi; 1 si no hay registro |
| `RecordCombat(won, health01, rivalsDefeated)` | Resuelve sala de combate (ver reglas) |
| `RecordTrial(health01, material)` | Resuelve sala de prueba (ver reglas) |
| `ToResult()` | Convierte a `ExpeditionResult` para `ExpeditionHandoff.ReturnToStore` |

## Generación de Tramo

- Cantidad de salas: entre `MinRooms` y `MaxRooms`.
- Rivales máximos: Depth 1 → `FirstTramoMaxRivals`; Depth ≥ 2 → 3 (clamp 1..3).
- Rivales mínimos: 1, o 2 desde `HardFromDepth`.
- La última sala es siempre combate con el máximo de rivales.
- Resto de salas: muñecos (`DummiesChance`), minerales (`MineralsChance`) o combate con rivales aleatorios entre mín y máx.

## Reglas de Resolución

- **Combate ganado:** `Material += rivalsDefeated × MaterialPerRival × Depth`; `RoomsCleared++`; `RoomIndex++`. Todos los IDs del equipo reciben `HealAfterCombat` (tope 1).
- **Combate perdido:** `Lost = true`; `MaterialLost = ceil(Material × LossFraction)`; `Material -= MaterialLost`. La salud se actualiza sin curación extra.
- **Sala de prueba:** actualiza salud sin curación extra; `Material += max(0, material)`; `RoomsCleared++`; `RoomIndex++`. Nunca marca derrota.
- `RecordCombat`, `RecordTrial` y `PlanNextTramo` no hacen nada si `Lost`.

## Conversión a Resultado (`ToResult`)

- `Seed = BaseSeed`; `Winner = Lost ? Rival : Player`; `PlayerSecured = Material`; `RivalSecured = 0`; `Floors = RoomsCleared`; `Lost`; `TeamIds` copiado.
- `FallenIds` vacío y `Fallen = 0`: la derrota marca al equipo entero vía `TeamIds`, no por caídos (ver `ExpeditionBridge`).

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlRunRulesSO]] — todos los números de la bajada
- [[BrawlRoom]] — salas del tramo
- [[BrawlRunDirector]] — único consumidor: `PlanNextTramo`, `RecordCombat`, `RecordTrial`, `ToResult`
- [[ArenaRun]] — `FloorSeedOf` (semilla determinista)
- [[ExpeditionHandoff]] — tipo `ExpeditionResult`

## Notas

- La salud de un MoriMochi caído queda en 0 en el snapshot, pero la curación post-victoria le suma `HealAfterCombat` igual: vuelve a la siguiente sala con esa fracción.
- `RoomSeed()` asume menos de 16 salas por tramo (multiplicador 16 en la semilla).
- `Health01` por ID es la única memoria entre salas además del botín.
