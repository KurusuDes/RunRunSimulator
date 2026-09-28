---
tags: [script, ui, presenter]
---

# BreedingBreedTabPresenter.cs

**Ruta:** `UI/BreedingBreedTabPresenter.cs`

**Responsabilidad:** Presenter UITK para tab "Criar" (seleccionar padre+madre, preview, iniciar breed). Implementa `ITabPresenter`. Flujo: entrada a tab → foco en slots → seleccionar padre → seleccionar madre → TryBreed() → transición a tab Huevos. **S131:** Cría síncrona; borrados `Busy` y async/await. **S135:** Sin cambios sustanciales en estructura; mantiene compatibilidad con BodyPart modular.

## Subestados (SubFocus enum)

| Estado | Descripción |
|--------|-------------|
| `Slots` | Navegación entre padre/madre/criar button (3 slots) |
| `FatherList` | ScrollView de padres seleccionables |
| `MotherList` | ScrollView de madres seleccionables |

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `getRegistry` | `Func<CreatureRegistrySO>` | Acceso dinámico a registry |
| `database` | `CreatureDatabaseSO` | Acceso a partes para preview |
| `incubation` | `IncubationService` | Servicio de incubación |
| `onBred` | `Action` | Callback al completar cría |
| `selectedFatherId` / `selectedMotherId` | `string` | IDs seleccionados |
| `fatherCards` / `motherCards` | `List<VisualElement>` | Tarjetas renderizadas |
| `criarIndex` / `fatherIndex` / `motherIndex` | `int` | Índice de navegación por subestado |
| `focus` | `SubFocus` | Subestado actual |

## Métodos ITabPresenter

| Método | Descripción |
|--------|-------------|
| `Enter()` | Al entrar tab: reset foco a Slots, índice 0 |
| `Navigate(h, v)` | Manejo de input: mueve cursor en subestado actual |
| `Submit()` | Acción Enter: abre listas o confirma selección |

## Flujo de Cría (S131)

```
1. Usuario en Tab 0 selecciona padre (índice criarIndex=0) → abre FatherList
2. Selecciona padre → selectedFatherId = ID
3. Regresa a Slots, mueve a madres (índice criarIndex=1) → abre MotherList
4. Selecciona madre → selectedMotherId = ID
5. Regresa a Slots, mueve a criar button (índice criarIndex=2)
6. Submit → TryBreed()
   - BreedingController.StartBreeding(selectedMotherId, selectedFatherId) [síncrono]
   - Si ok: UIManager.Toast + transición a Tab 1 (Huevos)
   - Si error: UIManager.Toast("Error") + permanece en Tab 0
```

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `Enter()` | Reset estado: focus=SubFocus.Slots, criarIndex=0 |
| `Navigate(h, v)` | Maneja navegación según `focus` (slots/listas) |
| `Submit()` | Dispara acción según `focus` |
| `OpenList(SubFocus which)` | Cambia focus a lista padre/madre |
| `SelectFather(id)` | Asigna selectedFatherId, redibuja preview |
| `SelectMother(id)` | Asigna selectedMotherId, redibuja preview |
| `TryBreed()` | Valida selecciones + BreedingController.StartBreeding() |
| `ApplyCriarFocus()` / `ClearCriarFocus()` | Manejo visual de focus |
| `MoveList()` | Navegación dentro de ScrollView |

## Integración

- Instanciado en `BreedingPanelUITK` (host del UITK document)
- Inyecta `IncubationService` para verificación de estado de huevo
- Consumidor de `CreatureRegistrySO` (padre/madre disponibles)
- Transición a tab "Huevos" via `onBred` callback

## Cambios S131

**Cría síncrona:** TryBreed() ya no es async; BreedingController.StartBreeding() retorna bool inmediatamente.

**Removidos:** 
- `public bool Busy` property
- `private void SetBreedBusy(bool)` method
- `private async Task TryBreedAsync()` method

**Nuevo:**
- `private void TryBreed()` — síncrono, retorna bool de BreedingController

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/09 - Active Context]]

## Conexiones

[[ITabPresenter]], [[BreedingPanelUITK]], [[BreedingController]], [[IncubationService]], [[CreatureRegistrySO]], [[CreatureDatabaseSO]]
