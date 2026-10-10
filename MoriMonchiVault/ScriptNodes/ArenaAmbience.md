---
tags: [script, world, expedition, ambience, particles, light-shafts]
---

# ArenaAmbience.cs

**Ruta:** `World/Expedition/ArenaAmbience.cs`

**Responsabilidad:** Ambiente visual de la arena según la paleta activa. Se suscribe al evento `Applied` de `ArenaPaletteApplier` y, por cada paleta, prende o apaga luciérnagas (`fireflies`), polvo de hada (`fairyDust`, teñido con `DustColor`) y los rayos de luz (`ArenaShapeShafts`). En `LateUpdate` desplaza los emisores en XZ hacia el `focus` (ArenaTargetGroup) para que el ambiente siga la cámara sin alterar su altura. S147.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]] (sección 8f)

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `palette` | ArenaPaletteApplier (Required) | Fuente del evento `Applied` y de `Current` |
| `fireflies` | ParticleSystem | Luciérnagas; on/off según `ArenaPaletteSO.Fireflies` |
| `fairyDust` | ParticleSystem | Polvo de hada; on/off según `FairyDust`, color según `DustColor` |
| `shafts` | List<ArenaShapeShafts> | Rayos de luz; `enabled` según `LightShafts` |
| `focus` | Transform | Objetivo de seguimiento en XZ (ArenaTargetGroup). Si es null no sigue |
| `followSharpness` | float (Min 0, default 1.5) | Suavizado del seguimiento: `t = 1 - exp(-sharpness * dt)` |

## Métodos Públicos

Ninguno. Acceso solo por evento `ArenaPaletteApplier.Applied`.

## Métodos Privados

| Método | Descripción |
|--------|-------------|
| `Apply(ArenaPaletteSO p)` | Enciende/apaga luciérnagas y polvo; tiñe los hijos de `fairyDust` con `DustColor` conservando el alpha original de cada `startColor`; fija `enabled` de cada `ArenaShapeShafts` |
| `SetSystem(ParticleSystem, bool on)` | `on` → `Play(true)` si no está reproduciendo; `off` → `Stop(true, StopEmittingAndClear)` |
| `Follow(ParticleSystem, float t)` | Lerp en XZ hacia `focus`, mantiene Y actual |

## Ciclo de Vida

1. **OnEnable:** suscribe `palette.Applied += Apply`; si `palette.Current` ya existe, aplica de inmediato.
2. **Applied (evento):** `Apply(p)` con la paleta nueva.
3. **LateUpdate:** si hay `focus`, mueve `fireflies` y `fairyDust` hacia el focus en XZ.
4. **OnDisable:** desuscribe `palette.Applied`.

## Invariantes

- Solo lee estado de `ArenaPaletteSO`; no persiste ni toca red.
- Solo reacciona al evento `Applied`; no busca otros sistemas con `Find*`. Las referencias se asignan en el Inspector.
- El tinte de `fairyDust` se aplica a todos los `ParticleSystem` hijos (`GetComponentsInChildren`, incluye inactivos).
- Los emisores solo cambian X/Z; la altura queda como la tiene el prefab.

## Conexiones

- [[ArenaPaletteApplier]] (evento `Applied`, origen de la paleta)
- [[ArenaPaletteSO]] (campos `Fireflies`, `LightShafts`, `FairyDust`, `DustColor`)
- [[ArenaShapeShafts]] (rayos de luz; se togglea `enabled`)
- ArenaTargetGroup (Transform `focus`, asignado en Inspector)
