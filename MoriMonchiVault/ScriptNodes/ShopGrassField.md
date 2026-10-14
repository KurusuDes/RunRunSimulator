---
tags: [script, world, store, graphics, mesh, procedural]
---

# ShopGrassField.cs

**Ruta:** `World/Store/ShopGrassField.cs`

**Responsabilidad:** Siembra pasto procedural en la tienda por **areas rectangulares** (no por forma de arena como `ArenaGrassField`). Cada `Area` (Rect en el plano XZ, Height en Y) se trocea en parcelas cuadradas de `chunkSize`; descarta candidatos bloqueados por `exclusions` y por colliders de `excludeColliderRoots` que esten por encima de la altura del area; muestrea densidad con `ArenaGrassCover.Sample()`; y arma una malla por parcela con `ArenaGrassBlades.Build()`. No usa `ArenaShape`, no suscribe eventos y no toca persistencia. Vive en `WORLD/ShopGrass` de GameScene con material `Materials/Shop/Grass/ShopGrassBlades.mat`.

**Campos serializados:**

**Semilla y Material:**
- `seed` (int, default 11) — semilla del `System.Random` compartido por todas las areas
- `bladeMaterial` (Material) — material de los chunks (`ShopGrassBlades.mat`)

**Parcelas:**
- `chunkSize` (float, Min 2, default 5) — tamano de parcela cuadrada
- `maxBlades` (int, default 150000) — tope global de briznas entre todas las areas

**Areas:**
- `areas` (List&lt;Area&gt;) — cada `Area` es un struct con:
  - `Name` (string) — etiqueta para el inspector
  - `Rect` (Rect, XZ) — `x` = X, `y` = Z del rectangulo
  - `Height` (float) — altura Y donde nace el pasto
  - `Density` (float) — briznas candidatas por unidad²; si `<= 0` o Rect vacio, el area se salta
  - `HeightRange` / `WidthRange` (Vector2) — rangos de brizna
  - `Tilt` (float) — inclinacion maxima
  - `Segments` (int) — segmentos por brizna; no tiene tope superior en este script (`ArenaGrassBlades.Build` solo garantiza minimo 1, asi que el default 0 del struct se trata como 1)
  - `Cover` (ArenaGrassCover.Settings) — si `clumpSpacing <= 0`, se usa `ArenaGrassCover.Settings.Default`

**Exclusiones:**
- `exclusionMargin` (float, default 0.4) — margen alrededor de colliders bloqueantes
- `exclusions` (List&lt;Rect&gt;, XZ) — rectangulos fijos donde no nace pasto
- `excludeColliderRoots` (List&lt;Transform&gt;) — raices cuyos colliders habilitados (y `GetComponentsInChildren`) bloquean pasto

**Metodos publicos:**

- **`void Sow()`** — boton `[Button("Sembrar")]` en el inspector; regenera todo el pasto.

**Metodos privados:**

**Sow() (OnEnable, boton Sembrar, y OnValidate en edit mode via delayCall):**

1. `DestroyGrassField()` — limpia la siembra anterior
2. Valida `bladeMaterial != null` y `areas.Count > 0`
3. Crea GameObject `GrassField` (hideFlags DontSave) hijo de este transform
4. `rng = new System.Random(seed)`; `colliders = CollectColliders()`
5. Por cada area valida (Rect con ancho/alto > 0 y Density > 0):
   - Elige `cover` (area.Cover o Default)
   - `blocked = BuildBlockedRects(area, colliders)` → exclusions + AABB de colliders con `bounds.max.y > area.Height + 0.05`, expandidos por `exclusionMargin`
   - Itera parcelas `chunkSize` dentro del Rect (la ultima se recorta con `Mathf.Min`)
   - Filtra los bloqueados que tocan la parcela (`nearBlocked`)
   - Genera `round(Density * w * h)` candidatos: descarta si cae en bloqueado; `ArenaGrassCover.Sample()` da densidad y heightScale; descarta si `rng.NextDouble() >= density`
   - Recorta al tope global `maxBlades` (retorna si ya no quedan)
   - `ArenaGrassBlades.Build(roots, rng, HeightRange, WidthRange, Tilt, chunkCenter, heights, Segments)`
   - Crea chunk GameObject con MeshFilter + MeshRenderer (sharedMaterial, sin sombra emitida, recibe sombras)

**DestroyGrassField():**
- Destruye el GameObject `grassField` y cualquier hijo `GrassField` historico; libera las mallas con `DestroyImmediate`

**DestroyChunks(Transform field):**
- Libera el `sharedMesh` de cada chunk hijo

**CollectColliders() / BuildBlockedRects() / IsBlocked():**
- Helpers de bloqueo descritos arriba

**OnValidate() (editor-only):**
- En edit mode: `EditorApplication.delayCall` → `SowIfAlive` (preview en vivo)

**Invariantes:**

- **Determinismo por seed:** un unico RNG se comparte entre areas y parcelas, en orden fijo. Cambiar la densidad o el numero de candidatos de un area mueve la secuencia de todas las areas siguientes.
- **Solo bloquean colliders altos:** un collider cuyo techo no supera `Height + 0.05` (suelo, piso) no genera exclusion.
- **Coordenadas:** `Rect` esta en XZ; la altura viene de `Height`; las mallas se posicionan en `chunkCenter` (origen local por chunk).
- **Tope global:** `maxBlades` cuenta entre todas las areas, no por area.
- **Sin eventos ni persistencia:** no suscribe `GameEvents`, no toca `GameManager` ni `SaveSystem`. Es decoracion pura.
- **Sin ClearAround:** a diferencia de `ArenaGrassField`, no hay huella de pasos; el pasto de tienda no se pisa.
- **Destruccion:** chunks con `hideFlags.DontSave`; mallas destruidas al resembrar y en OnDisable.

**Shader asociado:** `Shaders/ArenaGrass.shader`, compartido con la arena. Desde S154 tiene rafagas (`_Gust*`), manchas (`_Patch*`), translucidez de punta (`_TipGlow*`) y trample seguro: si `_ArenaTrampleArea.z <= 0` no hay pisotado.

**Estado:** NUEVO en S154.

**Conexiones:** [[ArenaGrassBlades]], [[ArenaGrassCover]], [[ArenaGrassField]] (hermano de la arena; misma tecnica de chunks, distinta fuente de area)

**Vinculado a:** [[Index/06 - Player & World]], S154
