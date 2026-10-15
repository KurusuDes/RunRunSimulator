---
tags: [script, ui, uitk]
---

# MorimonchiDetailInfoUITK.cs

**Ruta:** `UI/MorimonchiDetailInfoUITK.cs`

**Responsabilidad:** Panel de detalles UITK de MoriMochi. Pestañas: Info (ranuras visuales de partes, bloque de personalidad, datos, necesidades, ✓ apta para bajar, rol de combate sugerido, partes con el poder de su kit y evolución por parte), Crianza, Linaje (árboles genealógicos) y Relaciones. **S75:** Sin tab Combate (demolición). **S93:** Usa `UiPanels.RootOf()`. **S129:** Eliminada pestaña Equipo (demolición HC-1). Muestra: partes genéticas, 3 barras de necesidades (color según `NeedsDisplay`), marca de apta para explorar, y subtítulo género · rol · elemento. **S145:** la pestaña Info recibe el `BrawlKitDatabaseSO` para mostrar poderes y rol sugerido. **S148:** la pestaña Info recibe el `EvolutionEffectSO` para el botón de evolución y los bloques por parte. **S151:** el panel suma el presenter de herencia (`DetailInheritancePresenter`) en la pestaña Linaje. **S160:** rediseño de la ficha con el kit v2 de UI (ver Cambios en S160).

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del panel (`UiPanels.RootOf`) |
| `panel` | `UIPanelType` | `MorimonchiDetail` | Clave de registro en `UIManager` |
| `database` | `CreatureDatabaseSO` | — | Resuelve nombres, sets e iconos de partes |
| `careGate` | `CareGateSO` | — | Umbral de la marca de apta |
| `kits` | `BrawlKitDatabaseSO` | — | Kits de combate: poderes, rol sugerido y escalones de mejora (S145, S148) |
| `evolution` | `EvolutionEffectSO` | — | Efecto de evolución con Minerita (S148). Sin asignar, no hay botón ni bloques de evolución |
| `sortingOrder` | `int` | 100 | Orden de dibujo; el modal queda sobre la grilla |

## Tabs (según `WireStaticLabels`)

- **Info** (`tab-info`) — ranuras visuales de partes (`slots-left` / `slots-right`), bloque de personalidad (`personality-*`), bloque de datos (`stat-*`: estado, nacimiento, crianzas, batallas), necesidades (3 barras con porcentaje y color), marca de apta, rol de combate sugerido, lista de partes con poder de kit y evolución. Títulos de sección `ui.detail.section.personality`, `ui.detail.section.data`, `ui.detail.section.powers` (clase `section-title`, en ese orden).
- **Crianza** (`tab-breed`) — placeholder `breed-empty`.
- **Linaje** (`tab-lineage`) — árboles genealógicos (`DetailTreesPresenter`) y línea de herencia por parte (`DetailInheritancePresenter`, S151); placeholder `lineage-empty`.
- **Relaciones** (`tab-relations`) — amigos y enemigos (títulos `ui.detail.section.friends` / `.foes`); placeholder `relations-empty`.

## Flujo

- **Awake:** aplica `sortingOrder` al documento.
- **OnEnable / OnDisable:** suscribe y desuscribe `UIManager.OnCreatureSelected` (→ `Show`), `GameEvents.OnRegistryChanged` y `GameEvents.OnInventoryChanged`. Ambos eventos de datos repueblan si el panel está visible; el botón de evolución depende del saldo de Minerita.
- **Start:** `Wire()` y registro navegable.
- **Wire():** busca `title`, `portrait`, `tabs`, `close-button`; aplica `WireStaticLabels`; crea los presenters: `DetailInfoTabPresenter(root, database, careGate, kits, evolution, () => registry)`, `DetailTreesPresenter(root, database, () => registry)`, `DetailInheritancePresenter(root, () => registry)` (S151) y `DetailRelationsPresenter(root, () => registry)`.
- **WireStaticLabels(root):** asigna textos localizados a los tabs, a los títulos de sección y a los labels estáticos: `care-title`, `need-*-label`, `stat-*-label` (state, born, breeds, battles), `prompt-tab`, `prompt-close` y los placeholders `*-empty`.
- **Show(dna, registry):** guarda registry y `current`, `Wire`, `Populate`, selecciona el tab 0 y `RequestPanelSet(panel, true)`.
- **Populate(dna):** título (`CustomName` o `ToStringID`), retrato con `MonchiPortraitUI.ApplyLive`, `info.Rebuild`, `trees.Rebuild`, `inheritance.Rebuild` (S151), `relations.Rebuild`.
- **OnRegistryChanged / OnInventoryChanged:** si el panel está visible, repuebla `current`.
- **OnUINavigate:** cambia de tab con el eje x. `OnUISubmit` no hace nada. `OnUICancel` devuelve false.

## Cambios en S160

- La pestaña Info se rediseñó con el kit v2 de UI. El presenter `DetailInfoTabPresenter` ya no llena los labels `identity`, `role-element` ni `progression`; llena `subtitle`, `stat-*-value`, `personality-*`, `need-*-value` y construye las ranuras de partes.
- `WireStaticLabels` suma los títulos de sección de `tab-info` (personality, data, powers), los labels `stat-*-label`, `prompt-tab` y `prompt-close`.

## Cambios en S151

- Nuevo presenter `DetailInheritancePresenter`, creado en `Wire()` y repoblado en `Populate()`.

## Cambios en S129

- **ELIMINADO:** Tab Equipo (HC-1: borrado equipo del sistema)
- **ELIMINADO:** Mostrar stats efectivos (HC-1: eliminados stats base)
- **AGREGADO:** Barras de necesidades con colores (Health/Energy/Affect)
- **AGREGADO:** Badge ✓ si `CreatureAvailability.CanExplore(dna, careGate)`

## Necesidades Display

Usa `NeedsDisplay.ColorClass()` y `Fill01()` para:
- Mapear valor a [0-1]
- Asignar clase CSS (good/warn/crit)
- Mostrar relleno de barra y porcentaje

Affect usa rango [-100, 100]; Health/Energy [0, 100].

## Invariantes S129+

- No serializa stats (fueron eliminados)
- No toca equipo (sistema removido)
- Muestra partes genéticas con el poder de su kit, necesidades, rol sugerido de combate, datos del DNA y evolución por parte (S148)
- Badge "Apta para bajar" si `CanExplore(dna, careGate)` = true

## Vinculado a

- [[Index/05 - UI System]]
- [[Index/28 - Cimientos y camino a Game Ready]]
- [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[DetailInfoTabPresenter]], [[DetailRelationsPresenter]], [[DetailTreesPresenter]], [[DetailInheritancePresenter]] (S151), [[BrawlKitDatabaseSO]], [[EvolutionEffectSO]], [[NeedsDisplay]], [[CreatureAvailability]], [[CareGateSO]], [[MonchiPortraitUI]], [[UiPanels]], [[GameEvents]], [[UIManager]]
