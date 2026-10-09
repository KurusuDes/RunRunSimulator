---
tags: [script, world, brawl, run, director, orchestrator]
---

# BrawlRunDirector.cs

**Ruta:** `World/Brawl/BrawlRunDirector.cs`

**Responsabilidad:** Orquestador de la bajada Brawl en la escena de arena. Crea el `BrawlRun` desde `ExpeditionHandoff`, pide tramos y salas, arranca partidas en `BrawlMatch` (modo `Driven`), prepara a cada combatiente (poder y vida), traduce el resultado de cada sala a `BrawlRun` y decide cuándo volver a la tienda. Ejecuta con `[DefaultExecutionOrder(-50)]`.

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
| `State` | `BrawlRunState` | `Planning`, `Fighting`, `RoomResult`, `Over` |
| `Team` | `IReadOnlyList<CreatureDNA>` | Equipo resuelto del save por `UniqueID` |
| `LastRoomSummary` | `string` | Texto del último resultado (lo muestra el panel) |

**Evento:** `Changed` (`Action`) — se dispara en cada transición de estado.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `AcceptTramo()` | `Planning` → inicia la primera sala del tramo |
| `NextRoom()` | `RoomResult` → si el tramo terminó, planifica el siguiente (`Planning`); si no, inicia la sala siguiente |
| `Leave()` | Si no está `Fighting`: `ExpeditionHandoff.ReturnToStore(run.ToResult())` |

## Flujo

1. **Awake:** si `ExpeditionHandoff.CameFromStore`, activa `rules`, crea `BrawlRun(RunSeed, SelectedIds, rules)` y fija `match.Driven = true`.
2. **Start:** resuelve los DNA del equipo en `ArenaCastSource.LoadLocal()` por `UniqueID`. Si no encuentra ninguno, avisa y llama `ReturnToStore(null)`. Si hay equipo: `PlanNextTramo()` y estado `Planning`.
3. **StartRoom:** `match.StartMatch(run.RoomSeed(), team, rivales)`, con rivales = `Rivals` en combate o 3 en salas de prueba. En sala de prueba además `trial.Begin(kind, rules)`.
4. **HandleRoster** (`OnRosterSpawned`, solo en `Fighting`): jugadores `Prime(1, Health01)`; rivales de combate `Prime(RivalPower, 1)`; rivales de sala de prueba `Dummy = true` y `Prime(DummyPower, 1)`.
5. **HandleEnded** (`OnMatchEnded`, solo en `Fighting`): toma la salud (`Hp01`) de los jugadores y cuenta los rivales caídos. Combate → `RecordCombat`; prueba → `RecordTrial(health, trial.End())`. Estado `Over` si `Lost`, si no `RoomResult`. Log con tramo, sala, resultado y botín.

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
- [[BrawlRun]] — estado de la bajada
- [[BrawlRunRulesSO]] — números; `Activate`/`Deactivate`
- [[BrawlTrialRoom]] — `Begin` / `End`
- [[BrawlFighter]] — `Prime`, `Dummy`, `Hp01`, `Team`
- [[BrawlRunPanel]] — lee `State`, `Run`, `Team`, `LastRoomSummary`; escucha `Changed`; llama `AcceptTramo`, `NextRoom`, `Leave`
- [[ExpeditionHandoff]] — `CameFromStore`, `RunSeed`, `SelectedIds`, `ReturnToStore`
- [[ArenaCastSource]] — equipo desde el save local
- [[CreatureDNA]]

## Notas

- Los rivales de sala de prueba son muñecos `Dummy` (congelados, sin IA rival); ver [[BrawlTrialRoom]].
- Una derrota en combate termina la bajada (`Over`); no hay reintentos.
- Sin equipo válido en el save, vuelve a la tienda sin resultado (`CameFromStore` queda en false).
- Sin IDs de equipo (por ejemplo, `Depart(null)` desde el botón de debug), la arena vuelve a la tienda por el mismo camino.
