---
tags: [script, systems, localization, data]
---

# DataLoc.cs

**Ruta:** `Systems/Localization/DataLoc.cs`

**Responsabilidad:** Utilidad estática que resuelve nombres localizados de datos de juego (partes, mejoras, ítems, decoraciones, cajas). Prioriza la clave de `Loc`; si no existe, usa `DisplayName` y, si está vacío, el `Id`. No guarda estado.

## Métodos Públicos

| Método | Retorna | Clave `Loc` | Fallback |
|--------|---------|-------------|----------|
| `PartName(BodyPart p)` | `string` | `part.{ID}.name` | `p.Name` |
| `UpgradeName(ShopUpgradeSO u)` | `string` | `upgrade.{Id}.name` | `DisplayName` o `Id` |
| `ItemName(ItemDefinitionSO i)` | `string` | `item.{Id}.name` | `DisplayName` o `Id` |
| `DecorName(BreedingDecorSO d)` | `string` | `decor.{Id}.name` | `DisplayName` o `Id` |
| `BoxName(CreatureBoxSO b)` | `string` | `box.{Id}.name` | `DisplayName` o `Id` |

## Conexiones

**Entrada:** [[Loc]] (`Loc.Tr`), BodyPart, ShopUpgradeSO, ItemDefinitionSO, BreedingDecorSO, CreatureBoxSO.

**Consumidores:** capa de UI de tienda y ficha (nombres de mejoras, ítems, decoraciones y cajas), y de partes del MoriMochi.

## Invariantes

- Argumento null → cadena vacía.
- Clave no encontrada (`Loc.Tr` devuelve la misma clave) → fallback.
- Sin estado ni suscripciones.
