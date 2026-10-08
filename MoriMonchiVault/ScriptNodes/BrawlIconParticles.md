---
tags: [script, world, brawl, vfx, presentation, particles]
---

# BrawlIconParticles.cs

**Ruta:** `World/Brawl/BrawlIconParticles.cs`

**Responsabilidad:** Pool dinámico de `ParticleSystem` (uno por texture + dirección de gravedad). Emite sprites de íconos de partes (`BodyPart.Icon`) con velocidades vectoriales y ciclos de vida. Métodos: `Burst()` (explosión radial), `Spray()` (abanico direccional), `Ring()` (anillo), `Converge()` (converge hacia centro). Todo icon usa la misma malla Billboard, shader teñido con `BrawlTheme.Color`, gravity +0.9 para caída o -0.15 para ascenso ("rise").

**Métodos públicos:**
- `Burst(pos, theme, count, speed, size, life, rise=false)` — émite `count` íconos en esfera; si `rise`, solo Y positiva
- `Spray(origin, direction, angleDeg, theme, count, speed, size, life)` — abanico cónico en dirección; Y aleatorio 0-0.25
- `Ring(center, theme, count, radius, speed, size, life)` — circulo de íconos saliendo radialmente
- `Converge(center, theme, count, radius, size, life)` — íconos convergen hacia centro en `life` segundos

**Campos principales:**
- Pool keyed por (Texture, rise) → ParticleSystem
- Material del sistema: `lib.ParticleMaterial` (shader que soporta `_BaseMap`/`_MainTex`)

**Notas:**
- ParticleSystems creados lazy (primera llamada con (texture, rise) crea GO + PS)
- Cada PS: World space, 300 max particles, `colorOverLifetime` fade, `sizeOverLifetime` shrink 100→70%
- Rotation aleatoria ±180° por frame
- Spray añade jitter en Z para profundidad (angle/2 a cada lado)
- Ring comienza en ángulo aleatorio para evitar patrón visual
- Converge calcula velocidad necesaria para llegar al centro en `life` (inward = radius/life)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlRainFx]], [[BrawlSignatureFx]], [[BrawlVfxLibrarySO]], [[BrawlTheme]]
