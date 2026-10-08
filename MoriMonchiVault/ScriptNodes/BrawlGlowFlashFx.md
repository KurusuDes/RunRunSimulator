---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlGlowFlashFx.cs

**Ruta:** `World/Brawl/BrawlGlowFlashFx.cs`

**Responsabilidad:** Destellos de glow en cada nodo de rayo Lightning (firma de tormenta visual). `Pop(points[], color)` crea `SpriteRenderer` para cada punto del rayo, todos animados en paralelo: pop-in (scale 0.2→1.2 rápido), plateau, pop-out (1.2→0 lento). Usa pool de `SpriteRenderer` para reutilización. Se anula automáticamente.

**Métodos públicos:**
- `Pop(Vector3[] points, Color color)` — crea N sprites (uno por punto), llena Run con metadata

**Animación:**
- Rise (0s → 0.4*Seconds): LERP 0.2→1.2 (ease-out cuadrático)
- Plateau (0.4→0.6 de duración)
- Fall (0.6→1.0): LERP 1.2→0 (ease-in cuadrático)

**Campos principales:**
- Pool de `SpriteRenderer` free
- Lista de `Run` activos (cada Run = array de sprites + puntos + timing)

**Notas:**
- Billboard-faced (mira a cámara)
- GlowSprite + ParticleAdditiveMaterial (bloom)
- Pushed 0.5 unidades hacia cámara (CameraNudge) para evitar z-fight con rayo
- Duración fija 0.18s (rápido)
- Escala mínima 0.2, pico 1.2, máximo tamaño alcanzado en 40% de duración

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlLineFx]], [[BrawlVfxLibrarySO]]
