---
tags: [script, world, brawl, vfx, presentation, helper]
---

# BrawlTeamLook.cs

**Ruta:** `World/Brawl/BrawlTeamLook.cs`

**Responsabilidad:** Clase estática pura (sin estado). Aplica el visual de "lectura de equipo" a todos los VFX: **rivales lavados en rojo conservando forma (interpolación LERP al `FoeTint`), aliados saturados y más grandes**. Helper centralizado que usan `BrawlVfx`, `BrawlRainFx`, `BrawlProjectile`, `BrawlTelegraphs` y las firmas (`BrawlSignatureFx`, etc.). Datos de síntesis viven en `BrawlVfxLibrarySO.Current`.

**Métodos públicos:**
- `IsAlly(ExpeditionTeam team) → bool` — retorna true si `team == Player`
- `Wash(Color color, team) → Color` — **rivales**: LERP a `FoeTint` por `FoeWash` (rojo conservador); **aliados**: aumenta saturación en +`AllySaturation`, asegura valor mínimo `AllyMinValue`
- `Wash(BrawlTheme theme, team) → BrawlTheme` — aplica Wash al color preservando icon + signature
- `Size(ExpeditionTeam team) → float` — aliados retornan `AllySizeBoost` (~1.2), rivales retornan 1.0

**Notas:**
- No cambia alfa en Wash (preserva trasparencia original)
- En aliados usa HSV para saturación sin perder luminancia
- Rivales: mezcla suave con tint rojo sin destruir silueta
- Datos de síntesis en SO: `FoeTint`, `FoeWash`, `AllySaturation`, `AllyMinValue`, `AllySizeBoost`

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlVfxLibrarySO]], [[BrawlTheme]], [[BrawlVfx]], [[BrawlTelegraphs]], [[BrawlProjectile]]
