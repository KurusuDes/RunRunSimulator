---
tags: [script, world, brawl, skills, support]
---

# BrawlSkillSupport.cs

**Ruta:** `World/Brawl/BrawlSkillSupport.cs`

**Responsabilidad:** Ejecutores estáticos de habilidades de apoyo (4 familias). Pull (atracción + taunt), Zone (área de efecto), Ward (escudo), Mend (curación).

## Ejecutores Públicos

| Ejecutor | Entrada | Salida |
|----------|---------|--------|
| `Pull(cast)` | BrawlCast | Knockback + taunt + VFx remolino |
| `Zone(cast)` | BrawlCast | Spawn zona; throw VFx si delay |
| `Ward(cast)` | BrawlCast | Escudo propio + aliado; taunt rivales |
| `Mend(cast)` | BrawlCast | Curación dirección o área |

## Familias de Apoyo

### Pull (Señuelo)
- Atrae enemigos en radio a caster
- Aplica taunt (fuerza a atacar a caster)
- Damage bajo; knockback fuerte

### Zone (Lana, Cristales, Malvaviscos, LomoLana)
- Spawn `BrawlZone` con demora + duración
- Tick damage/heal cada `TickSeconds`
- Efecto: daño, curación, slow, stun, knockback, pull
- `FollowOwner` sigue al lanzador
- `HitOnArm` arma al lanzar (sin demora)

### Ward (Coraza, Placas, PuasDobles, AletasCara)
- Escudo al blanco (LowestAlly si aplica)
- Escudo secundario a aliado cercano (60 % escudo)
- Taunt a rivales en rango (provocación)
- No stack shields; usa máximo

### Mend (Alforja, Borla, Cresta, Unicornio)
- **LowestAlly:** Curación directa a aliado con mínima vida
- **Area:** Heal a todos aliados en zona; rayo de curación visual

## Búsquedas

Usa [[BrawlQuery]] para:
- `FoesWithin()` — enemigos en radio
- `LowestAlly()` — aliado con mínima vida
- `AlliesWithin()` — aliados en radio

## Curación Escala

- `HealFactor` del caster (puede ser modificado)
- Limitado a espacio disponible en vida máxima

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Entrada:**
- [[BrawlSkillEffects]] → `Execute(cast)` → routing

**Salida:**
- [[BrawlFighter]] → `ApplyTaunt()`, `AddShield()`, `Heal()`
- [[BrawlZone]] → `Spawn()` zonas
- [[BrawlFx]] → `Emit()` eventos visuales
- [[BrawlQuery]] — búsquedas de targets

## Notas

- BuddyShieldFactor 0,6 (escudo secundario 60 %)
- BeamSeconds 0,6 s duración de rayo de curación
- MinLobBlastRadius 1,2 m (mínimo zona de lob)
- PullMinDistance 0,1 m (mínimo para aplicar pull)
