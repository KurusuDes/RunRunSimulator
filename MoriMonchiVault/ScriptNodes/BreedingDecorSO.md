---
tags: [data, breeding, decor, scriptableobject, odin]
---

# BreedingDecorSO.cs

**Ruta:** `Data/Breeding/BreedingDecorSO.cs`

**Responsabilidad:** Dato de una decoracion de cria (mueble de incubacion/cria comprable en tienda). Define identidad, precio, icono, prefab, tinte y los modificadores que alteran las probabilidades de herencia. Se descubre tras cierto numero de crias.

## Campos Publicos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `Id` | `string` | Identificador estable (persistencia en `WorldStateSO` por slot) |
| `DisplayName` | `string` | Nombre visible una vez descubierta |
| `Effect` | `string` (TextArea) | Descripcion del efecto para UI |
| `Price` | `int` | Precio en tienda |
| `Icon` | `Sprite` | Icono de tienda |
| `Prefab` | `GameObject` | Visual en el slot. Si es null, `DecorSlot` usa un cubo tintado |
| `Tint` | `Color` | Color del cubo fallback (`_BaseColor` via MPB) |
| `DiscoverAtBreeds` | `int` (Min 0) | Crias totales necesarias para revelar el nombre |
| `Modifiers` | `List<BreedingModifier>` | Deltas sobre pesos de herencia |

## Metodos Publicos

| Metodo | Retorna | Descripcion |
|--------|---------|-------------|
| `IsDiscovered(int bredTotal)` | `bool` | `bredTotal >= DiscoverAtBreeds` |

**Conexiones:** [[BreedingModifier]], [[BreedingOdds]] (consume los modificadores), [[BreedingDecorDatabaseSO]], [[DecorSlot]], [[PlayerInventorySO]], [[ShopCatalogSO]] (`DecorListings`), [[StoreManager]] (`BuyDecor`)
