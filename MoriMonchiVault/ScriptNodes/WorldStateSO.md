---
tags: [script, scriptable-object, world-state, data]
---

# WorldStateSO.cs

**Ruta:** `Data/World/WorldStateSO.cs`

**Responsabilidad:** ScriptableObject runtime: estado del mundo (día, minuto, tutorial, mejoras, stock de tienda, restock, criaturas criadas, decoraciones colocadas por slot, niveles de estaciones de necesidades, encargos de tienda, contadores y metas completadas). **S138:** añade diccionario de niveles de mejoras. **S149:** añade `shopStock`, `lastRestockDay`, `bredTotal`, `decorSlots` y `stationLevels`. **S151:** añade `orders` (encargos del día) y `ordersDay`. **S152:** añade `counters` (contadores de progreso) y `completedGoals` (ids de metas cumplidas). Métodos: GetData(), LoadFrom(). La persistencia la dispara [[GameManager]] al recibir `GameEvents.OnWorldStateChanged`; el SO no se suscribe a eventos.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `day` | int | Día actual (default 1) |
| `minuteOfDay` | float | Minuto del día (default 360 = 6 AM) |
| `tutorialStep` | int | Paso tutorial (default 0; 1-based, ver [[TutorialDirector]]) |
| `upgradeLevels` | Dictionary<string, int> | **(S138)** Nivel de cada mejora por ID |
| `shopStock` | Dictionary<string, int> | **(S149)** Stock de la tienda por ID de listing |
| `lastRestockDay` | int | **(S149)** Último día en que se reabasteció la tienda |
| `bredTotal` | int | **(S149)** Crías totales. Revela decoraciones (`BreedingDecorSO.IsDiscovered`) |
| `decorSlots` | Dictionary<string, string> | **(S149)** Decoración colocada por `SlotId` de `DecorSlot` |
| `stationLevels` | Dictionary<string, float> | **(S149)** Nivel de cada `StationSupply` por nombre de GameObject |
| `orders` | List<ShopOrder> | **(S151)** Encargos vigentes del día |
| `ordersDay` | int | **(S151)** Día para el que se tiraron los encargos (evita re-tirar) |
| `counters` | Dictionary<string, int> | **(S152)** Contadores de progreso de metas (`sold`, `earned`, `descents`, `orders`) |
| `completedGoals` | List<string> | **(S152)** Ids de `GoalSO` ya cumplidas (cada una se paga una vez) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Day` | int | Getter/setter |
| `MinuteOfDay` | float | Getter/setter |
| `TutorialStep` | int | Getter/setter |
| `LastRestockDay` | int | **(S149)** Getter/setter |
| `BredTotal` | int | **(S149)** Getter/setter |
| `ShopStock` | `IReadOnlyDictionary<string, int>` | **(S149)** Lectura |
| `DecorSlots` | `IReadOnlyDictionary<string, string>` | **(S149)** Lectura |
| `Orders` | `List<ShopOrder>` | **(S151)** Getter/setter (null → lista vacía) |
| `OrdersDay` | int | **(S151)** Getter/setter |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `UpgradeLevel(string id)` | `int` | **(S138)** Lee nivel de mejora (default 0 si no existe) |
| `SetUpgradeLevel(string id, int level)` | `void` | **(S138)** Escribe nivel de mejora |
| `SetShopStock(Dictionary<string, int> stock)` | `void` | **(S149)** Copia el stock (null → vacío) |
| `GetDecorSlot(string slotId)` | `string` | **(S149)** Decoración del slot, null si vacío |
| `SetDecorSlot(string slotId, string decorId)` | `void` | **(S149)** Escribe el slot; decorId vacío lo borra |
| `TryGetStationLevel(string id, out float level)` | `bool` | **(S149)** Lee nivel de estación |
| `SetStationLevel(string id, float level)` | `void` | **(S149)** Escribe nivel de estación |
| `Counter(string key)` | `int` | **(S152)** Lee contador (0 si no existe) |
| `AddCounter(string key, int amount)` | `void` | **(S152)** Suma al contador |
| `IsGoalDone(string id)` | `bool` | **(S152)** Si la meta ya está cumplida |
| `MarkGoalDone(string id)` | `void` | **(S152)** Marca la meta como cumplida (idempotente) |
| `GetData()` | `WorldStateData` | Serializa a struct para persistencia (incluye `Orders`, `OrdersDay`, `Counters`, `CompletedGoals`) |
| `LoadFrom(WorldStateData data)` | `void` | Carga desde struct; null-safe (defaults) |

## WorldStateData (Serializable)

```csharp
[Serializable]
public class WorldStateData
{
    public int   Day          = 1;
    public float MinuteOfDay  = 360f;
    public int   TutorialStep = 0;
    public Dictionary<string, int> UpgradeLevels = new Dictionary<string, int>();
    public Dictionary<string, int> ShopStock = new Dictionary<string, int>();   // S149
    public int LastRestockDay = 0;                                              // S149
    public int BredTotal = 0;                                                   // S149
    public Dictionary<string, string> DecorSlots = new Dictionary<string, string>();   // S149
    public Dictionary<string, float> StationLevels = new Dictionary<string, float>();  // S149
    public List<ShopOrder> Orders = new List<ShopOrder>();                      // S151
    public int OrdersDay = 0;                                                   // S151
    public Dictionary<string, int> Counters = new Dictionary<string, int>();    // S152
    public List<string> CompletedGoals = new List<string>();                    // S152
}
```

Struct para serialización JSON vía SaveSystem.

## Ciclo de Vida

1. **Init (GameScene):** Inyectado en GameManager. SaveSystem.LoadWorldState() lo carga.
2. **Runtime:** GameClock actualiza MinuteOfDay. Cambios disparan GameEvents.WorldStateChanged().
3. **Persistencia:** GameManager.OnEnable() suscribe PersistWorldState() → SaveSystem.SaveWorldState() + push cloud.
4. **Cloud Reload:** CloudSyncService dispara OnWorldStateReloaded cuando sincroniza.

## Integración S138, S149, S151 y S152

- StoreManager.BuyUpgrade() llama `world.SetUpgradeLevel()` + dispara `GameEvents.WorldStateChanged()`
- ShopZone lee `UpgradeLevel` para abrir o cerrar zonas
- DecorSlot escribe `SetDecorSlot` y StationSupply escribe `SetStationLevel`; ambos disparan `WorldStateChanged`
- OrderBoardService tira `Orders` al cambiar el día (`OrdersDay`) y quita uno al completarlo; ambos disparan `WorldStateChanged`
- **S152:** GoalService suma `Counter` / `AddCounter` y marca `MarkGoalDone`; StoreManager y StoreRows consultan `IsGoalDone` para bloquear compras y filas
- WorldStateSO persiste automáticamente en SaveSystem

## Vinculado a

- [[Index/28 - Currency & Monetization]] (mejoras)
- [[Index/07 - Persistence & Identity]] (persistencia)

**Conexiones:** [[GameManager]], [[GameClock]], [[SaveSystem]], [[CloudSyncService]], [[GameEvents]], [[StoreManager]], [[ShopZone]], [[DecorSlot]], [[StationSupply]], [[BreedingDecorSO]], [[OrderBoardService]] (S151), [[ShopOrder]] (S151), [[GoalService]] (S152), [[GoalSO]] (S152), [[TutorialDirector]] (S152)
