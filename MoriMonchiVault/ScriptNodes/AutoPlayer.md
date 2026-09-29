---
tags: [script, dev, testing]
---

# AutoPlayer.cs

**Ruta:** `Systems/Dev/AutoPlayer.cs`

**Responsabilidad:** Bot de testing automatizado (solo dev) que ejecuta un escenario de 11 pasos: partida nueva → comprar caja de huevos → abrir caja → colocar incubadora → meter huevos → eclosionar 3 → expedición (arena) → combate automático → retorno → eclosionar restantes → fin. Singleton `DontDestroyOnLoad`. Suscribe a `GameEvents.OnExpeditionReturned` para registrar resultado. Expone `Status` string (público) con estado actual. Timeout 60s por paso, 240s para piso arena (arenaTimeScale=4x). Si falla: Debug.Break() y registra `Status="FALLA paso X · motivo"`.

## Singleton + Lifecycle

- `Instance { get; private set; }` — singleton persistente
- `DontDestroyOnLoad` en Awake
- `Status { get; private set; } = "Idle"` — string público con estado actual paso (e.g., "OK paso 3 · Abrir caja · huevos=5")

## Campos Serializados

- `arenaTimeScale` (float, default 4) — aceleración de tiempo durante combate (step 8)
- `stepTimeout` (float, default 60) — timeout por paso en segundos

## Ciclo de Pasos (11 total)

### Step 1: Arrival
- Espera CloudSync.StartupSyncDone
- Verifica TutorialStep >= 1 (kit aplicado)
- Valida Minerita: balance >= 3 × hatchCost
- Verifica incubadora en inventario

### Step 2: BuyEggBox
- Busca StoreManager + Catalog
- Localiza caja de Form.Egg con precio=0 (gratis)
- Ejecuta BuyCreatureBox()

### Step 3: OpenBox
- Espera DeliveryBox en escena
- Registra IDs previos del registry
- Interactúa con DeliveryBox
- Espera 5 huevos nuevos spawneados + controllers spawned

### Step 4: PlaceIncubator
- Busca FurnitureService + PlacementGrid
- Localiza mueble incubadora del kit
- Intenta colocar en espiral desde (0,0) con radio 25
- Espera IncubatorContainer en escena

### Step 5: EggsIntoIncubator
- Busca MoriMochiSpawner
- Por cada huevo: lanza controller hacia incubadora (impulso hacia abajo)
- Espera 5 ocupantes en incubadora

### Step 6: HatchThree
- Interactúa incubadora 3 veces (+ delay 0.3s)
- Valida: 3 slimes + 2 huevos restantes
- Interactúa 4ta vez, verifica que NO eclosione (límite UI/lógica)

### Step 7: Departure
- Filtra slimes en registry
- Llama `ExpeditionBridge.RequestDeparture(slimeIds)`
- Espera cambio de escena a ArenaScene

### Step 8: ArenaRun
- Time.timeScale = arenaTimeScale
- Espera ArenaRound + ArenaRunDirector spawned
- Lanza ronda si no corriendo
- Espera director.FloorRecorded (timeout 240s)
- Lee Run.Material y Run.Lost
- Llama director.Retreat()
- Restaura Time.timeScale = 1

### Step 9: Return
- Espera vuelta a StoreScene + OnExpeditionReturned disparado
- Restaura Time.timeScale = 1
- Valida: si no perdió, cada slime debe tener Explorations=1

### Step 10: HatchRemaining
- Filtra huevos restantes en registry
- Espera incubadora persistida con esos huevos
- Valida Minerita para 2 eclosiones
- Interactúa 2 veces
- Verifica 0 huevos restantes

### Step 11: Fin
- Status = "FIN tanda 1"
- fin de secuencia

## Métodos Públicos

- `Run()` — inicia secuencia si no está corriendo
- `Status { get; }` — estado actual (lecture pública)

## Métodos Privados

- `WaitFor(Func<bool> condition, float timeout, string what) → IEnumerator` — loop until condition true o timeout. Si timeout: Fail()
- `Fail(string reason)` — asigna `failed=true`, `Status="FALLA paso X · reason"`, restaura Time.timeScale=1, Debug.Break()
- `Ok(string name, string data)` — asigna Status="OK paso X · name · data", Debug.Log()
- Helpers de búsqueda: `FindIncubatorFurnitureDefinition()`, `TryFindController()`, `AllControllersSpawned()`, `CountFormNotIn()`, `CountForm()`, `CountOccupantsAmong()`, `SpiralCells()`

## Suscripciones

- `OnEnable()` suscribe a `GameEvents.OnExpeditionReturned` (registra último retorno)
- `OnDisable()` desuscribe

## Invariantes

- **Singleton + Persistent**: una sola instancia en escena, persiste entre escenas
- **Falla en Debug.Break()**: desarrollo interactivo, permite inspeccionar estado
- **Status público**: dev consola/UI puede leer progreso en vivo
- **Timeouts grandes**: arena (240s) vs steps normales (60s)
- **Time.timeScale 4x en arena**: acelera combate para testing rápido

## Vinculado a

- [[Index/09 - Active Context]] (S137: AutoPlayer en DevConsole)
- [[Index/23 - Arena Sandbox y Expedicion]] (pasos 7-9)

## Conexiones

- [[CloudSyncService]] (sincronización)
- [[GameManager]] (WorldState, Registry)
- [[BreedingController]] (costo eclosión)
- [[StoreManager]] (compra de caja)
- [[DeliveryBox]] (abrir caja)
- [[FurnitureService]] + [[PlacementGrid]] (colocar muebles)
- [[IncubatorContainer]] (eclosionar)
- [[MoriMochiSpawner]] (localizar controllers)
- [[ExpeditionBridge]] (partir a arena)
- [[ArenaRound]] + [[ArenaRunDirector]] (combate)
- [[GameEvents]] (OnExpeditionReturned)
- [[Wallet]] (validar Minerita)
