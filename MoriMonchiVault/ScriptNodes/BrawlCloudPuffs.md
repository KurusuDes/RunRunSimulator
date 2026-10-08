---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlCloudPuffs.cs

**Ruta:** `World/Brawl/BrawlCloudPuffs.cs`

**Responsabilidad:** Firma Cloud (Lana, LomoLana). Nube de 10 puffs mullidos orbitando zona de duración. `Armed(BrawlFxEvent)` dispara en zonas one-shot (no duración). `Step()` pollea zonas activas con duración, crea/actualiza/destruye nubes dinámicamente. Cada puff wobbles suave + respira (±6% de escala). Fade-out al expirar.

**Métodos públicos:**
- `Armed(BrawlFxEvent)` — crea nube one-shot (1.4s - fade 0.4s = 1.0s visible)
- `Step(float now, Quaternion face)` → void` — pollea zonas, actualiza puffs
- `Clear()` → void` — limpia todas las nubes

**Animación de puff:**
- Posición: center + offset + wobble sinusoidal (7 Hz, ±0.12)
- Escala: base × appear (0→1 smooth en 0.25s) × breathe (1±0.06 a 1.7 Hz) × shrink (fade-out)
- Wobble: sin onda trifase (XY0.5Z), fase aleatoria por puff
- Respiración: amplitud 6%, frecuencia 1.7 Hz

**Campos principales:**
- Pool `BrawlSignatureSprites` (acquireSprite/releaseSprite)
- Lista de `Cloud` (zona + centro + tint + timing + array de puffs)
- Diccionario zoneClouds (zone → cloud) para attach/detach

**Notas:**
- Tint: LERP 30% desde white hacia color de zona (evita oversaturación)
- Alpha fijo 55%, fade-out 0.4s
- Attach: si zona.Age retrocede, detach (puede resetear zona)
- Spread: puffs distribuidos en disco de radius×Spread (70%)
- Sorting order 8 (atrás, detrás de fighters)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlSignatureFx]], [[BrawlZone]], [[BrawlSignatureSprites]], [[BrawlTeamLook]]
