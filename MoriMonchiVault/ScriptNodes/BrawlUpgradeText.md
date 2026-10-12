---
tags: [script, ui, brawl, upgrade, text, static]
---

# BrawlUpgradeText.cs

**Ruta:** `UI/BrawlUpgradeText.cs`

**Responsabilidad:** Convierte un `BrawlUpgradeStep` en una línea de texto para la ficha (por ejemplo "+20 % · +1"). Clase estática sin estado. Solo arma el texto y lo traduce con `Loc.Tr`; no conoce la UI.

**Vinculado a:** [[Index/05 - UI System]], [[Index/32 - Demo Brawl 3v3 arcade]]

## Método Público

| Método | Descripción |
|--------|-------------|
| `Describe(step, family)` | Une los modificadores con ` · `. Devuelve `""` si el escalón es null o no tiene `Mods` |

## Formato

- Clave de traducción: `ui.upgrade.stat.<stat en minúscula>`.
- `Count` con familia `Chain`, `Nova` o `Ward` agrega el sufijo `.chain`, `.nova` o `.ward`. Otras familias o `null` usan la clave base.
- Multiplicador (`Multiply`): cambio porcentual, `(valor − 1) × 100`, redondeado, con signo y ` %`.
- Suma (`Add`), según el stat:
  - Duraciones (`Duration`, `SlowSeconds`, `StunSeconds`, `TauntSeconds`): segundos con ` s`, formato `0.#`.
  - `Slow`, `Haste`, `DamageBoost`: valor por 100 con ` %`.
  - `Count`, `Bounces`: entero.
  - Resto: formato `0.#`.
- Signo siempre visible: `+`, o `−` (U+2212) para negativos.

## Conexiones

- [[BrawlUpgradeStep]] — entrada
- [[BrawlEnums.cs]] — `BrawlUpgradeStat`, `BrawlUpgradeOp`, `BrawlSkillFamily`
- [[DetailEvolutionBlock]] — usa `Describe` para escalones aplicados, próximo escalón y resultado

## Notas

- Las claves `ui.upgrade.stat.*` y sus sufijos deben existir en las tablas de Localization.
