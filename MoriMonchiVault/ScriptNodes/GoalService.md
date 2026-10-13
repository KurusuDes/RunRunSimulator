---
tags: [script, system, progress, goals, singleton]
---

# GoalService.cs

**Ruta:** `Systems/Progress/GoalService.cs`

**Responsabilidad:** Evalúa las metas de tienda (`GoalSO`) y las marca como completadas. Mantiene los contadores de progreso en `WorldStateSO` (ventas, bajadas, encargos, Dabloons ganados) y, al cumplirse una meta, paga la recompensa, la marca como hecha y dispara `GameEvents.GoalCompleted`. Responde también a "¿está bloqueado este ítem o expansión?" para la tienda.

## Singleton

- `GoalService.Instance` asignado en `Awake`, limpiado en `OnDestroy`.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `goals` | `List<GoalSO>` | vacía | Metas del juego |
| `cloudSync` | `CloudSyncService` (Required) | — | Espera a `StartupSyncDone` |
| `syncTimeoutSeconds` | `float` | 20 | Timeout de la espera (tiempo unscaled) |

## Contadores (claves en `WorldStateSO`)

| Clave | Incremento |
|-------|-----------|
| `sold` | +1 por `OnCustomerSold` |
| `earned` | +precio de venta por `OnCustomerSold` |
| `descents` | +1 por `OnExpeditionReturned` |
| `orders` | +1 por `OnOrderCompleted` |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Goals` | `IReadOnlyList<GoalSO>` | Lista de metas (para `StoreRows`) |
| `Progress(GoalSO g)` | `int` | Progreso clamp a `[0, Target]`; `Target` si ya está completada |
| `IsDone(GoalSO g)` | `bool` | Si `WorldStateSO.IsGoalDone(g.Id)` |
| `LockingGoal(ShopUpgradeSO u)` | `GoalSO` | Meta no completada que bloquea la expansión, o `null` |
| `LockingGoal(ItemDefinitionSO item)` | `GoalSO` | Meta no completada que bloquea el ítem, o `null` |

## Ciclo

1. `Start()` espera `cloudSync.StartupSyncDone` (con timeout), marca `ready` y evalúa (`Apply(false)`).
2. Eventos de gameplay suman contadores y llaman `Apply(true)`.
3. `Apply`: para cada meta no completada con `Progress >= Target` → `MarkGoalDone`, `Wallet.Add(Dabloons, RewardDabloons, "goal")`, `GameEvents.GoalCompleted(g)`. Si algo cambió, `GameEvents.WorldStateChanged(world)` (persistencia por evento).

## Suscripciones (OnEnable / OnDisable)

| Evento | Efecto |
|--------|--------|
| `OnCustomerSold` | Suma `sold` y `earned`; `Apply(true)` |
| `OnExpeditionReturned` | Suma `descents`; `Apply(true)` |
| `OnOrderCompleted` | Suma `orders`; `Apply(true)` |
| `OnBreedingCompleted` | `Apply(false)` |
| `OnShopZoneOpened` | `Apply(false)` (expansiones) |
| `OnWorldStateReloaded` | `Apply(false)` tras pull de nube |

## Invariantes

- No evalúa antes de `ready` (sincronización inicial de nube terminada o timeout).
- Una meta se completa una sola vez (`IsGoalDone` previo a todo).
- Persistencia solo por `GameEvents.WorldStateChanged`; no llama a `SaveSystem` ni a la nube.

## Conexiones

- [[GoalSO]] — definición de cada meta
- [[WorldStateSO]] — contadores (`Counter`, `AddCounter`), metas completadas (`IsGoalDone`, `MarkGoalDone`), `BredTotal`, `UpgradeLevel`
- [[StoreManager]] — consulta `LockingGoal` antes de vender (`BuyResult.Locked`)
- [[StoreRows]] — consulta `Goals`, `Progress`, `IsDone` y `LockingGoal`
- [[CloudSyncService]] — `StartupSyncDone`
- [[GameEvents]] — suscribe 6 eventos; dispara `GoalCompleted` y `WorldStateChanged`
- [[Wallet]] — pago de la recompensa
