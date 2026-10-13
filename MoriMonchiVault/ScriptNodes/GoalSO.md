---
tags: [script, scriptable-object, data, progress, goals]
---

# GoalSO.cs

**Ruta:** `Data/Progress/GoalSO.cs`

**Responsabilidad:** Define una meta de progreso de la tienda (dato puro). Contiene el tipo de métrica que mide (`GoalKind`), el objetivo numérico, la recompensa en Dabloons y qué desbloquea al cumplirse (expansiones e ítems). No evalúa nada: la evaluación la hace [[GoalService]].

## Enum `GoalKind`

| Valor | Métrica que mide `GoalService` |
|-------|--------------------------------|
| `CreaturesSold` | Contador `sold` (ventas de clientes) |
| `CreaturesBred` | `WorldStateSO.BredTotal` |
| `Descents` | Contador `descents` (bajadas a la arena) |
| `OrdersCompleted` | Contador `orders` (encargos completados) |
| `DabloonsEarned` | Contador `earned` (Dabloons ganados por ventas) |
| `ExpansionOpened` | Nivel de la expansión `ExpansionId` |

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `Id` | `string` | — | Identificador; se guarda en `WorldStateSO.CompletedGoals` |
| `TitleKey` | `string` | — | Clave de `Loc` del título de la meta |
| `Kind` | `GoalKind` | — | Métrica a medir |
| `ExpansionId` | `string` | — | Solo visible si `Kind == ExpansionOpened` (`[ShowIf]`) |
| `Target` | `int` | 1 | Valor a alcanzar |
| `RewardDabloons` | `int` | 0 | Recompensa al completarla |
| `UnlocksExpansions` | `List<ShopUpgradeSO>` | vacía | Expansiones que quedan desbloqueadas (y listadas como bloqueadas antes) |
| `UnlocksItems` | `List<ItemDefinitionSO>` | vacía | Ítems que quedan desbloqueados |

## Base

`SerializedScriptableObject` (Odin). Menú: `RunRunSimulator/Progress/Goal`.

## Conexiones

- [[GoalService]] — lista de metas, progreso e invariante de completado
- [[StoreRows]] — muestra metas (pestaña Goals) y oculta/bloquea expansiones e ítems según `UnlocksExpansions` y `UnlocksItems`
- [[StoreManager]] — rechaza compras de ítems o expansiones bloqueados por una meta (`BuyResult.Locked`)
- [[InfoOverlayUITK]] — toast al completar (`GameEvents.OnGoalCompleted`)
- [[WorldStateSO]] — persiste `Id` completados y contadores
