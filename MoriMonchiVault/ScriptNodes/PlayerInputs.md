---
tags: [script, world]
---

# PlayerInputs.cs

**Ruta:** `Player/PlayerInputs.cs`

**Responsabilidad:** Dueño del action map "Player" (único script que toca Input System). Traduce callbacks del asset a eventos estáticos, decoupled (GameEvents patrón). El gating por foco de UI es automático: el mapa Player se deshabilita en menús vía `UIManager.OnUIFocusChanged`. Look/aim NO está aquí (Cinemachine lo lee directamente).

**Eventos estáticos:**
- `MoveChanged` (Action<Vector2>) — Move action (continuous, fired on change)
- `Jumped` (Action) — Jump pressed
- `InteractPressed` (Action) — Interact key DOWN
- `InteractReleased` (Action) — Interact key UP
- `ThrowPressed` (Action) — Attack button (lanzar lo sostenido o usar el item activo)
- `HotbarScrolled` (Action<int>) — Mouse wheel scroll (+1/-1 por step, threshold configurable)
- `DropPressed` (Action) — Q key (drop active hotbar item)

**S149:** Se retira `BuildToggled` junto con el modo construcción.

**Vinculado a:** [[Index/06 - Player & World]]

**Conexiones:** [[PlayerController]], [[PlayerAnimator]], [[HotbarController]], [[UIManager]]

**Notas:**
- Action map "Player" se habilita en `OnEnable` y se deshabilita en `OnDisable`. También se deshabilita en `OnUIFocusChanged(true)` y se vuelve a habilitar en `false`.
- `InputSystem_Actions` se crea en `Awake` y se libera en `OnDestroy`.
- Campo `scrollThreshold` (default 0.1) en editor para tuning sensibilidad rueda.
- Desuscripción completa en OnDisable (patrón: OnEnable/OnDisable mirror).
