---
tags: [dev, tooling, admin, odin, debug]
---

# AdminDevConsole.cs

**Ruta:** `Systems/Player/AdminDevConsole.cs`

**Responsabilidad:** Herramienta de desarrollo con botones Odin para ajustar saldos, resetear el save, forzar la llamada del tio y volcar el estado del juego. Solo actua en Play mode (`CanMutate`). No es parte del gameplay.

## Botones

| Boton | Accion |
|-------|--------|
| `Set Dabloons` / `Set Minerita` | Iguala el saldo via `Wallet.Add` o `Wallet.TrySpend` |
| `Reset Save` | `CloudSyncService.ResetProgressAsync()` y luego `StarterKitService.TryApply()` |
| `Force Uncle Call` | `UncleRescueService.ForceCall()` |
| `Dump` | Log y retorno de saldos, vivos/idos, TutorialStep, Day, StartupSyncDone y SoftBlocked |

## Referencias Serializadas

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `cloudSync` | `CloudSyncService` | Si |
| `starterKit` | `StarterKitService` | Si |
| `uncleRescue` | `UncleRescueService` | No |

**Nota:** `Reset Save` llama `CloudSyncService` directamente. Es excepcion de tooling dev, no flujo de gameplay.

**Conexiones:** [[CloudSyncService]], [[StarterKitService]], [[UncleRescueService]], [[Wallet]], [[GameManager]], [[DevToolsConsole]]
