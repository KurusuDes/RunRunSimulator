---
tags: [script, system, startup]
---

# StarterKitService.cs

**Ruta:** `Systems/Player/StarterKitService.cs`

**Responsabilidad:** Servicio que aplica el kit inicial (moneda + muebles) en partida nueva. Espera a que `CloudSyncService.StartupSyncDone == true` y `TutorialStep >= 1`. Detecta nueva partida: `TutorialStep == 0 && registry.Count == 0`. Si es nueva: suma Minerita/Dabloons via `Wallet.Add()`, agrega muebles al inventario, dispara `GameEvents.InventoryChanged` si hubo cambios, avanza TutorialStep a 1, y emite `GameEvents.WorldStateChanged`. Timeout 20s si cloud stall. MonoBehaviour stateless wired en escena.

## Campos Serializados

- `kit` (StarterKitSO, required) — asset con valores iniciales
- `cloudSync` (CloudSyncService, required) — esperar a sync
- `syncTimeoutSeconds` (float, default 20) — timeout para CloudSync.StartupSyncDone

## Ciclo de Vida

### Start()
1. Inicia corrutina `ApplyKitRoutine()` (async, no bloquea)

### ApplyKitRoutine()
1. Espera a CloudSyncService.StartupSyncDone (con timeout)
2. Obtiene `GameManager.Instance.WorldState`, `GameManager.Instance.Registry`, `GameManager.CurrentInventory`
3. Si alguna ref falta → warning y fin
4. Detecta nueva partida: `TutorialStep == 0 && registry.Count == 0`
5. Si no es nueva → log y fin (kit no aplicado a saves existentes)
6. Si es nueva:
   - Suma `kit.Minerita` y `kit.Dabloons` via `Wallet.Add(currency, amount, "starter")`
   - Por cada mueble en kit.Furniture: si no null, suma via `inventory.AddFurniture(def.Id)`
   - Si hubo muebles agregados: dispara `GameEvents.InventoryChanged(inventory)`
   - Avanza `worldState.TutorialStep = 1`
   - Dispara `GameEvents.WorldStateChanged(worldState)`
   - Registra log con detalles

## Invariantes

- **Una sola vez**: detecta nueva partida por estado (TutorialStep=0, Count=0), no hay flag
- **No sobrescribe si existe**: el kit es solo para init (partida nueva solo)
- **Wallet es singleton**: `Wallet.Add()` es estático, centraliza currency
- **Eventos disparan**: InventoryChanged si muebles, WorldStateChanged siempre

## Vinculado a

- [[Index/06 - Gameplay Loop]] (onboarding)
- [[Index/07 - Persistence & Identity]]

## Conexiones

- [[StarterKitSO]] (asset de config)
- [[CloudSyncService]] (señal de inicio de sesión)
- [[GameManager]] (WorldState, Registry, refs)
- [[Wallet]] (currency manipulation)
- [[GameEvents]] (InventoryChanged, WorldStateChanged)
