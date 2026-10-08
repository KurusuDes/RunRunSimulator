---
tags: [script, world, brawl, vfx, presentation, lines]
---

# BrawlLightningBranches.cs

**Ruta:** `World/Brawl/BrawlLightningBranches.cs`

**Responsabilidad:** Contenedor de 3-4 `LineRenderer` (ramas procedurales de rayo de tormenta). Creadas bajo parent GO, inicialmente deshabilitadas. Se arman con material + color al castear habilidad de tormenta. `Rebuild()` regenera geometría de ramas cada jitter (~40ms). Fade suave al desaparecer rayo.

**Constructor:**
- `BrawlLightningBranches(Transform parent, int sortingOrder)` — crea 4 LineRenderers dummy

**Métodos públicos:**
- `Arm(Material material, Color color)` — activa 3-4 líneas random, aplica material, color, offset aleatorio
- `Rebuild(Vector3[] main)` — llama `BrawlLightningShapes.BuildBranch()` para cada rama activa, actualiza posiciones
- `Fade(float fade)` — multiplica ancho de todas las líneas activas por fade (0→1 = visible→invisible)
- `Disable()` — desactiva todas las líneas, resetea count

**Notas:**
- Ramas creadas una sola vez (lazy pool)
- Cada rama tiene alpha 0.8 (más opacas que glow principal)
- Ancho 0.1 (thin accent)
- Randomiza 3-4 ramas por armada (MinCount=3, MaxCount=4)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlLineFx]], [[BrawlLightningShapes]]
