---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlWardFx.cs

**Ruta:** `World/Brawl/BrawlWardFx.cs`

**Responsabilidad:** VFX de escudos (Ward): 5 íconos de parte orbitando (Coraza, Placas, AletasCara). `Ward()` crea órbita suave, aparece suavemente, late si escudo sigue activo, desaparece pop-out cuando expira/rompe/muere. También `Toss()` anima proyectiles lanzados (arco parabólico, rotación, tamaño fijo). Usa pool de `SpriteRenderer`.

**Métodos públicos:**
- `Ward(target, theme, seconds)` — crea órbita de 5 sprites alrededor de target
- `Toss(from, to, theme, seconds, size)` — lanza proyectil con arco + rotación

**Ward animation:**
- AppearSeconds 0.15s: scale 0→1 smoothstep
- Latido: amplitud ±0.15 altura, frecuencia 3 Hz
- Órbita: 2.2 rad/s, fase aleatoria por sprite
- Shrink: 0.15s pop-out cuando ShieldGraceSeconds (0.3s) + escudo roto

**Toss animation:**
- Parabólico: Z es lerp, Y es arco (4×height×t×(1-t))
- Rotación: ×540°/segundo (3 vueltas)
- Duración variable según distancia XZ

**Notas:**
- Ward se reutiliza si el mismo target ya tiene uno (resetea timer)
- Checa cada frame si target es null, escudo<=0, o edad>=segundos
- Pool de sprites es compartida
- GracePeriod permite 0.3s de latido incluso si escudo ya roto

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlFighter]], [[BrawlTeamLook]], [[BrawlVfxLibrarySO]]
