---
tags: [script, visual, component]
---

# MonchiFaceTransition.cs

**Ruta:** `World/Creatures/MonchiFaceTransition.cs`

**Responsabilidad:** Coordinador de feedback visual para transiciones faciales. Mantiene dos `MMF_Player` (blink y pop) y sus `ShaderController` asociados. `Bind(Renderer)` vincula los controllers al renderer de cara. `Play(bool pop)` detiene una secuencia y reproduce la otra, permitiendo animaciones sincronizadas con el cambio de textura de cara (shader `MoriMonchi/MonchiFace` anima la transición de _MainTex a _PrevTex sobre _FaceT).

## Campos Públicos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `onBlink` | `MMF_Player` | Secuencia de feedback para blink (transición suave) |
| `onPop` | `MMF_Player` | Secuencia de feedback para pop (transición abrupta/cómica) |
| `blinkController` | `ShaderController` | Controller de shader para blink (Feel) |
| `popController` | `ShaderController` | Controller de shader para pop (Feel) |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Bind(Renderer face)` | Vincula ambos controllers al renderer de cara, llama `Initialization()` en cada uno |
| `Play(bool pop)` | Reproduce feedback: si `pop==true`, detiene onBlink y reproduce onPop; sino, detiene onPop y reproduce onBlink |

## Método OnDisable()

Detiene ambas secuencias de feedback al destruir/desactivar el componente (limpieza de estado).

## Flujo de Uso (S139)

1. **Bind en Assemble():** MonchiVisualizer.Assemble() llama `faceTransition.Bind(faceRenderer)` después de asignar `faceRenderer.sharedMaterial = bank.FaceMaterial`
2. **Play en SetMood():** Cuando SetMood() detecta cambio de textura (`prev != tex`), llama `faceTransition.Play(pop)` si la transición está activa (`faceTransition.isActiveAndEnabled`)
3. **Feedback sincronizado:** Mientras MMF_Player reproduce, ShaderController escribe en el material (MPB) propiedades que el shader anima (ej: _FaceT 0→1)

## Invariantes

- Ambos controllers deben estar asignados para que Bind() funcione (usa null-check)
- Solo una secuencia juega a la vez (Play detiene la otra primero)
- OnDisable para limpieza garantiza que feedback no siga reproduciéndose si componente es destruido

## Notas S139

- Reemplaza swapeo de material directo con animación shader-driven
- ShaderController (de MoreMountains.Feedbacks) escribe en material target cada frame durante feedback
- Usado por MonchiVisualizer.SetMood() para sincronizar animación facial con cambio de textura de ánimo
- Quirk: ShaderController escribe por Material, no por MPB — la cadena es: banco entrega Material único → SetMood() escribe MPB global → ShaderController escribe el material específico durante feedback

## Vinculado a

- [[Index/10 - Visualization]]

## Conexiones

- [[MonchiVisualizer]] (llamador de Bind() y Play())
- [[MonchiVisualBankSO]] (FaceMaterial)
- MoreMountains.Feedbacks (MMF_Player, ShaderController)
