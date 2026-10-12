---
tags: [cloud, synchronization, networking]
---

# CloudSyncOps

**Ruta:** `Systems/Cloud/CloudSyncOps.cs`

**Responsabilidad:** Orquestador de sincronización nube/local con reconciliación inteligente. `SyncOnStartupAsync()` reconcilia tres timestamps. `PushAsync/PullAsync()` manejan las claves creatureregistry, playerinventory, socialgraph y worldstate, más `sync_meta`. S131: Constructor recibe `WorldStateSO`. **S149:** Se retira `FurnitureRegistrySO` del constructor y de push/pull. La clave de muebles solo se borra en `ResetProgressAsync`, como limpieza de datos viejos.

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `PushAsync()` | `Task` | Sube creatureregistry, sync_meta, socialgraph, playerinventory y worldstate |
| `PullAsync()` | `Task` | Baja creatureregistry, sync_meta, playerinventory, socialgraph y worldstate |
| `SyncOnStartupAsync()` | `Task` | Reconcilia nube vs local (timestamps) |
| `ResetProgressAsync()` | `Task` | Borra datos de nube (incluida la clave de muebles, legado) y resetea local (debug) |
| `RefreshSecurityDisplay()` | `void` | Actualiza displays para debug |

## Claves Sincronizadas

| Clave | Contenido | Estado |
|-------|-----------|--------|
| `creatureregistry` | RegistryData (Alive+Departed) | Push y pull |
| `playerinventory` | Cartera, hotbar, props y decoraciones | Push y pull |
| `socialgraph` | Pairwise relationships | Push y pull |
| `worldstate` | WorldStateData (day/minute/tutorial/mejoras/stock/bredTotal/decor/estaciones) | Push y pull (S131) |
| `sync_meta` | SyncMeta (LocalPulledAt, LocalKnownCloudAt, CloudPushedAt) | Push y pull |
| `furnitureregistry` | Muebles (legado) | **Solo borrado en reset** (S149) |

## Constructor

```csharp
public CloudSyncOps(CloudAuth auth, CreatureRegistrySO registry,
    PlayerInventorySO inventory, WorldStateSO worldState, Action<string> setStatus)
```

**S149:** Se elimina el parámetro `FurnitureRegistrySO`.

## Push y Pull

- **PushAsync:** Si ya hay un push en curso, marca `pushAgain` y reintenta al terminar. Valida con `ValidateBeforePush()` (alerta de "CHEAT ALERT" solo como log, dev: push permitido). Sube el payload y escribe `LocalKnownCloudAt` local.
- **PullAsync:** Reemplaza registry, inventario, grafo social y world state. Dispara `RegistryReloaded`, `InventoryReloaded` y `WorldStateReloaded`. Guarda cada copia en disco con `SaveSystem`.

## SyncOnStartupAsync

Compara `CloudPushedAt` de la nube con `LocalKnownCloudAt` local y con `SaveSystem.LatestLocalSavedAt()`:
- Nube vacía: push si hay datos locales.
- Coinciden y local más nuevo: push.
- Nube más nueva: pull.
- Conflicto: backup local con `SaveSystem.BackupLocal("conflict")` y gana el más reciente.

## Cambios S149

- **Retirado:** `FurnitureRegistrySO` del constructor, de push y de pull.
- **Conservado:** `FURNITURE_KEY` solo en `ResetProgressAsync`, para borrar la clave vieja de la nube.
- **Efecto en `SaveSystem.BackupLocal`:** ahora respalda 4 archivos (sin muebles).

## Cambios S131

**Agregado:**
- `private WorldStateSO worldState` — referencia
- `worldstate` clave en push/pull/reset
- Manejo de `SaveKind.World` en migrations

**Propósito:** Sincronización de día/minuto del juego con cloud.

## Vinculado a

- [[Index/07 - Persistence & Identity]]
- [[Index/09 - Active Context]]

## Conexiones

- [[CloudAuth]] — autenticación
- [[SaveSystem]] — serialización (con WorldState)
- [[CloudSyncService]] — orquestador superior
- [[CloudEndpoint]] — envuelve push, pull y reset (`Guarded`)
- [[GameManager]], [[GameEvents]]

## Notas

- **Backward compat:** Guardados v3 siguen migrando a v4 sin pérdida.
- **Muebles:** ningún dato de muebles viaja en el payload desde S149.
