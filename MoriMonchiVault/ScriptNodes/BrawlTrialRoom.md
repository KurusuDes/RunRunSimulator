---
tags: [script, world, brawl, run, trial]
---

# BrawlTrialRoom.cs

**Ruta:** `World/Brawl/BrawlTrialRoom.cs`

**Responsabilidad:** Estado de las salas de prueba (Muñecos y Minerales) de la bajada Brawl. Lleva el cronómetro (`TrialSeconds`), acumula el daño del equipo a los muñecos, cura aliados en salas de Muñecos y convierte el daño en material en salas de Minerales. Al agotarse el tiempo termina la partida con `BrawlMatch.EndNow(Player)`.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `match` | `BrawlMatch` | Partida que observa y termina (Required) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Active` | `bool` | Sala de prueba en curso |
| `Kind` | `BrawlRoomKind` | `Dummies` o `Minerals` |
| `TimeLeft` | `float` | Segundos restantes |
| `Damage` | `float` | Daño acumulado del equipo a rivales |
| `Material` | `int` | En Minerales: `floor(Damage / MineralDamagePerMaterial)`; 0 en otros casos |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Begin(kind, runRules)` | Reinicia `Damage`, `TimeLeft = TrialSeconds`, `Active = true` |
| `End()` | `Active = false`; devuelve `Material` |

## Comportamiento

- **Update:** el cronómetro solo corre en fase `Fight`. Al llegar a 0 llama `match.EndNow(ExpeditionTeam.Player)`.
- **HandleDamaged** (suscrito a `BrawlFighter.OnDamaged`): cuenta solo daño de jugador a rival que no sea drenaje (`IsDrain`). `hit.Amount` llega ya con multiplicador, escudo y tope de vida restante aplicados.
- **Muñecos:** cada golpe cura a cada jugador vivo `hit.Amount × DummyHealFraction`, con el atacante como fuente.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlMatch]] — `Phase`, `EndNow`
- [[BrawlFighter]] — `OnDamaged`, `Team`, `IsAlive`, `Heal`
- [[BrawlRunDirector]] — llama `Begin` y `End`
- [[BrawlRunRulesSO]] — `TrialSeconds`, `DummyHealFraction`, `MineralDamagePerMaterial`
- [[BrawlRunPanel]] — lee `TimeLeft`, `Damage`, `Kind`, `Active` para la tira de la pelea
- [[BrawlEnums.cs]] — `BrawlRoomKind`, `BrawlMatchPhase`

## Notas

- Si los tres muñecos caen antes del tiempo, la partida termina por `TryEnd` (ganan azules) y la sala cuenta igual con el daño acumulado.
- `End()` solo desactiva; `Damage` se reinicia en `Begin`.
- La vida de los muñecos es `DummyPower` veces la base, así que el daño que hace falta para tumbarlos depende de ese valor.
