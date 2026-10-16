---
tags: [script, world, brawl, ai, brain]
---

# BrawlBrain.cs

**Ruta:** `World/Brawl/BrawlBrain.cs`

**Responsabilidad:** IA autónoma del combatiente. Personalidad (boldness, sociability) del DNA. Intención (Idle, Engage, Retreat, Cast, Heal, Protect, Hunt, Kite). Think cada `thinkInterval` (0,2 s). Elige blanco por score, decide postura (melé: strafe cerca; a distancia: kite o reposicionamiento), intenta habilidades vía `BrawlSkillJudge`, cohesiona con aliados y se retira cuando está dañado bajo umbral. No guarda referencias a otros sistemas fuera del combate: todo el movimiento pasa por `BrawlMotor` y `BrawlWing`.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Target` | `BrawlFighter` | Enemigo elegido |
| `Intent` | `BrawlIntent` | Estado de decisión (Idle, Engage, Retreat, Cast, Heal, Protect, Hunt, Kite) |
| `PostureLabel` | string | "Osado · protector" etc., armado con `BrawlLoc.Posture(stance, bond)` (S162) |
| `Boldness` | float | 0-1; osadía del DNA (clamp) |
| `Sociability` | float | 0-1; socialidad del DNA (clamp) |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Init(owner, tuningSo)` | Toma boldness y sociability del DNA (0,5 si no hay DNA), arma `PostureLabel` (stance: osado ≥ 0,65 / cauto ≤ 0,35 / parejo; bond: guardian ≥ 0,65 / solitario ≤ 0,35 / equipo), limpia intención y blanco, aleatoriza el primer think y el sentido del strafe |
| `Impatient(slot)` | `true` si la habilidad del slot lleva listo más de `PatienceSeconds` sin lanzarse (lo usa `BrawlSkillJudge`) |

## Método Think

Cada `thinkInterval`, si está vivo, no congelado, sin forzado ni casteando:
1. `TrackReadiness()` — marca desde cuándo está lista cada habilidad (para `Impatient`)
2. `TryCastSkill()` — prueba los slots listos con `BrawlSkillJudge.Want`
3. Invierte el sentido de strafe cada `StrafeFlipSeconds`
4. `TryHealAlly()` si el kit cura y hay aliado bajo umbral (Heal)
5. `SelectTarget()` — si no hay enemigo vivo, Idle
6. `ShouldRetreat()` → `Retreat()`; si no, `Reposition()` (elige Engage, Hunt, Kite o Protect según distancia y personalidad)
7. Ataque básico con `Wing.TryAttack` si está en rango y con línea de vista (a distancia)

## Comportamientos

### Selección de blanco
- Taunt vigente manda: el provocador es el blanco
- Si no, score por enemigo: mezcla de distancia propia y distancia al centroide del equipo (según sociability), más peso de HP del enemigo, y bonus negativo si amenaza al aliado más débil (`threatRadius`)
- Cambia de blanco solo si el nuevo supera al actual por `switchMargin`

### Engage / Hunt / Kite / Protect
- **Engage:** melé o dentro de `range × 1,3`
- **Hunt:** a distancia y poca sociabilidad (caza independiente)
- **Kite:** a distancia dentro de rango
- **Protect:** sociabilidad ≥ 0,65 y un aliado cerca del blanco

### Retreat (Retirada)
- HP bajo `RetreatHp` (lerp por boldness) y con enemigo dentro de `retreatFoeRange` (+ `retreatRelease` si ya estaba retirándose)
- Destino: centroide de aliados si está lejos, si no alejarse `retreatDistance` del blanco
- Usa movilidad de escape (rodar, saltar, blink, planear, sprint) si el kit la tiene

### Heal (Curación)
- Busca aliado bajo umbral (`HealBelow`, modulado por sociability) dentro de `range + 3`
- Se posiciona a `healStandoff` del aliado, del lado opuesto al enemigo más cercano a él

### Idle
- Sin blanco vivo: `Motor.Stop()`

## Strafe (Esgrima)

- Ángulo `StrafeAngle` con signo aleatorio; en melé escala por `meleeStrafeScale` (40 %)
- Cambia de sentido cada `StrafeFlipSeconds`
- Acercamiento circular alrededor del blanco hasta `pref` (`PreferredRange` por boldness; 0,75 × rango en melé)

## Cohesión

- Sociability > 0,5 con aliados: el punto de strafe se mezcla hacia el centroide del equipo
- Sociability ≥ 0,65 y aliado cerca del blanco: Protect
- Sociability baja: Hunt (caza independiente)

## Conexiones

**Dueño:**
- [[BrawlFighter]] — propietario; llama `Init` en `Bind`

**Entrada:**
- [[BrawlFighter]] — DNA para personalidad, HP, equipo, kit (`WingKit`), `Taunter`
- [[BrawlTuningSO]] — `StrafeFlipSeconds`, `PatienceSeconds`, `RetreatHp`, `PreferredRange`, `StrafeAngle`

**Salida:**
- [[BrawlMotor]] → `MoveTo()`, `Stop()`, `LookAt`
- [[BrawlWing]] → `TryAttack()`, `TryMobility()`
- [[BrawlSkillCaster]] → `TryCast()`, `IsReady(slot)`
- [[BrawlSkillJudge]] → `Want()` para decisiones de habilidad

**Consultas:**
- [[BrawlQuery]] — `AlliesCentroid`, `LowestAlly`, `NearestFoe`, `AlliesWithin`, `HasLineOfSight`, `Planar`
- `NavMesh.SamplePosition` — ajusta cada destino al navmesh (radio 2,5 m)
- [[BrawlLoc]] — `Posture` (S162)

## Notas

- thinkInterval 0,2 s por defecto (configurable)
- PostureLabel se forma en Init según boldness/sociability
- closeRange 2,6 m (distancia de cuerpo a cuerpo); melé si el kit es Melee o su rango es menor
- retreatDistance 6 m; retreatFoeRange 6 m
- Solo piensa si vivo, no congelado, no forzado, no casteando
- **S162:** `PostureLabel` pasa por `BrawlLoc.Posture` (loc de datos); la lógica de intención no cambió

## Estado

- MODIFICADO en S162 (documentacion puesta al dia: intenciones Protect/Hunt/Kite, `Init`, `Impatient`, flujo de Think, `BrawlLoc.Posture`)
