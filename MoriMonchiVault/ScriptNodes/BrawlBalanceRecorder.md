---
tags: [script, world, brawl, development, balance, recording, stats]
---

# BrawlBalanceRecorder.cs

**Ruta:** `World/Brawl/BrawlBalanceRecorder.cs`

**Responsabilidad:** Captura de telemetría detallada de combate 3v3: daño desglosado por parte (ala, cuerno, espalda), curación, escudos, movilidad, usos de habilidades. Acciona por eventos estáticos de `BrawlMatch`, `BrawlFighter`, `BrawlSkillCaster`, `BrawlWing`. Vuelca dos archivos CSV: `matches.csv` (1 línea de resumen/partida) y `fighters.csv` (6 líneas de detalle/partida).

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Done` | bool | Partida finalizada (armada y procesada) |
| `FightSeconds` | float | Segundos de combate transcurridos (desde fase Fight) |
| `MatchHeader` | const string | Header CSV matches: `batch;seed;mirror;winner;duration;sudden;...` |
| `FighterHeader` | const string | Header CSV fighters: `batch;seed;mirror;team;won;name;body;...` |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Arm(batchLabel, matchSeed, mirrorFlag)` | Prepara recorder para nueva partida (limpia stats, arma escuchas de eventos) |
| `ForceFinish()` | Finaliza partida antes de que acabe (timeout, error) |
| `MatchLine(realSeconds)` | Devuelve string CSV para matches.csv (1 línea) |
| `FighterLines()` | Devuelve string CSV para fighters.csv (6 líneas) |

## Estructura de Datos Internas

**Clase `Stat` privada:**
- `Fighter`: ref al `BrawlFighter`
- `Team`: `ExpeditionTeam.Player` ó `.Rival`
- `DmgWing`, `DmgHorn`, `DmgBack`: daño desglosado por fuente
- `Taken`: daño recibido total
- `SelfHeal`, `HealTaken`: curación emitida y recibida
- `ShieldTaken`: escudo aplicado (no absorbido, registrado)
- `Kos`: knockouts logrados
- `Attacks`, `HealShots`, `Mobility`: acciones (básico, curación, movimiento)
- `HornUses`, `BackUses`: activaciones de habilidades
- `LastStand`: si fue último en pie (1 ó 0)
- `DeathAt`, `Alive`: momento de muerte y estado final
- `Dmg`, `Heal`: totales finales de damage/healing

**Diccionarios:**
- `byFighter`: `BrawlFighter` → `Stat` (búsqueda O(1) en eventos)
- `stats`: lista de `Stat` para volcado ordenado

## CSV `matches.csv`

| Campo | Fuente |
|-------|--------|
| batch, seed, mirror | parámetros de `Arm()` |
| winner | `OnMatchEnded` |
| duration | `FightSeconds` al finalizar |
| sudden | `true` si entró `SuddenDeath` |
| suddenAt | segundos hasta `SuddenDeath` |
| firstKoTeam | equipo del primer KO |
| comeback | `winner != firstKoTeam` |
| lastStandTeam | equipo que activó Last Stand |
| lastStandWon | `lastStandTeam == winner` |
| kos | total de knockouts en partida |
| blueAlive, redAlive | sobrevivientes Player/Rival |
| timeout | `true` si fue forzado |
| real | segundos de wall-clock (`realSeconds` parámetro) |

## CSV `fighters.csv`

| Campo | Descripción |
|-------|-------------|
| batch, seed, mirror, team | contexto |
| won | 1=victoria, 0=derrota, 0,5=timeout |
| name, body | atributos visuales |
| bold, social, posture | rasgos IA (`Brain` dials) |
| wing, wingTitle | ID y nombre de ala |
| horn, hornTitle, hornFamily, hornRole | cuerno (ID, nombre, familia, rol) |
| back, backTitle, backFamily, backRole | espalda (ID, nombre, familia, rol) |
| maxHp | vida máxima |
| dmg, dmgWing, dmgHorn, dmgBack | daño total y desglosado |
| taken | daño recibido |
| heal, selfHeal, healTaken | curación emitida, de sí, recibida |
| shieldTaken | escudos aplicados |
| kos | knockouts logrados |
| alive | sobreviviente final |
| deathAt | tiempo de muerte (vacío si vivo) |
| attacks, healShots, mobility | acciones |
| hornUses, backUses | activaciones de habilidades |
| lastStand | 1 si fue último en pie |
| wingPart, hornPart, backPart | etiquetas de tema (`BrawlTheme.Label`) |

## Eventos Suscritos

**En `OnEnable()`:**

| Evento | Handler |
|--------|---------|
| `BrawlMatch.OnPhaseChanged` | Inicia timer en fase `Fight`, marca `sudden = true` en `SuddenDeath` |
| `BrawlMatch.OnMatchEnded` | Captura `winner`, finaliza partida |
| `BrawlMatch.OnRosterSpawned` | Inicializa stats de 6 combatientes |
| `BrawlMatch.OnLastStand` | Marca primer equipo en Last Stand |
| `BrawlFighter.OnDamaged` | Suma daño (origen: ala/cuerno/espalda) |
| `BrawlFighter.OnHealed` | Registra curación (auto/ajena) |
| `BrawlFighter.OnShielded` | Suma escudos |
| `BrawlFighter.OnKnockedOut` | Registra KO, captura tiempo, marca primer equipo KO |
| `BrawlSkillCaster.OnCastFired` | Incrementa `HornUses` o `BackUses` |
| `BrawlWing.OnAttackFired` | Incrementa `Attacks`, marca si fue curación |
| `BrawlWing.OnMobilityUsed` | Incrementa `Mobility` |

Desuscripción completa en `OnDisable()`.

## Desglose de Daño

- Si `hit.FromSkill == false` → `DmgWing`
- Si tema coincide con `HornTheme` → `DmgHorn`
- Si tema coincide con `BackTheme` → `DmgBack`
- Si duda (tema no coincide pero BackSkill existe) → `DmgBack`, sino `DmgHorn`
- Si drenaje (`hit.IsDrain`) → no se cuenta en `DmgWing/Horn/Back`

## Limpieza de Strings CSV

Método `Clean()`: reemplaza `;` `/CR/LF` por espacios (CSV-safe).

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]
- [[BrawlBalanceDev]] — usa `MatchLine()` + `FighterLines()` para volcado

## Conexiones

**Eventos:**
- [[BrawlMatch]] — fases, roster, last stand, victoria
- [[BrawlFighter]] — vida, daño, muerte
- [[BrawlSkillCaster]] — cast de habilidades
- [[BrawlWing]] — ataques básicos y movilidad
- [[BrawlTheme]] — identificación de tema para desglose

**Generación:**
- [[BrawlBalanceDev]] — llama a `Arm()` y `MatchLine()`/`FighterLines()`

## Notas

- **Armed state**: `Arm()` es gate de grabación; si no está armado, eventos se ignoran silenciosamente.
- **Timeout**: `BrawlBalanceDev` llama a `ForceFinish()` si sobrepasa duración esperada.
- **No persistencia**: stats viven solo durante partida activa en memoria.
- **Formato CSV invariante**: `CultureInfo.InvariantCulture` para decimales (`.` no `,`).
- **Tema match**: `SameTheme()` compara tanto `Label` como `Icon` (evita falsos positivos).
