---
tags: [script, genetics, breeding, container]
---

# BreedingContainer.cs

**Ruta:** `World/Containers/BreedingContainer.cs`

**Responsabilidad:** Corral de cría (hereda MoriMochiContainer). Solo acepta adultos (Form=Adult). Pairing automático con affinity×diceChance. Maneja interacción: si hay eclosión lista, `TryHatch()` vía `BreedingController`. Anima courtship + resultado (éxito/falla). S137: ciclo de vida redondeado (huevo nace como Form=Slime, luego incubadora lo resucita, crece a Adult).

**S138:** Sin cambios. Nodo clarificado.

## Accepts() — Ciclo de Vida S137

```csharp
protected override bool Accepts(MoriMochiAgent agent) =>
    agent != null && agent.DNA != null && agent.DNA.Form == MonchiForm.Adult;
```

**Solo adultos:** excluye Eggs (no vivos, incubables) y Slimes (exploradores jóvenes, no reproducibles aún). Validación de entrada al corral.

## TryRollPair() — Pairing Automático

Usa `BreedingController.GetAffinity(mother.Role, father.Role)` para calcular probabilidad:

```csharp
float affinity = BreedingController.Instance?.GetAffinity(mother.Role, father.Role) ?? 0.5f;
float pairChance = affinity * diceChance;
return Random.value < pairChance;
```

Ambos padres deben estar en corral y pasar validación de forma + ocupantes.

## Interact() — Ciclo de Eclosión

1. **Detecta estado breeding:** ¿Algún ocupante con BusyReason=Breeding?
2. **Si hay eclosión lista:** `BreedingController.TryHatch(motherID, fatherID)` → switch(HatchResult)
   - `Hatched` — anima huevo, hijo nace Form=Egg (ó Form=Slime según spawn), dispara GameEvents
   - `NotReady` — toast "Aún falta tiempo"
   - `InsufficientMinerita` — toast "Insuficiente Minerita"
   - `Invalid` — toast error
3. **Si no hay eclosión:** muestra timer resta + UI visual

## Campos Serializados

| Campo | Tipo | Propósito |
|-------|------|----------|
| `diceChance` | float | Probabilidad base antes de affinity (0–1) |

## Ciclo de Vida Completo (S137+)

1. **Corral vacío:** espera ocupantes adultos
2. **Pairing:** automático si 2+ adultos + affinity roll
3. **StartBreeding:** padres marcan BusyState=Breeding, timer inicia
4. **TryHatch (al tapear E):** si ready, hijo nace Form=Egg
5. **Hijo a incubadora:** incubadora lo hatcha a Form=Slime
6. **Slime crece:** expedición → Adult
7. **Adult de vuelta al corral:** puede reproducirse

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/04 - Breeding System]]

**Conexiones:** [[MoriMochiContainer]], [[BreedingController]], [[IncubationService]], [[GameClock]], [[GameEvents]], [[MoriMochiAgent]]
