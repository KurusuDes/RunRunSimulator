---
tags: [script, world, expedition, graphics, mesh, procedural]
---

# ArenaGrassField.cs

**Ruta:** `World/Expedition/ArenaGrassField.cs`

**Responsabilidad:** Siembra pasto procedural por parcelas al reconstruirse la forma de arena. Divide bounds en chunks cuadrados, valida cada chunk contra bordes (distancia a edge) y obstaculos (rocas, lagos, pits, bosques), genera raices por densidad/chunk, **S117:** usa ArenaGrassCover.Sample() para densidad procedural y height scale, delega a `ArenaGrassBlades.Build()` para armar malla, instancia GameObjects con MeshFilter/MeshRenderer por chunk. Reinicia al evento shape.Rebuilt. Destruye field completo en OnDisable. **S117:** expone ClearAround() para limpiar pasto alrededor de spawns (ArenaSandbox.S117). **S154:** expone `segments` y lo pasa a Build (briznas curvas).

**Campos serializados:**

**Semilla y Material:**
- `seed` (int, default 11) — semilla RNG para determinismo (posicion/tamano/rotacion de briznas)
- `bladeMaterial` (Material) — material para los chunks (recibe ramp de ArenaPaletteApplier)

**Parcelas (Chunks):**
- `chunkSize` (float, Min 2, default 5) — tamano de parcela cuadrada
- `density` (float, Min 0.1, default 50) — briznas/unidad² (candidatas por chunk)
- `maxBlades` (int, default 120000) — limite total de briznas generadas

**Briznas (Blades):**
- `heightRange` (Vector2, default 0.12 - 0.26) — rango de altura de brizna
- `widthRange` (Vector2, default 0.045 - 0.075) — rango de ancho de brizna
- `tilt` (float, default 0.25) — angulo maximo de inclinacion/lean de brizna
- `segments` (int, Range 1-4, default 1) — **S154 NUEVO:** niveles de la brizna. 1 = 3 vertices (como antes); 2-4 = brizna curva con estrechamiento

**Cobertura — S117 NUEVA:**
- `cover` (ArenaGrassCover.Settings, default ArenaGrassCover.Settings.Default) — parametros de densidad procedural:
  - clumpSpacing, clumpRadius, haloDensity, patchScale, patchThreshold, patchDensity, looseDensity, looseHeight
  - Determina densidad y altura de cada brizna por posicion

**Margenes:**
- `edgeMargin` (float, default 0.6) — distancia de seguridad a bordes de arena
- `obstacleMargin` (float, default 0.5) — distancia de seguridad a obstaculos

**Metodos publicos:**

- **`void ClearAround(IReadOnlyList<Vector4> zones)`** — **S117 NUEVO:** limpia pasto alrededor de zonas (spawn points, obstaculos)
  - Itera chunks cercanos a alguna zone (distancia <= zone.w + chunkSize * 0.7071)
  - Para cada raiz dentro de zone (distancia < zone.w): filtra fuera
  - Reconstruye malla con raices restantes (`ArenaGrassBlades.Build`, pasa `segments` desde S154)
  - Destruye chunk si todas las raices fueron removidas

**Metodos privados:**

**Sow() (inicialmente llamado en OnEnable, luego en shape.Rebuilt):**

1. DestroyGrassField() — limpia anterior
2. Valida shape.OutlinePolygon.Count >= 3, bladeMaterial != null
3. Crea GameObject("GrassField", hideFlags.DontSave)
4. Inicializa RNG con seed
5. Recolecta obstacle bounds (rocks, lakes, pits, groves) con margen
6. Itera chunks en bounds:
   - Calcula chunkCenter, chunkCenter2D
   - Detecta si centro esta dentro (shape.Contains)
   - Calcula distancia a edge
   - Si esta fuera de circumRadius (chunkSize * 0.7071), skipa
   - Genera ~density * chunkSize² candidatos por raiz
   - Para cada raiz:
     - **S117:** `float density = ArenaGrassCover.Sample(pos, seed, in cover, out float heightScale)`
     - Si `rng.NextDouble() >= density`, skipa (probabilidad dinamica)
     - Añade raiz + heightScale a listas
   - Valida: dentro de shape, claro de obstaculos, y lejos de edge (si no bordeSeguro)
   - Llama `ArenaGrassBlades.Build(roots, rng, heightRange, widthRange, tilt, chunkCenter, heights, segments)` → Mesh (**S154:** pasa segments)
   - Crea chunk GameObject con MeshFilter(mesh) + MeshRenderer(bladeMaterial)
   - Stoppe si totalBlades >= maxBlades

**DestroyGrassField():**
- Destruye GameObject grassField (y sus mallas)
- Limpia hijos historicos con nombre "GrassField"
- Libera mallas de MeshFilter (DestroyImmediate)

**CollectObstacleBounds(polygons, margin, bounds):**
- Por cada poligono en lista: agrega PolygonBounds con margen

**PolygonBounds(polygon, margin) → Rect:**
- Computa AABB de poligono, expande por margin
- Retorna Rect

**OnValidate() (editor-only):**
- En edit mode: scheduleDelayCall → SowIfAlive (regenera preview)

**DestroyChunks(Transform field):**
- Limpia mallas de MeshFilter en hijos

**PlanarDistance(Vector3 a, Vector4 b) — S117 NUEVO:**
- Distancia 2D entre punto 3D y Vector4(x,z,_,_)

**Invariantes S117:**

- **Procedural per seed:** RNG determinista por seed → reproducible
- **Densidad dinamica:** ArenaGrassCover.Sample() por posicion → grumos + halos + parches + suelta
- **Height scale dinamico:** ArenaGrassCover.Sample() out heightScale → altura de brizna varia con densidad
- **Limite de briznas:** soft cap maxBlades (early exit si se alcanzo)
- **Edge margin:** evita briznas al filo del mapa
- **Obstacle avoidance:** rechaza candidatos en radio de rocas/lagos/pits/bosques
- **Chunk-based:** paralelizable, permite regeneracion selectiva
- **ClearAround:** limpia pasto alrededor de spawns post-siembra (ArenaSandbox.BuildRoom S117)
- **Editor preview:** OnValidate permite pre-visualizar en edit mode
- **Destruccion lazy:** gameobjects transitorios (hideFlags.DontSave)

**Shader asociado (S154):** `Shaders/ArenaGrass.shader` ahora tiene rafagas (`_Gust*`), manchas (`_Patch*`), translucidez de punta (`_TipGlow*`) y trample seguro si `_ArenaTrampleArea.z <= 0`.

**S117 Cambios:**

- Integracion de ArenaGrassCover.Sample() para densidad procedural
- heightScale aplicado a cada brizna (ArenaGrassBlades.Build ahora recibe lista de scales)
- ClearAround() expuesto publicamente para ArenaSandbox
- Pasto dinamico que mantiene huella de pasos (area despejada por zonas)

**S154 Cambios:**

- Campo `segments` (Range 1-4, default 1) en el grupo Brizna
- `segments` pasa a `ArenaGrassBlades.Build` tanto en Sow como en ClearAround
- Con `segments = 1` el resultado es igual al de antes

**Conexiones:** [[ArenaShape]], [[ArenaGrassBlades]], [[ArenaGrassCover]], [[ArenaPaletteApplier]], [[ArenaSandbox]]. Hermano de tienda: [[ShopGrassField]] (misma tecnica sobre areas rectangulares, sin ClearAround)

**Vinculado a:** [[Index/23 - Arena Sandbox & Expedicion]], [[Index/22 - Bajada Nocturna y Linaje]], S117, S154
