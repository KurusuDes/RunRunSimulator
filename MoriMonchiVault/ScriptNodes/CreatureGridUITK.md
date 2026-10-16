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
| `sideName`, `countLabel`, `emptyLabel` | `Label` | Nombre del seleccionado, conteo y aviso de libro vacío |
| `openButton`, `closeButton` | `Button` | Abrir el seleccionado y cerrar el panel |
| `tiles`, `filterButtons` | `List` | Elementos renderizados |
| `currentRegistry` | `CreatureRegistrySO` | Registry en uso |
| `filter` | `GridFilter` | Filtro activo: `All`, `Adult`, `Slime`, `Egg` (por `MonchiForm`) |
| `selectedIndex` | `int` | Índice seleccionado |
| `wired` | `bool` | Elementos ya enlazados |

Constantes: `Columns = 5`, `MinRows = 5` (la grilla siempre rellena hasta 5 filas con tiles vacíos).

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `Wire()` | Resuelve elementos del UXML, enlaza botones, traduce etiquetas, crea los filtros y la ficha `DetailInfoTabPresenter` |
| `BuildFilters` / `AddFilter` / `RefreshFilterButtons` / `SetFilter` | Filtros por forma (`GridFilter`); cambiar filtro limpia la selección y reconstruye |
| `Passes(dna)` | Aplica el filtro activo a cada criatura |
| `Rebuild(registry)` | Reconstruye las tiles ordenadas por `BirthDate` desc., rellena hasta `MinRows`, actualiza conteo y aviso vacío |
| `BuildTile(dna)` / `BuildEmptyTile()` | Tile con retrato (`MonchiPortraitUI.Apply`), punto de estado (listo/bloqueado según `CreatureAvailability.CanExplore`) y marco; click selecciona, doble click abre |
| `Select(idx, scrollIntoView)` | Clampa el índice, marca la tile activa, hace scroll y llama `ShowSelected` |
| `ShowSelected(dna)` | Actualiza nombre, ficha (`presenter.Rebuild`) y vitrina en vivo (`MonchiPortraitUI.ApplyLive`) si el panel es visible |
| `OnPanelVisibility(type, visible)` | Al abrir el panel refresca la vitrina del seleccionado |
| `OnUINavigate(dir)` / `OnUISubmit()` / `OnUICancel()` | Navegación por `IUINavigable` (izq/der ±1, arriba/abajo ±5 columnas); Submit abre; Cancel no consume |
| `OpenSelected()` / `OnCloseClicked()` | Abrir el seleccionado (`UIManager.SelectCreature`) y cerrar el panel (`UIManager.RequestPanelToggle`) |

## Eventos y Conexiones

- Suscribe `GameEvents.OnRegistryChanged` y `GameEvents.OnRegistryReloaded` → `Rebuild` (desuscribe en `OnDisable`)
- Suscribe `UIManager.OnPanelVisibilityChanged` → `OnPanelVisibility`
- Se registra como `IUINavigable` en `UIManager.RegisterNavigable(panel, this)` en `Start`
- [[CreatureRegistrySO]], [[CreatureDisplay]], [[NeedsDisplay]], [[CreatureAvailability]], [[UiPanels]], [[MonchiPortraitUI]], [[GameEvents]]
- [[DetailInfoTabPresenter]] (S161) — ficha resumida
- [[EvolutionEffectSO]] (S161) — efecto de evolución
- [[BrawlKitDatabaseSO]] (S161) — kits para la ficha

## Cambios S161

- Overhaul del libro: grilla de retratos + vitrina en vivo + ficha resumida, con el kit de Synty.
- Filtros por forma (`GridFilter`).
- Reusa `DetailInfoTabPresenter` en lugar de la ficha propia anterior.

## Cambios S162

- Libro de 5 columnas sin scroll sobrante: la grilla rellena hasta `MinRows` con tiles vacíos (`BuildEmptyTile`).
- Conteo y aviso de libro vacío con loc (`ui.grid.count`, `ui.grid.empty`).

## Cambios en S129

- **ELIMINADO:** columnas de stats (Constitution, Attack, Speed, etc.) y slots de equipo.
- **AGREGADO:** 3 barras de necesidades con colores y badge ✓ si apta para explorar.

## Vinculado a

[[Index/05 - UI System]]
[[Index/28 - Cimientos y camino a Game Ready]]
