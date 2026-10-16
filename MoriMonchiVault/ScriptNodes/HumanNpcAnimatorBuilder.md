---
tags: [script, editor, humanos, animacion]
---

# HumanNpcAnimatorBuilder.cs

**Ruta:** `Editor/HumanNpcAnimatorBuilder.cs`

**Responsabilidad:** Herramienta de editor (menú `RunRunSimulator/Humans/Build NPC Animator`) que genera el controller `HumanNpcSK` para los clientes NPC y su override femenino `HumanNpcSK_Femn`. Arma la máquina de estados con locomoción, estados de negociación y reacciones de pago y enojo. No corre en runtime.

**Vinculado a:** [[Index/06 - Player & World]], [[Index/04 - Customer System]]

**Conexiones:** [[HumanBodyAssembler]] (los prefabs de cuerpos NPC usan este controller, así que debe correr antes), [[NpcBody]] (envía los parámetros `Speed`, `State`, `Pay` y `Upset`), [[HumanoidClipBaker]] (controller `PlayerBody`, no comparte nada con este)

## Qué genera

| Salida | Ruta | Detalle |
|--------|------|---------|
| Controller | `Resources/Animations/Humans/HumanNpcSK.controller` | Parámetros, blend tree y estados (ver abajo). Se reconstruye desde cero. |
| Override femenino | `Resources/Animations/Humans/HumanNpcSK_Femn.overrideController` | Reemplaza cada clip `_Masc` por su par `_Femn` cuando existe. |

## Clips

Se buscan por nombre en `Synty/AnimationBaseLocomotion`, `Synty/AnimationIdles`, `Synty/AnimationEmotesAndTaunts` y `Resources/Animations/Humans/Sidekick`. Los nombres están fijos en `MascNames`:

| Índice | Clip masculino | Uso | Loop |
|--------|----------------|-----|------|
| 0 | `A_MOD_IDL_Idle_Base_Masc` | Locomoción, Speed 0 | sí |
| 1 | `A_MOD_BL_Walk_F_Masc` | Locomoción, Speed 1.4 | sí |
| 2 | `A_MOD_BL_Run_F_Masc` | Locomoción, Speed 3.6 | sí |
| 3 | `A_MOD_IDL_Thoughtful_L_Loop_Masc` | State 1 (Browse) | sí |
| 4 | `A_MOD_IDL_ArmsFolded_Casual_Loop_Masc` | State 2 (Queue) | sí |
| 5 | `A_MOD_IDL_HandsOnHips_Base_Loop_Masc` | State 3 (Talk) | sí |
| 6 | `A_MM_Pay_Masc` | Trigger Pay | no |
| 7 | `A_MOD_EMOT_Happy_ThumbsUp_Masc` | Después de Pay | no |
| 8 | `A_MOD_EMOT_Reproach_WaveAway_Masc` | Trigger Upset | no |

Los clips `_Femn` usan el mismo nombre con `_Femn` en lugar de `_Masc`.

## Estructura del controller

- **Parámetros:** `Speed` (float), `State` (int), `Pay` y `Upset` (triggers).
- **Estado por defecto:** blend tree `Locomotion` sobre `Speed` con umbrales 0, 1.4 y 3.6.
- **Estados Browse, Queue y Talk:** entran desde locomoción cuando `State` iguala su valor y vuelven cuando deja de igualarlo (transición de 0.25 s, sin exit time).
- **Pay → Happy:** transición con exit time 0.9 (duración 0.15 s). **Happy** y **Upset** vuelven a locomoción con exit time 0.92 (duración 0.25 s).
- **Any State:** `Pay` y `Upset` transicionan desde cualquier estado (duración 0.15 s, sin autotransición).

## Flujo

1. Indexa todos los clips de las carpetas buscadas (ignora `__preview__`).
2. Resuelve los 9 clips masculinos. Si falta alguno, aborta con error y no toca el controller.
3. Resuelve los clips femeninos. Si falta un par, el override deja el masculino y loguea warning.
4. `BuildController`: reinicia el controller (`FreshController`), agrega parámetros, estados y transiciones.
5. `BuildOverride`: crea o reutiliza `HumanNpcSK_Femn` y lo mapea a los pares femeninos.

## Quirks ⚠️

- **Orden:** los prefabs de cuerpos NPC necesitan este controller. Correr antes de `Build Bodies`.
- **Loop forzado:** si un clip de los primeros 6 no está marcado como loop, `Resolve` cambia su `loopTime` en el importer del FBX y lo reimporta. Esto modifica el archivo fuente del pack, no solo el controller.
- **Reconstrucción destructiva:** `FreshController` borra estados, transiciones, parámetros y blend trees existentes del controller. Cualquier edición manual en el Animator Controller se pierde al re-correr.
- **Faltantes femeninos sin bloqueo:** el override puede quedar parcial (pares sin femenino usan el masculino). Revisar el log `faltan Femn`.
- El override se crea con `AnimatorOverrideController`; si ya existe, reemplaza sus overrides en vez de recrearlo.
