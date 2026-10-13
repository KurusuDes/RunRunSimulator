---
tags: [script, core, singleton]
---

# GameManager

**Ruta:** `Core/GameManager.cs`

**Responsabilidad:** Ciclo de vida del juego. Singleton que centraliza acceso a databases y registries. **Único orquestador de persistencia local:** escucha `GameEvents.OnRegistryChanged`, `OnInventoryChanged`, `OnWorldStateChanged` e invoca `SaveSystem` a disco. S128: Push agrupado a nube con `pushDelaySeconds` (default 5); se cancela y sube ya en quit/pause; `Time.unscaledTime` para que pausa no congele timer. S131: Agregado `WorldStateSO` y `PersistWorldState()` para sincronización de estado de mundo. S149: se retiran los muebles del gestor (`FurnitureRegistry`, `PersistFurniture`, `GrantPlacedFurniture`, suscripción a `OnFurnitureChanged`). `FlushToCloudAsync` además guarda el grafo social. **S151:** el push tiene piso de frecuencia (`minPushIntervalSeconds` = 30) y se agrega el campo `socialTuning`.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `PushToCloud()` | Dispara `cloudSync.PushAsync()` (fire-and-forget) |
| `FlushToCloudAsync()` | Guarda registry, grafo social y WorldState a disco + espera push cloud |
| `FlushToCloud()` | Versión sin await de `FlushToCloudAsync` |
| `MintRandomCreature()` | Genera random, asigna género/elemento/rol/diales/nombre, registra, **dispara RegistryChanged** |
| `MintCreature()` | Genera random DNA, registra, retorna CreatureDNA — **NO dispara evento** (responsibility del caller) |
| `CollectLooseWorldProps()` | Recoge props sueltos de la escena al inventario (en quit/pause) |

## Propiedades Estáticas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Instance` | `GameManager` | Singleton; null si destroyed |
| `CurrentInventory` | `PlayerInventorySO` | Acceso rápido |

## Getters de Referencias (serializados)

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Registry` | `CreatureRegistrySO` | Registro de criaturas vivas/muertas |
| `Database` | `CreatureDatabaseSO` | Bases de partes (Horns, Backs, Wings, Faces) |
| `Inventory` | `PlayerInventorySO` | Cartera y objetos del jugador |
| `FurTypeDatabase` | `FurTypeDatabaseSO` | Tipos de pelaje |
| `RarityOddsTable` | `RarityOddsTableSO` | Odds de rareza |
| `MonchiVisualBank` | `MonchiVisualBankSO` | Banco de visuals (también lo consulta `PartPool`) |
| `RoleWorldProfiles` | `RoleWorldProfileSO` | Perfiles de rol para arena |
| `WorldState` | `WorldStateSO` | **(S131)** Estado del mundo (día, minuto, tutorial, encargos) |

**Campo sin getter (S151):** `socialTuning` (`SocialTuningSO`, Required, AssetsOnly). Se serializa en el inspector; GameManager no lo expone por propiedad.

## Persistencia S128+ + S131 + S149 + S151

**Push agrupado:**
1. Evento gameplay → `Persist()` / `PersistInventory()` / `PersistWorldState()` (S131)
2. Guarda a disco vía [[SaveSystem]]
3. `RequestPush()` → `pushPending = true`, `pushDeadline = max(Time.unscaledTime + pushDelaySeconds, lastPushTime + minPushIntervalSeconds)` (S151)
4. `Update()` → si `Time.unscaledTime >= pushDeadline` → `PushToCloud()` y guarda `lastPushTime`

**Suscriptores de eventos (OnEnable):**
```csharp
GameEvents.OnRegistryChanged  += Persist;
GameEvents.OnInventoryChanged += PersistInventory;
GameEvents.OnWorldStateChanged += PersistWorldState;  // S131
```

**PersistWorldState (S131):**
```csharp
private void PersistWorldState(WorldStateSO state)
{
    SaveSystem.SaveWorldState(state);
    RequestPush();
}
```

**Flush forzado:**
- `OnApplicationQuit()` y `OnApplicationPause(paused: true)` → `CollectLooseWorldProps()` y `FlushToCloud()` (guarda a disco + espera push)
- Expedición retorno: [[ExpeditionBridge]] aplica `RegistryChanged` → GameManager persiste
- CreatureLifecycle.Kill/Adopt → RegistryChanged → persist

**Variación S128 vs S93:** Timer usa `Time.unscaledTime` (no `Time.time`), así pausa no bloquea el push.

## Ciclo de Vida

1. `Awake()` → `Instance = this`
2. `OnEnable()` → Suscribe a 3 eventos (Registry/Inventory/WorldState)
3. Gameplay → eventos → `Persist()` (SaveSystem + RequestPush)
4. `Update()` → si deadline vencido → push async
5. Quit/Pause → `FlushToCloudAsync()`
6. `OnDestroy()` → Limpia `Instance` si es el mismo

## Cambios S151

**Agregado:** `socialTuning` (campo serializado, Required). `minPushIntervalSeconds` (default 30): entre dos pushes pasa como mínimo ese intervalo aunque haya mutaciones seguidas.

## Cambios S149

**Retirado:** `furnitureRegistry` (campo y getter), `PersistFurniture`, `GrantPlacedFurniture` (escuchaba `OnInventoryReloaded`), suscripción a `OnFurnitureChanged`.

**Agregado:** `SaveSystem.SaveSocialGraph()` en `FlushToCloudAsync`.

## Cambios S131

**Agregado:**
- `worldState` field (serializado, AssetsOnly, required)
- `WorldState` getter property
- `PersistWorldState(WorldStateSO state)` método privado
- Suscripción a `GameEvents.OnWorldStateChanged`
- `SaveSystem.SaveWorldState(worldState)` en FlushToCloudAsync

**Propósito:** Sincronizar estado de mundo (día/minuto) con persistencia y cloud. Ahora Day/MinuteOfDay mutados por GameClock disparan `WorldStateChanged` → autoguardado sin gameplay code adicional.

## Invariantes S128+ / S131 / S149 / S151

- Singleton: Awake crea, OnDestroy limpia si es el mismo
- No disparador de eventos: solo consumidor de persistencia
- Acceso centralizado: todas las referencias por getter, no SerializeField directo
- Persistencia order: Disco (SaveSystem) → Nube (PushAsync) — nunca inversión
- Push agrupado: múltiples mutaciones → un solo push en 5 s, y nunca más de un push cada 30 s
- Sin escala de tiempo: push no se congela con pausa
- WorldState integrado: estado de mundo unificado y persistido automáticamente

## Vinculado a

- [[Index/07 - Persistence & Identity]]
- [[Index/28 - Cimientos y camino a Game Ready]]
- [[Index/09 - Active Context]]

## Conexiones

**Data:**
- [[CreatureRegistrySO]], [[CreatureDatabaseSO]], [[PlayerInventorySO]], [[WorldStateSO]], [[SocialTuningSO]]

**Sistemas:**
- [[CloudSyncService]] — push async
- [[GameClock]] — dispara WorldStateChanged
- [[CreatureGenerator]] — mint
- [[GameEvents]] — bus de eventos
- [[SaveSystem]] — persistencia a disco
- [[CreatureLifecycle]] — vía RegistryChanged
- [[DeliveryBox]] — vía RegistryChanged
- [[OrderBoardService]] — lee `WorldState` y `Database` (S151)

## Notas (S131 HC-4)

- **WorldState ownership:** GameManager es propietario; GameClock muta, eventos disparan, GameManager persiste.
- **Bootstrap:** SaveSystem.LoadWorldState() debe llamarse durante init de escena antes de que GameClock load.
- **FlushToCloudAsync:** Ahora también guarda world state (línea `SaveSystem.SaveWorldState(worldState)`).
