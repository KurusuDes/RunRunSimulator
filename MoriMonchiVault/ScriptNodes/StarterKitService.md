---
tags: [script, system, startup]
---

# StarterKitService.cs

**Ruta:** `Systems/Player/StarterKitService.cs`

**Responsabilidad:** Servicio que aplica el kit inicial (moneda) en partida nueva. Espera a que `CloudSyncService.StartupSyncDone == true` o un timeout de 20 s (medido en tiempo sin escala). **S152:** si la tienda se abrió desde el título con "nueva partida" (`SceneFlow.ConsumeNewGameRequest()`), primero resetea el progreso en la nube con `CloudSyncService.ResetProgressAsync()` y luego aplica el kit. Detecta nueva partida: `TutorialStep == 0 && registry.Count == 0`. Si es nueva: suma Minerita y Dabloons via `Wallet.Add()`, avanza TutorialStep a 1 y emite `GameEvents.WorldStateChanged`. **S149:** Se retira el kit de muebles (ya no existen); `TryApply()` pasa a ser público y lo llama también `AdminDevConsole`. MonoBehaviour stateless wired en escena.

## Campos Serializados

- `kit` (StarterKitSO, required) — asset con valores iniciales (Minerita, Dabloons)
- `cloudSync` (CloudSyncService, required) — esperar a sync y resetear progreso
- `syncTimeoutSeconds` (float, default 20) — timeout para CloudSync.StartupSyncDone

## Ciclo de Vida

### Start()
1. Inicia corrutina `ApplyKitRoutine()` (no bloquea)

### ApplyKitRoutine()
1. Espera a `CloudSyncService.StartupSyncDone` (con timeout, en `unscaledDeltaTime`)
2. **(S152)** Si `SceneFlow.ConsumeNewGameRequest()` devuelve `true` y hay `cloudSync`: `ResetProgressAsync()` y espera a que termine (log de excepción si falla)
3. Llama `TryApply()`

### TryApply() (público, bool)
1. Obtiene `GameManager.Instance.WorldState`, `Registry` y `CurrentInventory`
2. Si alguna ref o `kit` falta → warning y devuelve false
3. Detecta nueva partida: `TutorialStep == 0 && registry.Count == 0`
4. Si no es nueva → log y devuelve false (kit no aplicado a saves existentes)
5. Si es nueva:
   - Suma `kit.Minerita` y `kit.Dabloons` via `Wallet.Add(currency, amount, "starter")` (solo si > 0)
   - Avanza `worldState.TutorialStep = 1`
   - Dispara `GameEvents.WorldStateChanged(worldState)`
   - Devuelve true

## Invariantes

- **Una sola vez**: detecta nueva partida por estado (TutorialStep=0, Count=0), no hay flag
- **No sobrescribe si existe**: el kit es solo para init (partida nueva solo)
- **Wallet es singleton**: `Wallet.Add()` es estático, centraliza currency
- **Eventos disparan**: WorldStateChanged siempre que aplica (S149: ya no dispara InventoryChanged)
- **(S152)** El reset de nube solo ocurre con la bandera de `SceneFlow`; un arranque normal de la tienda no borra nada

## Cambios S149

- **Retirado:** Kit de muebles (`kit.Furniture`) y la llamada `AddFurniture`.
- **Retirado:** Evento `InventoryChanged` en el kit.
- **Público:** `TryApply()` ahora devuelve bool y lo usa `AdminDevConsole` (reset de save).

## Cambios S152

- **Nueva partida desde el título:** reset de progreso en nube antes de aplicar el kit (`SceneFlow.RequestNewGame` → `ConsumeNewGameRequest`).

## Vinculado a

- [[Index/06 - Gameplay Loop]] (onboarding)
- [[Index/07 - Persistence & Identity]]

## Conexiones

- [[StarterKitSO]] (asset de config)
- [[CloudSyncService]] (señal de inicio de sesión; `ResetProgressAsync` en S152)
- [[SceneFlow]] (bandera de partida nueva, S152)
- [[TitleScreenUITK]] (origen de la partida nueva, S152)
- [[AdminDevConsole]] (llama `TryApply`)
- [[GameManager]] (WorldState, Registry, refs)
- [[Wallet]] (currency manipulation)
- [[GameEvents]] (WorldStateChanged)
