---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlVortexFx.cs

**Ruta:** `World/Brawl/BrawlVortexFx.cs`

**Responsabilidad:** VFX de remolino en espiral (Pull/Señuelo). `Vortex(center, radius, color, seconds)` crea 3 brazos de espiral que giran a 540°/s. Cada brazo es `LineRenderer` con 24 puntos, barrido de 3.2 rad desde interno (center) a externo (radius). Opcional halo (sprite aditivo) que crece/desvanece. Radio converge al final, ancho encoge. Usado por `BrawlVfx` en Pull.

**Métodos públicos:**
- `Vortex(center, radius, color, seconds)` — crea remolino rotatorio

**Animación:**
- 3 brazos: girar a `SpinDegreesPerSecond` (540°/s = 3π rad/s)
- Cada brazo: barrido de `ArmSweep` (3.2 rad ≈ 183°) desde el eje
- Radio: LERP desde input → EndRadius (0.3) a lo largo de duración
- Ancho: curve de 0.14→0.02 (afila hacia la punta)
- Fade: comienza al 70% de duración (FadeStart 0.7)
- Halo (opcional): sprite creciente (0.4→1.6), rotación hacia cámara, alpha fade

**Campos principales:**
- 3 LineRenderer (brazos)
- 1 SpriteRenderer (halo)
- Pool de Entry reutilizables

**Notas:**
- Ground snap: muestrea NavMesh para altura de inicio
- Lift de 0.3 unidades sobre suelo para evitar clip
- Halo solo si `lib.GlowSprite` + `lib.ParticleAdditiveMaterial` disponibles
- Cada brazo recorre desde centro (u=0) a radio máximo (u=1)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlVfxLibrarySO]]
