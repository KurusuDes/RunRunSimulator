---
tags: [script, world, brawl, run, director, orchestrator]
---

# BrawlRunDirector.cs

**Ruta:** `World/Brawl/BrawlRunDirector.cs`

**Responsabilidad:** Orquestador de la bajada Brawl en la escena de arena. Crea el `BrawlRun` desde `ExpeditionHandoff`, planea tramos, lleva el ciclo de estados (`Planning` → `Transition` → `Fighting` → `RoomResult` → `Transition` | `Planning` | `Over`), arranca partidas en `BrawlMatch` (modo `Driven`), prepara a cada combatiente (poder y vida), traduce el resultado de cada sala a `BrawlRun`, expone el botín de la última sala para el HUD y decide cuándo volver a la tienda. Ejecuta con `[DefaultExecutionOrder(-50)]`. El empate en combate cuenta como victoria.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `match` | `BrawlMatch` | Partida 3v3 que dirige (Required) |
| `rules` | `BrawlRunRulesSO` | Números de la bajada (Required) |
| `trial` | `BrawlTrialRoom` | Cronómetro y daño de salas de prueba (Required) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Active` | `bool` | `run != null`; solo si se llegó desde la tienda |
| `Run` | `BrawlRun` | Estado de la bajada |
| `State` | `BrawlRunState` | `Planning`, `Transition`, `Fighting`, `RoomResult`, `Over` |
| `Team` | `IReadOnlyList<CreatureDNA>` | Equipo resuelto del save por `UniqueID` |
| `LastRoomSummary` | `string` | Texto del último resultado (lo muestra el HUD o la tarjeta) |
| `LastRoomLoot` | `int` | Botín de la última sala en unidades de `Material`; 0 en derrota y en muñecos |

**Evento:** `Changed` (`Action`). Se dispara en cada cambio de estado y de sala.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `AcceptTramo()` | `Planning` (y no perdida) → `EnterTransition()`: el velo cubre y luego arranca la primera sala del tramo |
| `Leave()` | `Planning` u `Over` → `ExpeditionHandoff.ReturnToStore(run.ToResult())` |

`NextRoom()` se eliminó en S146: el paso entre salas es automático desde `RoomResult`.

## Estados

| Estado | Entra por | Sale por |
|--------|-----------|----------|
| `Planning` | `Start`; `RoomResult` con el tramo terminado | `AcceptTramo()` → `Transition` |
| `Transition` | `AcceptTramo()`; `RoomResult` tras `LootBeatSeconds` | `VeilCoverSeconds` → `StartRoom()` → `Fighting` |
| `Fighting` | `StartRoom()` | `OnMatchEnded` → `RoomResult` (o `Over` si la run se perdió) |
| `RoomResult` | `HandleEnded` (sala no perdida) | `LootBeatSeconds` → `Transition`, o `Planning` si el tramo terminó |
| `Over` | `HandleEnded` (derrota en combate) | `Leave()` |

`Update` solo actúa cuando pasó `stateUntil`. Los tiempos vienen de `BrawlRunRulesSO`.

## Flujo

1. **Awake:** si `ExpeditionHandoff.CameFromStore`, activa `rules`, crea `BrawlRun(RunSeed, SelectedIds, rules)` y fija `match.Driven = true`.
2. **Start:** resuelve los DNA del equipo en `ArenaCastSource.LoadLocal()` por `UniqueID`. Si no encuentra ninguno, avisa y llama `ReturnToStore(null)`. Si hay equipo: `PlanNextTramo()` y estado `Planning`.
3. **EnterTransition:** estado `Transition` y `stateUntil = ahora + VeilCoverSeconds`.
4. **StartRoom** (al vencer el velo): `room = run.CurrentRoom`, estado `Fighting`, `match.StartMatch(run.RoomSeed(), team, rivales)` con rivales = `Rivals` en combate o 3 en salas de prueba. En sala de prueba además `trial.Begin(kind, rules)`.
5. **HandleRoster** (`OnRosterSpawned`, solo en `Fighting`): jugadores `Prime(1, Health01)`; rivales de combate `Prime(RivalPower, 1)`; rivales de sala de prueba `Dummy = true` y `Prime(DummyPower, 1)`.
6. **HandleEnded** (`OnMatchEnded`, solo en `Fighting`): toma la salud (`Hp01`) de los jugadores y cuenta los rivales caídos.
   - Combate: `won = winner == Player || winner == None` (el empate cuenta como victoria) → `RecordCombat(won, health, defeated)`.
   - Prueba: `RecordTrial(health, trial.End())`.
   - `LastRoomSummary`: "Perdiste: se pierden X Minerita", "Empate: cuenta como victoria · +X Minerita", "Ganaste: +X Minerita", "Muñecos: el equipo se curó" o "Minerales: +X Minerita". X = botín × `rules.MineritaPerLoot`.
   - `LastRoomLoot` = 0 si la run se perdió o es sala de muñecos; si no, la diferencia de `Material`.
   - Si `Lost` → `Over`. Si no → `RoomResult` con `stateUntil = ahora + LootBeatSeconds`. Log con tramo, sala, resultado y botín.
7. **Update en `RoomResult`** (al vencer `LootBeatSeconds`): si `run.TramoDone` → `PlanNextTramo()` y `Planning`; si no → `EnterTransition()`.

## Eventos Suscritos

| Evento | Manejador | Descripción |
|--------|-----------|-------------|
| `BrawlMatch.OnRosterSpawned` | `HandleRoster` | Prime de combatientes |
| `BrawlMatch.OnMatchEnded` | `HandleEnded` | Traduce resultado a la bajada |

`OnDisable` desuscribe ambos y llama `BrawlRunRulesSO.Deactivate(rules)`.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlMatch]] — `StartMatch`, `Driven`, eventos de roster y fin
- [[BrawlRun]] — estado de la bajada: `CurrentRoom`, `RoomIndex`, `TramoDone`, `PlanNextTramo`, `RecordCombat`, `RecordTrial`, `ToResult`
- [[BrawlRunRulesSO]] — números; `Activate`/`Deactivate`; `MineritaPerLoot`, `LootBeatSeconds`, `VeilCoverSeconds`
- [[BrawlTrialRoom]] — `Begin` / `End`
- [[BrawlTrialProps]] — props de sala de prueba que arrancan con `trial.Began`
- [[BrawlFighter]] — `Prime`, `Dummy`, `Hp01`, `Team`
- [[BrawlRunPanel]] — tarjeta en `Planning` y `Over`; llama `AcceptTramo` y `Leave`
- [[BrawlRunHud]] — HUD en `Fighting` y `RoomResult`; lee `LastRoomLoot` y `Run`
- [[BrawlRunVeil]] — velo en `Transition`
- [[ExpeditionHandoff]] — `CameFromStore`, `RunSeed`, `SelectedIds`, `ReturnToStore`
- [[ArenaCastSource]] — equipo desde el save local
- [[CreatureDNA]]

## Notas

- Los rivales de sala de prueba son muñecos `Dummy` (congelados, sin IA rival); ver [[BrawlTrialRoom]].
- Una derrota en combate termina la bajada (`Over`); no hay reintentos.
- Sin equipo válido en el save, vuelve a la tienda sin resultado (`CameFromStore` queda en false).
- Sin IDs de equipo (por ejemplo, `Depart(null)` desde el botón de debug), la arena vuelve a la tienda por el mismo camino.
- `Changed` se dispara en `Start`, `EnterTransition`, `StartRoom`, `HandleEnded` y al pasar a `Planning` tras un tramo.
- S145: empate = victoria (`won = winner == Player || winner == None`). Los textos de Minerita usan `MineritaPerLoot`.
- S146: nuevo estado `Transition` (velo entre salas); `NextRoom()` eliminado; `RoomResult` avanza solo tras `LootBeatSeconds`; `LastRoomLoot` nuevo para el HUD.
