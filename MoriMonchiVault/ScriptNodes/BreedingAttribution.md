---
tags: [script, data, breeding, decor, static]
---

# BreedingAttribution.cs

**Ruta:** `Data/Breeding/BreedingAttribution.cs`

**Responsabilidad:** Atribución de herencia: dado el slot de origen de una parte (padre, abuelo, bisabuelo, mutación, base) y el lado materno/paterno, decide qué decoración de crianza (`BreedingDecorSO`) "se lleva el crédito" de ese origen. Static, sin estado. Es el dato que alimenta `PartOrigin.DecorID`.

## Regla de atribución

1. Si alguna decoración tiene un modificador con `Delta > 0` sobre el stat del slot (`ParentWeight`, `GrandparentWeight`, `GreatGrandparentWeight`, `MutationWeight`, `BaseWeight`), esa decoración (la primera en la lista) es la que acredita.
2. Si no, y el slot es ancestral (Parent / Grandparent / GreatGrandparent), se busca un boost de sesgo (`MotherBias` o `FatherBias`) según el lado.
3. Si nada coincide, devuelve `""`.

## Metodos publicos

| Metodo | Retorno | Descripcion |
|--------|---------|-------------|
| `CreditFor(Slot slot, bool motherSide, IReadOnlyList<BreedingDecorSO> decors)` | `string` (ID de decoración o `""`) | Aplica la regla de arriba |

## Conexiones

- [[InheritanceOddsTableSO]] — define `Slot`
- [[BreedingDecorSO]] — `Modifiers`, `Id`
- [[PartOrigin]] — consume el resultado como `DecorID`
- [[BreedingService]] — arma los orígenes al nacer una criatura (vía `PartOrigin`)
