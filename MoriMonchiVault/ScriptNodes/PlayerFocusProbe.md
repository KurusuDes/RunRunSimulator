---
tags: [script, player, focus, probe, hud]
---

# PlayerFocusProbe.cs

**Ruta:** `Player/PlayerFocusProbe.cs`

**Responsabilidad:** Sonda de foco del jugador. Cada `interval` segundos (tiempo unscaled) lanza un raycast desde la cámara y decide qué ofrece el punto de mira: acariciar un MoriMochi, usar/interactuar con un objeto, soltar lo que lleva encima o usar el ítem activo del hotbar. Publica el resultado como `FocusPrompt` y el `IFocusLabel` del objeto apuntado. No dibuja nada: lo pinta `FocusPromptUITK` (S161).

**Vinculado a:** [[Index/06 - Player & World]], [[Index/05 - UI System]]

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `cameraTransform` | `Transform` | — | Cámara desde la que sale el rayo. Sin ella, el foco es `None` |
| `range` | `float` | 2.5 | Alcance del rayo en metros |
| `mask` | `LayerMask` | `~0` | Capas que el rayo puede tocar |
| `interval` | `float` | 0.1 | Segundos entre sondeos |

## Estado Estático Público

| Miembro | Tipo | Descripción |
|---------|------|-------------|
| `Changed` | `static event Action<FocusPrompt>` | Se dispara solo si cambia el valor o la referencia del `IFocusLabel` |
| `Current` | `static FocusPrompt` | Último prompt calculado |
| `CurrentLabel` | `static IFocusLabel` | Rótulo del objeto apuntado (puede ser null) |

## Prioridad de Prompt (`Compute`)

1. Sin cámara, UI con foco (`UIManager.OnUIFocusChanged`) o acariciando → `None`.
2. Sosteniendo algo (`HeldChanged` con transform no nulo) → `Carrying`.
3. Raycast ordenado por distancia, saltando colliders hijos del propio jugador:
   - Primer `IFocusLabel` encontrado se guarda como rótulo.
   - `MoriMochiAgent` → `Creature`.
   - `IInteractable` → `Interactable`.
   - Un collider sólido sin nada de lo anterior corta la búsqueda; un trigger se atraviesa.
4. Si `HotbarController.Instance.HasActiveItem` → `Item`.
5. Si no, `None`.

## Suscripciones (OnEnable / OnDisable)

| Evento | Handler | Efecto |
|--------|---------|--------|
| `PlayerController.HeldChanged` | `OnHeldChanged` | Marca si sostiene algo |
| `PlayerController.PetChanged` | `OnPetChanged` | Marca si está acariciando |
| `UIManager.OnUIFocusChanged` | `OnUIFocusChanged` | Oculta el prompt con UI abierta |

`OnDisable` desuscribe y resetea el prompt a `None` con rótulo `null`.

## Conexiones

- [[PlayerController]] — eventos `HeldChanged` y `PetChanged`
- [[IFocusLabel]] — rótulo del objeto apuntado
- [[IInteractable]], [[MoriMochiAgent]] — clasificación del objetivo
- [[HotbarController]] — `HasActiveItem`
- [[UIManager]] — foco de UI
- [[FocusPromptUITK]] — consumidor (lee `Changed`, `Current` y `CurrentLabel`)
- [[UIEnums]] — enum `FocusPrompt`

## Notas

- Sin `Find*` ni lookups por nombre: la sonda consulta la cámara serializada y los eventos estáticos.
- No persiste ni toca la nube.
