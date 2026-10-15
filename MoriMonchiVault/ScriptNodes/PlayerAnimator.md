---
tags: [script, world, player]
---

# PlayerAnimator.cs

**Ruta:** `Player/PlayerAnimator.cs`

**Responsabilidad:** Capa de animación del jugador. Traduce eventos de `PlayerInputs` y de `PlayerController` a parámetros del Animator y a IK de manos. Anima los brazos en primera persona (FPArms, con `animator`) y el cuerpo visible (PlayerBody, con `bodyAnimator`). No decide estado de juego ni persiste nada.

**Vinculado a:** [[Index/06 - Player & World]]

## Referencias y tuning

**Referencias:** `animator` (Animator de FPArms; si está vacío, `Awake` toma el del propio GameObject), `bodyAnimator` (Animator de PlayerBody, opcional).

**Locomotion:** `speedDampTime` (0.1), `bodyTopSpeed` (3.6: el Speed del cuerpo es `moveInput.magnitude * bodyTopSpeed`).

**IK Blend:** `ikBlendSpeed` (4).

**Pet IK:** `petHeight` (0.35), `petStrokeSpeed` (7), `petStrokeAmplitude` (0.08), `petMaxWeight` (0.85).

**Hold IK:** `holdHandSpread` (0.18), `holdUnder` (0.12), `holdMaxWeight` (0.7).

## Parámetros del Animator

| Parámetro | Tipo | Quién lo escribe | Efecto en FPArms |
|-----------|------|------------------|------------------|
| `Speed` | float | `Update` (con `speedDampTime`) | Blend Idle / Walk |
| `Holding` | bool | `OnHeldChanged` | Estado Hold |
| `Petting` | bool | `OnPetChanged` | Estado Pet |
| `Throw` | trigger | `OnThrew` | Estado Throw |
| `Interact` | trigger | `OnInteracted` | Estado Interact |
| `Jump` | trigger | `OnJump` | Sin efecto: el controller no tiene transición que lo use |

En `bodyAnimator` solo se escribe `Speed` (escalado por `bodyTopSpeed`).

## Eventos suscritos

| Evento | Handler | Efecto |
|--------|---------|--------|
| `PlayerInputs.MoveChanged` | `OnMoveChanged` | Guarda el vector de movimiento |
| `PlayerInputs.Jumped` | `OnJump` | Trigger `Jump` |
| `PlayerController.HeldChanged` | `OnHeldChanged` | Guarda el `Transform` sostenido; `Holding = target != null` |
| `PlayerController.PetChanged` | `OnPetChanged` | Guarda el `Transform` acariciado; `Petting = target != null` |
| `PlayerController.Threw` | `OnThrew` | Trigger `Throw` |
| `PlayerController.Interacted` | `OnInteracted` | Trigger `Interact` |

`OnEnable` suscribe y `OnDisable` desuscribe todo.

## Métodos clave

- **`Update()`**: mueve `petWeight` y `holdWeight` hacia 1 o 0 a `ikBlendSpeed * dt` según haya target. Escribe `Speed` en `bodyAnimator` y en `animator`.
- **`OnAnimatorIK(layer)`**: con petting, la mano derecha va a `petTarget.position + up * petHeight` con un vaivén lateral (`petStrokeAmplitude`). Con hold, la mano izquierda va a `holdTarget - side + under` y la derecha a `holdTarget + side + under`. Si hay petting y hold a la vez, el peso de la derecha es el máximo de ambos. Sin target, los pesos IK van a 0.

## Invariantes

- Solo se suscribe a eventos static; no guarda referencias a `PlayerController` ni a `PlayerInputs`.
- Todas las escrituras al Animator van null-safe.
- Los pesos IK se desvanecen con `MoveTowards`, no saltan, al entrar y salir de hold o petting.

## Cambios S156

- Se agrega como componente al prefab FPArms (lo hace `HumanBodyAssembler`). `bodyAnimator` apunta al PlayerBody.
- Maneja los brazos en primera persona (IK de sostener y acariciar) y el cuerpo visible, con parámetros y eventos de `PlayerController`.

## Conexiones

[[PlayerInputs]], [[PlayerController]] (eventos `HeldChanged`, `PetChanged`, `Threw`, `Interacted`), [[HumanBodyAssembler]] (arma FPArms y PlayerBody), [[HumanoidClipBaker]] (controller `FPArms` con sus clips).
