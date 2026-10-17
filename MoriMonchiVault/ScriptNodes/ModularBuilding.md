---
tags: [script, world, modular, component]
---

# ModularBuilding.cs

**Ruta:** `World/Modular/ModularBuilding.cs`

**Responsabilidad:** Componente de escena que describe un edificio modular "lego" (S165) sobre la grilla de POLYGON Fantasy Village: tamano en celdas, set de piezas, flags de construccion (piso, techo, zocalo, preset de techo) y la lista de aberturas por borde. No arma nada por si mismo: el armado vive en `ModularBuildingBuilder` (editor) y se dispara desde `ModularBuildingEditor` con los botones Armar/Limpiar. Los objetos generados cuelgan del hijo `_Armado`.

## Campos serializados

| Campo | Tipo | Atributos | Descripcion |
|-------|------|-----------|-------------|
| `PieceSet` | `ModularPieceSetSO` | — | Kit de piezas que usa el armado |
| `SizeCells` | `Vector2Int` | `[MinValue(1)]`, default (4, 4) | Ancho x fondo en celdas |
| `BuildFloor` | `bool` | default true | Genera piso |
| `BuildRoof` | `bool` | default true | Genera techo |
| `UsePresetRoof` | `bool` | default true | Usa preset de techo si existe para el tamano |
| `BuildPlinth` | `bool` | default true | Genera zocalo y medias columnas |
| `Edges` | `List<ModularEdge>` | — | Aberturas por borde; los bordes no listados son muro liso |

**Tipos asociados (mismo archivo):**

- `enum ModularSide { South, East, North, West }`
- `enum ModularOpening { Wall, Window, Door, Open }`
- `struct ModularEdge { ModularSide Side; int Index; ModularOpening Opening; int Variant; }` (`Index` con `[MinValue(0)]`)

## Metodos publicos

- `ModularOpening OpeningAt(ModularSide side, int index, out int variant)` — busca la entrada de `Edges` para ese borde/indice; si no existe devuelve `Wall` con variante 0

## Constantes

- `GeneratedName = "_Armado"` — nombre del hijo raiz donde el builder deja todas las piezas generadas

## Invariantes

- Las piezas generadas son hijas de `_Armado`; `Clear` las borra por nombre, y `Build` siempre limpia antes de armar (re-armar no duplica).
- Ningun script de runtime lee este componente: es solo authoring de escena (no entra al flujo de juego ni a persistencia).

## Vinculado a

[[Index/09 - Active Context]] (Session 165)

## Conexiones

- [[ModularPieceSetSO]] (kit de piezas, `PieceSet`)
- [[ModularBuildingBuilder]] (lee el componente y genera las piezas)
- [[ModularBuildingEditor]] (Inspector Odin con botones Armar/Limpiar)
