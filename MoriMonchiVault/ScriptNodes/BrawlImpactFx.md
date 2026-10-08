---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlImpactFx.cs

**Ruta:** `World/Brawl/BrawlImpactFx.cs`

**Responsabilidad:** Destellos de impacto (estrella + anillo). `Hit(point, color, scale)` crea un par de sprites: estrella blanca (pop 1.3×), anillo tintado (expandir 0.3→1.7). Ambos rotados hacia cámara, alfa fade. Usado por `BrawlVfx` en cada golpe. Genera ring texture dinamicamente (disco suave de 64×64).

**Métodos públicos:**
- `Hit(point, color, scale)` — crea pair en point, anima paralelo

**Animación:**
- Star: 0s→0.16s, scale LERP 0→1.3 (rise en 30%, caída suave), luego fade
- Ring: 0s→0.22s, scale LERP 0.3→1.7 (ease-out cuadrática), alpha fade (1→0)
- Ambos billboard-face rotados

**Generación de ring:**
- Texture 64×64 RGBA, pixel a pixel
- Distancia desde centro = radio 0.8, half-width 0.14
- Alpha smoothstep suave (Hermite 3t²-2t³)
- Sprite creado una sola vez, reutilizado

**Campos principales:**
- Pool de Pair (Star + Ring SpriteRenderer)
- Lista de Run (punto + color + scale + ángulo + timing)

**Notas:**
- Star siempre blanco, ángulo rotado al azar
- Ring tintado del color del impacto
- CameraNudge 0.5 hacia cámara para no z-fight
- Sorting order: ring 40, star 41 (star adelante)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlVfxLibrarySO]]
