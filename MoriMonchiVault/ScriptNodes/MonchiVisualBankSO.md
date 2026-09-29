---
tags: [scriptable-object, visual-data, genetics]
---

# MonchiVisualBankSO.cs

**Ruta:** `Data/Databases/MonchiVisualBankSO.cs`

**Responsabilidad:** Banco visual: body FBX, partes modulares (Adult/Egg/Slime), modelos base, AnimatorControllers. **S138:** Agregado `eggScale` (default 3.4 en asset).

## S138 Cambios

**Nuevo campo:**
```csharp
[SerializeField] private float eggScale = 3.4f;
public float EggScale => eggScale;
```

**Propósito:** MonchiEggBody.Build() escala huevo con `eggScale` en X/Z y `eggScale * eggHeight` en Y. Asset 2.6 utiliza 3.4.

## Escalas por Forma

| Forma | Campos | Uso |
|-------|--------|-----|
| Adult | animatorController | Adulto Suriyun |
| Egg | eggModel, eggAnimatorController, eggScale, eggHeight | Huevo modular |
| Slime | slimeModel, slimeAnimatorController, slimeScale | Slime modular |

## Métodos

- `GetBody(bodyShapeId)` — Body adulto
- `GetPartMesh(partId, form)` — Parte por forma
- `GetGem(uniqueId)` — Material gema
- `SetPartMesh()` — Editor: registra parte

## Conexiones

- [[MonchiEggBody]], [[MonchiSlimeBody]], [[MonchiVisualizer]]
