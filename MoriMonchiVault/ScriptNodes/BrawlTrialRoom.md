---
tags: [script, world, brawl, run, trial]
---

# BrawlTrialRoom.cs

**Ruta:** `World/Brawl/BrawlTrialRoom.cs`

**Responsabilidad:** Estado de las salas de prueba (Muñecos y Minerales) de la bajada Brawl. Lleva el cronómetro (`TrialSeconds`), que arranca con el primer golpe del equipo o al agotarse `TrialStartGrace`; acumula el daño del equipo a los muñecos, cura aliados en salas de Muñecos y convierte el daño en material en salas de Minerales (`MineralBaseLoot + daño / MineralDamagePerMaterial`). Al agotarse el tiempo termina la partida con `BrawlMatch.EndNow(Player)`. Avisa su inicio con `Began` para que `BrawlTrialProps` coloque los props.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `match` | `BrawlMatch` | Partida que observa y termina (Required) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Active` | `bool` | Sala de prueba en curso |
| `Started` | `bool` | La prueba ya arrancó: primer golpe del equipo o gracia agotada. El cronómetro solo corre desde aquí |
| `Kind` | `BrawlRoomKind` | `Dummies` o `Minerals` |
| `TimeLeft` | `float` | Segundos restantes |
| `Damage` | `float` | Daño acumulado del equipo a rivales |
| `Material` | `int` | En Minerales: `MineralBaseLoot + floor(Damage / MineralDamagePerMaterial)`; 0 en otros casos |

**Evento:** `Began` (`System.Action`) — se dispara al final de `Begin`. Lo escucha `BrawlTrialProps`.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Begin(kind, runRules)` | Reinicia `Damage`, `TimeLeft = TrialSeconds`, `graceLeft = TrialStartGrace`, `Started = false`, `Active = true`; dispara `Began` |
| `End()` | `Active = false`; devuelve `Material` |

## Comportamiento

- **Update:** solo actúa en fase `Fight`. Antes de `Started`, descuenta la gracia y al llegar a 0 marca `Started`. Después, descuenta `TimeLeft`; al llegar a 0 llama `match.EndNow(ExpeditionTeam.Player)`.
- **HandleDamaged** (suscrito a `BrawlFighter.OnDamaged`): cuenta solo daño de jugador a rival que no sea drenaje (`IsDrain`). Marca `Started = true` y suma el daño. `hit.Amount` llega ya con multiplicador, escudo y tope de vida restante aplicados.
- **Muñecos:** cada golpe cura a cada jugador vivo `hit.Amount × DummyHealFraction`, con el atacante como fuente.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlMatch]] — `Phase`, `EndNow`
- [[BrawlFighter]] — `OnDamaged`, `Team`, `IsAlive`, `Heal`
- [[BrawlRunDirector]] — llama `Begin` y `End`
- [[BrawlTrialProps]] — escucha `Began` y `Kind` para colocar los props
- [[BrawlRunRulesSO]] — `TrialSeconds`, `TrialStartGrace`, `DummyHealFraction`, `MineralDamagePerMaterial`, `MineralBaseLoot`
- [[BrawlRunPanel]] — lee `Active`, `Started`, `Kind` y `Material` para la tira de la pelea
- [[BrawlHud]] — oculta la columna roja mientras `Active`; [[BrawlHudClock]] lee `TimeLeft`
- [[BrawlEnums.cs]] — `BrawlRoomKind`, `BrawlMatchPhase`

## Notas

- Si los tres muñecos caen antes del tiempo, la partida termina por `TryEnd` (ganan azules) y la sala cuenta igual con el daño acumulado.
- `End()` solo desactiva; `Damage` se reinicia en `Begin`.
- La vida de los muñecos es `DummyPower` veces la base, así que el daño que hace falta para tumbarlos depende de ese valor.
- S145: la prueba arranca con el primer golpe o al agotarse `TrialStartGrace`; el material de minerales suma `MineralBaseLoot` aunque el daño sea 0.
