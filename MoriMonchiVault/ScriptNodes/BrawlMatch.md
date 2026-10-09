---
tags: [script, world, brawl, match, game]
---

# BrawlMatch.cs

**Ruta:** `World/Brawl/BrawlMatch.cs`

**Responsabilidad:** Orquestación de partida 3v3. Dos modos: autónomo (genera rosters aleatorios y reinicia solo) y `Driven` (lo dirige `BrawlRunDirector` para la bajada: el equipo del jugador viene del save y los rivales los pide cada sala; no reinicia). Fases (Setup, Countdown, Fight, SuddenDeath, Ended). Evento de Last Stand (1 vs ≥2). Rampa de daño por KO. Seed aleatorio o configurable.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `layout` | `ArenaLayoutBuilder` | — | Construye el escenario por seed (Required) |
| `palette` | `ArenaPaletteApplier` | — | Paleta visual por seed |
| `fighterPrefab` | `BrawlFighter` | — | Prefab con NavMeshAgent (Required) |
| `creatureDatabase`, `furDatabase`, `visualBank` | SO | — | Generación y visuales de MoriMonchis (Required) |
| `kits` | `BrawlKitDatabaseSO` | — | Kits de ala, cuerno y espalda (Required) |
| `tuning` | `BrawlTuningSO` | — | Parámetros de partida (Required) |
| `vfx` | `BrawlVfxLibrarySO` | — | Biblioteca de VFX activa mientras existe la partida (Required) |
| `seed` | `int` | 4242 | Semilla si no se randomiza |
| `randomizeEachPlay` | `bool` | true | Semilla por `TickCount` en cada Play |
| `teamSize` | `int` | 3 | Tamaño de equipo |
| `spawnSpread` | `float` | 2.5 | Radio del anillo de spawn |
| `autoRestart` | `bool` | true | Reinicia tras `EndHoldSeconds` (no aplica si `Driven`) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Current` | `BrawlMatch` (static) | Partida activa (se fija en OnEnable) |
| `Driven` | `bool` | Lo dirige una bajada: no arranca sola en Start y no reinicia |
| `Phase` | `BrawlMatchPhase` | Fase actual |
| `PhaseTime` | float | Segundos desde el inicio de la fase |
| `TimeLeft` | float | Cronómetro de la ronda |
| `SuddenDeathElapsed` | float | Segundos de muerte súbita |
| `Seed`, `MatchIndex` | int | Semilla y número de partida |
| `Winner` | `ExpeditionTeam` | Ganador (None = empate) |
| `KnockOuts` | int | KOs en la partida |
| `DamageRamp` | float | `1 + KoDamageRamp × KnockOuts` |
| `Fighters` | `IReadOnlyList<BrawlFighter>` | Combatientes vivos y muertos de la partida |
| `Tuning` | `BrawlTuningSO` | Parámetros |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `NewMatch()` | Botón Odin. `StartMatch(TickCount)` con roster aleatorio |
| `Rematch()` | Botón Odin. Repite la semilla y el roster de la última partida |
| `StartMatch(seed, roster = null)` | Prepara la arena y spawnea. Sin roster, mintea uno autónomo |
| `StartMatch(seed, players, rivalCount)` | Usado por la bajada: `players` es el equipo del jugador; `rivalCount` rivales minteados (clamp 0..teamSize) |
| `EndNow(winner)` | Termina la partida con ese ganador. Lo usa `BrawlTrialRoom` al agotarse el tiempo. No hace nada en `Idle` o `Ended` |

## Fases de Partida

| Fase | Duración | Descripción |
|------|----------|-------------|
| Setup | Instantánea | `SpawnRoster` → `OnRosterSpawned` → Countdown |
| Countdown | `tuning.CountdownSeconds` | Combatientes congelados (`Frozen`) |
| Fight | `tuning.RoundSeconds` | Cronómetro de ronda. Al llegar a 0 pasa a SuddenDeath |
| SuddenDeath | Sin límite | Sin cronómetro. Drenaje por segundo: `MaxHp × (SuddenDeathStart + SuddenDeathRamp × s)`. Curación ×`SuddenDeathHealFactor` |
| Ended | `tuning.EndHoldSeconds` | Resultado y MVP. Reinicia solo si `autoRestart && !Driven` |

La partida termina cuando un equipo queda sin vivos (`TryEnd`). Si ambos quedan en 0, el ganador es `None` (empate).

## Last Stand

Se activa cuando, tras un KO:
- Un equipo queda con 1 miembro vivo
- El equipo rival tiene ≥ 2 miembros vivos

Efectos sobre el sobreviviente (una vez por partida, `lastStanders`):
- Escudo de `LastStandShield` × vida máxima durante `LastStandSeconds`
- Daño `LastStandBoost` y velocidad `LastStandHaste`
- Recarga de habilidades (`Caster.Refill`)
- Pulso visual y evento `OnLastStand`

## Rampa de Daño

`DamageRamp = 1 + KoDamageRamp × KnockOuts`

- Cada KO suma `KoDamageRamp` al factor, que se copia a `RoundDamageFactor` de todos los combatientes.
- Mostrado en el HUD bajo el reloj.

## Eventos Estáticos

| Evento | Parámetros | Cuándo |
|--------|-----------|--------|
| `OnPhaseChanged` | `phase` | Cambio de fase |
| `OnMatchEnded` | `winner` (`ExpeditionTeam`: Player, Rival o None = empate) | Fin de partida |
| `OnRosterSpawned` | `fighters` | Tras spawnear, antes de Countdown |
| `OnLastStand` | `survivor` | Último en pie activado |

## Generación de Roster

**Autónomo** (`MintRoster`): `MintTeam(teamSize)` para cada equipo.

**Driven** (`StartMatch(seed, players, rivalCount)`): el equipo del jugador viene del save; los rivales se mintean con `MintTeam(rivalCount)`.

- `MintTeam`: wing único por equipo (hasta `MaxWingRerolls = 12` reintentos).
- `MintRandom`: `CreatureGenerator.GenerateRandom`, género, elemento, rol, dos dials (sociabilidad, osadía), nombre de `CreatureNameBank`, Form Adult, Generation 1, `Stamp()`.

## Spawn

- Centro: `layout.SpawnPoint(team)`. Ángulo de inicio aleatorio; anillo de radio `spawnSpread` si hay más de un combatiente.
- Posición: `NavMesh.SamplePosition` con 3 m de tolerancia.
- `SpawnFighter`: `Instantiate(fighterPrefab)`, `NavMeshAgent.Warp`, `Bind`, `Frozen = true` hasta `BeginFight`.

## Preparación de Arena (`PrepareArena`)

`ClearFighters`, `BrawlProjectile.ClearAll`, `BrawlZone.ClearAll`; `MatchIndex++`; `Random.InitState(seed)`; `layout.Build(seed, filter)`; `palette.ApplyIndex(IndexForSeed(seed))` y `SetArenaCenter`.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Componentes escena:**
- [[ArenaLayoutBuilder]] — layout
- [[ArenaPaletteApplier]] — paleta visual
- [[BrawlFighter]] — prefab spawn
- [[BrawlTuningSO]] — parámetros

**Datos:**
- [[CreatureDatabaseSO]], [[BrawlKitDatabaseSO]] — assets
- [[MonchiVisualBankSO]], [[FurTypeDatabaseSO]] — visuals
- [[CreatureGenerator]], [[CreatureNameBank]] — minteo de roster autónomo

**Bajada Brawl:**
- [[BrawlRunDirector]] — pone `Driven`, llama `StartMatch(seed, players, rivalCount)` y escucha `OnRosterSpawned` / `OnMatchEnded`
- [[BrawlTrialRoom]] — llama `EndNow` al agotarse el tiempo de la sala de prueba

**Suscriptores:**
- [[BrawlCamera]], [[BrawlAnimator]], [[BrawlHud]] → eventos

## Notas

- `Current` es singleton (acceso vía `BrawlMatch.Current`); se fija en `OnEnable`.
- Seed aleatorio cada Play si `randomizeEachPlay`.
- `Start` pone `Application.runInBackground = true`. Si `Driven`, sale sin arrancar partida.
- `Driven` se fija desde `BrawlRunDirector.Awake` (orden -50), antes del `Start` de esta clase.
- Logs de inicio (roster con partes) y de fin (daño, curación, KOs por combatiente).
- Sin persistencia; todo en memoria.
