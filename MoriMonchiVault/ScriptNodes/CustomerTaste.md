---
tags: [data, customers, taste, struct, npc]
---

# CustomerTaste.cs

**Ruta:** `Data/Customers/CustomerTaste.cs`

**Responsabilidad:** Gusto de un cliente sobre una criatura. Tres tipos (`TasteKind`): Role, Color o PartSet. `Roll` lo sortea del arquetipo y, con probabilidad `TasteFromDisplayChance`, lo copia de una criatura en exhibicion. `Match` devuelve 1 si la criatura cumple, 0 si no; `TasteKind.None` devuelve 0.5 (neutral). `Describe` arma el texto via `Loc`.

## Campos

| Campo | Tipo | Uso |
|-------|------|-----|
| `Kind` | `TasteKind` | Tipo de gusto. None = sin preferencia |
| `Role` | `Role` | Usado si Kind = Role |
| `Color` | `Color` | Usado si Kind = Color (distancia RGB < 0.35) |
| `Set` | `PartSetSO` | Usado si Kind = PartSet (cualquiera de las 3 partes pertenece al set) |

## Metodos Publicos

| Metodo | Retorna | Descripcion |
|--------|---------|-------------|
| `Match(CreatureDNA dna, CreatureDatabaseSO db)` | `float` (0, 0.5 o 1) | Puntua una criatura contra el gusto |
| `Describe()` | `string` | Texto localizado (`npc.taste.*`) |
| `static Roll(archetype, onDisplay, db)` | `CustomerTaste` | Sortea gusto desde arquetipo y exhibicion |

**Conexiones:** [[CustomerArchetypeSO]] (`Taste`, `TasteFromDisplayChance`), [[CreatureDNA]], [[CreatureDatabaseSO]], [[PartSetSO]], [[NpcAgent]] (`Taste`), [[Loc]], [[LocEnumMaps]]
