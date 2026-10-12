---
tags: [cloud, authentication, service]
---

# CloudSyncService

**Ruta:** `Systems/Cloud/CloudSyncService.cs`

**Responsabilidad:** Orquestador de nube (autenticación + sincronización). Expone métodos públicos para push/pull/reset. En `Start()` inicializa `CloudAuth` (autenticación UGS) y `CloudSyncOps` (reconciliación). Al autenticarse, carga datos locales scoped y dispara startup sync. Propiedad `StartupSyncDone` para aguardar sincronización. S131: Integra `WorldStateSO` para sincronización de estado de mundo. **S149:** Se retira `FurnitureRegistrySO` de las referencias y de la carga local.

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `InitializeAsync()` | `Task` | Inicia autenticación UGS |
| `PushAsync()` | `Task` | Sube creatureregistry, inventario, grafo social y world state |
| `PullAsync()` | `Task` | Baja las mismas claves (no recomendado post-S128) |
| `SyncOnStartupAsync()` | `Task` | Reconcilia nube vs local |
| `ResetProgressAsync()` | `Task` | Borra datos de nube y resetea local (debug). Lo llama `AdminDevConsole` |
| `UpdatePlayerNameAsync(string)` | `Task` | Actualiza nombre de jugador en UGS |

## Propiedades

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `StartupSyncDone` | `bool` | True si startup sync completó (o sin sesión). `StarterKitService` y `UncleRescueService` esperan esta bandera |
| `ServerOffset` | `TimeSpan` | Offset UTC servidor para hora sincronizada |

## Ciclo de Vida

1. `Start()` → Obtiene referencias desde `GameManager`:
   - registry, inventory, **worldState** (S131)
2. `Start()` → Crea `CloudAuth` y `CloudSyncOps` (pasando worldState)
3. `Start()` → `auth.InitializeAsync()` (UI UGS o anónimo). Si no hay sesión, `StartupSyncDone = true`
4. Auth success → `HandleSignedInAsync(method)`
   - Setea `SaveSystem.SetUserScope(PlayerID)`
   - Carga datos locales scoped:
     - `SaveSystem.LoadInto(registry)` → dispara `RegistryReloaded`
     - `SaveSystem.LoadSocialGraph(registry)` (sin evento)
     - `SaveSystem.LoadInventory(inventory)` → dispara `InventoryReloaded`
     - `SaveSystem.LoadWorldState(worldState)` → dispara `WorldStateReloaded` (S131)
   - `auth.FetchServerTimeAsync()`
   - Sincroniza nube vía `syncOps.SyncOnStartupAsync()`
   - En `finally` setea `StartupSyncDone = true`
5. `OnDestroy()` → `auth.Teardown()` (cleanup UGS)

## Cambios S149

- **Retirado:** `furnitureRegistry` (campo y referencia), la carga `LoadFurniture` y el evento `FurnitureReloaded`.
- **Constructor de `CloudSyncOps`:** ya no recibe muebles.
- `TryApply` del kit no se llama desde aquí; lo llama `StarterKitService` (y el botón de `AdminDevConsole`).

## Cambios S131

**Agregado:**
- `private WorldStateSO worldState;` (resolución en Start)
- Pasado a `CloudSyncOps` constructor
- `HandleSignedInAsync()` ahora carga y dispara `WorldStateReloaded`

**Propósito:** Sincronización de estado de mundo (día/minuto) con cloud, integrado al bootstrap.

## Integración S128/S131/S149

**SyncOnStartupAsync():** Reconciliación inteligente. En lugar de pull ciego:
- Nube vacía → sube local
- Al día → nada
- Otra PC subió → baja, dispara Reloaded events
- Conflicto → respaldo + gana el más nuevo

**Claves sincronizadas:**
- `creatureregistry` (registry)
- `playerinventory` (cartera, props, decoraciones)
- `socialgraph` (relaciones)
- `worldstate` (estado de mundo, S131)

## Referencias Resueltas en Start

```csharp
registry   = GameManager.Instance.Registry;
inventory  = GameManager.Instance.Inventory;
worldState = GameManager.Instance.WorldState;  // S131
auth    = new CloudAuth(...);
syncOps = new CloudSyncOps(auth, registry, inventory, worldState, ...);
```

## DisplayDebug (Odin)

- `PlayerID`, `PlayerName`, `SignedIn`, `AuthMethod` — desde `CloudAuth`
- `LastPullDisplay`, `LastKnownCloudDisplay`, `SecurityStatus` — desde `CloudSyncOps`
- `ServerTimeOffset` — offset UTC
- Botones: Sign In anónimo (DEV), Sign In Unity, Sign Out, Update Name, Reset All Progress (DEV), Push, Pull

## Invariantes

- `worldState` puede ser null (fallback graceful en CloudSyncOps)
- `LoadWorldState()` null-safe (devuelve estado default si no existe)
- `WorldStateReloaded` dispara tras carga (permite GameClock actualizar)

## Vinculado a

- [[Index/07 - Persistence & Identity]]
- [[Index/09 - Active Context]]

## Conexiones

**Cloud:**
- [[CloudAuth]] — autenticación UGS
- [[CloudSyncOps]] — lógica de reconciliación

**Data:**
- [[CreatureRegistrySO]], [[PlayerInventorySO]], [[WorldStateSO]]

**Sistemas:**
- [[SaveSystem]] — carga/serialización
- [[GameManager]] — proporciona referencias
- [[GameClock]] — reacciona a WorldStateReloaded
- [[GameEvents]] — dispara Reloaded events
- [[StarterKitService]], [[UncleRescueService]] — esperan `StartupSyncDone`
- [[AdminDevConsole]] — llama `ResetProgressAsync`

## Notas (S131 HC-4)

- **Bootstrap ordering:** CloudSyncService.Start() resuelve worldState antes de sync, permitiendo que GameClock se inyecte con estado precargado.
- **Event chain:** LoadWorldState → WorldStateReloaded → GameClock.HandleWorldStateReloaded → DayBlockChanged.
