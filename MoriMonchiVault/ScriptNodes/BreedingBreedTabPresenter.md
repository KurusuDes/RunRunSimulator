---
tags: [script, ui, presenter]
---

# BreedingBreedTabPresenter.cs

**Ruta:** `UI/BreedingBreedTabPresenter.cs`

**Responsabilidad:** Presenter UITK para el tab "Criar" de la Crianza (`ITabPresenter`). Elige padre y madre desde una grilla filtrada por sexo, muestra la herencia por parte con `BreedingInheritanceView` y dispara la cría síncrona. Al criar con éxito avisa con `onBred`. Flujo: entrar al tab → foco en la grilla → elegir padre → elegir madre → botón Criar → `TryBreed()`.

**Vinculado a:** [[Index/02 - Genetics & Breeding]], [[Index/09 - Active Context]]

## Estado Privado

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `getRegistry` | `Func<CreatureRegistrySO>` | Acceso dinámico al registry |
| `database` | `CreatureDatabaseSO` | Partes para la vista de herencia |
| `incubation` | `IncubationService` | Verificación de estado de huevo |
| `onBred` | `Action` | Callback al completar la cría |
| `grid` | `ScrollView` | Grilla de candidatos |
| `tiles` | `List<VisualElement>` | Tiles renderizadas |
| `selectedFatherId` / `selectedMotherId` | `string` | IDs seleccionados |
| `filter` | `CreatureGender` | Sexo mostrado (Male = padres, Female = madres). Default Male |
| `gridIndex` | `int` | Cursor en la grilla |
| `focus` | `SubFocus` | Subestado actual. Default `Grid` |

## Métodos ITabPresenter y Públicos

| Método | Descripción |
|--------|-------------|
| `Enter()` | Al entrar al tab, vuelve al foco de la grilla |
| `Navigate(h, v)` | Mueve el cursor según el subestado actual |
| `Submit()` | Asigna el candidato del cursor o dispara la cría |
| `Cancel()` | Deshace el subestado actual; devuelve si consumió la acción |
| `ClearFocus()` | Quita el resaltado de foco |
| `Rebuild()` | Reconstruye la grilla y los slots desde el registry |
| `Teardown()` | Libera suscripciones y referencias del tab |

## Métodos Privados Clave

| Método | Descripción |
|--------|-------------|
| `OnFilterFathers` / `OnFilterMothers` / `ChangeFilter(gender)` | Cambia el sexo mostrado y reconstruye la grilla |
| `RebuildGrid()` | Arma las tiles del sexo filtrado |
| `RefreshSlots()` | Actualiza los slots de padre y madre y llama a `BreedingInheritanceView.Build` |
| `Assign(id)` | Asigna el candidato al slot que corresponde al filtro |
| `TryBreed()` | Valida selección y llama `BreedingController.StartBreeding()` (síncrono, retorna bool) |
| `ApplyFocus()` / `ApplyFocusIfActive()` | Pinta el foco visual |

## Flujo de Cría

```
1. Tab Criar: la grilla muestra padres (filtro Male) por defecto
2. Elegir padre → selectedFatherId; RefreshSlots muestra herencia
3. Cambiar filtro a madres → elegir madre → selectedMotherId
4. Criar → TryBreed()
   - BreedingController.StartBreeding(selectedMotherId, selectedFatherId) [síncrono]
   - Si ok: UIManager.Toast + onBred (transición al tab Huevos)
   - Si error: UIManager.Toast("Error") + permanece en el tab
```

## Conexiones

- [[ITabPresenter]], [[BreedingPanelUITK]] (host), [[BreedingController]], [[IncubationService]]
- [[CreatureRegistrySO]], [[CreatureDatabaseSO]], [[CreatureDNA]]
- [[BreedingInheritanceView]] (S161) — vista de herencia por parte

## Cambios S161

- La vista de herencia sale de `BreedingInheritanceView` (fila por parte con color de set, sin porcentajes).
- La grilla se filtra por sexo con el selector de padres/madres; el tab "Criar" se rehizo como composición de crafteo.
- Pendiente de Juan: mostrar % de herencia (S162).

## Cambios S131

**Cría síncrona:** `TryBreed()` ya no es async; `BreedingController.StartBreeding()` retorna bool inmediatamente. Se removieron `Busy`, `SetBreedBusy` y `TryBreedAsync`.

## Notas

- `BreedingPanelUITK` es el host del documento; este presenter no abre ni cierra el panel.
