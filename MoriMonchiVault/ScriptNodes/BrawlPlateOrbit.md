---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlPlateOrbit.cs

**Ruta:** `World/Brawl/BrawlPlateOrbit.cs`

**Responsabilidad:** Firma Plates (Placas, Coraza). 6 placas grandes orbitando target. `Ward(BrawlFxEvent)` crea o reutiliza órbita, cada placa pop-in escalonado (0.05s stagger). Órbita de 1.25 unidades, rotación 90°/s. Inclina 18° (tilt) para profundidad. Fade-out graceful si escudo rompe.

**Métodos públicos:**
- `Ward(BrawlFxEvent)` → void` — crea órbita con icon + color del evento
- `Step(float now, Quaternion face)` → void` — anima placas
- `Clear()` → void` — limpia todas las órbitas

**Animación de placa:**
- Posición: center + (rotación orbital)
- Escala: pop(edad) × shrink, donde pop es ease-out custom (Hermite 1+2.7t³+1.7t²)
- Pop-in: staggered, placa i comienza en i×0.05s
- Órbita: giro 90°/s alrededor de eje Y
- Inclinación: aplicar Tilt (18° roll, 10° pitch) a todas las posiciones
- Shrink: lineal 1→0 en 0.2s si escudo rompe

**Campos principales:**
- Pool `BrawlSignatureSprites` (acquireSprite/releaseSprite)
- Lista de `Run` (target + timing + fase + sprites[6])

**Notas:**
- Sorting order 10 (delante de rain, detrás de impacts)
- Tamaño placa fijo 0.75
- Índices de placa: 360°/6 = 60° de separación
- Grace period 0.3s: si escudo rompe en los primeros 0.3s de órbita, se tolera
- Detach: reutiliza si target ya tiene órbita (End() mata previas)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlSignatureFx]], [[BrawlSignatureSprites]], [[BrawlFighter]]
