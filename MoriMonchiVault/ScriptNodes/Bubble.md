---
tags: [script, world, props, toys, bubbles]
---

# Bubble.cs

**Ruta:** `World/Props/Bubble.cs`

**Responsabilidad:** Burbuja flotante que deriva en una dirección, sube y baja con un bamboleo sutil dentro de una franja de altura, y explota por vida agotada o por un monchi que la revienta. Al explotar reproduce feedback (`MMF_Player onPop`), oculta el render y se destruye con retardo. Mantiene el registro estático `All` de burbujas vivas.

## Campos serializados

`onPop` (MMF_Player), `driftSpeed` 0.6, `lifeMin` 6, `lifeMax` 9, `heightMin` 0.5, `heightMax` 1.8, `bobAmplitude` 0.2, `bobFrequency` 1.1, `riseSpeed` 0.5, `destroyDelay` 0.5.

## API pública

| Miembro | Descripción |
|---------|-------------|
| `All` (static) | Lista de burbujas activas (add en OnEnable, remove en OnDisable) |
| `Popped` | Si ya explotó |
| `Initialize(direction, floorHeight)` | Fija dirección plana, piso, vida y altura inicial |
| `Claim(agent)` | Registra a un monchi que la persigue (no duplica) |
| `Pop(by)` | Explota; devuelve los otros monchis que la reclamaban (excluye `by`) |

## Invariantes

- Si `Initialize` no se llamó, lo hace en el primer `Update` con dirección aleatoria.
- La vida agotada llama `Pop(null)`, sin autor.

## Conexiones

- [[BubbleMachine]] — la instancia y la inicializa
- [[ToyBuddyPlay]] — la persigue y la revienta (`Claim`, `Pop`, `Bubble.All`)
- [[MoriMochiAgent]] — cliente que la reclama
- [[MMF_Player]] — feedback de explosión (regla VFX: juice solo por MMFeedbacks)
