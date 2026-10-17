---
tags: [script, editor, modular, tooling]
---

# ModularBuildingBuilder.cs

**Ruta:** `Editor/ModularBuildingBuilder.cs`

**Responsabilidad:** Herramienta de editor (S165) que arma o limpia un `ModularBuilding` en escena. Lee el `ModularPieceSetSO` y las aberturas del componente y spawnea prefabs como hijos de `_Armado` en la grilla de celdas de 2,5 m con piso de 3 m: piso, muros con ventanas/puertas, zocalo, pilares, vigas, techo a dos aguas (filas, cierres, medias filas impares y frentes a dos aguas) o preset de techo por tamano. Asigna materiales exterior/interior segun la orientacion real de la malla. Todo queda en Undo y marca la escena dirty. Es tooling dev: no toca gameplay ni persistencia.

## Metodos publicos

- `static void Build(ModularBuilding b)` — limpia el armado previo y genera todas las piezas segun flags y aberturas. Avisa con `LogWarning` si no hay `PieceSet`.
- `static void Clear(ModularBuilding b)` — destruye el hijo `_Armado` (con Undo) si existe.

## Metodos privados clave

- `BuildRoof(...)` — techo a dos aguas: filas por nivel (`rise` por fila), cierres a los extremos, media fila si el ancho es impar, y frentes de muro/angulo por fila. Si `UsePresetRoof` y hay preset para el tamano, `Build` usa el preset en vez de esto.
- `Place(w, d, side, index, y) → (pos, yaw)` — posicion y rotacion de una pieza sobre un borde.
- `Spawn(prefab, parent, label, pos, yaw, scale)` — `PrefabUtility.InstantiatePrefab`, renombra `prefab_label`, registra Undo. Devuelve null si el prefab es null (omite sin fallar).
- `SpawnWall(...)` — spawn de muro + asignacion de materiales. Decide cual submalla es exterior con `FirstSubmeshFacesPlusZ`, que invierte el orden si la malla mira a +Z.
- `FirstSubmeshFacesPlusZ(Mesh)` — promedia normales Z de la primera submalla; resultado cacheado en `facesPlusZCache` (por Mesh). Requiere mesh legible; si no lo es, asume no invertido.
- `SetMaterials(go, mats)` — aplica `sharedMaterials` a todos los Renderer hijos.

## Campos internos

- `facesPlusZCache` — `Dictionary<Mesh, bool>` estatico, cache del chequeo de orientacion por malla

## Invariantes

- Solo se usa en editor (`UnityEditor`, `EditorSceneManager`, `PrefabUtility`); no debe compilarse en runtime.
- Las aberturas de un borde se leen con `ModularBuilding.OpeningAt`; un borde con abertura `Open` no genera muro, zocalo ni viga en esa celda.
- Los nombres de pieza siguen el patron `side_Tipo_n` (usado para leer/depurar en la jerarquia).

## Vinculado a

[[Index/09 - Active Context]] (Session 165)

## Conexiones

- [[ModularBuilding]] (componente que arma; lee `SizeCells`, flags, `Edges`, `PieceSet`)
- [[ModularPieceSetSO]] (kit de piezas, constantes de medida, presets)
- [[ModularBuildingEditor]] (unico llamador: botones Armar/Limpiar)
