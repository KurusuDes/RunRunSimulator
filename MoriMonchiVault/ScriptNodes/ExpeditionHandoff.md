---
tags: [script, core, handoff, expedition, time-scale]
---

# ExpeditionHandoff.cs

**Ruta:** `Core/ExpeditionHandoff.cs`

**Responsabilidad:** Puente estático entre escenas (tienda/arena). Encapsula traspaso de datos, resultado. **S138:** Captura y restaura `fixedDeltaTime` para que MMTimeManager (que multiplica paso escalado) no distorsione physics en arena.

## Estado Estático (S138)

- `CameFromStore`, `HasResult`, `Result`, `RunSeed`, `SelectedIds`
- **S138:** `defaultFixedDeltaTime` — capturado en ResetState(), restaurado en ResetTime()

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `GoToArena(ids)` | ResetTime(), genera RunSeed, LoadScene(ArenaScene) |
| `ReturnToStore(result?)` | ResetTime(), LoadScene(GameScene) |
| `ResetTime()` | **(S138 NUEVO)** timeScale=1f, restaura fixedDeltaTime |

## S138: Time Management

**ResetState() — SubsystemRegistration:**
```csharp
defaultFixedDeltaTime = Time.fixedDeltaTime;
```

**ResetTime() — Antes de cambiar escena:**
```csharp
Time.timeScale = 1f;
if (defaultFixedDeltaTime > 0f) Time.fixedDeltaTime = defaultFixedDeltaTime;
```

Arena escala timeScale 4x. MMTimeManager multiplica fixedDeltaTime por timeScale. Restaurar ambos previene physics distorsionado al volver a tienda.

## Vinculado a

- [[Index/23 - Arena Sandbox y Expedicion]]

**Conexiones:** [[ExpeditionBridge]], [[MMTimeManager]], [[ArenaRunDirector]]
