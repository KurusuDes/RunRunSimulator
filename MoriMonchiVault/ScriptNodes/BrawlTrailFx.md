---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlTrailFx.cs

**Ruta:** `World/Brawl/BrawlTrailFx.cs`

**Responsabilidad:** Estelas de movimiento (dash/salto/movilidad forzada). `Follow(fighter, color, width)` crea o reutiliza `TrailRenderer`, lo empareja con fighter. Sigue la posición del fighter mientras está forzado (motor.IsForced) o durante los primeros 0.12s. Se detiene automáticamente y fade-out 0.35s. Pool de trails reutilizables.

**Métodos públicos:**
- `Follow(fighter, color, width)` — comienza trail en fighter con color + ancho

**Animación:**
- Activa emisión mientras fighter forzado O edad < 0.12s
- Detiene emisión, fade-out se ejecuta 0.35s (tiempo de trail del renderer)
- Start alpha 0.85, end alpha 0.0 (gradual)
- Release margin 0.05s extra para seguridad

**Campos principales:**
- Pool de `TrailRenderer` free
- Lista de `Running` (trail + fighter + timing + bool following)

**Notas:**
- Trail time fijo 0.35s (duración en pantalla)
- Vertex distance mínimo 0.05 (calidad vs rendimiento)
- No destruye automáticamente (autodestruct=false), manejo manual
- Se detiene seguimiento si fighter muere o si alcanza edad > MinFollowSeconds (0.12s)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlFighter]], [[BrawlVfxLibrarySO]]
