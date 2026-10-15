---
tags: [script, world, store, graphics, mesh, procedural, flowers, math]
---

# MeadowFlowers.cs

**Ruta:** `World/Store/MeadowFlowers.cs`

**Responsabilidad:** Utilidad estatica (matematica pura, sin estado mutable) que arma UNA malla con flores de pradera: tallo curvo de 2 segmentos, cabeza con 5 petalos y nucleo central. Recibe raices, color por flor, RNG, rangos de altura y radio, y el origen del chunk. Sin estado, sin referencias a componentes; lo unico que devuelve es el `Mesh`.

**Metodo publico estatico:**

- `Build(IReadOnlyList<Vector3> roots, IReadOnlyList<Color> colors, System.Random rng, Vector2 stemHeight, Vector2 headSize, Vector3 origin) → Mesh`
  - Retorna null si `roots` es null o vacio
  - `colors[i]` da el color de los petalos de la flor `i`; si `i >= colors.Count` usa blanco
  - Mesh name `MeadowFlowers`, hideFlags DontSave, IndexFormat UInt32 si supera 65k vertices, UInt16 si no

**Constantes internas (no serializadas):** `StemSegments = 2`, `PetalCount = 5`, `StemWidth = 0.018`, `MaxStemLean = 0.12` (proporcional a la altura), `MaxHeadTilt = 20°`, `PetalBaseRadius = 0.3`, `PetalHalfAngle = 28°`, `CoreRadius = 0.28`, `HeadLift = 0.005`, `CoreLift = 0.004`, `CoreColor = (1, 0.85, 0.4, alpha 0)`.

**Algoritmo Build() (por flor):**

1. **Muestras del RNG en orden fijo (9 por flor):** altura del tallo, radio de cabeza, yaw (eje lateral), magnitud y direccion del lean, hue del tallo, angulo de inclinacion y direccion de la cabeza, angulo inicial de los petalos.
2. **Tallo:** 2 niveles de vertices laterales `center ± sideAxis * halfWidth` (el ancho decrece con `t`) mas un vertice de punta. El desplazamiento de lean es cuadratico (`tipOffset * t²`). Color gris `Color(hue, hue, hue, 1)`. UVs `(0, t)` / `(1, t)`.
3. **Cabeza:** centro en la punta + `HeadLift`, rotado por la inclinacion alrededor del eje perpendicular a up. Su normal es `rotation * up`.
4. **Petalos:** 5 triangulos en abanico desde el centro. Cada petalo tiene base izquierda y derecha a `PetalBaseRadius * radius` y punta a `radius`. Color = `colors[i]` con alpha 0.
5. **Nucleo:** 5 vertices a `CoreRadius * radius`, elevados `CoreLift` sobre la normal de la cabeza, color `CoreColor`, en abanico con el centro.
6. **Finalizacion:** SetVertices, SetNormals, SetUVs, SetColors, SetTriangles, RecalculateBounds.

**Vertex color (contrato con el shader):**

- Tallo: alpha 1
- Petalos y nucleo: alpha 0. `Shaders/ArenaGrass.shader` los trata como petalo cuando `alpha < 0.5`.

**Costo:** 26 vertices y 54 triangulos por flor (fijo, sin LOD).

**Invariantes:**

- **Coordenadas locales al chunk:** cada raiz se resta de `origin`. El llamador (`ShopGrassField.CreateChunk`) posiciona el GameObject en `chunkCenter`.
- **RNG compartido con el muestreo:** el RNG es `rngFlower` de `ShopGrassField`, el mismo que consume el muestreo de candidatos. Cambiar la cantidad de candidatos cambia tambien las flores de la malla.
- **Una malla por parcela:** Build no reutiliza mallas; cada chunk de flores recibe la suya.
- **Alpha de entrada ignorado:** el alpha de `colors` se pisa a 0 en los petalos. `ShopGrassField` pasa alpha 1 por convencion.
- **Sin estado:** misma entrada, misma malla. Sin side effects.
- **Normales:** tallo `normalize(up + side * 0.25)`; cabeza y petalos usan la normal inclinada de la cabeza.

**Shader asociado:** `Shaders/ArenaGrass.shader`, el mismo material que las briznas del area. El alpha de vertice separa tallo de pétalo; el shader aplica `_FlowerTint` y `_FlowerLift`. Detalle en [[ArenaGrassBlades]].

**Estado:** NUEVO en S155.

**Conexiones:** [[ShopGrassField]] (unico cliente, en `SowFlowerChunk`), [[ArenaGrassBlades]] (hermano: misma tecnica de malla por utilidad estatica)

**Vinculado a:** [[Index/06 - Player & World]], S155
