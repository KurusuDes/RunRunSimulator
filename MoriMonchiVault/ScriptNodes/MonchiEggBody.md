---
tags: [script, visualization, genetics, egg-builder]
---

# MonchiEggBody.cs

**Ruta:** `World/Creatures/MonchiEggBody.cs`

**Responsabilidad:** Constructor estático: arma visual huevo. **S138:** Escala huevo = `EggScale` en X/Z, multiplicado por `EggHeight` en Y.

## Build() — S138

```csharp
instance.transform.localScale = new Vector3(
    bank.EggScale, 
    bank.EggScale * bank.EggHeight, 
    bank.EggScale
);
```

**Propósito:** Asset 2.6 usa eggScale=3.4 base, eggHeight=1.15. Escala XY separada para huevo oblongo.

## Método

- `Build(dna, bank, parent)` — Instancia EggModel, aplica escala, injerta espalda genética, desactiva Egg_Scales

## Conexiones

- [[MonchiVisualBankSO]], [[MonchiVisualizer]], [[CreatureDNA]]
