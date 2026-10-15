---
tags: [script, world, npc]
---

# NpcBody.cs

**Ruta:** `World/Npc/NpcBody.cs`

**Responsabilidad:** Representación visual de un cliente NPC. En `Start` instancia un cuerpo y una piel al azar desde `HumanBodyCatalogSO`, arranca la animación en un tiempo aleatorio y, cada frame, traduce la velocidad del `NavMeshAgent` a `Speed` y el estado de `NpcAgent` a `Talking`. No tiene lógica de juego.

**Vinculado a:** [[Index/06 - Player & World]], [[NpcAgent]]

**Conexiones:** [[HumanBodyCatalogSO]] (fuente de cuerpos y pieles), [[NpcAgent]] (estado de negociación), [[HumanoidClipBaker]] (controller `HumanNpc`), [[HumanBodyAssembler]] (genera los prefabs de cuerpos)

## Campos

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `catalog` | `HumanBodyCatalogSO` | (inspector) | Catálogo de cuerpos y pieles |
| `bodyAnchor` | `Transform` | transform propio | Padre del cuerpo instanciado |
| `speedDamp` | float | 0.1 | Suavizado del parámetro `Speed` |

## Ciclo de vida

- **`Awake`**: cachea `NavMeshAgent` y `NpcAgent` del mismo GameObject.
- **`Start`**: `catalog.TryPick`; instancia el cuerpo bajo el anchor con posición y rotación cero; reemplaza todos los slots de los `SkinnedMeshRenderer` por la piel elegida; cachea el `Animator` hijo; pone `applyRootMotion = false` y `cullingMode = CullUpdateTransforms`; arranca el estado actual en un `normalizedTime` aleatorio.
- **`Update`**: `Speed` = velocidad planar (XZ) del agente con `speedDamp`. `Talking` = `NpcAgent.State` es `Negotiating` o `WaitingAtRegister`.

## Animator

Parámetros usados: `Speed` (float) y `Talking` (bool), los mismos que el controller `HumanNpc` (ver [[HumanoidClipBaker]]).

## Quirks ⚠️

- **Dependencias:** `Update` no tiene null-check para `NavMeshAgent` ni para `NpcAgent`. Ambos deben estar en el mismo GameObject que este script.
- **Sin animación:** si el catálogo no tiene cuerpos, o el cuerpo no tiene Animator o controller, `animator` queda null y el NPC se queda estático, sin error (solo el warning de `TryPick`).
- **Un cuerpo por NPC:** cada cliente instancia su propio cuerpo en `Start`. Cada uno recibe una piel única, porque se reemplazan los slots de material por la misma piel dentro del cuerpo.
