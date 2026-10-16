---
tags: [script, ui, uitk]
---

# CreatureGridUITK.cs

**Ruta:** `UI/CreatureGridUITK.cs`

**Responsabilidad:** Libro de MoriMonchis (UITK). Grilla de retratos de las criaturas del registry, con filtros, y a la derecha una vitrina en vivo y una ficha resumida del seleccionado. La ficha reusa `DetailInfoTabPresenter`. Ordena por `BirthDate` descendente. Bindea nombre, estado (viva/muerta/ocupada), retrato, necesidades (3 barras) y marca de apta para bajar. Muestra solo genética, necesidades y estado de vida (sin stats ni equipo desde S129).

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento del libro |
| `panel` | `UIPanelType` | Default `CreatureGrid` |
| `database` | `CreatureDatabaseSO` | Partes para resolver la vista |
| `careGate` | `CareGateSO` | Criterio de aptitud (`CreatureAvailability`) |
| `kits` | `BrawlKitDatabaseSO` | Kits de combate para la ficha |
| `evolution` | `EvolutionEffectSO` | Efecto de evolución de la vitrina |

## Estado Privado

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `scroll` | `ScrollView` | Grilla de tiles |
| `portrait` | `VisualElement` | Vitrina en vivo del seleccionado |
| `presenter` | `DetailInfoTabPresenter` | Ficha resumida |
| `tiles`, `filterButtons` | `List` | Elementos renderizados |
| `currentRegistry` | `CreatureRegistrySO` | Registry en uso |
| `filter` | `GridFilter` | Filtro activo (`All` y filtros por forma) |
| `selectedIndex` | `int` | Índice seleccionado |
| `wired` | `bool` | Elementos ya enlazados |

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `Wire()` | Resuelve elementos del UXML, crea la ficha y los filtros |
| `BuildFilters` / `AddFilter` / `RefreshFilterButtons` / `SetFilter` | Filtros por forma (`GridFilter`) |
| `Passes(dna)` | Aplica el filtro activo a cada criatura |
| `Rebuild(registry)` | Reconstruye las tiles |
| `Select(idx, scrollIntoView)` / `ShowSelected(dna)` | Selección y actualización de vitrina y ficha |
| `OnPanelVisibility(type, visible)` | Enlaza o libera al abrir o cerrar el panel |
| `OpenSelected()` / `OnCloseClicked()` | Acciones de abrir el seleccionado y cerrar el panel |
| `OnUINavigate(dir)` / `OnUISubmit()` / `OnUICancel()` | Navegación por `IUINavigable` |

## Eventos y Conexiones

- `UIManager` (visibilidad de panel, `RequestPanelToggle`), navegación `IUINavigable`.
- [[CreatureRegistrySO]], [[CreatureDisplay]], [[NeedsDisplay]], [[CreatureAvailability]], [[UiPanels]], [[MonchiPortraitUI]], [[GameEvents]]
- [[DetailInfoTabPresenter]] (S161) — ficha resumida
- [[EvolutionEffectSO]] (S161) — efecto de evolución
- [[BrawlKitDatabaseSO]] (S161) — kits para la ficha

## Cambios S161

- Overhaul del libro: grilla de retratos + vitrina en vivo + ficha resumida, con el kit de Synty.
- Filtros por forma (`GridFilter`).
- Reusa `DetailInfoTabPresenter` en lugar de la ficha propia anterior.

## Cambios en S129

- **ELIMINADO:** columnas de stats (Constitution, Attack, Speed, etc.) y slots de equipo.
- **AGREGADO:** 3 barras de necesidades con colores y badge ✓ si apta para explorar.

## Vinculado a

[[Index/05 - UI System]]
[[Index/28 - Cimientos y camino a Game Ready]]
