---
tags: [script, data, so]
---

# BrawlWingKitSO.cs

**Ruta:** `Data/Brawl/BrawlWingKitSO.cs`

**Responsabilidad:** SO de ala en Brawl. Define movimiento (locomoción, velocidad), ataque básico (tipo, rango, daño, velocidad proyectil, patrón), movilidad (tipo, distancia, enfriamiento) y curación aliada opcional. Un asset por ala (W0-W5: Vela, Colibrí, Aletas, Cintas, Plumitas, Murciélago).

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]] (sección "2 · Alas")

## Campos Principales

| Sección | Campo | Tipo | Descripción |
|---------|-------|------|-------------|
| **Identidad** | `PartId` | string | ID único del ala (ej. "W0", "W1") |
| | `Title` | string | Nombre legible (ej. "Vela", "Colibrí") |
| | `Description` | string | Descripción gameplay |
| | `IconOverride` | Sprite | Ícono custom; sino usa BodyPart.Icon |
| | `ColorOverride` | Color | Color custom (alpha 0 = usa Set.Color) |
| | `Signature` | BrawlSignature | Firma visual (Rainbow, Storm, etc.) |
| **Movimiento** | `Locomotion` | BrawlLocomotion | Ground (NavMesh) o Hover (libre 3D) |
| | `MoveSpeed` | float | Velocidad base (m/s) |
| **Ataque básico** | `Attack` | BrawlAttackKind | Tipo (Melee, Shotgun, Sniper, Boomerang, etc.) |
| | `Range` | float | Rango del ataque (metros) |
| | `Damage` | float | Daño por golpe |
| | `Windup` | float | Duración anticipación antes de disparar |
| | `Reload` | float | Enfriamiento entre ataques |
| | `Count` | int | # proyectiles por ataque |
| | `Spread` | float | Ángulo de spread en escopeta (grados) |
| | `Angle` | float | Ángulo del cono de fuego (0-360°) |
| | `ProjectileSpeed` | float | Velocidad de proyectil (m/s) |
| | `HitRadius` | float | Radio de colisión del proyectil |
| | `Knockback` | float | Fuerza de empuje |
| | `Slow` | float | % ralentización (0,0-0,9) |
| | `SlowSeconds` | float | Duración ralentización |
| | `SpriteSize` | float | Tamaño del ícono como proyectil |
| | `AttackAnim` | string | Nombre del anim de ataque |
| **Curación aliada** | `AllyHeal` | float | Curación por golpe a aliados (ej. Colibrí) |
| | `HealBelow` | float | Solo si aliado < X% vida (ej. 0,62 para 62%) |
| **Movilidad** | `Mobility` | BrawlMobilityKind | Tipo (Leap, Sprint, Roll, etc.) |
| | `MobilityDistance` | float | Distancia de desplazamiento |
| | `MobilitySeconds` | float | Duración de la movilidad |
| | `MobilityCooldown` | float | Enfriamiento entre usos |
| | `MobilityDamage` | float | Daño al impactar con movilidad |

## Referencia: Alas S142

| Ala | PartId | Locomotion | Attack | Heal? | Firma |
|-----|--------|-----------|--------|-------|-------|
| Vela | W0 | Ground | Boomerang | No | None |
| Colibrí | W1 | Hover | Burst | Sí (250 curacion, 62%) | None |
| Aletas | W2 | Ground | Shotgun | No | None |
| Cintas | W3 | Ground | Whip | No | None |
| Plumitas | W5 | Ground | Sniper | No | None |
| Murciélago | W4 | Ground | Melee | No | None |

## Dependencias

**Entrada:**
- Linkado en inspector en `BrawlKitDatabaseSO.Wings`
- Cargado por `BrawlKitDatabaseSO.Wing(partId)`

**Salida:**
- `BrawlFighter.WingKit` (asignado en SetWing)
- `BrawlWing` copia valores a instancia personal (stats del fighter)
- `BrawlBody` usa para VFX (tamaño sprite, patrón proyectil)
- `BrawlHudCard` muestra tema del ala
- `BrawlBrain` usa MoveSpeed para cálculos de distancia

## Notas S142

- Un asset por ala, editado en inspector
- No hay random: valores fijos determinan reproducibilidad
- Signature es puramente visual (raya arcoíris, tormenta, etc.) — no afecta daño
- AllyHeal (Colibrí) es mechanics especial: el ala básico cura aliados bajo threshold
- HealBelow evita waste (no cura al 99% de vida)
- AttackAnim permite custom animaciones por ala en future
