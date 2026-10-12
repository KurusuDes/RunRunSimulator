---
tags: [data, breeding, decor, database, scriptableobject]
---

# BreedingDecorDatabaseSO.cs

**Ruta:** `Data/Breeding/BreedingDecorDatabaseSO.cs`

**Responsabilidad:** Catalogo de decoraciones de cria. Lista de `BreedingDecorSO` con busqueda por Id. Es la fuente de orden para `DecorSlot` (el ciclo de un slot recorre esta lista en orden).

## Metodos Publicos

| Metodo | Retorna | Descripcion |
|--------|---------|-------------|
| `All` | `IReadOnlyList<BreedingDecorSO>` | Lista completa, en orden de catalogo |
| `Get(string id)` | `BreedingDecorSO` | Busca por Id. Null si vacio o no existe |

**Conexiones:** [[BreedingDecorSO]], [[BreedingController]] (expone `DecorDatabase`), [[DecorSlot]], [[IncubationService]]
