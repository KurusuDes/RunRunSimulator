---
tags: [script, world, props, toys, mess]
---

# MessEmitter.cs

**Ruta:** `World/Props/MessEmitter.cs`

**Responsabilidad:** Deja manchas en el suelo cuando un juguete se mueve. Sigue el desplazamiento planar del `Toy` y, cada `spacing` metros de recorrido (con probabilidad `chance`), coloca un `stainPrefab` sobre el suelo bajo el juguete. No deja manchas si el juguete está en manos del jugador. Si está libre, solo deja manchas cuando se mueve más rápido que `minSpeed`; si lo lleva un monchi, cuenta siempre. Respeta un máximo de manchas y una distancia mínima a charcos existentes (`Puddle.All`).

## Campos serializados

`toy` (Toy, Required), `stainPrefab` (GameObject, AssetsOnly, Required), `spacing` 3, `chance` 0.35, `minGap` 1, `maxStains` 12, `minSpeed` 0.5, `groundMask`.

## Reglas

- Raycast hacia abajo de 3 m desde el juguete; si no hay suelo, no spawnea.
- Descarta si hay un `Puddle` a menos de `minGap`.
- Las manchas se acumulan en `stains` y se recortan al `maxStains`.

## Conexiones

- [[Toy]] — fuente de movimiento y estado (`IsHeldByPlayer`, `Holder`)
- [[Puddle]] — `Puddle.All` para la distancia mínima
