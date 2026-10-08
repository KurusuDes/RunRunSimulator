---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlStormCrackle.cs

**Ruta:** `World/Brawl/BrawlStormCrackle.cs`

**Responsabilidad:** Firma Storm (Rayo/Antenas). Dibuja bolts crispantes alrededor de target. `Crackle(target, color, seconds)` crea o reutiliza correr de tormenta: 3 bolts de 5 puntos cada uno, se regeneran cada 0.05s aleatoriamente (inicio en sphere alrededor de target, dirección aleatoria con caída, jitter en puntos intermedios). Frame-synced: elimina targets muertos.

**Métodos públicos:**
- `Crackle(target, color, seconds)` — crea/extiende crackle en target
- `Step(float now)` → void` — anima bolts, regenera cuando listo, limpia muertos
- `Clear()` → void` — desactiva todos los bolts

**Regeneración de bolt:**
- Inicio: esfera aleatoria radio 0.5 alrededor del target center
- Dirección: aleatoria 3D
- Longitud: 0.5-0.8 unidades
- Caída: Y negativo garantizado
- Jitter: ±0.12 en puntos intermedios
- Ancho fijo 0.07

**Campos principales:**
- Lista de `Run` (target + color + timing + 3 bolts)
- Pool de `LineRenderer` free
- Array de puntos (5) para rebuild

**Notas:**
- 3 bolts simultáneos, 3-4 ramas por generación estática (vs Lightning que son dinámicas)
- Frecuencia regeneración: RegenSeconds 0.05s (20 Hz, crispy)
- Sorting order 22 (adelante)
- Duración variable: se extiende si ya hay crackle activa

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlSignatureFx]], [[BrawlFighter]], [[BrawlVfxLibrarySO]]
