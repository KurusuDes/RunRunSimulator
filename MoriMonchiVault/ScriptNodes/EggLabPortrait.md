---
tags: [script, ui, render, creature]
---

# EggLabPortrait.cs

**Ruta:** `UI/EggLabPortrait.cs`

**Responsabilidad:** Renderizador de portrait 3D para huevos en laboratorio. **S136 NUEVO.** Cámara dedicada con RenderTexture, orbita automática alrededor del target, restringe visibilidad a layer MonchiFocus, retorna RT para mostrar en UI.

## Campos Serializados (Required)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `portraitCamera` | `Camera` | Cámara dedicada para renderizar portrait |

## Campos Serializados (Configuración)

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `textureSize` | `int` | 512 | Resolución de RenderTexture (512x512) |
| `orbitSpeed` | `float` | 35 | Velocidad de rotación orbital (grados/segundo) |
| `distance` | `float` | 0.95 | Distancia de cámara al target |
| `height` | `float` | 0.16 | Altura de cámara sobre target |
| `pitch` | `float` | 8 | Ángulo vertical (pitch) de órbita |

## Ciclo de Vida

| Evento | Acción |
|--------|--------|
| `Awake()` | Obtiene layer MonchiFocus, crea RenderTexture, asigna a camera, deshabilita camera, setea culling mask |
| `LateUpdate()` | Si target existe: incrementa yaw, llama UpdateOrbit() |
| `OnDestroy()` | Libera RenderTexture |

## Métodos Públicos

### Show(Transform newTarget)

```csharp
public RenderTexture Show(Transform newTarget)
```

**Responsabilidad:** Activa renderización de un nuevo target.

**Flujo:**
1. Si hay target previo → Hide()
2. Asigna `target = newTarget`
3. Si focusLayer >= 0 y target != null:
   - Itera todos los Transform hijos (recursivo)
   - Almacena (transform, layer) original en lista
   - Cambia gameObject.layer a focusLayer
4. Habilita cámara: `portraitCamera.enabled = true`
5. Llama UpdateOrbit() para posicionar inicial
6. Retorna RenderTexture

**Resultado:** Solo el target (y sus hijos) es visible en la RT; orbita comienza desde yaw actual

### Hide()

```csharp
public void Hide()
```

**Responsabilidad:** Detiene renderización y restaura state.

**Flujo:**
1. RestoreLayers() → reestablece capas originales de todos los hijos
2. Deshabilita cámara
3. Asigna `target = null`
4. Limpia lista de originalLayers

## Métodos Privados

### RestoreLayers()

Itera originalLayers y restaura `gameObject.layer` a su valor original. Limpia lista.

### LateUpdate()

Ejecutado cada frame.

**Flujo:**
1. Si target es null → return (no hacer nada)
2. `yaw += orbitSpeed * Time.deltaTime` (incremento continuo)
3. Llama UpdateOrbit() para re-posicionar cámara

**Resultado:** Órbita suave alrededor del target

### UpdateOrbit()

```csharp
private void UpdateOrbit()
```

**Responsabilidad:** Posiciona y rota cámara en órbita.

**Flujo:**
1. Si target es null → return
2. Centro: `center = target.position + Vector3.up * height`
3. Dirección: `dir = Quaternion.Euler(pitch, yaw, 0) * Vector3.forward` (rotación pitch+yaw)
4. Posición: `pos = center - dir * distance` (retrocede de la dirección)
5. Asigna posición y rotación a portraitCamera:
   - `transform.position = pos`
   - `transform.rotation = Quaternion.LookRotation(center - pos, Vector3.up)` (mira hacia center)

**Geometría:** Cámara orbita en círculo a altura `height`, ángulo `pitch` arriba, distancia `distance`, con yaw cambiante

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `rt` | `RenderTexture` | Texture renderizada, creada en Awake |
| `target` | `Transform` | Target actual (huevo) |
| `yaw` | `float` | Ángulo horizontal acumulado (incrementado en LateUpdate) |
| `focusLayer` | `int` | ID numérico de layer MonchiFocus (cacheado) |
| `originalLayers` | `List<(Transform, int)>` | Backup de capas originales de target y hijos |

## Cambios S136

**Nuevo script de renderización de portrait:**
- Cámara dedicada (no interfiere con escena principal)
- Layer culling para aislar target (solo MonchiFocus visible)
- Órbita automática (sin input)
- RenderTexture reutilizable (misma RT para todos los targets)

**Pattern:**
- Show(target) activa, Hide() desactiva
- Restauración de layers automática
- Sin estado global (cada instancia tiene su propia RT y lista de layers)

## Notas S136

- `portraitCamera.enabled = false` en Awake (se habilita con Show())
- Culling mask = MonchiFocus layer (modo de enfoque, otros GameObjects ignorados)
- RenderTexture es permanente durante sesión (creada en Awake, liberada en OnDestroy)
- Layer restoration es automática (no deja suciedad en escena)
- Órbita es continua (yaw nunca se resetea, acumula infinitamente)
- yaw comienza en 0 (no se inicializa en Awake)

## Invariantes

- RenderTexture tiene resolución fija (512x512)
- Órbita es circular (constante distance + height, solo yaw/pitch varían)
- Si focusLayer no existe (NameToLayer retorna -1), se ignora layer switching (cull mask stays default)
- UpdateOrbit() se ejecuta en LateUpdate (después de animaciones)
- Target se sustituye sin transición (Hide/Show es limpio, no fade)

## Performance

- Una RenderTexture compartida (no se crea per-target)
- Culling mask reduce sobrecarga (solo renderiza target + hijos)
- LateUpdate cada frame (orbita suave, no discretizada)
- Layer swap es O(N hijos), acceptable para modelos pequeños (huevos ~10-20 transforms)

## Vinculado a

- [[Index/31 - EggLab & Incubadora]]
- [[Resources/Scenes/EggLab.unity]] — escena única
- [[EggLabPanel]] — llamador de Show/Hide

## Conexiones

**Entrada:**
- Show(Transform) → target a renderizar
- LateUpdate → posiciona órbita

**Salida:**
- RenderTexture con portrait (asignado a UI backgroundImage en EggLabPanel.OnSelected)
- Layer switching temporal (restaurado en Hide)

**Dependencias:**
- Layer "MonchiFocus" debe existir en proyecto
- portraitCamera debe estar en escena EggLab
