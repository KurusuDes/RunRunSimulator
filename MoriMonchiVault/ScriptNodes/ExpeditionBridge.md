---
tags: [script, system, expedition, bridge, monetization]
---

# ExpeditionBridge.cs

**Ruta:** `Systems/Expedition/ExpeditionBridge.cs`

**Responsabilidad:** Orquestador transiciones tienda↔arena. Aplica rewards: **S138** `mineritaPerMaterial=5`, MineritaGained = material × tasa.

## S138: Monetización

**Campo:**
```csharp
[SerializeField, Min(1)] private int mineritaPerMaterial = 5;
```

**ApplyResult() — línea 81:**
```csharp
int minerita = result.Lost ? 0 : result.PlayerSecured * mineritaPerMaterial;
```

**Cambio:** Material del resultado (integer) se multiplica por tasa fija. PlayerSecured sigue siendo material (no se convierte).

**Ejemplo:** Aseguras 10 material → 10 × 5 = 50 Minerita.

## Métodos

- `Depart(ids)` — Inicia bajada
- `ApplyResult()` — Suma Minerita, mata caídos, registra exploraciones

## Conexiones

- [[ExpeditionHandoff]], [[Wallet]], [[CreatureLifecycle]], [[GameEvents]]
