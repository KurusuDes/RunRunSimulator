---
tags: [script, ui, service, singleton, graphics]
---

# MonchiPortraitService.cs

**Ruta:** `UI/MonchiPortraitService.cs`

**Responsabilidad:** Singleton "fotomatón" estudio oculto. Renderiza capturas 2D de MoriMonchis (full-body retrato). Cachea Texture2D/Sprite por UniqueID/ToStringID. Pipeline: Assemble visual, SetMood, pose Idle, encuadre automático por Bounds, RenderTexture + ReadPixels. **S93:** Pipeline de headshot eliminado completamente (`GetHeadshot`, `GetHeadshotSprite`, `CaptureHeadshot`, cachés de headshot y 8 campos serializados de configuración). **S145:** el encuadre sale de `MonchiFraming.TryWorldBounds` sobre el ModelRoot del booth, y el render se hace con sombras desactivadas.

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `GetPortrait(CreatureDNA dna)` | `Texture2D` | Retrato full-body (caché) |
| `GetPortraitSprite(CreatureDNA dna)` | `Sprite` | Sprite full-body (caché) |

Clave de caché: `UniqueID` o, si está vacío, `ToStringID()`.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `visualBank` | `MonchiVisualBankSO` | - | Visual bank Suriyun |
| `furTypeDatabase` | `FurTypeDatabaseSO` | - | Fur types |
| `boothVisualizer` | `MonchiVisualizer` | - | Visualizador |
| `boothCamera` | `Camera` | - | Cámara capture |
| `boothRoot` | `GameObject` | - | Raíz booth (desactivada) |
| `textureSize` | `int` | 384 | Tamaño retrato |
| `framePadding` | `float` | 1.15 | Padding retrato |
| `cameraPitch` | `float` | 12 | Pitch retrato |
| `cameraYaw` | `float` | 180 | Yaw retrato (frontal) |
| `portraitMood` | `MonchiMood` | Neutral | Expresión |

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `cache` | `Dictionary<string, Texture2D>` | Caché retrato full-body |
| `spriteCache` | `Dictionary<string, Sprite>` | Caché sprite retrato |
| `rt` | `RenderTexture` | RenderTexture retrato (384×384) |
| `bakedMesh` | `Mesh` | Malla de trabajo para `MonchiFraming`; se crea en el primer `Capture` (S145) |

## Pipeline de Capture (S145)

1. Activa `boothRoot` (los renderers deben estar activos para contar en el encuadre).
2. `SetBank`, `SetFurDatabase`, `Assemble(dna)` y `SetMood(portraitMood)` en el booth.
3. Reproduce la animación `Idle` en frame 0 y fuerza `Update(0)`.
4. `MonchiFraming.TryWorldBounds(ModelRoot)`. Si falla, desactiva el booth y devuelve null.
5. Cámara: radio = `extents.magnitude × framePadding`; distancia = `radio / sin(fov/2)`; dirección = `Euler(pitch, yaw) × forward`; posición = `center − dirección × distancia`; mira con `LookRotation(dirección)`.
6. Render a `rt` con sombras desactivadas (`QualitySettings.shadows`), `ReadPixels` a un `Texture2D` RGBA32 sin mipmaps, y restaura `RenderTexture.active`.
7. Desactiva el booth y guarda la textura en `cache[key]`.

## Cambios S58-S92

**Métodos legacy (desaparecidos S93):**
- `GetHeadshot()`, `GetHeadshotSprite()` — fueron removidas en S93
- `CaptureHeadshot()` — pipeline de cabeza eliminado
- Cachés: headshotCache, headshotSpriteCache eliminadas
- Campos: headshotWidth, headshotHeight, headshotPadding, headshotTopFraction, headshotCenterHeight, headshotPitch, headshotYaw, headshotRoll eliminados (8 campos totales)

## Vinculado a

- [[Index/10 - Visualization]]
- [[MonchiPortraitUI]] — consumer principal
- [[MonchiVisualBankSO]], [[FurTypeDatabaseSO]] — data visual

## Conexiones

**Entrada:**
- API: GetPortrait (por DNA)
- Construcción serializada en GameScene

**Encuadre y visual:**
- [[MonchiFraming]] — bounds del ModelRoot del booth
- [[MonchiVisualizer]] — `SetBank`, `SetFurDatabase`, `Assemble`, `SetMood`, `Animator`, `ModelRoot`
- [[MonchiMood]] — expresión del retrato

**Salida:**
- Texture2D/Sprite caché
- UI panels (vía `MonchiPortraitUI`)

## Notas

- `OnDestroy` destruye las texturas cacheadas, `rt` y `bakedMesh`.
- Si el booth no tiene renderers activos, `Capture` devuelve null y no cachea.
