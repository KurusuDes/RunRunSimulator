---
tags: [script, editor, humanos, animacion]
---

# HumanoidClipBaker.cs

**Ruta:** `Editor/HumanoidClipBaker.cs`

**Responsabilidad:** Herramienta de editor (menú `RunRunSimulator/Humans/Bake Clips`) que genera por código los clips humanoides (curvas de músculos genéricos de Unity) y los dos AnimatorController del proyecto: `HumanNpc` (clientes) y `FPArms` (brazos del jugador). Son provisorios hasta tener un pack de animaciones. No corre en runtime.

**Vinculado a:** [[Index/06 - Player & World]]

**Conexiones:** [[HumanBodyAssembler]] (asigna los controllers a los prefabs), [[NpcBody]] (usa `HumanNpc` vía prefab), [[PlayerAnimator]] (escribe los parámetros de `FPArms`)

## Clips generados

Carpeta: `Resources/Animations/Humans/`. Cada clip usa 24 muestras y una curva de `RootT.y` para el bob. La raíz no rota ni se mueve en XZ.

| Clip | Duración | Loop | Uso |
|------|----------|------|-----|
| `Human_Idle` | 3.0 s | sí | Cliente parado (blend con Speed 0) |
| `Human_Walk` | 1.05 s | sí | Cliente caminando (Speed 1.4 y 3.6; el segundo a timeScale 1.9) |
| `Human_Talk` | 2.4 s | sí | Cliente negociando (bool `Talking`) |
| `FP_Idle` | 3.0 s | sí | Brazos FP en reposo |
| `FP_Walk` | 0.7 s | sí | Brazos FP al caminar (Speed 1) |
| `FP_Hold` | 2.5 s | sí | Sostener un MoriMochi (`Holding`) |
| `FP_Pet` | 1.2 s | sí | Acariciar (`Petting`) |
| `FP_Throw` | 0.5 s | no | Lanzar (trigger `Throw`) |
| `FP_Interact` | 0.45 s | no | Interactuar (trigger `Interact`) |

## Controllers

- **`HumanNpc`:** parámetros `Speed` (float) y `Talking` (bool). Blend "Locomotion" (Idle / Walk) y estado `Talk`. Transiciones de 0.25 s.
- **`FPArms`:** parámetros `Speed`, `Holding`, `Petting` (bool) y `Throw`, `Interact`, `Jump` (trigger). Layer 0 con `iKPass`. Blend Idle / Walk. Hold y Pet entran y salen por `Link` con condición bool. Throw e Interact entran por AnyState y vuelven a Locomotion con exit time 0.85.

## Flujo de Bake

1. `Bake(name, length, loop, pose)` crea el `.anim` o reutiliza el existente, hace `ClearCurves` y lo reescribe.
2. Cada función de pose (`IdlePose`, `WalkPose`, `FpWalkPose`, etc.) llama `Stand` o `FpBase` y ajusta músculos. `Fingers(curl, spread)` genera los dedos.
3. Las curvas se suavizan con `SmoothTangents(0)` y se aplican con `SetEditorCurve`.
4. `BuildNpcController` y `BuildFpController` reconstruyen los controllers. `FreshController` borra estados, AnyState y blend trees previos.

## Quirks ⚠️

- **`Jump` sin efecto:** `FPArms` tiene el parámetro `Jump`, pero ninguna transición lo usa. `PlayerAnimator` lo dispara sin efecto visible.
- **Dedos:** `AttributeName` convierte `Left Index 1 Stretched` en `LeftHand.Index.1 Stretched`, la ruta que espera el Animator para los dedos.
- **Poses calibradas a ojo:** los valores `FpRest`, `FpCarry`, `FpStroke`, `FpReach`, `FpWindUp` y `FpRelease` salieron de medir dónde cae la mano en el viewport. Son provisorios.
- **Orden:** correr antes de `Build Bodies`, porque `HumanBodyAssembler` carga los controllers por path.

## Invariantes

- Solo edición; no se usa en runtime.
- Re-correr es idempotente: reescribe clips y reconstruye controllers, sin acumular estados.
