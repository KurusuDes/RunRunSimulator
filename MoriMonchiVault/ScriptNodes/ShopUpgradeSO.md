---
tags: [script, data, shop, upgrade]
---

# ShopUpgradeSO.cs

**Ruta:** `Data/Store/ShopUpgradeSO.cs`

**Responsabilidad:** Define una mejora de tienda comprable: nivel, precio por nivel, y bonus acumulativo. Modela la progresión de mejoras de infraestructura (vitrina ampliada, stock extra, etc). Lee el nivel actual de `WorldStateSO.UpgradeLevel(id)`.

**S138:** Nueva SO para el sistema de mejoras. Cada mejora tiene lista de precios (uno por nivel), multiplicador de bonus, y comprobación de si esta maxeada.

## Campos

- `Id` — Clave única en WorldState (no puede contener `-`)
- `DisplayName` — Etiqueta visual
- `LevelPrices` — Precio en Dabloons para cada nivel
- `BonusPerLevel` — Cantidad de bonus acumulativo por nivel

## Propiedades

- `MaxLevel` — Máximo nivel: `LevelPrices.Count`
- `CurrentLevel` — Nivel actual en WorldState
- `CurrentBonus` — Bonus en el nivel actual

## Métodos

- `IsMaxed(level)` — Comprueba si un nivel es >= MaxLevel
- `PriceFor(currentLevel)` — Precio para pasar a nivel siguiente (bounds-safe)
- `BonusAt(level)` — Bonus a un nivel dado (clampeado a 0..MaxLevel)

## Vinculado a

- [[Index/28 - Currency & Monetization]]

**Conexiones:** [[WorldStateSO]], [[ShopCatalogSO]], [[StoreManager]], [[GameManager]]
