---
tags: [script, world, brawl, projectile, trail, vfx]
---

# BrawlProjectileTrail.cs

**Ruta:** `World/Brawl/BrawlProjectileTrail.cs`

**Responsabilidad:** Configurador de TrailRenderer para proyectiles. Dos modos: plain (color sólido alisado) y comet (gradiente fuego arcoíris). Aplicación de team look wash.

## Métodos Estáticos

| Método | Descripción |
|--------|-------------|
| `Apply(trail, shot, plainTime, width, color)` | Configura trail según signature |

## Modos

### Plain
- Tiempo: plainTime (parámetro)
- Color: sólido + fade (entrada)
- Ancho: linealmente a 0
- Uso: mayoría de proyectiles

### Comet (Signature.Comet)
- Tiempo: 0,5 s
- Gradiente: fuego (amarillo → naranja → rojo oscuro)
- Ancho: 1,6× escala
- Uso: Cometa, Cometitas skills

## Team Look Wash

- Comet palette pasa por `BrawlTeamLook.Wash()` para colorear rival/aliado
- Plain color pasa directo (pre-teñido por [[BrawlSkillSO]] ColorOverride)

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Entrada:**
- [[BrawlProjectile]] → `Apply()` en Launch

**Datos:**
- [[BrawlTheme]].Signature (Comet vs otro)
- [[BrawlTeamLook]] → Wash color

## Notas

- Cometales cacheadas globales (evita allocations)
- Gradiente reutilizable
- Comet solo si shot.Theme.Signature == BrawlSignature.Comet
