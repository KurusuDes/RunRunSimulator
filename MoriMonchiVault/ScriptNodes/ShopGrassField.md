---
tags: [script, world, store, graphics, mesh, procedural, flowers, relief]
---

# ShopGrassField.cs

**Ruta:** `World/Store/ShopGrassField.cs`

**Responsabilidad:** Siembra pasto y flores procedurales en la tienda por **areas rectangulares** (no por forma de arena como `ArenaGrassField`). Cada `Area` (Rect en el plano XZ, Height en Y) se trocea en parcelas cuadradas de `chunkSize`. Por parcela genera dos mallas independientes: briznas (`SowGrassChunk` → `ArenaGrassBlades.Build()`) y flores (`SowFlowerChunk` → `MeadowFlowers.Build()`). Descarta candidatos bloqueados por `exclusions` (con `exclusionInset`) y, si `blockByColliders` esta activo, por colliders de `excludeColliderRoots` que esten por encima de la altura del area. **S155:** suaviza los bordes del area con `EdgeFade` (`EdgeSmooth`) y permite material propio por area. **S162:** la Y de cada raiz sale del relieve (`ReliefY`, raycast contra `reliefRoot`). No usa `ArenaShape`, no suscribe eventos y no toca persistencia.

Vive en `WORLD/ShopGrass` de GameScene. Material de fallback `Materials/Shop/Grass/ShopGrassBlades.mat`. El relieve de la tienda vive en `WORLD/ShopRelief`.

**Campos serializados:**

**Semilla y Material:**
- `seed` (int, default 11) — semilla base. De ella salen tres `System.Random` independientes: `seed` (briznas), `seed + 7` (borde de briznas) y `seed + 13` (flores). Los hash de cluster de flores usan `seed` (presencia) y `seed + 101` (color).
- `bladeMaterial` (Material) — material de fallback de los chunks; cada area puede sobreescribirlo con `Area.Material`

**Parcelas:**
- `chunkSize` (float, Min 2, default 5) — tamano de parcela cuadrada
- `maxBlades` (int, default 150000) — tope global de briznas entre todas las areas; **no cuenta flores**

**Areas:**
- `areas` (List&lt;Area&gt;) — cada `Area` es un struct con:
  - `Name` (string) — etiqueta para el inspector
  - `Rect` (Rect, XZ) — `x` = X, `y` = Z del rectangulo
  - `Height` (float) — altura Y base donde nace el pasto y las flores (el relieve la puede subir)
  - `Density` (float) — briznas candidatas por unidad²; si `<= 0` o Rect vacio, el area se salta
  - `HeightRange` / `WidthRange` (Vector2) — rangos de brizna
  - `Tilt` (float) — inclinacion maxima
  - `Segments` (int) — segmentos por brizna; `ArenaGrassBlades.Build` lo clampa a minimo 1
  - `Cover` (ArenaGrassCover.Settings) — si `clumpSpacing <= 0`, se usa `ArenaGrassCover.Settings.Default`
  - **S155:** `Material` (Material) — material de los chunks (briznas y flores) de esta area; si es null, usa `bladeMaterial`
  - **S155:** `EdgeFade` (float) — ancho del degradado en el borde del area; `0` lo desactiva
  - **S155:** `FlowerDensity` (float) — flores candidatas por unidad²; `0` = el area no tiene flores

**Flores (S155):**
- `flowerColors` (List&lt;Color&gt;) — paleta; cada cluster toma un color por hash de celda. Default: crema, amarillo, lila, celeste, rosa pastel. Lista vacia = sin flores
- `flowerClusterSize` (float, default 3.5) — lado de la celda que agrupa flores
- `flowerClusterChance` (float 0..1, default 0.45) — probabilidad de que una celda tenga flores
- `flowerStemHeight` (Vector2, default 0.18–0.32) — rango de altura de tallo
- `flowerHeadSize` (Vector2, default 0.05–0.08) — rango de radio de cabeza

**Exclusiones:**
- `exclusionMargin` (float, default 0.4) — margen alrededor de colliders bloqueantes
- `exclusions` (List&lt;Rect&gt;, XZ) — rectangulos fijos donde no nace pasto ni flores
- **S162:** `exclusionInset` (float, Min 0, default 0.5) — se resta a cada lado de los rects de `exclusions` antes de bloquear (solo si el rect es mayor que 2 × inset)
- `excludeColliderRoots` (List&lt;Transform&gt;) — raices cuyos colliders habilitados (y `GetComponentsInChildren`) bloquean
- **S162:** `blockByColliders` (bool, default `false`) — si esta apagado, `excludeColliderRoots` no bloquea nada; el bloqueo por colliders quedo como opcion y la mascara de la tienda (`ShopGrassMask`) cubre el caso normal

**Relieve (S162):**
- `reliefRoot` (Transform) — raiz de los colliders de relieve (`WORLD/ShopRelief`, montículos de PolygonNature). Solo cuentan colliders habilitados y no trigger

**Metodos publicos:**

- **`void Sow()`** — boton `[Button("Sembrar")]` en el inspector; regenera todo el pasto y las flores.
- **`IReadOnlyList<Rect> Exclusions`** — expone `exclusions` (lectura).

**Metodos privados:**

**Sow() (OnEnable, boton Sembrar, y OnValidate en edit mode via delayCall):**

1. `DestroyGrassField()` — limpia la siembra anterior
2. Valida `bladeMaterial != null` y `areas.Count > 0`
3. Crea GameObject `GrassField` (hideFlags DontSave) hijo de este transform
4. Crea `rng` (seed), `rngEdge` (seed + 7), `rngFlower` (seed + 13); `colliders = blockByColliders ? CollectColliders() : vacio`; **S162:** `reliefColliders = CollectReliefColliders()`
5. Por cada area valida (Rect con ancho/alto > 0 y Density > 0 para el pasto; FlowerDensity > 0 para flores):
   - Elige `cover` (area.Cover o Default) y `material` (area.Material o `bladeMaterial`)
   - `blocked = BuildBlockedRects(area, colliders)` → exclusions (con inset) + AABB de colliders con `bounds.max.y > area.Height + 0.05`, expandidos por `exclusionMargin`
   - `fade = max(0, EdgeFade)`
   - Itera parcelas `chunkSize` dentro del Rect (la ultima se recorta con `Mathf.Min`)
   - Filtra los bloqueados que tocan la parcela expandida por `fade` (`nearBlocked`)
   - Si `totalBlades < maxBlades`: `SowGrassChunk(...)` y suma su retorno
   - Si `FlowerDensity > 0`: `SowFlowerChunk(...)` — **siempre**, aunque ya se haya llegado al tope de briznas

**SowGrassChunk(...) → int (S155, extraido de Sow):**
- Genera `round(Density * w * h)` candidatos con `rng`; descarta los bloqueados y los que fallan `ArenaGrassCover.Sample()` (`rng.NextDouble() >= density`)
- Si `EdgeFade > 0`: `s = EdgeSmooth(...)`; descarta con `rngEdge` segun `Lerp(0.35, 1, s)` y escala la altura por `Lerp(0.3, 1, s)`
- **S162:** la raiz toma `Y = ReliefY(x, z, Height)`; la altura base se mantiene si no hay relieve debajo
- Recorta al `remaining` del tope global `maxBlades`
- `ArenaGrassBlades.Build(...)` → `CreateChunk("GrassChunk", ...)`; retorna la cantidad de briznas

**SowFlowerChunk(...) (S155):**
- Sale sin hacer nada si `flowerColors` esta vacia
- Genera `round(FlowerDensity * w * h)` candidatos con `rngFlower`; descarta los bloqueados
- **Clusters:** celda de `flowerClusterSize` por `(floor(x/s), floor(z/s))`; si `CellHash(celda, seed) >= flowerClusterChance` la celda queda vacia
- **Densidad radial:** dentro de la celda se acepta mas cerca del centro (`rngFlower.NextDouble() <= 1 - distancia/(0.5 * s)`)
- Si `EdgeFade > 0` y `EdgeSmooth < 0.6`, descarta (las flores no nacen en el borde suave)
- **Color:** un color por celda, `flowerColors[CellHash(celda, seed + 101) * count]`, con brillo por flor `Lerp(0.92, 1.05)` (el alpha se fija en 1 aca y `MeadowFlowers` lo pisa a 0)
- **S162:** raiz con `Y = ReliefY(...)`
- `MeadowFlowers.Build(roots, colors, rngFlower, flowerStemHeight, flowerHeadSize, chunkCenter)` → `CreateChunk("FlowerChunk", ...)`

**EdgeSmooth(point, area, nearBlocked) → float (S155):**
- Distancia efectiva = minimo entre `fade` y la distancia al bloqueo mas cercano (`DistanceToRect`)
- En las 4 direcciones cardinales avanza de a `EdgeStep` (0.25) hasta salir de cualquier area a la misma altura (`InsideAnyArea`) y usa esa distancia si es menor
- Normaliza por `EdgeFade` y aplica smoothstep (0 = borde, 1 = interior)

**InsideAnyArea(point, height) (S155):** ignora areas con Density 0 o Rect vacio y las de otra altura (`|Height - height| >= 0.1`).

**CellHash(x, z, salt) → float (S155, static):** hash entero de finalizador tipo murmur, normalizado a `[0, 1)`. Es determinista por celda y salt.

**CreateChunk(name, mesh, material, position) (S155):** GameObject hijo de `grassField` con MeshFilter + MeshRenderer (sharedMaterial, sin sombra emitida, recibe sombras). Lo usan briznas y flores.

**DestroyGrassField():** destruye el GameObject `grassField` y cualquier hijo `GrassField` historico; libera las mallas con `DestroyImmediate`.

**DestroyChunks(Transform field):** libera el `sharedMesh` de cada chunk hijo (briznas y flores).

**CollectColliders() / CollectReliefColliders() / ReliefY() (S162) / BuildBlockedRects() / IsBlocked() / DistanceToRect():** helpers de bloqueo, relieve y distancia descritos arriba. `ReliefY` lanza un rayo desde `baseHeight + 20` hacia abajo (40 m) contra los colliders de relieve y devuelve la Y mas alta encontrada, nunca menor que `baseHeight`.

**OnValidate() (editor-only):** en edit mode, `EditorApplication.delayCall` → `SowIfAlive` (preview en vivo).

**Invariantes:**

- **Determinismo por seed:** tres RNG independientes (briznas, borde, flores), cada uno en orden fijo. Cambiar la densidad o el numero de candidatos de un area mueve la secuencia de las areas siguientes en ese RNG. Las flores no consumen el RNG de briznas: cambiar `FlowerDensity` no mueve el pasto.
- **Solo bloquean colliders altos:** un collider cuyo techo no supera `Height + 0.05` (suelo, piso) no genera exclusion.
- **Colliders apagados por default (S162):** `blockByColliders = false`; el bloqueo real de la tienda sale de `exclusions` y de la mascara de pasto, no de colliders.
- **Relieve solo sube:** `ReliefY` nunca devuelve menos que la altura del area.
- **Tope global de briznas:** `maxBlades` cuenta solo briznas entre todas las areas, no por area. Las flores no tienen tope.
- **Flores siempre se siembran:** la rama de flores no depende de `totalBlades`; una parcela con tope de briznas agotado igual puede tener flores.
- **Flores fuera del borde suave:** con `EdgeFade > 0` las flores exigen `EdgeSmooth >= 0.6`.
- **Un color por cluster:** la celda elige el color; por flor solo varia el brillo.
- **Material por area:** `Area.Material` gana sobre `bladeMaterial`; briznas y flores de esa area comparten material.
- **Coordenadas:** `Rect` esta en XZ; la altura viene de `Height` (ajustada por relieve); las mallas se posicionan en `chunkCenter` (origen local por chunk).
- **Sin eventos ni persistencia:** no suscribe `GameEvents`, no toca `GameManager` ni `SaveSystem`. Es decoracion pura.
- **Sin ClearAround:** a diferencia de `ArenaGrassField`, no hay huella de pasos en este script. El pisoteo de la tienda vive en `ShopTrampleMap` + `GrassTrampler` (S162).
- **Destruccion:** chunks con `hideFlags.DontSave`; mallas destruidas al resembrar y en OnDisable.

**Shader asociado:** `Shaders/ArenaGrass.shader`, compartido con la arena. Desde S154 tiene rafagas (`_Gust*`), manchas (`_Patch*`), translucidez de punta (`_TipGlow*`) y trample seguro (si `_ArenaTrampleArea.z <= 0` no hay pisotado). Desde S155 las flores usan el mismo shader: los petalos se distinguen por alpha de vertice < 0.5 y reciben `_FlowerTint` / `_FlowerLift`. **S158:** el shader suma la propiedad `_Lean`. **S162:** el shader usa rampas `ShopGrassRamp_Genshin` (patio) y `_Fenyx` (afuera), altura por UV1 y mascara global `_ShopGrassMaskTex` (`ShopGrassMask`, fuera de este script). Detalle en [[ArenaGrassBlades]].

**Estado:** NUEVO en S154; MODIFICADO en S155 (Area con `Material`, `EdgeFade`, `FlowerDensity`; campos de flores; Sow partido en `SowGrassChunk` / `SowFlowerChunk` / `CreateChunk` / `EdgeSmooth` / `CellHash`); MODIFICADO en S162 (relieve `reliefRoot` + `ReliefY`, `exclusionInset`, `blockByColliders` apagado por default, property `Exclusions`).

**Conexiones:** [[ArenaGrassBlades]] (briznas), [[MeadowFlowers]] (flores), [[ArenaGrassCover]], [[ArenaGrassField]] (hermano de la arena; misma tecnica de chunks, distinta fuente de area), [[ShopGrassMask]] (mascara del shader, S162), [[ShopTrampleMap]] / [[GrassTrampler]] (pisoteo, S162)

**Vinculado a:** [[Index/06 - Player & World]], S154, S155, S158, S162
