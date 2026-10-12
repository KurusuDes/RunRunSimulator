---
tags: [script, genetics, breeding, container]
---

# BreedingContainer.cs

**Ruta:** `World/Containers/BreedingContainer.cs`

**Responsabilidad:** Corral de cría (hereda `MoriMochiContainer`). Solo acepta adultos (Form=Adult). Tira parejas automáticamente cada `rollInterval` según afinidad × dado. Al formar pareja asigna un slot fijo de cría, pasa la lista de decoraciones a `BreedingController.StartBreeding` y pone en cortejo a la pareja. Restaura necesidades a los ocupantes. Al eclosionar la cría, la lanza fuera del corral. Sirve la interacción de eclosión (`TryHatch`).

## Accepts() — Ciclo de Vida

```csharp
protected override bool Accepts(MoriMochiAgent agent) => agent.DNA != null && agent.DNA.Form == MonchiForm.Adult;
```

**Solo adultos:** excluye Eggs (incubables) y Slimes (exploradores jóvenes).

## Campos Serializados

| Campo | Tipo | Default | Propósito |
|-------|------|---------|----------|
| `diceChance` | float (0-1) | 0.5 | Dado de pareja; se multiplica por la afinidad |
| `rollInterval` | float (Min 1) | 10 s | Cada cuánto se intenta una pareja |
| `pairCooldown` | float (Min 0) | 60 s | Cooldown de un adulto tras formar pareja |
| `restoreRate` | float (Min 0) | 5 | Salud, energía y afecto por segundo para cada ocupante |
| `breedingSlots` | `BreedingSlot[]` | — | **(S149)** Un slot por pareja con `spotA` y `spotB` (anclas hijas) |
| `launchHeight` | float (Min 0) | 1.5 | Altura desde la que se lanza la cría |
| `birthEjectDistance` | float (Min 0) | 2 | Distancia fuera del borde del corral donde cae la cría |
| `onPairFormed` | `UnityEvent` | — | Feedback al formar pareja |

## Ciclo de Pareja (TryRollPair)

1. Necesita al menos 2 ocupantes y `BreedingController` en escena.
2. Filtra hembras y machos disponibles (vivos, no ocupados, adultos, `BreedCount < MaxBreedCount`, sin cooldown).
3. Elige una hembra y un macho al azar.
4. `chance = GetAffinity(mother.Role, father.Role) × diceChance`. Si el dado no alcanza, reporta y termina.
5. Llama `controller.StartBreeding(mother.UniqueID, father.UniqueID, DecorIds())` **(S149)**.
6. Si arrancó, asigna `LocationKey` y `LocationSlot` (primer slot libre, `FindFreeSlot`) a ambos, pone cooldown y dispara `RegistryChanged`.

## Cortejo (ManageCourtship)

Cada frame busca pares de ocupantes con `BusyState == Breeding` y `BreedPartnerID` recíproco. Pone a la hembra y al macho en `EnterCourtship` apuntando al centro del slot (`ResolveCourtAnchor`: promedio de `spotA` y `spotB`). Los ocupantes que dejan de formar pareja salen del cortejo.

## Decoraciones (S149)

- `decorSlots` se toma de los hijos (`DecorSlot`).
- `DecorIds()` devuelve los IDs de decoración colocados. Se pasan a la cría en curso.

## Eclosión (Interact)

Busca una hembra con `BusyState == Breeding` y `BreedReadyAt > 0`, y llama `BreedingController.TryHatch(mother, partner)`. Según el resultado:
- `Hatched`: mensaje de éxito.
- `NotReady`: muestra las horas de juego que faltan.
- `InsufficientMinerita`: muestra el costo de `HatchCostFor`.
- Otro: error genérico.

## Nacimiento (OnBreedingCompleted)

Al completarse la cría (`GameEvents.OnBreedingCompleted`), si los padres están en este corral, registra el lanzamiento de la cría con `MoriMochiSpawner.Instance.RegisterBirthLaunch(child.UniqueID, LaunchPoint, BirthLanding())` y saca a los padres del cortejo. `BirthLanding()` cae fuera del borde (`birthEjectDistance`).

## Restauración (PassiveRestore)

Cada frame suma `restoreRate * dt` a salud, energía y afecto de cada ocupante vivo.

## Release y cancelación

Al retirar un agente (`Release`), si estaba en cría, `CancelBreeding` limpia el estado de cría, la ubicación y el de la pareja, y llama `BreedingController.CancelBreeding`.

## Diagnóstico

`PairDiagnostics` (solo en Play) muestra por ocupante por qué está disponible o no: muerto, incubando, ocupado, máx. crías, no adulto, cooldown o disponible.

## Registro estático

`All` lista los corrales de cría activos (`Start` agrega, `OnDestroy` quita).

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/04 - Breeding System]]

## Conexiones

**Padre:** [[MoriMochiContainer]]

**Sistemas:**
- [[BreedingController]] — `StartBreeding`, `TryHatch`, `CancelBreeding`, `GetAffinity`, `Incubation`
- [[IncubationService]] — `HatchCostFor`
- [[MoriMochiSpawner]] — `RegisterBirthLaunch`
- [[DecorSlot]] — decoraciones (S149)
- [[GameClock]], [[GameEvents]] (`OnBreedingCompleted`, `RegistryChanged`)
- [[MoriMochiAgent]] — `EnterCourtship`, `ExitCourtship`, `DNA`
- [[CreatureDNA]], [[BreedingService]] (`MaxBreedCount`)
