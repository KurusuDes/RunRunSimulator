---
tags: [script, world, brawl, vfx, bus]
---

# BrawlFx.cs

**Ruta:** `World/Brawl/BrawlFx.cs`

**Responsabilidad:** Bus de eventos VFX. Estructura de datos `BrawlFxEvent` (kind, posición, tema, equipo, source). Singleton con event estático `Emitted` que consume presentación.

## BrawlFxEvent

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Kind` | `BrawlFxKind` enum | Tipo efecto (Slash, Whip, Lightning, Land, etc.) |
| `From`, `To` | Vector3 | Posición inicio/fin |
| `Path` | Vector3[] | Ruta (rayo chain) |
| `Radius` | float | Radio zona/anillo |
| `Angle` | float | Ángulo cono |
| `Duration` | float | Duración (zona con demora) |
| `Theme` | `BrawlTheme` | Color e ícono |
| `Team` | `ExpeditionTeam` | Player/Rival (para Wash) |
| `Source` | `BrawlFighter` | Lanzador (aliado/rival) |
| `Target` | `BrawlFighter` | Objetivo opcional |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Emit(event)` | Dispara evento a suscriptores |

## Evento Estático

```csharp
public static event Action<BrawlFxEvent> Emitted;
```

Suscriptores:
- [[BrawlAnimator]] — cambios de estado
- [[BrawlBody]] — flash de impacto
- [[BrawlVfx]], VFX presentación — render particles

## Tipos de Efecto

| Kind | Uso | Ejemplo |
|------|-----|---------|
| Slash | Melé cono | Mordisco melé, Cone skill |
| Whip | Latigazo línea | Cintas ala W3 |
| Muzzle | Disparo projectil | Shotgun, Sniper, Burst |
| Lightning | Rayo | Chain, Unicornio |
| Dash | Embestida | Ariete skill |
| Pulse | Pulso | Movilidad Sprint, Last Stand |
| Land | Aterrizaje | Leap salto |
| Ring | Anillo impacto | Salto sobre blanco |
| Throw | Lanzamiento zona | Zone con demora |
| Pull | Atracción vórtex | Señuelo skill |

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Emisores:**
- [[BrawlWing]] → `Emit()` ataque
- [[BrawlMotor]] → `Emit()` land
- [[BrawlSkillOffense]], [[BrawlSkillSupport]] → `Emit()` skills
- [[BrawlFighter]] → eventos de daño/curación delegados a [[BrawlBody]]

**Suscriptores:**
- [[BrawlBody]], [[BrawlAnimator]], [[BrawlVfx]], VFX especializado

## Notas

- Estructura de datos pura (sin lógica)
- Bus centralizado; todos los VFX pasan por aquí
- Theme + Team definen color y apariencia (lavado rojo rival, saturado aliado)
- Source/Target para efectos direccionales
