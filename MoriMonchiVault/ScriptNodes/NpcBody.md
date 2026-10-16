---
tags: [script, world, npc]
---

# NpcBody.cs

**Ruta:** `World/Npc/NpcBody.cs`

**Responsabilidad:** Representación visual de un cliente NPC. En `Start` pide a `HumanBodyCatalogSO` un cuerpo y una piel según el arquetipo del `NpcAgent`, instancia el cuerpo, arranca la animación en un tiempo aleatorio y, cada frame, envía al Animator la velocidad, el estado de negociación y los disparadores de pago o enojo. No tiene lógica de juego.

**Vinculado a:** [[Index/06 - Player & World]], [[Index/04 - Customer System]], [[NpcAgent]]

**Conexiones:** [[HumanBodyCatalogSO]] (fuente de cuerpos y pieles, filtrada por arquetipo), [[NpcAgent]] (estado, motivo de salida y arquetipo), [[HumanNpcAnimatorBuilder]] (construye el controller `HumanNpcSK`), [[HumanBodyAssembler]] (genera los prefabs de cuerpos)

## Campos

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `catalog` | `HumanBodyCatalogSO` | (inspector) | Catálogo de cuerpos y pieles |
| `bodyAnchor` | `Transform` | transform propio | Padre del cuerpo instanciado |
| `speedDamp` | float | 0.1 | Suavizado del parámetro `Speed` |

## Ciclo de vida

- **`Awake`**: cachea `NavMeshAgent` y `NpcAgent` del mismo GameObject.
- **`Start`**: `catalog.TryPick(npc.Archetype, ...)`; instancia el cuerpo bajo el anchor con posición y rotación cero; reemplaza todos los slots de los `SkinnedMeshRenderer` por la piel elegida; cachea el `Animator` hijo; pone `applyRootMotion = false` y `cullingMode = CullUpdateTransforms`; arranca el estado actual en un `normalizedTime` aleatorio.
- **`Update`**: 
  - `Speed` = velocidad planar (XZ) del agente con `speedDamp`.
  - `State` (int) según `NpcAgent.State`: `InspectingDisplay` = 1 (Browse); `Queueing` = 2 (Queue) si la velocidad planar es < 0.15, si no 0 (locomoción); `WaitingAtRegister` y `Negotiating` = 3 (Talk); el resto = 0. Solo se envía al cambiar.
  - Al entrar a `Leaving` dispara el trigger `Pay` si `LeaveReason` es `Purchased`, o `Upset` en cualquier otro caso.

## Animator

Parámetros usados (los mismos que `HumanNpcSK`, ver [[HumanNpcAnimatorBuilder]]):

| Parámetro | Tipo | Uso |
|-----------|------|-----|
| `Speed` | float | Blend de locomoción (idle, walk, run) |
| `State` | int | 0 locomoción, 1 Browse, 2 Queue, 3 Talk |
| `Pay` | trigger | Estado Pay → Happy al salir comprado |
| `Upset` | trigger | Estado Upset al salir sin comprar |

**S163:** el parámetro `Talking` (bool) fue reemplazado por `State` (int). El controller `HumanNpc` de [[HumanoidClipBaker]] ya no lo usa.

## Quirks ⚠️

- **Dependencias:** `Update` no tiene null-check para `NavMeshAgent` ni para `NpcAgent`. Ambos deben estar en el mismo GameObject que este script.
- **Sin animación:** si el catálogo no tiene cuerpos, o el cuerpo no tiene Animator o controller, `animator` queda null y el NPC se queda estático, sin error (solo el warning de `TryPick`).
- **Un cuerpo por NPC:** cada cliente instancia su propio cuerpo en `Start`. Cada uno recibe una piel única, porque se reemplazan los slots de material por la misma piel dentro del cuerpo.
- **Disparadores sin estado:** `Pay` y `Upset` son triggers: si el NPC sale antes de que el Animator los consuma, no se reproducen más tarde.
