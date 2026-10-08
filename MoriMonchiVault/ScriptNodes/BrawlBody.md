---
tags: [script, world, brawl, body, visual]
---

# BrawlBody.cs

**Ruta:** `World/Brawl/BrawlBody.cs`

**Responsabilidad:** Deformación visual del cuerpo. Spring pulso (squash-stretch). Flash de impacto (rojo aliado, blanco rival). Curación en verde. KO encogimiento. Gestión de material flash.

## Propiedades Internas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `pulse`, `pulseVelocity` | float | Spring animation |
| `koScale` | float | Escala post-KO (encogimiento) |
| `flashing` | bool | En animación flash |
| `flashColor`, `flashPeak` | Color, float | Color y pico alpha |

## Pulso (Spring)

- Aplica a escala del pivot: `(1-s×0.5, 1+s, 1-s×0.5)`
- Stiffness 260 (rigidez), Damping 12 (amortiguación)
- Resorte calcula suavemente: velocity → aceleración → posición
- MaxPulse ±0,6 (límite de deformación)
- SpringStep 1/120 (resolución fija 8,3 ms)

## Triggers de Pulso

| Trigger | Magnitud |
|---------|----------|
| Hit (golpe recibido) | +0,3 |
| Cast (casteo habilidad) | -0,18 (inversión) |
| Fire (disparo básico) | +0,25 |
| Land (salto aterrizaje) | -0,35 |
| Heal (curación) | +0,12 |

## Flash de Impacto

**Impacto recibido:**
- **Aliado (nuestro):** Rojo (1, 0,12, 0,08)
- **Rival (enemigo):** Blanco puro

**Intensidad:**
- **Light (< 600 dmg):** Alpha 0,6, duración 0,2 s
- **Heavy (≥ 600 dmg):** Alpha 0,85, duración 0,2 s

**Implementación:**
- Capa material flash en final de sharedMaterials (MonchiVisualizer.SetFlash)
- Desvanece linealmente en 0,2 s

## Flash de Curación

- Color verde (0,45, 1, 0,55)
- Alpha 0,35, duración 0,25 s
- Aplicado cuando heal > 0,5

## KO Encogimiento

- Demora 1,4 s después de KO
- Duración encogimiento 0,5 s
- Escala → 0 (desvanecimiento visual)

## Eventos Suscritos

| Evento | Handler |
|--------|---------|
| `BrawlFighter.OnBound` | `HandleBound()` — init refs |
| `BrawlFighter.OnDamaged` | `HandleDamaged()` — flash + pulso |
| `BrawlFighter.OnHealed` | `HandleHealed()` — flash curación + pulso |
| `BrawlFighter.OnKnockedOut` | `HandleKnockedOut()` — KO routine |
| `BrawlSkillCaster.OnCastStarted` | `HandleCastStarted()` — pulso -0,18 |
| `BrawlSkillCaster.OnCastFired` | `HandleCastFired()` — lock acción |
| `BrawlWing.OnAttackFired` | `HandleAttackFired()` — pulso fuego |
| `BrawlFx.Emitted` | `HandleFx()` — responde a efectos especiales |

## Componentes

- **Pivot:** Transform escaleado y elevado (Lift)
- **Visualizer:** Acceso a materiales
- **BrawlTuningSO:** Parámetros globales

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Dueño:**
- [[BrawlFighter]] — propietario

**Entrada:**
- [[BrawlFighter]], [[BrawlWing]], [[BrawlSkillCaster]], [[BrawlFx]] → eventos
- [[MonchiVisualizer]] → SetFlash(), acceso materiales

## Notas

- LateUpdate calcula spring (suavidad independiente de Time.deltaTime)
- MaxSpringDt 0,034 (34 ms máx per frame; multi-stepping si dt > 34 ms)
- RimPower 0,55; RimInsideMask 0,55 (parámetros shader rim light)
- HeavyHitDamage 1000 dmg (umbral visual impacto pesado)
- Pivot.localPosition Y = fighter.Lift (controlado por Motor)
- KO routine encadena delay + shrink para timing cinético
