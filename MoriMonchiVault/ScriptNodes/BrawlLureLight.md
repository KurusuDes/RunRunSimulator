---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlLureLight.cs

**Ruta:** `World/Brawl/BrawlLureLight.cs`

**Responsabilidad:** Firma Lure (Señuelo). Orbe pulsante con luz real durante carga del skill. `Started(caster, skill, theme)` crea orbe (glow sprite + light point range=5). Anima pulsación suave (6 Hz) + escala creciente según windup (0→WindupIntensity). `Fired()` dispara flash destello (escala 2.5×, fade-out 0.25s). Usa pool `BrawlSignatureSprites`.

**Métodos públicos:**
- `Started(caster, skill, theme)` — crea orbe pulsante durante carga
- `Fired(caster, skill)` — activa flash destello
- `Step(float now, Quaternion face)` → void` — anima orbe + luz + flash
- `Clear()` → void` — limpia todos los orbes

**Animación de carga:**
- Orbe: pulsación 0.5+0.5×sin(6Hz)
- Escala: LERP(0.6, 1.0, pulsación) × appear (0.12s)
- Alpha 90%
- Luz intensity: LERP(0, WindupIntensity, t/windup) donde t es edad

**Animación de flash:**
- Escala fijo 2.5×
- Intensity LERP(6.0, 0.0, t/0.25s)
- Alpha fade (90%→0%)

**Campos principales:**
- Pool `BrawlSignatureSprites` (acquireSprite/releaseSprite + acquireLight/releaseLight)
- Lista de `Run` (caster + skill + orb + light + anchor + timing)

**Notas:**
- Anchor: center + lift 1.1 + forward 0.35 (delante del caster a la altura de pecho)
- Se reutiliza por caster (End() mata orbes previos del mismo caster)
- Si caster muere o skill no es el actual, termina
- Luz color del tema (tintado por equipo)
- Sorting order 12 (sombra oscura)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlSignatureFx]], [[BrawlSkillCaster]], [[BrawlSignatureSprites]], [[BrawlFighter]]
