---
tags: [script, genetics, breeding, world-container]
---

# BreedingContainer

**Ruta:** `World/Containers/BreedingContainer.cs`

**Responsabilidad:** Corral de cría (hereda de MoriMochiContainer). Pairing automático con affinity×diceChance, restaura pasivamente necesidades. Gestiona visuals (courtship poses). S131: Cría síncrona vía `BreedingController.StartBreeding/TryHatch/CancelBreeding`. S137: Solo acepta adultos (excluye Eggs y Slimes que no son reproducibles).

## Interacción (IInteractable)

**Tap E:**
1. Detecta si hay criaturas criando (BusyReason.Breeding)
2. Si huevo listo: `BreedingController.TryHatch(motherID, fatherID)` → procesa HatchResult
   - Hatched: anima eclosión, asigna Form=Egg al huevo, dispara CreatureFormChanged
   - NotReady: toast "Aún falta tiempo"
   - InsufficientMinerita: toast "Insuficiente Minerita"
   - Invalid: toast "Error"
3. Si huevo no listo: muestra timer restante

## Métodos S137 (Ciclo de Vida)

### Accepts() — S137 MODIFICADO

```csharp
protected override bool Accepts(MoriMochiAgent agent) =>
    agent != null && agent.DNA != null && agent.DNA.Form == MonchiForm.Adult;
```

Cambio: Ahora excluye Eggs (incubable, no vivo) y Slimes (explorador, no reproduce). Solo adultos pueden reproducirse.

## Métodos S131 (Cría Síncrona)

| Método | Descripción |
|--------|-------------|
| `BreedingController.StartBreeding(motherID, fatherID)` | Inicia cría local (marca BusyState, deduce energía, fija BreedReadyAt) |
| `BreedingController.TryHatch(motherID, fatherID)` | Hatcha si ready (retorna HatchResult); asigna Form=Egg al hijo |
| `BreedingController.CancelBreeding(motherID, fatherID)` | Cancela cría (limpia BusyState) |

## IsAdult (S131)

```csharp
private bool IsAdult(CreatureDNA dna)
{
    if (dna == null) return false;
    int today = GameClock.Instance != null ? GameClock.Instance.Day : 1;
    int ageDays = dna.AgeDays(today);
    
    // Threshold: ejemplo 7 días = adulto
    return ageDays >= AdultAgeThresholdDays;  // default 7
}
```

**Propósito:** Determinar elegibilidad de cría por edad (no solo rol). Nota: este IsAdult es por edad del juego, NO por MonchiForm.Adult. Luego se agregó check de Form (S137).

## TryRollPair (S131 + S137)

Cambios:
- Usa `BreedingController.Instance.GetAffinity(mother.Role, father.Role)` (S39)
- Agregó check: `IsAdult(mother) && IsAdult(father)` (edad en días)
- S137: también valida `mother.Form == MonchiForm.Adult && father.Form == MonchiForm.Adult`

```csharp
if (!IsAdult(mother) || !IsAdult(father)) return false;  // S131: edad
if (mother.Form != MonchiForm.Adult || father.Form != MonchiForm.Adult) return false;  // S137: solo adultos
float affinity = BreedingController.Instance?.GetAffinity(mother.Role, father.Role) ?? 0.5f;
float pairChance = affinity * diceChance;
```

## Campos Serializados (S131)

| Campo | Tipo | Propósito |
|-------|------|----------|
| `adultAgeThresholdDays` | int | Edad mínima para reproducción (default 7) |

## Ciclo de Vida S137

1. Corral acepta solo adultos (Eggs/Slimes no entran)
2. Pairing automático entre adultos (affinity × diceChance)
3. StartBreeding: marca padres Breeding, deduce energía, fija timer
4. TryHatch: cuando timer listo, hatcha vía BreedingService.Breed
5. Huevo nuevo: Form=Egg, Explorations=0, listo para incubadora

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/09 - Active Context]] (S137: ciclo de vida)

## Conexiones

**Sistemas:**
- [[BreedingController]] — API de cría síncrona
- [[IncubationService]] — orquestador (vía BreedingController)
- [[GameClock]] — proporciona Day para AgeDays
- [[GameEvents]] — reacciona a RegistryChanged

## Notas (S137 HC-4 + Ciclo de Vida)

- **Cría síncrona:** StartBreeding ejecuta localmente (sin await). TryHatch retorna HatchResult enum.
- **Edad adulta:** AgeDays(today) compara BirthDay contra Day actual (simple resta clamped).
- **Form filter:** Aceptación ahora valida Form == Adult, no solo edad
- **HatchResult handling:** switch(result) en Interact para animaciones/toasts.
- **Pairing:** Solo adultos pueden emparejar; afinidad por Role (S39).
- **Huevos recién puestos:** Form=Egg, necesitan incubadora para eclosionar
