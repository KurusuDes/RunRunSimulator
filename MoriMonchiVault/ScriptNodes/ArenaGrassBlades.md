---
tags: [script, world, expedition, graphics, math]
---

# ArenaGrassBlades.cs

**Ruta:** `World/Expedition/ArenaGrassBlades.cs`

**Responsabilidad:** Utilidad estatica (matematica pura) que arma una malla de briznas de pasto. Recibe lista de raices (Vector3), parametros de altura/ancho/inclinacion, **S117:** opcionalmente lista de heightScales por densidad procedural, y **S154:** opcionalmente `segments` para que cada brizna sea curva (varios niveles de vertices en lugar de un triangulo). Sin estado, sin referencias.

**Metodo publico estatico:**

- `Build(IReadOnlyList<Vector3> roots, System.Random rng, Vector2 heightRange, Vector2 widthRange, float tilt, Vector3 origin, IReadOnlyList<float> heightScales = null, int segments = 1) → Mesh`
  - Valida `roots != null && Count > 0`, retorna null si falla
  - **S117:** heightScales opcional: si presente, aplica `scale[i] * height` a cada brizna
  - **S154:** `segments` se clampa a minimo 1. Con `segments = 1` el resultado es identico al de antes (3 vertices, 1 triangulo y el mismo consumo de RNG)
  - Retorna Mesh (name `ArenaGrassBlades`, hideFlags DontSave) con IndexFormat UInt32 si supera 65k vertices, UInt16 si no

**Algoritmo Build():**

1. **Inicializacion:** calcula `vertsPerBlade = segments * 2 + 1` y `trisPerBlade = (segments * 2 - 1) * 3`; aloca listas de vertices, normales, UVs, colores y triangulos con esa capacidad.

2. **Loop por raiz (i < roots.Count):**
   - Samplea height, width, yaw aleatorios del RNG
   - **S117:** si heightScales != null y i < Count: `height *= heightScales[i]`
   - Calcula sideAxis perpendicular al yaw (horizontal)
   - Samplea leanAngle y leanDirection; computa leanAxis y `tipOffset = leanAxis * sin(leanAngle) * height`
   - Normal constante para toda la brizna: `normalize(up + sideAxis * 0.25)`
   - Color por brizna: `Color(hue, hue, hue, 1)` con hue aleatorio (escala de grises)

3. **Geometria de la brizna (S154, por segmento k = 0..segments-1):**
   - `t = k / segments`
   - `center = root + up * (height * t) + tipOffset * t²` (la curva del lean crece cuadratica)
   - `halfWidth = width * 0.5 * (1 - t)` (se estrecha hacia la punta)
   - Dos vertices laterales `center ± sideAxis * halfWidth`, UVs `(0, t)` y `(1, t)`
   - Al final, un vertice de punta `root + up * height + tipOffset`, UV `(0.5, 1)`

4. **Triangulacion:**
   - Entre cada par de niveles consecutivos: 2 triangulos (franja izquierda-derecha)
   - Ultimo nivel: 1 triangulo que cierra en la punta
   - Con `segments = 1` queda solo el triangulo de la punta, como antes

5. **Finalizacion:** SetVertices, SetNormals, SetUVs, SetColors, SetTriangles, RecalculateBounds()

**Internals:**
- **Coordenadas relativas:** root se calcula como `roots[i] - origin` (para aplicar offset del chunk)
- **Costo:** con `segments = N` cada brizna usa `2N + 1` vertices y `2N - 1` triangulos. Con 3 vertices por brizna el costo es el minimo
- **Hue escala:** color en escala 0-1 (el shader debe interpretarlo)

**Invariantes:**
- **Determinismo:** RNG producido externamente (Sow pasa seed-based System.Random); el numero de muestras por brizna no depende de `segments`
- **Sin estado:** Build() es funcion pura, ningun side effect
- **Malla unica:** se crea una nueva Mesh por cada chunk (no reutilizacion)
- **IndexFormat adaptive:** UInt16 si <= 65k verts, UInt32 si mayor (evita overflow)
- **Normales constantes por brizna:** economia, suficiente para look billboard
- **heightScales alineado con roots:** ambos crecen juntos en Build de ArenaGrassField y ShopGrassField
- **Segments sin tope aqui:** el tope 1-4 vive en el campo serializado de ArenaGrassField; ShopGrassField pasa el valor del area tal cual (solo se clampa a 1)

**Shader asociado:** `Shaders/ArenaGrass.shader`. Desde S154 el shader tiene rafagas (`_Gust*`), manchas (`_Patch*`), translucidez de punta (`_TipGlow*`) y trample seguro si `_ArenaTrampleArea.z <= 0`. Los UV `(0, t)` / `(1, t)` alimentan el gradiente a lo largo de la brizna. **S155:** el shader suma normal blend (`_NormalBlend`), raiz (`_Root*`), saturacion (`_Saturation`), color de punta (`_TipColor*`), variacion de tono (`_Hue*`) y de brizna (`_BladeVariation`). Los petalos de `MeadowFlowers` (flores de `ShopGrassField`) se identifican por alpha de vertice < 0.5 y reciben `_FlowerTint` / `_FlowerLift`. **S158:** el shader suma la propiedad `_Lean`; su efecto vive en el shader y este script no cambia.

**S117 Cambios:**
- Parametro `IReadOnlyList<float> heightScales` opcional
- Aplicacion de `scale[i] * height` para modular altura segun densidad (ArenaGrassCover.Sample)

**S154 Cambios:**
- Parametro `int segments = 1` opcional; briznas curvas con estrechamiento y lean cuadratico
- Con `segments = 1` se conserva el comportamiento anterior

**Conexiones:** [[ArenaGrassField]] (cliente de arena), [[ShopGrassField]] (cliente de tienda), [[MeadowFlowers]] (hermano de tienda para flores)

**Vinculado a:** [[Index/23 - Arena Sandbox & Expedicion]], [[Index/22 - Bajada Nocturna y Linaje]], S117, S154, S155, S158
