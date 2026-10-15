---
tags: [script, editor, humanos, animacion]
---

# HumanoidClipBaker.cs

**Ruta:** `Editor/HumanoidClipBaker.cs`

**Responsabilidad:** Herramienta de editor (menú `RunRunSimulator/Humans/Bake Clips`) que genera por código los clips humanoides (curvas de músculos genéricos de Unity) y los tres AnimatorController del proyecto: `HumanNpc` (clientes), `FPArms` (brazos del jugador en primera persona) y `PlayerBody` (cuerpo visible del jugador, desde S158). Son provisorios hasta tener un pack de animaciones. No corre en runtime.

**Vinculado a:** [[Index/06 - Player & World]]

**Conexiones:** [[HumanBodyAssembler]] (asigna los controllers a los prefabs), [[NpcBody]] (usa `HumanNpc` vía prefab), [[PlayerAnimator]] (escribe los parámetros de `FPArms`; `PlayerBody` solo recibe `Speed`)

## Clips generados

Carpeta: `Resources/Animations/Humans/`. Cada clip usa 24 muestras y una curva de `RootT.y` para el bob. La raíz no rota ni se mueve en XZ. **S158:** son 11 clips (antes 9).

| Clip | Duración | Loop | Uso |
|------|----------|------|-----|
| `Human_Idle` | 3.0 s | sí | Cliente parado (blend con Speed 0) |
| `Human_Walk` | 1.05 s | sí | Cliente caminando (Speed 1.4 y 3.6; el segundo a timeScale 1.9) |
| `Human_Talk` | 2.4 s | sí | Cliente negociando (bool `Talking`) |
| `FP_Idle` | 3.0 s | sí | Brazos FP en reposo (parten de `Stand` vía `FpLowered`) |
| `FP_Walk` | 0.7 s | sí | Brazos FP al caminar (Speed 1), sobre `Stand` |
| `FP_Hold` | 2.5 s | sí | Sostener un MoriMochi (`Holding`) |
| `FP_Pet` | 1.2 s | sí | Acariciar (`Petting`) |
| `FP_Throw` | 0.5 s | no | Lanzar (trigger `Throw`) |
| `FP_Interact` | 0.45 s | no | Interactuar (trigger `Interact`) |
| `Player_Idle` | 3.0 s | sí | Cuerpo visible del jugador en reposo (`IdlePose` + `OpenArms`). S158 |
| `Player_Walk` | 1.05 s | sí | Cuerpo visible del jugador caminando (`WalkPose` + `OpenArms`). S158 |

## Controllers

- **`HumanNpc`:** parámetros `Speed` (float) y `Talking` (bool). Blend "Locomotion" (Idle / Walk, armado por `BuildLocomotion`) y estado `Talk`. Transiciones de 0.25 s.
- **`FPArms`:** parámetros `Speed`, `Holding`, `Petting` (bool) y `Throw`, `Interact`, `Jump` (trigger). Layer 0 con `iKPass`. Blend Idle (0) / Walk (1) armado en la propia función. Hold y Pet entran y salen por `Link` con condición bool. Throw e Interact entran por AnyState y vuelven a Locomotion con exit time 0.85. **S158:** duraciones para subir desde el reposo fuera de cuadro y bajar: Loco→Hold/Pet 0.25 s, Hold/Pet→Loco 0.4 s, AnyState→Throw 0.12 s, AnyState→Interact 0.15 s, regreso de one-shots 0.35 s.
- **`PlayerBody` (S158):** parámetro `Speed` (float). Un solo estado, Locomotion, armado por `BuildLocomotion` con los mismos umbrales que `HumanNpc` (Idle 0, Walk 1.4, Walk 3.6 a timeScale 1.9). Sin transiciones. Es el default state.

## Flujo de Bake

1. `Bake(name, length, loop, pose)` crea el `.anim` o reutiliza el existente, hace `ClearCurves` y lo reescribe.
2. Cada función de pose (`IdlePose`, `WalkPose`, `FpWalkPose`, etc.) llama `Stand` o `FpBase` y ajusta músculos. `Fingers(curl, spread)` genera los dedos. **S158:** `FpLowered` es solo `Stand` y lo usan `FP_Idle` y `FP_Walk`. `PlayerIdlePose` y `PlayerWalkPose` son la pose NPC más `OpenArms`.
3. Las curvas se suavizan con `SmoothTangents(0)` y se aplican con `SetEditorCurve`.
4. `BuildNpcController`, `BuildFpController` y `BuildPlayerBodyController` reconstruyen los controllers. `FreshController` borra estados, AnyState y blend trees previos.

## Quirks ⚠️

- **`Jump` sin efecto:** `FPArms` tiene el parámetro `Jump`, pero ninguna transición lo usa. `PlayerAnimator` lo dispara sin efecto visible.
- **Dedos:** `AttributeName` convierte `Left Index 1 Stretched` en `LeftHand.Index.1 Stretched`, la ruta que espera el Animator para los dedos.
- **Poses calibradas a ojo:** los valores `FpRest`, `FpCarry`, `FpStroke`, `FpReach`, `FpWindUp` y `FpRelease` salieron de medir dónde cae la mano en el viewport. Son provisorios.
- **`OpenArms` es aditivo (S158):** suma `PlayerArmOpen` (0.38) al `Arm Down-Up` que deja `Stand` (-0.8), así que los brazos del cuerpo quedan cerca de -0.42. Cambiar `Stand` mueve la apertura.
- **Orden:** correr antes de `Build Bodies`, porque `HumanBodyAssembler` carga los controllers por path (incluido `PlayerBody.controller`).

## Invariantes

- Solo edición; no se usa en runtime.
- Re-correr es idempotente: reescribe clips y reconstruye controllers, sin acumular estados.

## Cambios S158

- Clips `Player_Idle` y `Player_Walk` nuevos: cuerpo visible del jugador con brazos abiertos (`PlayerArmOpen`).
- Controller `PlayerBody` nuevo. `BuildLocomotion` se extrae como helper compartido por `HumanNpc` y `PlayerBody`.
- `FP_Idle` y `FP_Walk` se apoyan en `FpLowered` (reposo = `Stand`).
- El log final cuenta 11 clips y los controllers HumanNpc / FPArms / PlayerBody.
