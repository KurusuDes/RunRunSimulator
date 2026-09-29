---
tags: [script, dev, camera, cinematography]
---

# TrailerCameraRig.cs

**Ruta:** `Systems/Dev/TrailerCameraRig.cs`

**Responsabilidad:** Controlador de cámara para grabación de tráilers. **S138:** Herramienta dev que se instancia en runtime por MCP (clon de Main Camera). Implementa tres modos de movimiento: Orbit (orbita suave alrededor de un punto), Dolly (interpolación lineal entre posiciones), Static (posición fija). Evita obstáculos con SphereCast y controla FOV + DepthOfField dinámicamente. Hace parte del pipeline `Tools/Trailer/` (synth.py, logo.py, make_trailer.sh).

## Modos de cámara

- **Orbit:** Orbita circular/helicoidal alrededor de un punto de anclaje (Target o FixedPoint). Radio inicial Radius puede interpolar a RadiusEnd. Altura fija Height. Velocidad angular AngularSpeed (°/s). Ideal para retratos de criaturas y muestras de arena.
- **Dolly:** Interpolación suave lineal desde `From` a `To` durante `Duration`. Usado para tránsitos cinematográficos.
- **Static:** Cámara anclada a posición fija (Mode.Static sin cambios en LateUpdate).

## Campos serializados

**Anclaje:**
- `Target` (Transform) — Punto dinámico a perseguir (nul = usa FixedPoint). LookOffset offset de ojo al punto.
- `FixedPoint` (Vector3) — Punto estático de anclaje si Target es null
- `LookOffset` (Vector3) — Offset desde anclaje a punto de enfoque visual (defecto: 0.4 hacia arriba)

**Orbit:**
- `Radius` (float) — Radio inicial de órbita (defecto: 3)
- `Height` (float) — Altura de cámara sobre anclaje (defecto: 1.2)
- `StartAngle` (float) — Ángulo inicial en °
- `AngularSpeed` (float) — °/segundo de rotación (defecto: 20)
- `RadiusEnd` (float) — Radio final si != -1, interpola desde Radius. -1 = radio constante

**Dolly:**
- `From` (Vector3) — Posición de inicio
- `To` (Vector3) — Posición final
- `Duration` (float) — Tiempo de transición en segundos (defecto: 3)

**Óptica:**
- `FovStart` (float) — FOV inicial en ° (defecto: 40)
- `FovEnd` (float) — FOV final en ° (defecto: 40)
- `Smoothing` (float) — Exponential smoothing del punto de enfoque. Valores más altos = más lag (defecto: 8)

**Obstáculos y DOF:**
- `AvoidObstacles` (bool) — Habilita SphereCast para evitar colisiones (defecto: true)
- `ObstaclePadding` (float) — Distancia de separación de obstáculos (defecto: 0.3)
- `Dof` (DepthOfField URP) — Componente de DOF opcional. Si asignado, focusDistance se actualiza automáticamente

## Métodos públicos

- `Restart()` — Resetea elapsed y lookInitialized. Útil para reiniciar una toma.

## State internals

- `cam` (Camera) — Caché de componente Camera
- `elapsed` (float) — Tiempo acumulado desde inicio
- `smoothedLook` (Vector3) — Punto de enfoque suavizado
- `lookInitialized` (bool) — Flag de inicialización del smoothing

## Lógica en LateUpdate

1. Calcula `k` (normalized progress, 0-1 según Duration)
2. Determina `anchor` desde Target o FixedPoint
3. Calcula `look` = anchor + LookOffset
4. Según Mode: resuelve posición deseada (Orbit → helix, Dolly → lerp, Static → nada)
5. Si AvoidObstacles, aplica `Unblocked()` (SphereCast evita hijos de Target)
6. Smooth exponencial sobre `smoothedLook` para lag visual natural
7. Orienta cámara hacia `smoothedLook`
8. Actualiza DOF focusDistance y FOV interpolado

## Obstáculo avoidance

Método `Unblocked()` lanza SphereCast (radio 0.2) desde `from` hacia `to`. Si golpea (ignorando triggers + hijos de Target), retorna posición sobre la colisión menos `ObstaclePadding`. Mantiene vista limpia a coste mínimo.

## Uso en escena

Crear un clon de Main Camera en runtime vía MCP. Asignar este script, configurar Target (Creature/jugador), Mode, parámetros Orbit/Dolly. Play mode: rige automáticamente en LateUpdate. Para múltiples tomas, llamar `Restart()` entre clips.

**Vinculado a:** [[Index/12 - Unity MCP]] (tooling dev)

**Conexiones:** Camera (URP), DepthOfField, Physics.SphereCast, Tools/Trailer/ pipeline
