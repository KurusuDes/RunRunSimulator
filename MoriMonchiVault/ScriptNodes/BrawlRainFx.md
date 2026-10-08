---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlRainFx.cs

**Ruta:** `World/Brawl/BrawlRainFx.cs`

**Responsabilidad:** Lluvia de íconos (tema Zone/Throw). `Rain(center, radius, theme, seconds, count)` distribuye `count` gotas programadas a caer en secuencia (el primero 45%, el último 100% de `seconds`). Cada gota cae desde altura 7 unidades con arco parabólico. Ambiente: por cada zona armada, cada 0.22s emite burst de íconos (curación sube, daño cae). Usado por `BrawlVfx` en Throw, coordinado por `BrawlSignatureFx` en Cloud.

**Métodos públicos:**
- `Rain(center, radius, theme, seconds, count)` — programa lluvia
- `Ambient(zone)` — emite VFX ambiental de zona activa (rise para curación, fall para daño)

**Animación de gota:**
- Parabólica: XZ lerp, Y arco (4×height×t×(1-t)) donde height = 3 unidades para zona drop
- Rotación spin aleatorio ±720°/segundo
- Size fijo por gota (lerp 0.6-0.9)
- Fall fijo 0.02s (zona) o variable según distancia (lluvia)

**Campos principales:**
- Lista de `Drop` (sprite + theme + ground + timing + fall + height + size + spin)
- Diccionario de `ZoneClock` por zona (acum + frame contador)
- Pool de `SpriteRenderer` free

**Notas:**
- Trigger Land en cada impacto: 3 íconos explotan
- Zona polling: detecta cambios en zona (si Age regresa, detach + recrear)
- Ambient frame-synced: solo emite si zona presente ese frame
- Altura de lanzamiento: max(2, distancia×0.35)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlIconParticles]], [[BrawlZone]], [[BrawlTeamLook]], [[BrawlVfxLibrarySO]]
