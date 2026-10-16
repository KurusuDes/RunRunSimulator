---
tags: [script, world, store, grass, trample, shader]
---

# ShopTrampleMap.cs

**Ruta:** `World/Store/ShopTrampleMap.cs`

**Responsabilidad:** Mantiene un mapa de pisado en RenderTexture (ARGBHalf) para el pasto de la tienda. Cada frame: decae el mapa (fresco y rastro con vida media distinta), estampa las huellas de los [[GrassTrampler]] activos y publica la textura como global. Solo corre en play mode.

## Campos Serializados

| Campo | Default | Descripción |
|-------|---------|-------------|
| `trampleShader` | — | Shader con los pases de decay (0) y stamp (1) |
| `area` | Rect(-80, -30, 110, 105) | Área XZ del mapa |
| `resolution` | 1024 | Resolución de la RT (mín. 64) |
| `freshHalfLife` | 0.35 s | Vida media de la huella fresca |
| `trailHalfLife` | 6 s | Vida media del rastro |
| `trailGain` | 0.6 | Ganancia base del rastro |
| `stampRate` | 8 | Presión de estampado por segundo |

## Shader Globals

| Propiedad | Contenido |
|-----------|-----------|
| `_ArenaTrampleTex` | RT de pisado (canal R fresco, G rastro) |
| `_ArenaTrampleArea` | Origen XZ + 1/tamaño (cuadrado) |
| `_FreshDecay`, `_TrailDecay` | Factores de decay del frame (material, no global) |

## Ciclo por frame (`LateUpdate`)

1. `ApplyDecay`: blit de `current` a `scratch` con el pase 0, luego swap.
2. `CollectStamps`: un request por `GrassTrampler.All`.
3. `DrawStamps`: quads GL sobre `current` con pase 1; limpia la cola.
4. Publica `_ArenaTrampleTex`.

En edición no decae ni estampa: publica textura negra.

## Conexiones

**Entrada:** [[GrassTrampler]] (`All`, `Position`, `Radius`, `Trail`).

**Salida:** shader del pasto vía `_ArenaTrampleTex` y `_ArenaTrampleArea`.

**Relacionado:** [[ShopGrassMask]] (máscara estática de cobertura, distinta de este mapa dinámico).

## Invariantes

- `OnEnable` crea RTs y materiales; `OnDisable` los libera y restablece la textura negra global.
- Sin `trampleShader` no hace nada.
- Área cuadrada para el shader: lado = max(ancho, alto), centrada en `area`.
