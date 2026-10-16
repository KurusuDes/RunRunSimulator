---
tags: [script, ui, uitk, detail, breeding, presenter]
---

# DetailInheritancePresenter.cs

**Ruta:** `UI/DetailInheritancePresenter.cs`

**Responsabilidad:** Presenter UITK de la sección "herencia" de la ficha de detalle de un MoriMochi. Por cada `PartOrigin` de `dna.Origins` dibuja una línea: parte, quién la aportó (padre/abuelo/bisabuelo/mutación/azar) y, si aplica, la decoración que la acreditó. Solo lee datos; no persiste.

## Comportamiento

- Oculta título y lista si `Origins` está vacío.
- Texto del ancestro: resuelve `AncestorID` en el `CreatureRegistrySO` (vía `getRegistry`) para tomar el `CustomName`; la clave de localización depende de slot, lado y género del ancestro.
- Decoración: resuelve `DecorID` en `BreedingController.DecorDatabase` y añade "por <nombre>", con el nombre salido de `DataLoc.DecorName` (S162).
- Mutación y Base usan textos fijos.

## Claves de localización (prefijo `ui.detail.`)

`inherit.title`, `inherit.sep`, `inherit.by`, `inherit.mutation`, `inherit.random`, `inherit.parent.{mother|father}`, `inherit.{grand|great}.{m|f}.{mother|father}`, `slot.{role}`.

## Conexiones

- [[PartOrigin]] — datos por línea
- [[CreatureDNA]] — `Origins`, `Gender`, `CustomName`
- [[CreatureRegistrySO]] — resuelve ancestros
- [[BreedingController]] — `DecorDatabase`
- [[BreedingDecorSO]] — nombre de la decoración (vía `DataLoc.DecorName`)
- [[DataLoc]] — nombre localizado de decoraciones (S162)
- [[MorimonchiDetailInfoUITK]] — es quien la construye y le pasa el `root`

## Estado

- MODIFICADO en S162: el nombre de la decoración pasa por `DataLoc.DecorName` (loc de datos). Sin cambio de contrato.
