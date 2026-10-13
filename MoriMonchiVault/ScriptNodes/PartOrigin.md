---
tags: [script, data, breeding, genetics, serializable]
---

# PartOrigin.cs

**Ruta:** `Data/Breeding/PartOrigin.cs`

**Responsabilidad:** Dato serializable que registra de dónde vino cada parte de un MoriMochi (procedencia genética). Sin lógica. Lo llena la crianza y lo lee la UI de detalle para mostrar la línea de herencia.

## Campos publicos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `Role` | `PartRole` | Parte afectada (cuerno, espalda, ala, cara, etc.) |
| `Slot` | `InheritanceOddsTableSO.Slot` | Origen: Parent, Grandparent, GreatGrandparent, Mutation o Base |
| `MotherSide` | `bool` | `true` si el origen es materno |
| `AncestorID` | `string` | ID del ancestro (vacío si no aplica, p.ej. Mutation/Base) |
| `DecorID` | `string` | ID de la decoración que acredita el origen (vacío si ninguna) |

## Conexiones

- [[CreatureDNA]] — `Origins` (lista de `PartOrigin`)
- [[BreedingAttribution]] — calcula `DecorID`
- [[InheritanceOddsTableSO]] — tipo `Slot`
- [[DetailInheritancePresenter]] — muestra la línea de herencia
