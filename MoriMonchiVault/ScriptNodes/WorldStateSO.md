---
tags: [script, scriptable-object, world-state, data]
---

# WorldStateSO.cs

**Ruta:** `Data/World/WorldStateSO.cs`

**Responsabilidad:** ScriptableObject runtime: estado del mundo (día, minuto, tutorial). **S138:** añade diccionario de niveles de mejoras. Métodos: GetData(), LoadFrom(). Suscripción automática a GameEvents.OnWorldStateChanged → SaveSystem.SaveWorldState().

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `day` | int | Día actual (default 1) |
| `minuteOfDay` | float | Minuto del día (default 360 = 6 AM) |
| `tutorialStep` | int | Paso tutorial (default 0) |
| `upgradeLevels` | Dictionary<string, int> | **(S138)** Nivel de cada mejora por ID |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Day` | int | Getter/setter |
| `MinuteOfDay` | float | Getter/setter |
| `TutorialStep` | int | Getter/setter |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `UpgradeLevel(string id)` | `int` | **(S138)** Lee nivel de mejora (default 0 si no existe) |
| `SetUpgradeLevel(string id, int level)` | `void` | **(S138)** Escribe nivel de mejora |
| `GetData()` | `WorldStateData` | Serializa a struct para persistencia |
| `LoadFrom(WorldStateData data)` | `void` | Carga desde struct; null-safe |

## WorldStateData (Serializable)

```csharp
[Serializable]
public class WorldStateData
{
    public int   Day          = 1;
    public float MinuteOfDay  = 360f;
    public int   TutorialStep = 0;
    public Dictionary<string, int> UpgradeLevels = new Dictionary<string, int>();
}
```

Struct para serialización JSON vía SaveSystem.

## Ciclo de Vida

1. **Init (GameScene):** Inyectado en GameManager. SaveSystem.LoadWorldState() lo carga.
2. **Runtime:** GameClock actualiza MinuteOfDay. Cambios disparan GameEvents.WorldStateChanged().
3. **Persistencia:** GameManager.OnEnable() suscribe PersistWorldState() → SaveSystem.SaveWorldState() + push cloud.
4. **Cloud Reload:** CloudSyncService dispara OnWorldStateReloaded cuando sincroniza.

## Integración S138

- StoreManager.BuyUpgrade() llama `world.SetUpgradeLevel()` + dispara `GameEvents.WorldStateChanged()`
- AutoPlayer.Step16_Upgrade() itera catálogo, llama BuyUpgrade()
- WorldStateSO persiste automáticamente en SaveSystem

## Vinculado a

- [[Index/28 - Currency & Monetization]] (mejoras)
- [[Index/07 - Persistence & Identity]] (persistencia)

**Conexiones:** [[GameManager]], [[GameClock]], [[SaveSystem]], [[CloudSyncService]], [[GameEvents]], [[StoreManager]]
