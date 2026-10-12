---
tags: [script, world, player]
---

# PlayerController.cs

**Ruta:** `Player/PlayerController.cs`

**Responsabilidad:** Movimiento first-person del jugador con `CharacterController`. Lee input solo a través de los eventos estáticos de `PlayerInputs` y de `UIManager.OnUIFocusChanged`. Maneja el estado `PlayerStateType` (en el código actual solo se usan Exploring y Menu), el grab de MoriMonchis por hold-E, el tap-interact, el lanzamiento de objetos del hotbar y el petting por hold-E. **S149:** el controlador ya no tiene modo construcción; el estado distingue Exploring de Menu.

## Campos Tuning

**Move:** `moveSpeed` (5), `jumpForce` (5), `gravity` (-20).

**Reach (grab / interact):** `grabHoldDuration` (0.3 s: E sostenida más que esto = grab, menos = tap-interact), `grabRange` (3), `grabMask`.

**Pet:** `creatureLayer` (capa de los MoriMonchis; el petting usa `OverlapSphere` para que los paneles de NameTag no bloqueen).

**Throw:** `throwForce` (10), `throwUpwardBias` (0.15), `throwAimDistance` (30).

**Referencias:** `cinemachineCamera` (`CinemachineCamera`; se lee su transform y su `CinemachineInputAxisController` para congelar la cámara en menús), `holdAnchor` (`Transform` donde flota lo sujetado).

## Estado

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `state` | `PlayerStateType` | Exploring (primera persona, cursor bloqueado) o Menu (cursor libre, cámara congelada) |
| `held` | `IThrowable` | Lo que el jugador sostiene (un MoriMochi por grab, o un objeto del hotbar) |
| `petTarget` | `MoriMochiAgent` | Criatura en sesión de petting |
| `grabbing`, `grabTimer` | bool, float | Estado de la E sostenida |

## Eventos Suscritos

| Evento | Handler | Efecto |
|--------|---------|--------|
| `PlayerInputs.MoveChanged` | `OnMoveChanged` | Guarda el vector de movimiento |
| `PlayerInputs.Jumped` | `OnJump` | Salto si está en el suelo y en Exploring |
| `PlayerInputs.InteractPressed` | `OnInteractPressed` | Drop si sostiene algo; si no, petting; si no, inicia el timer de grab |
| `PlayerInputs.InteractReleased` | `OnInteractReleased` | Termina petting, o si fue tap, ejecuta `IInteractable.Interact` |
| `PlayerInputs.ThrowPressed` | `OnThrow` | Lanza lo sostenido; si no, `HotbarController.UseActive()` |
| `UIManager.OnUIFocusChanged` | `OnUIFocusChanged` | Pasa a Menu o vuelve a Exploring |

Se desuscribe en `OnDisable`.

## Métodos clave

- **`Move()`** (Update, solo Exploring): movimiento relativo a la cámara (forward/right sin Y), gravedad propia y `controller.Move`.
- **`UpdateGrabHold()`**: si la E lleva `grabHoldDuration`, busca un `MoriMochiAgent` en vista y lo agarra con `OnGrab(holdAnchor)`. Si no hay, lanza el item activo del hotbar con `ComputeThrowImpulse`.
- **`TryBeginPetting(out agent)`**: `OverlapSphere(transform.position, grabRange, creatureLayer)`; el primer agente que acepte `BeginPetting()` gana.
- **`TryFindInView<T>()`**: raycast de la cámara con `QueryTriggerInteraction.Collide`, ordenado por distancia. Un collider sólido que no sea T bloquea; un trigger que no sea T se atraviesa.
- **`ComputeThrowImpulse(ignore)`**: busca el punto de mira con un raycast de la cámara y lanza desde `holdAnchor` hacia ese punto, con `throwUpwardBias`.
- **`SetState(PlayerStateType)`**: Exploring bloquea el cursor y habilita el `CinemachineInputAxisController`; Menu lo libera. Salir de Exploring termina el petting activo.

## Prioridades de tecla E

| Situación | Resultado |
|-----------|-----------|
| Sostiene algo + PRESS | Suelta en el lugar (`Drop`) |
| Libre + PRESS sobre criatura acariciable | Petting mientras se mantiene E |
| Libre + TAP | `IInteractable.Interact()` (no aplica a `MoriMochiAgent`) |
| Libre + HOLD >= `grabHoldDuration` | Agarra un MoriMochi en vista, o lanza el item activo del hotbar |

Click de ataque (`ThrowPressed`): lanza lo sostenido, o usa el item activo del hotbar.

## Invariantes

- No referencia `PlayerInputs` directamente, solo se suscribe a sus eventos static (mismo patrón que `GameEvents`).
- Look/aim lo posee Cinemachine; el controller solo lee el forward de la cámara.
- Grab y throw pasan por `IThrowable`, así el controller no conoce el tipo concreto sujetado.
- En Menu el action map Player está deshabilitado (`PlayerInputs` lo gatea por foco de UI): no llega ningún grab ni interact.
- `TryFindInView` usa `QueryTriggerInteraction.Collide` porque los MoriMonchis llevan collider trigger mientras están NavMesh-driven.
- El petting termina al salir de Exploring (safety net).

## Cambios S149

- **Retirado:** modo construcción. Ya no existe `OnBuildModeChanged` ni movimiento en Building.
- **Petting:** `TryBeginPetting` usa `agent.BeginPetting()` (bool) como filtro, no `CanBePetted`.

## Vinculado a

[[Index/06 - Player & World]]

## Conexiones

[[PlayerInputs]], [[PlayerAnimator]], [[ThrowableObject]], [[MoriMochiAgent]], [[HotbarController]], [[UIManager]], [[IInteractable]], [[IThrowable]]
