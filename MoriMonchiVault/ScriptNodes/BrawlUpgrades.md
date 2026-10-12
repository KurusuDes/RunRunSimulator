---
tags: [script, data, brawl, upgrade, static]
---

# BrawlUpgrades.cs

**Ruta:** `Data/Brawl/BrawlUpgrades.cs`

**Responsabilidad:** Aplica los escalones de mejora por tier. Clase estática sin estado: calcula el tier máximo de una parte, devuelve copias mejoradas de `BrawlSkillSO` y `BrawlWingKitSO` (nunca muta el asset original) y calcula los multiplicadores de HP y velocidad del cuerpo.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Métodos Públicos

| Miembro | Descripción |
|---------|-------------|
| `MaxSteps = 3` | Máximo de escalones aplicables |
| `MaxLevel(steps)` | `1 + min(steps.Count, 3)`: tier máximo de la parte (1 a 4) |
| `Upgraded(BrawlSkillSO, level, owned)` | Si `level <= 1` o no hay escalones, devuelve el mismo asset. Si no, hace `Object.Instantiate`, copia el nombre, agrega la copia a `owned` y aplica los primeros `min(level - 1, count, 3)` escalones |
| `Upgraded(BrawlWingKitSO, level, owned)` | Igual que el anterior, para alas |
| `Body(steps, level, out hpMul, out speedMul)` | Multiplicadores acumulados de `Hp` y `MoveSpeed` del cuerpo. Base 1 |

## Reglas de Aplicación

- `Add` suma y `Multiply` multiplica. Los multiplicadores y sumas nunca bajan de 0.
- Solo se aplican los escalones hasta el nivel: nivel 3 aplica los escalones 0 y 1.
- Topes por campo:
  - Habilidad: `Angle` máximo 360; `Count` mínimo 1; `Bounces` mínimo 0; `Slow` entre 0 y 0,9.
  - Ala: `Angle` máximo 360; `Count` mínimo 1; `Slow` entre 0 y 0,9; `Reload` mínimo 0,05.
- `Pierce` pasa a `true` con un `Add` mayor que 0. No vuelve a `false`.
- `Count` y `Bounces` redondean con `Mathf.RoundToInt`.
- Los stats que no aplican a una parte se ignoran en silencio:
  - `Body` solo lee `Hp` y `MoveSpeed`.
  - La habilidad no cubre `AllyHeal`, `Reload`, `HitRadius`, `MoveSpeed` ni las `Mobility*`.
  - El ala no cubre `Heal`, `Shield`, `Duration`, `Cooldown`, `Radius`, `Haste`, `DamageBoost`, `Thorns`, `TauntSeconds`, `Bounces`, `Pierce`, `ExplodeRadius` ni `Hp`.

## Conexiones

- [[BrawlFighter]] — `Bind` llama `Upgraded` para ala, cuerno y espalda, y `Body` para HP y velocidad
- [[PartLevelUpEffectSO]] — usa `MaxLevel` para saber si una parte puede subir
- [[BrawlUpgradeStep]] — datos de cada escalón
- [[BrawlSkillSO]], [[BrawlWingKitSO]] — assets que se copian
- [[CreatureDNA]] — `WingTier`, `HornTier`, `BackTier` y `BodyTier` llegan aquí como `level`
- [[BrawlEnums.cs]] — `BrawlUpgradeStat`, `BrawlUpgradeOp`

## Notas

- Las copias se destruyen desde la lista `owned` (la `upgraded` de `BrawlFighter`) en cada re-`Bind` y en `OnDestroy`. Los SO de kit nunca se modifican.
- `Upgraded` toma el nombre del asset original para que la copia no aparezca como `(Clone)`.
