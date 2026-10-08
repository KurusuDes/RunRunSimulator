---
tags: [script, data, so]
---

# BrawlSkillSO.cs

**Ruta:** `Data/Brawl/BrawlSkillSO.cs`

**Responsabilidad:** SO de habilidad (cuerno o espalda) en Brawl 3v3. Define lanzamiento (windup, cooldown, casteo, tracking), alcance y área, efectos (daño, curación, escudo, duración), estados (slow, stun, haste, boost, etc.), proyectil y firma visual. Un asset por parte (33 skills: 10 familias × 3-5 partes cada una).

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]] (sección "3 · Cuernos y espaldas")

## Campos Principales

| Sección | Campo | Tipo | Descripción |
|---------|-------|------|-------------|
| **Identidad** | `PartId` | string | ID único (ej. "H1", "B2") |
| | `Slot` | ClashSlot | Horn o Back |
| | `Title` | string | Nombre legible |
| | `Description` | string | Descripción gameplay |
| | `IconOverride` | Sprite | Ícono custom |
| | `ColorOverride` | Color | Color custom |
| | `Signature` | BrawlSignature | Rainbow, Storm, Cloud, Comet, Lure, Plates, etc. |
| **Clasificación** | `Family` | BrawlSkillFamily | Dash, Chain, Cone, Shot, Nova, etc. |
| | `Role` | BrawlSkillRole | Offense, Control, Support, Tank |
| | `Target` | BrawlSkillTarget | Enemy, EnemyCluster, Self, LowestAlly, AlliesAround |
| **Lanzamiento** | `Windup` | float | Duración anticipación (segundos) |
| | `Cooldown` | float | Enfriamiento tras casting |
| | `FirstDelay` | float | Delay de primer proyectil relativo a windup (0-1) |
| | `RootWhileCasting` | bool | Si se bloquea movimiento durante casteo |
| | `TracksTarget` | bool | Si el proyectil sigue al objetivo |
| | `CastAnim` | string | Nombre del anim de casteo |
| | `FireAnim` | string | Nombre del anim de disparo |
| **Alcance y área** | `Range` | float | Rango máximo de ataque |
| | `Radius` | float | Radio del área de efecto |
| | `Angle` | float | Ángulo del barrerido/cono (0-360) |
| **Efecto** | `Damage` | float | Daño directo |
| | `Heal` | float | Curación (aliados) |
| | `Shield` | float | Escudo (aliados) |
| | `Duration` | float | Duración del efecto (zonas, duraciones) |
| | `Delay` | float | Delay antes de aplicar efecto |
| | `TickSeconds` | float | Intervalo de tick (DOT, HoT) |
| | `Count` | int | # de proyectiles o ticks |
| | `Speed` | float | Velocidad de proyectil (m/s) |
| | `Knockback` | float | Fuerza de empuje |
| **Estados** | `Slow` | float | % ralentización (0-0,9) |
| | `SlowSeconds` | float | Duración ralentización |
| | `StunSeconds` | float | Duración aturdimiento |
| | `Haste` | float | % velocidad bonus |
| | `DamageBoost` | float | % daño bonus |
| | `Thorns` | float | Daño de retorno |
| | `TauntSeconds` | float | Duración provocación (atrae a atacante) |
| **Proyectil y visual** | `Bounces` | int | # rebotes antes de desaparecer |
| | `Pierce` | bool | Si pasa a través de objetivos |
| | `ExplodeRadius` | float | Radio de explosión (0 = sin explosión) |
| | `SpriteSize` | float | Tamaño del ícono como proyectil |
| | `FollowCaster` | bool | Si el proyectil sigue al lanzador |

## Familias de Habilidad (10 tipos)

| Familia | Efecto | Ejemplo Partes |
|---------|--------|---|
| Dash | Embestida en línea, empuja/aturde | Ariete, Carnero, Rinoceronte |
| Chain | Rayo que salta entre rivales | Rayo, Antenas |
| Cone | Barrerido en cono (360° = giro) | Astas, Cola, Hoz |
| Shot | Proyectil fuerte (rebota/atraviesa/estalla) | Cometa, Cristal, Mechón |
| Nova | Púas en todas direcciones | Espinas, PuasFinas |
| Homing | Proyectiles que persiguen | Cometitas |
| Pull | Atrae y provoca | Señuelo |
| Zone | Área con demora/duración (sueño, lluvia, curación) | Lana, Malvaviscos, Cristales |
| Ward | Escudo propio o aliado, espinas | AletasCara, Coraza, Placas |
| Mend | Cura o potencia aliados | Unicornio, Alforja, Borla, Cresta |

## Roles y Arquetipos

| Rol | Decisión de IA | Ejemplo |
|-----|---|---|
| Offense | Atacar si en rango | Dash, Shot, Nova (daño puro) |
| Control | Frenar/crowd control | Cone, Zone (ralentiza, aturde) |
| Support | Curar/escudar aliados | Ward, Mend (soporte) |
| Tank | Provocar/mantener agresión | Pull (Señuelo), Ward (escudo) |

## Dependencias

**Entrada:**
- Linkado en inspector en `BrawlKitDatabaseSO.Skills`
- Cargado por `BrawlKitDatabaseSO.Skill(partId, slot)` (búsqueda primero por partId, luego por slot fallback)

**Salida:**
- `BrawlFighter.HornSkill` / `BackSkill` (asignado en SetHornSkill/SetBackSkill)
- `BrawlSkillCaster` ejecuta casting (windup, cooldown, targeting)
- `BrawlSkillEffects` calcula daño/curación/estados
- `BrawlBrain.SkillJudge` evalúa cuándo castear (según Role)
- `BrawlHudCard.PulseSkill()` visualiza cooldown en slot
- `BrawlOverheads.HandleCastStarted()` muestra bubble con título

## Notas S142

- Un asset por parte (no hay skill "default" — fallback es skill=null)
- Familia determina geometría de raycast (rayo, cono, línea, etc.)
- Signature puramente visual pero consistente (ej. Unicornio y Borla = Rainbow)
- TracksTarget y FollowCaster se usan en paralelo (ej. rayo persigue pero también sigue al lanzador)
- ExplodeRadius > 0 convierte proyectil en explosión (Shot family)
- TickSeconds para DoT (daño continuado) y HoT (curación continuada)
- TauntSeconds hace que objetivo ataque al lanzador (mechanic de control)
- SpriteSize escala el ícono en representación visual (proyectil, VFX)
