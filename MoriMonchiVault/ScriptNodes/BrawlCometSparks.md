---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlCometSparks.cs

**Ruta:** `World/Brawl/BrawlCometSparks.cs`

**Responsabilidad:** Firma Cometa/Cometitas (proyectiles de fuego). Monitorea `BrawlProjectile.Active`, detecta signatures de Cometa, emite trail de chispas (amarillo/naranja alternado) cada 0.04s. En burst (explosión), emite 16 chispas multicolores + dos anillos (naranja, rojo) expandentes. Usa callback para registrar anillos en `BrawlSignatureFx`.

**Métodos públicos:**
- `Burst(BrawlFxEvent)` — emite ráfaga de chispas (mitad amarillo, mitad naranja) + dos anillos
- `Step(float dt)` — itera proyectiles Cometa, emite trail cada 0.04s
- `Clear()` → void` — limpia reloj de proyectiles

**Trail animation:**
- Intervalo 0.04s (25 Hz)
- 2 chispas por emit, velocidad 1.5
- Tamaño 0.22, vida 0.35s
- Alterna color (amarillo/naranja) por frame

**Burst animation:**
- 8 chispas amarillo + 8 naranja (radial)
- Velocidad 5 (rápido), tamaño 0.26, vida 0.5s
- Dos anillos: naranja (delay 0), rojo (delay 0.05s)
- Radio crece por `RingGrowth` (×1.2)

**Campos principales:**
- Clock dict keyed por `BrawlProjectile` (Accum + Alt + Frame)
- Referencia a `BrawlIconParticles` para emisiones
- Callback `addRing` para registrar anillos

**Notas:**
- Frame-synced: detecta proyectiles muertos eliminando del reloj si no update este frame
- Colores estáticos: Yellow (1, 0.9, 0.4), Orange (1, 0.5, 0.12), Red (1, 0.2, 0.08)
- Wash aplicado al color (equipo)
- Burst dispara dos anillos con delay de 0.05s (secuencial)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlSignatureFx]], [[BrawlProjectile]], [[BrawlIconParticles]], [[BrawlTeamLook]]
