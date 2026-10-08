---
tags: [script, world, brawl, vfx, presentation, lines]
---

# BrawlLineFx.cs

**Ruta:** `World/Brawl/BrawlLineFx.cs`

**Responsabilidad:** Orquestador de `LineRenderer` para rayos, vigas y latigazos. Pool de `Entry` (3 renderers: glow + outer + core). Tres tipos: `Lightning(path, color, signature)` con jitter y ramas de tormenta, `Beam(from, to, color, signature)` con ondulación sinusoidal + arcoíris para Unicornio/Borla, `Whip(from, to, color)` con Bezier cuadrático. Cada línea se anima en `LateUpdate()`, fade-out suave. Crea destellos en nodos del rayo con `BrawlGlowFlashFx` si es Lightning.

**Campos principales:**
- Pool de `Entry` (Glow, Outer, Core LineRenderers + Branch system)
- `BrawlLightningBranches` para tormentas (Rayo/Antenas)
- Gradient rainbow preconstruido para beams arcoíris
- Lista `running` de animaciones activas

**Métodos públicos:**
- `Lightning(path, color, seconds, signature)` — rayo con subdivisiones jitterizadas; si Storm, crea ramas
- `Beam(from, to, color, seconds, signature)` — viga entre dos fighters con ondulación; si Rainbow, colores HSV
- `Whip(from, to, color, seconds)` — latigazo Bezier que se enrolla y desvanece

**Detalles de animación:**
- Lightning: jitter cada 0.04s en ancho perpendicular + vertical, fade en último 50% de duración
- Beam: envolvente sinusoidal ±0.12 en ancho, parpadeante en bordes (30 Hz), fade lento al final
- Whip: Bezier suave (midpoint desplazado ±sweep dinámico), tamaño encoge ×0.5 linealmente
- Rainbow: 6 claves HSV que giran a velocidad 0.8, saturación 70%

**Notas:**
- Glow es overlay suave (ancho 0.6), Outer borde principal (0.24), Core finísimo (0.06)
- Storm (BrawlSignature.Storm): ancho ×1.3, genera 3-4 ramas aleatorias cada jitter
- Beam arcoíris: emisión de chispas también es dinámica (en `BrawlSignatureFx.RainbowBeam`)
- Freeze-out abrupto si source/target muere

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlLightningBranches]], [[BrawlLightningShapes]], [[BrawlGlowFlashFx]], [[BrawlFighter]]
