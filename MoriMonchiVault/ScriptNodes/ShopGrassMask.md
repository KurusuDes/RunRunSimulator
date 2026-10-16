---
tags: [script, world, store, grass, mask]
---

# ShopGrassMask.cs

**Ruta:** `World/Store/ShopGrassMask.cs`

**Responsabilidad:** Hornea una máscara 2D (R8) de cobertura sobre el suelo de la tienda. Donde hay colliders de suelo u obstáculos, el pasto se oculta; también recorta las exclusiones rectangulares de [[ShopGrassField]]. Publica la textura y el área como globals de shader. Corre en editor (`ExecuteAlways`).

## Campos Serializados

| Campo | Default | Descripción |
|-------|---------|-------------|
| `area` | Rect(-80, -30, 110, 105) | Área cubierta en XZ |
| `resolution` | 1024 | Resolución de la máscara (mín. 64) |
| `feather` | 0.45 | Suavizado del borde de colliders |
| `groundHeight` | 0 | Altura de referencia del suelo |
| `contactTolerance` | 0.35 | Tolerancia de contacto con el suelo |
| `roots` | [] | Raíces para buscar colliders (vacío = toda la escena activa) |
| `ignore` | [] | Transforms excluidos |
| `field` | — | [[ShopGrassField]] cuyas exclusiones se rasterizan |
| `rectFeather` | 0.45 | Suavizado de exclusiones rectangulares |
| `tallMeshHeight` | 3 | Altura a partir de la cual un mesh se trata como tronco |
| `trunkRadius` | 0.45 | Radio del tronco para meshes altos |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Bake()` | Rasteriza colliders y exclusiones, genera la textura y setea globals. Botón `Hornear` en Odin |

## Shader Globals

| Propiedad | Contenido |
|-----------|-----------|
| `_ShopGrassMaskTex` | Textura R8 de cobertura |
| `_ShopGrassMaskArea` | Origen XZ + 1/ancho + 1/alto |

## Conexiones

**Eventos suscritos (`GameEvents`):**
- `OnNavMeshRebaked` → `Bake`
- `OnShopZoneOpened` → re-bake (al abrir una expansión)

**Entrada:** [[ShopGrassField]] (`Exclusions`).

**Salida:** shader de pasto de la tienda vía globals.

## Invariantes

- Suscribe en `OnEnable`, desuscribe en `OnDisable`; libera la textura en ambos modos (Destroy en play, DestroyImmediate en editor).
- Colliders con `isTrigger`, `CharacterController`, rigidbody dinámico, o bajo un `NavMeshAgent` se ignoran.
- Si `isActiveAndEnabled` es false o el área es vacía, no hornea.
