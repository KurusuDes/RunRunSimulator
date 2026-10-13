---
tags: [script, world, props, toys, bubbles]
---

# BubbleMachine.cs

**Ruta:** `World/Props/BubbleMachine.cs`

**Responsabilidad:** Prop emisor de burbujas. Cada `interval` segundos instancia un `Bubble` desde el boquilla (`nozzle`) con un cono de dirección aleatorio (`coneAngle`), siempre que haya menos de `maxAlive` vivas. No emite mientras el prop está en manos del jugador (`WorldPropInstance.IsHeld`).

## Campos serializados

`bubblePrefab`, `nozzle`, `onEmit` (MMF_Player), `interval` 1.2, `maxAlive` 8, `coneAngle` 35°.

## Conexiones

- [[Bubble]] — prefab instanciado e inicializado
- [[WorldPropInstance]] — `IsHeld`
- [[MMF_Player]] — feedback de emisión
