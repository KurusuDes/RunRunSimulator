---
tags: [script, ui, uitk]
---

# MorimonchiDetailInfoUITK.cs

**Ruta:** `UI/MorimonchiDetailInfoUITK.cs`

**Responsabilidad:** Panel de detalles UITK de MoriMochi. Pestañas: Info (partes con el poder de su kit, necesidades, ✓ apta para bajar y rol de combate sugerido), Crianza, Linaje (árboles genealógicos) y Relaciones. **S75:** Sin tab Combate (demolición). **S93:** Usa `UiPanels.RootOf()`. **S129:** Eliminada pestaña Equipo (demolición HC-1). Muestra: partes genéticas, 3 barras de necesidades (color según `NeedsDisplay`), marca ✓ si apta para explorar (green badge), rol/elemento/gender. **S145:** la pestaña Info recibe el `BrawlKitDatabaseSO` para mostrar poderes y rol sugerido.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del panel (`UiPanels.RootOf`) |
| `panel` | `UIPanelType` | `MorimonchiDetail` | Clave de registro en `UIManager` |
| `database` | `CreatureDatabaseSO` | — | Resuelve nombres, sets y rareza de partes |
| `careGate` | `CareGateSO` | — | Umbral de la marca de apta |
| `kits` | `BrawlKitDatabaseSO` | — | Kits de combate: poderes y rol sugerido (S145) |
| `sortingOrder` | `int` | 100 | Orden de dibujo; el modal queda sobre la grilla |

## Tabs (según `WireStaticLabels`)

- **Info** (`tab-info`) — Partes con poder de kit, necesidades (3 barras con color), ✓ apta, rol de combate sugerido, demografía (rol/elemento/género).
- **Crianza** (`tab-breed`) — placeholder `breed-empty`.
- **Linaje** (`tab-lineage`) — árboles genealógicos; placeholder `lineage-empty`.
- **Relaciones** (`tab-relations`) — amigos y enemigos; placeholder `relations-empty`.

## Flujo

- **Awake:** aplica `sortingOrder` al documento.
- **OnEnable / OnDisable:** suscribe y desuscribe `UIManager.OnCreatureSelected` (→ `Show`) y `GameEvents.OnRegistryChanged`.
- **Start:** `Wire()` y registro navegable.
- **Wire():** busca `title`, `portrait`, `tabs`, `close-button`; aplica `WireStaticLabels`; crea los presenters: `DetailInfoTabPresenter(root, database, careGate, kits)`, `DetailTreesPresenter(root, database, () => registry)` y `DetailRelationsPresenter(root, () => registry)`.
- **Show(dna, registry):** guarda registry y `current`, `Wire`, `Populate`, selecciona el tab 0 y `RequestPanelSet(panel, true)`.
- **Populate(dna):** título (`CustomName` o `ToStringID`), retrato con `MonchiPortraitUI.ApplyLive`, `info.Rebuild`, `trees.Rebuild`, `relations.Rebuild`.
- **OnRegistryChanged:** si el panel está visible, repuebla `current`.
- **OnUINavigate:** cambia de tab con el eje x. `OnUISubmit` no hace nada. `OnUICancel` devuelve false.

## Cambios en S129

- **ELIMINADO:** Tab Equipo (HC-1: borrado equipo del sistema)
- **ELIMINADO:** Mostrar stats efectivos (HC-1: eliminados stats base)
- **AGREGADO:** Barras de necesidades con colores (Health/Energy/Affect)
- **AGREGADO:** Badge ✓ si `CreatureAvailability.CanExplore(dna, careGate)`

## Necesidades Display

Usa `NeedsDisplay.ColorClass()` y `Fill01()` para:
- Mapear valor a [0-1]
- Asignar clase CSS (good/warn/crit)
- Mostrar relleno de barra

Affect usa rango [-100, 100]; Health/Energy [0, 100].

## Invariantes S129+

- No serializa stats (fueron eliminados)
- No toca equipo (sistema removido)
- Muestra partes genéticas con el poder de su kit, necesidades, rol sugerido de combate y demografía
- Badge "Apta para bajar" si `CanExplore(dna, careGate)` = true

## Vinculado a

- [[Index/05 - UI System]]
- [[Index/28 - Cimientos y camino a Game Ready]]
- [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[DetailInfoTabPresenter]], [[DetailRelationsPresenter]], [[DetailTreesPresenter]], [[BrawlKitDatabaseSO]], [[NeedsDisplay]], [[CreatureAvailability]], [[CareGateSO]], [[MonchiPortraitUI]], [[UiPanels]], [[GameEvents]], [[UIManager]]
