---
tags: [script, genetics]
---

# BreedingService

**Ruta:** `Systems/Breeding/BreedingService.cs`

**Responsabilidad:** Lógica local de cruce. Hereda 5 partes genéticas (BodyShape/Horn/Back/Wing/Face) desde árbol genealógico, colores, FurType, género, rol, elemento, IsShiny, diales (Sociability/Boldness) y potenciales de partes. Valida género, muerte, busy state, `MaxBreedCount = 4`. Retorna hijo `CreatureDNA` o null si falla validación. **S129:** Eliminada herencia de stats base. **S149:** El cruce acepta decoraciones de cría que alteran los pesos de herencia (vía `BreedingOdds.From`), y las partes de reserva se tiran con `PartPool.Rollable`. **S151:** el cruce recibe las decoraciones como `BreedingDecorSO` (ya no `BreedingModifier`), registra la procedencia de cada parte en `CreatureDNA.Origins` (`PartOrigin`) y acredita la decoración con `BreedingAttribution`.

## Método Principal

```csharp
public static CreatureDNA Breed(
    string                 motherID,
    string                 fatherID,
    CreatureRegistrySO     registry,
    CreatureDatabaseSO     partDb,
    InheritanceOddsTableSO odds,
    IReadOnlyList<BreedingDecorSO> decors = null)   // S151: antes IEnumerable<BreedingModifier>
```

**Validaciones:**
1. Ambos padres existen en registry
2. Ambos vivos (not IsDead)
3. Ninguno ocupado (not IsBusy)
4. Madre Female, padre Male
5. Ambos < MaxBreedCount (4)

**Retorna:** CreatureDNA hijo o null si falla.

**Efecto secundario:** incrementa `BreedCount` de madre y padre al generar el hijo.

## Algoritmo de Herencia

### Odds efectivos (S149)

Antes de tirar, las decoraciones se aplanan en `BreedingModifier` (`decor.Modifiers`) y `BreedingOdds.From(odds, modifiers)` construye los pesos efectivos. Los modificadores suman deltas a los pesos base de `InheritanceOddsTableSO`, con mínimo 0.

### Partes Genéticas (5 slots)

Cada slot llama `ResolveSlot(PartRole role, ...)`: tira el origen con `effective.Roll()` y devuelve el ID de la parte. Además agrega un `PartOrigin` a la lista del hijo (S151) con: slot de origen, lado materno, ID del ancestro y `DecorID` (resultado de `BreedingAttribution.CreditFor`). Los valores de referencia (sin modificadores) son:
- **Parent (40%):** Una parte del padre elegido al azar (lado materno o paterno según `PickMotherSide`)
- **Grandparent (20%):** Una parte de un abuelo (dos generaciones de ancestros vía `ExpandGenerations`)
- **GreatGrandparent (10%):** Una parte de bisabuelo
- **Mutation (20%):** Parte aleatoria del pool (`RandomPartID`, filtrada con `PartPool.Rollable`)
- **Base (10%):** Fallback si no hay ancestros; también usa `RandomPartID`

Si el lado elegido no tiene candidatos, se usa el otro lado.

**Slots:**
```
BodyShapeID, HornID, BackID, WingID, FaceID
```

### Otros Campos

- **Colores:** `ColorGenetics.Inherit` de madre y padre + SecondaryColor derivado
- **Género:** 50/50
- **Role:** 50/50 de padres
- **Element:** mutación con `odds.ElementMutationChance`; si no, 50/50 de padres
- **IsShiny:** Roll nuevo `ColorGenetics.RollShiny()`
- **FurType:** `ColorGenetics.Inherit` de madre y padre
- **Generation:** máximo de padres + 1
- **Potenciales de partes:** `InheritPotential` promedio de padres + ruido, clamp `PotentialMin`-`PotentialMax` (1-10)
- **Diales:** `odds.RollDial()` elige entre promedio con jitter (`DialJitter`), copia de un padre, o diales nuevos (`CreatureGenerator.RandomDial`)

## Cambios S151

- Firma: `decors` es `IReadOnlyList<BreedingDecorSO>`; el método aplana sus `Modifiers`.
- `CreatureDNA.Origins` se llena con un `PartOrigin` por slot (5 entradas).
- `DecorID` por parte se calcula con [[BreedingAttribution]].

## Cambios S129

- **ELIMINADO:** Herencia de stats base (Constitution, Attack, Speed, Defense, Luck, Evasion)
- **MANTIENE:** 5 partes genéticas, potenciales, diales

## Cambios S149

- Parámetro de decoraciones (opcional) para decoraciones de cría.
- `Breed` usa `BreedingOdds` en lugar de leer la tabla directamente.
- Partes de reserva (Mutation/Base) filtradas con `PartPool.Rollable`.

## Vinculado a

[[Index/02 - Genetics & Breeding]]
[[Index/28 - Cimientos y camino a Game Ready]]

**Conexiones:** [[CreatureDNA]], [[PartOrigin]] (S151), [[BreedingAttribution]] (S151), [[InheritanceOddsTableSO]], [[BreedingOdds]], [[BreedingModifier]], [[BreedingDecorSO]], [[CreatureRegistrySO]], [[CreatureDatabaseSO]], [[ColorGenetics]], [[CreatureGenerator]], [[PartPool]], [[IncubationService]], [[BreedingController]]
