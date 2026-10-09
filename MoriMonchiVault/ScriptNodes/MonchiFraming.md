---
tags: [script, ui, graphics, camera, helper, static]
---

# MonchiFraming.cs

**Ruta:** `UI/MonchiFraming.cs`

**Responsabilidad:** Helper estático de encuadre: calcula los bounds en espacio mundo de un MoriMochi horneando sus `SkinnedMeshRenderer` con `BakeMesh`. Sin estado propio ni dependencias de escena. Lo usan los dos retratos (fotomatón y live) para enfocar la cámara sobre la criatura.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `TryWorldBounds(root, scratch, out bounds)` | Recorre los `SkinnedMeshRenderer` activos hijos de `root`. Por cada uno hornea la malla en `scratch`, toma las 8 esquinas de sus bounds locales y las pasa a mundo con `position + rotation × esquina`. Devuelve false si `root` o `scratch` son null o no hay renderers |

## Detalles

- `BakeMesh(scratch, false)` ya devuelve la malla escalada: por eso la transformación a mundo no aplica escala, solo posición y rotación del renderer.
- Solo considera GameObjects activos (`GetComponentsInChildren(false)`). Por eso el fotomatón activa su booth antes de encuadrar.
- `scratch` se reutiliza entre renderers y entre llamadas; el dueño (el retrato) es quien lo crea y lo destruye.

## Conexiones

- [[MonchiPortraitService]] — encuadre del retrato full-body (booth)
- [[MonchiLivePortrait]] — encuadre de la cámara live sobre `ModelRoot`
- [[MonchiVisualizer]] — `ModelRoot` (raíz de la malla)
- [[Index/10 - Visualization]]

## Notas

- Sin `scratch` o sin renderers, el llamador usa su fallback (la live usa un cubo de tamaño 1 sobre la raíz de la criatura).
