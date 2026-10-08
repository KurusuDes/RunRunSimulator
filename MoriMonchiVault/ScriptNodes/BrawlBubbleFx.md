---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlBubbleFx.cs

**Ruta:** `World/Brawl/BrawlBubbleFx.cs`

**Responsabilidad:** VFX de burbuja semi-transparente alrededor de target (Ward de AletasCara). `Bubble(target, color, seconds)` crea o reutiliza burbuja por target. Anima: pop-in (scale 0→1.15 con ease, 60% de tiempo), latido suave (wobble ±3%), pulsación alpha (3 Hz). Se desvanece suavemente (pop-out 1→1.3 con shrink) al expirar/romper escudo/morir target. Usa sphere primitiva como mesh.

**Métodos públicos:**
- `Bubble(target, color, seconds)` — crea/reutiliza burbuja para target, resetea timer + color + fase aleatoria

**Animación:**
- Appear (0→0.18s): scale LERP 0→1.15 (custom ease-out), la curva sube rápido luego se estabiliza
- Wobble: ±3% de escala, frecuencia 7 Hz, fase aleatoria por burbuja
- Pulse: alpha oscila Lerp(0.08, 0.14, 0.5+0.5×sin()), frecuencia 3 Hz
- Pop-out (grace 0.3s tras expirar): scale 1→1.3, alpha fade, duración 0.12s

**Campos principales:**
- Pool de `Entry` (GameObject + Transform + Material clonado)
- Lista de `Run` (target + timing + color + fase)
- Sphere mesh reutilizado (se crea una vez, destruye primitivo)

**Notas:**
- Material clonado para cada burbuja (permite color dinámico)
- Shader `_TintColor` + `_Color` (aditivo translúcido)
- MeshRenderer: sin sombras, sin light probes, sorting order 18
- Grace period 0.3s: si escudo se rompe EN los primeros 0.3s de la burbuja, se tolera latido

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfx]], [[BrawlFighter]], [[BrawlVfxLibrarySO]]
