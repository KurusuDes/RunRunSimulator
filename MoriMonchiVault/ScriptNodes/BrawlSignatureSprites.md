---
tags: [script, world, brawl, vfx, presentation, pool]
---

# BrawlSignatureSprites.cs

**Ruta:** `World/Brawl/BrawlSignatureSprites.cs`

**Responsabilidad:** Pool centralizado de `SpriteRenderer` + `Light` reutilizables. Usado por firmas (Cloud, Lure, Plates) para alojar assets visuales dinámicos. Métodos `AcquireSprite()` y `AcquireLight()` extraen del pool o crean nuevos. `ReleaseSprite()` y `ReleaseLight()` devuelven al pool. Sin estado lógico, puro almacén.

**Métodos públicos:**
- `AcquireSprite(Sprite sprite, Material material, int order) → SpriteRenderer` — extrae de pool o crea GO+SR
- `ReleaseSprite(SpriteRenderer sr) → void` — desactiva + apila
- `AcquireLight(float range) → Light` — extrae o crea GO+Light point
- `ReleaseLight(Light light) → void` — desactiva + apila

**Configuración de sprites:**
- ShadowCastingMode.Off, receiveShadows false
- Color white, scale zero (será seteado por consumidor)
- Sorting order variable (parámetro)

**Configuración de lights:**
- Type Point, no shadows
- Range variable
- Intensity 0 (será seteado por consumidor)

**Notas:**
- Sprites hijos del root GO (transform hierárquico)
- Lights también hijos del root
- Sin pooling de tamaño máximo (crece según demanda)
- Constructor toma Transform parent (permite anidar bajo BrawlVfx)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlSignatureFx]], [[BrawlCloudPuffs]], [[BrawlLureLight]], [[BrawlPlateOrbit]]
