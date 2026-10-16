---
tags: [script, ui, breeding, inheritance, static]
---

# BreedingInheritanceView.cs

**Ruta:** `UI/BreedingInheritanceView.cs`

**Responsabilidad:** Vista estática de herencia de la Crianza. Llena una lista con una fila por parte (cuerno, espalda, alas, cara, cuerpo) mostrando, para el padre y la madre, la pieza que aporta cada uno con su color de set. Si ambos aportan el mismo set, marca la celda como "igual". No muestra porcentajes (decisión pendiente de Juan, S162). Solo construye `VisualElement`; no guarda estado (S161).

**Vinculado a:** [[Index/02 - Genetics & Breeding]], [[Index/05 - UI System]]

## Método Público

| Método | Descripción |
|--------|-------------|
| `Build(VisualElement list, CreatureDatabaseSO database, CreatureDNA father, CreatureDNA mother)` | Limpia `list` y agrega una fila por rol en el orden Horn, Back, Wing, Face, Body |

## Estructura de Fila

- Caja `mm-statbox` con ícono `inherit-icon--{rol}`.
- Nombre del rol con `Loc` (`ui.detail.slot.{rol}`).
- Dos celdas `inherit-cell` (padre y madre): swatch con el color del `Set` de la parte (gris si no tiene set; oculto si no hay parte) y texto con el nombre de la parte (`DataLoc.PartName`, S162), o "—" si no hay progenitor o parte.
- Clase `inherit-cell--same` en ambas celdas cuando las dos partes pertenecen al mismo set.

## Resolución de Partes (`PartOf`)

Usa `CreatureDatabaseSO` según el rol: `GetHorn`, `GetBack`, `GetWing`, `GetFace`, `GetBodyShape` (cuerpo), con los IDs de `CreatureDNA`. Null si falta la base de datos o el DNA.

## Conexiones

- [[BreedingBreedTabPresenter]] — único consumidor (`Build` con padre y madre seleccionados)
- [[CreatureDatabaseSO]] — resolución de partes
- [[CreatureDNA]] — IDs de partes
- [[BodyPart]], [[PartRole]] — parte y rol
- [[Loc]] — nombres de rol
- [[DataLoc]] — nombre localizado de cada parte (S162)

## Notas

- Clase estática sin estado ni eventos.
- Los estilos viven en el kit `Skin.uss` (`inherit-row`, `inherit-cell`).
- S162: los nombres de parte salen de `DataLoc`, no del asset crudo.
