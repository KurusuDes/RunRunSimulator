---
tags: [script, data, scriptableobject, modular]
---

# ModularPieceSetSO.cs

**Ruta:** `Data/Modular/ModularPieceSetSO.cs`

**Responsabilidad:** ScriptableObject con el kit de piezas del armador modular "lego" (S165) sobre la grilla de POLYGON Fantasy Village. Guarda los prefabs de piso, muros, ventanas, puertas, pilares, zocalo, vigas y techo (filas, cierres, medias filas, presets por tamano) y los materiales exterior/interior/zocalo. Expone las constantes de medida (`Cell` 2,5 m, `Storey` 3 m, `RoofRise` 3 m, `PlinthHeight`, `PillarHalfHeight`, `RoofRiseHalf`) y los selectores `PickWindow`/`PickDoor` por variante. No instancia nada: solo es data que lee `ModularBuildingBuilder`.

## Campos publicos

- **Floor:** `GameObject Floor`, `Material[] FloorMaterials` (si no esta vacio, se aplica a las piezas de piso)
- **Walls:** `GameObject Wall`, `GameObject GableAngle`, `Material WallExterior`, `Material WallInterior`, `Material GableExterior` (fallback a WallExterior)
- **Openings:** `GameObject[] Windows`, `GameObject[] Doors`
- **Structure:** `GameObject Pillar`, `GameObject Beam`
- **Plinth:** `GameObject Plinth`, `Material PlinthMaterial`, `GameObject PillarHalf`
- **Roof:** `GameObject RoofRow`, `RoofEnd`, `RoofRowHalf`, `RoofEndHalf`, `GableAngleHalf`
- **Roof Presets:** `List<ModularRoofPreset> RoofPresets` (struct `ModularRoofPreset { Vector2Int Size; GameObject Prefab; }`)

## Constantes publicas

| Constante | Valor | Uso |
|-----------|-------|-----|
| `Cell` | 2.5 | Lado de celda de la grilla |
| `Storey` | 3 | Altura de piso (altura de viga) |
| `RoofRise` | 3 | Subida del techo por fila |
| `RoofRiseHalf` | 1.5 | Subida de la media fila central (lado impar) |
| `PlinthHeight` | 1.51 | Descenso del zocalo bajo el muro |
| `PillarHalfHeight` | 1.55 | Descenso de la media columna del zocalo |

## Metodos publicos

- `GameObject RoofPresetFor(Vector2Int size)` — devuelve el prefab del preset cuyo `Size` coincide (y tiene prefab asignado), o null
- `GameObject PickWindow(int variant)` — ventana por variante (modulo del largo del array), null si no hay
- `GameObject PickDoor(int variant)` — puerta por variante (modulo), null si no hay

## Invariantes

- Las constantes de medida son la fuente unica: el builder no tiene numeros magicos de celda/piso/techo.
- Variantes negativas se normalizan con `Mathf.Abs`.
- Piezas vacias no rompen el armado: el builder omite el spawn si el prefab es null.

## Vinculado a

[[Index/09 - Active Context]] (Session 165)

## Conexiones

- [[ModularBuildingBuilder]] (lee todos los campos y constantes para armar)
- [[ModularBuilding]] (referencia `PieceSet` y consulta `PickWindow`/`PickDoor`/`RoofPresetFor` via el builder)
- [[ModularBuildingEditor]] (no lo lee directamente)
