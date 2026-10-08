---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlSwooshFx.cs

**Ruta:** `World/Brawl/BrawlSwooshFx.cs`

**Responsabilidad:** Arco de barrido procedural para mordiscos (Melee) y conos (Cone). `Swoosh(origin, forward, radius, angleDeg, height, color, seconds)` crea mesh dinámico de 28 segmentos × 3 filas (outer/mid/inner). Cada frame anima dos envolventes: head (crece rápido, 55% de duración) y tail (retardo 0.2s). Borde desvanece. Meshes reutilizados.

**Campos principales:**
- Stack de Entry (mesh + renderer)
- Lista de Running (una por swoosh activo)
- Mesh dinámico: verts (28+1)×3, tris, UVs precalculados

**Animación:**
- Head: rapidez 0 → max sobre 55% de Seconds, usa ease-out cuadrática
- Tail: retardo 0.2s, luego head → cierre sobre 80% restante
- Outer/Mid/Inner: radios fijos de radio × (1.0 / 0.72 / 0.45)
- Fade: multiplica alpha una vez que tail comienza
- Tilt: 12° inclinación lateral para lectura de altura

**Notas:**
- Mesh dinámico: marcar como MarkDynamic() para optimización
- Colores: white en outer (borde), color en mid, transparent en inner
- Cada vértice tiene SqrtAlpha para luminancia suave (raíz cuadrada de u×sqrt(u))
- Ancho angular: 360° si angleDeg ≥ 360, sino clampear 1-360°

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlVfxLibrarySO]]
