---
tags: [script, world, player, camera]
---

# FirstPersonNeck.cs

**Ruta:** `Player/FirstPersonNeck.cs`

**Responsabilidad:** Mueve el ancla de la cámara en primera persona como si fuera un cuello. Lee el tilt de un `CinemachinePanTilt` y desplaza el transform local del objeto (CManchor) entre el pivote del cuello y el punto de los ojos, para que al mirar arriba o abajo la cámara pivote desde el cuello y no desde el centro del ancla. Solo escribe posición local; no decide estado, no suscribe eventos y no persiste nada.

**Vinculado a:** [[Index/06 - Player & World]]

## Referencias y tuning

**Referencias:** `panTilt` (CinemachinePanTilt que aporta el tilt; si está vacío, `Update` no hace nada).

**Tuning:** `neckPivot` (0, 1.45, 0.26) es el punto de articulación del cuello en espacio local del padre. `eyeOffset` (0, 0.16, 0.12) es el desplazamiento de los ojos respecto al pivote, rotado por el tilt.

## Métodos clave

- **`Update()`**: `transform.localPosition = neckPivot + Quaternion.Euler(panTilt.TiltAxis.Value, 0, 0) * eyeOffset`. Solo rota en X (tilt); el pan no pasa por este script.

## Invariantes

- Escribe solo `localPosition`. La rotación de la cámara la maneja el `CinemachinePanTilt`.
- Sin estado propio entre frames y sin eventos (no hay `OnEnable` ni `OnDisable`).
- **Quirk a verificar:** corre en `Update`. Si Cinemachine actualiza el tilt en `LateUpdate`, el ancla va un frame detrás de la cámara.

## Estado

NUEVO en S158.

## Conexiones

`CinemachinePanTilt` (fuente del tilt), CManchor (objeto donde vive el script, ancla de la cámara en primera persona).
