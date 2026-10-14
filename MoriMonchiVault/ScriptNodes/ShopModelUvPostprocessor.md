---
tags: [script, editor, import, shop, postprocessor]
---

# ShopModelUvPostprocessor.cs

**Ruta:** `Scripts/Editor/ShopModelUvPostprocessor.cs` (namespace `MoriMonchiSimulator`)

**Responsabilidad:** `AssetPostprocessor` que solo actúa sobre los FBX de `Assets/RunRunSimulator/Resources/Models/Shop/`. Garantiza que las mallas de la tienda sean legibles y tengan UV0 válido, para que el shader Toon no pinte negras las caras con tangentes degeneradas.

**Métodos:**
- `OnPreprocessModel()` — fuerza `ModelImporter.isReadable = true` en la carpeta Shop.
- `OnPostprocessModel(GameObject root)` — recorre los `MeshFilter` hijos (incluidos inactivos) y genera UV0 en las mallas que no tienen UV.
- `static GenerateBoxUv(Mesh)` — proyección de caja por triángulo: eje dominante de la normal de la cara (cross product) elige el plano (`ZY` / `XZ` / `XY`). Des-indexa los triángulos (vértices propios por triángulo), conserva normales si existen, mantiene submeshes, recalcula bounds y tangentes.

**Invariantes:**
- Solo actúa si `assetPath` empieza por `ShopFolder`; el resto de modelos del proyecto no se toca.
- Se saltea cualquier malla con `mesh.uv.Length > 0` (no pisa UV de Blender/DCC).
- Des-indexar implica más vértices; `indexFormat` pasa a UInt32 si superan 65535.
- Corre en importación (Editor), no en runtime.

**Motivo (S153):** los FBX de Blender sin UV dejaban las tangentes paralelas a la normal y el shader Toon pintaba negras las caras +X.

**Vinculado a:** [[Index/35 - Crecimiento de la tienda y Outer World]] · pipeline `Tools/Blender/props/README_props.md`

**Conexiones:** ninguna en código de gameplay. Afecta a los prefabs de tienda (`Resources/Models/Shop/`) generados desde `Tools/Blender/props/` (`shop_corral.py`, `shop_incubator.py`, `shop_pc.py`).
