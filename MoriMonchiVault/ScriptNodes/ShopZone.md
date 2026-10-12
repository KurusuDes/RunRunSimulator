---
tags: [world, store, expansion, zone, unlock]
---

# ShopZone.cs

**Ruta:** `World/Store/ShopZone.cs`

**Responsabilidad:** Zona de la tienda que se abre al alcanzar un nivel de `ShopUpgradeSO` (expansion). Muestra `openContent` y oculta `lockedContent` y `hideWhenOpen`. Al pasar de cerrada a abierta, en juego (no en carga), reproduce el feedback y dispara `GameEvents.ShopZoneOpened`, que dispara el rehorneado en `NavMeshRebaker`.

## Regla

`open = world.UpgradeLevel(expansion.Id) >= requiredLevel`. Las cargas (`OnWorldStateReloaded`, `Start`) aplican en silencio: no hay feedback ni evento.

## Referencias Serializadas

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `expansion` | `ShopUpgradeSO` | Si | Mejora que controla la zona |
| `requiredLevel` | `int` (Min 1) | No | Nivel minimo para abrir |
| `openContent` | `GameObject` | Si | Geometria visible al abrir |
| `lockedContent` | `GameObject` | No | Visible mientras esta cerrada |
| `hideWhenOpen` | `List<GameObject>` | No | Se oculta al abrir (muros, etc.) |
| `openFeedback` | `MMF_Player` | No | Feedback de apertura |

## Eventos

| Evento | Accion |
|--------|--------|
| `OnWorldStateReloaded` | `Apply(world, silent: true)` |
| `OnWorldStateChanged` | `Apply(world, silent: false)` |

**Conexiones:** [[ShopUpgradeSO]], [[WorldStateSO]], [[StoreManager]] (`BuyUpgrade` sube el nivel), [[NavMeshRebaker]] (escucha `ShopZoneOpened`), [[GameEvents]], [[GameManager]]
