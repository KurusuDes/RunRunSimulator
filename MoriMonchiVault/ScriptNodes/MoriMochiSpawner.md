---
tags: [script, world, spawner]
---

# MoriMochiSpawner

**Ruta:** `World/Spawning/MoriMochiSpawner.cs`

**Responsabilidad:** Convierte DATA (CreatureRegistrySO) → PRESENCIA (MoriMonchiController vivo en escena). Singleton. S137: Spawnea criaturas de cualquier Form (Egg/Slime/Adult) con visual correspondiente. Dispara criaturas como proyectiles (ragdoll mid-aire). **S57:** `PrewarmAndStart()` ensambla modelos mientras inactivos pasando `bank=GameManager.MonchiVisualBank` en Initialize (Assemble completo del modelo Suriyun off-screen). `Acquire()` con controller prewarmed pasa `bank=null` A PROPÓSITO (contrato: saltear re-ensamblado — el controller hace `RefreshLook` y CONSERVA el banco guardado en prewarm); cold spawn del pool pasa `bank=MonchiVisualBank` (Assemble completo). Espera World Ready (primer NavMesh bake + furniture cargada), luego pump activa. **Gate `dataReady`**: no puebla hasta primera carga autoritativa (OnRegistryReloaded o timeout `dataReadyTimeout` = 6s default). Cola prioritaria **`anchoredQueue`** (criaturas con LocationKey): se colocan DIRECTAMENTE en su lugar via `AnchorRegistry.TryGet()` + `place.TryReclaim()` (sin cañonazo). Si el lugar desaparece, cae al cañón y limpia LocationKey. Timeout `anchorPlaceTimeout` → si la place no aparece en tiempo, cannon-fire fallback. Criados lanzan desde punto registrado por `RegisterBirthLaunch()`. `OnRegistryReloaded()` re-vincula DNA/profile en spawned via `controller.Rebind()` (rápido, sin re-ensamblar); re-ancla sueltos tras pull nube. Usa ControllerPool para reutilizar, SpawnBallistics para balística. **S130:** Overload `RegisterBirthLaunch(id, muzzle)` — calcula landing automáticamente desde `LandingCenter` + random dentro de `spawnRadius`.

## Ciclo de vida (S57)

1. **Awake:** instancia ControllerPool
2. **Start:** lanza PrewarmAndStart (si hay registry)
3. **OnEnable:** suscribe a GameEvents (RegistryChanged, RegistryReloaded, NavMeshRebaked)
4. **PrewarmAndStart (S57):**
   - Itera registry, instancia 1 criatura/frame (inactivo) en prewarmPos
   - Llama `controller.Initialize(dna, table, player, bank=MonchiVisualBank, furDb)` → Assemble completo (Form-aware S137) mientras inactivo
   - Espera resto de startDelay
   - Bloquea en WorldReady (primer NavMesh bake) o navMeshWaitTimeout
   - Llama Sync() y desbloquea pump
5. **SpawnPump:** tickea cada spawnInterval, dequeues anchoredQueue → spawnQueue, despacha SpawnOne()
6. **Acquire (S57):** 
   - Si prewarmed: activa + `Initialize(dna, table, player, bank=null, furDb)` — null intencional: el controller hace RefreshLook y conserva el banco del prewarm (modelo ya armado, no se re-ensambla)
   - Si cold pool: `Initialize(dna, table, player, bank=MonchiVisualBank, furDb)` (Assemble completo, Form-aware S137)
7. **OnDisable:** limpia coroutines, suscripciones

## Cambios S137

**Form-aware assembly:** MonchiVisualizer.Assemble() ahora maneja Egg/Slime/Adult (builders estáticos vs prefab). Spawnea visual correcto según DNA.Form.

**Colas de spawn (sin cambio):** Eggs/Slimes/Adults usan mismo sistema (anchoredQueue para LocationKey, spawnQueue para libres).

## Colas de spawn

| Cola | Condición | Ruta |
|------|-----------|------|
| `anchoredQueue` | LocationKey != "" | TryPlaceAtAnchor() (via AnchorRegistry) o cannon fallback |
| `spawnQueue` | LocationKey == "" | Cannon (RandomLandingPoint) |

## Propiedades públicas (Readonly, internal accessores)

**Spawn state:**
- `Registry → CreatureRegistrySO` — fuente de datos (null si GameManager no inicializado)
- `Table → RoleWorldProfileSO` — perfiles comportamiento por Role (S39)
- `Bank → MonchiVisualBankSO` — banco visual Suriyun (S57, S137 Form-aware)
- `FurDb → FurTypeDatabaseSO` — database de pelajes

**Sincronización:**
- `Sync(CreatureRegistrySO registry)` — reconcilia spawned vs registry, enqueues deltas
- `RegisterBirthLaunch(childId, muzzle, landing)` — registra punto de salida y aterrizaje criado
- `RegisterBirthLaunch(childId, muzzle)` — registra punto de salida, calcula landing automático (S130 NUEVO)

**Spawner state (read-only, internal accesores para SpawnerDevConsole):**
- `Instance → MoriMochiSpawner` — singleton
- `WorldReady → bool` — gate de mundo (furniture + NavMesh)
- `DataReady → bool` — gate de datos (primera carga autoritativa)
- `SpawnedCount, QueuedCount, PrewarmedCount, PooledCount → int` — contadores
- `CreaturePrefab → MoriMonchiController` — prefab
- `MuzzlePosition → Vector3` — punto de salida cañón
- `LaunchAngleRange → Vector2` — ángulos min/max
- `SpawnedEntries → IEnumerable<KVP>` — iterador de spawned para debug

**Pool lifecycle:**
- `ClearAll()` — limpia todos los spawned, desqueues, poolea

## Vinculado a

- [[Index/02 - Genetics & Breeding]] (S137: Form-aware)
- [[Index/09 - Active Context]] (S137)
- [[Index/06 - Player & World]]

## Conexiones

- [[MonchiVisualBankSO]] (S137: Form-aware assembly)
- [[MonchiVisualizer]] (S137: Form-aware Assemble)
- [[MonchiEggBody]], [[MonchiSlimeBody]] (S137: builders para Egg/Slime)
- [[MoriMonchiController]] (poolea, initializa)
- [[ControllerPool]], [[SpawnBallistics]]
- [[GameEvents]] (suscribe RegistryChanged, RegistryReloaded, NavMeshRebaked)
