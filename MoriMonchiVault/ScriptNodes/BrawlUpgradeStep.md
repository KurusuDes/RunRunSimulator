---
tags: [script, data, brawl, upgrade]
---

# BrawlUpgradeStep.cs

**Ruta:** `Data/Brawl/BrawlUpgradeStep.cs`

**Responsabilidad:** Modelo de un escalón de mejora de una parte Brawl. Un `BrawlUpgradeStep` es una lista de modificadores (`BrawlUpgradeMod`) que se aplican juntos al subir de tier. Datos puros y serializables, sin lógica: la aplicación vive en `BrawlUpgrades` y el texto en `BrawlUpgradeText`.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Tipos

**`BrawlUpgradeMod`** (struct, serializable):

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Stat` | `BrawlUpgradeStat` | Estadística a modificar |
| `Op` | `BrawlUpgradeOp` | `Add` (suma) o `Multiply` (factor) |
| `Value` | `float` | Operando: suma en unidades del campo, o factor (1,2 = +20 %) |

**`BrawlUpgradeStep`** (class, serializable):

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Mods` | `List<BrawlUpgradeMod>` | Modificadores del escalón; inicia vacío |

## Dónde se usa

- `BrawlSkillSO.Upgrades` y `BrawlWingKitSO.Upgrades`: escalones de cada habilidad o ala.
- `BrawlKitDatabaseSO.BodyUpgrades`: escalones del cuerpo (solo HP y velocidad).
- El escalón de índice `i` (0-based) es el que se aplica al llegar al tier `i + 2`. El tier 1 es la base y no tiene escalón.

## Conexiones

- [[BrawlUpgrades]] — aplica los `Mods` a copias de SO y al cuerpo
- [[BrawlUpgradeText]] — describe el escalón en la ficha
- [[BrawlKitDatabaseSO]], [[BrawlSkillSO]], [[BrawlWingKitSO]] — dueños de las listas
- [[BrawlEnums.cs]] — `BrawlUpgradeStat`, `BrawlUpgradeOp`

## Notas

- El nombre del archivo declara también `BrawlUpgradeMod`; no hay un archivo aparte para el struct.
