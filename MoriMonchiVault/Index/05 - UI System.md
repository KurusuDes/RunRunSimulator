---
tags: [index, ui]
---

# 05 - UI System

**Responsabilidad:** Interfaz UITK, enrutamiento input a paneles, aislamiento Gameplay/Menu. Stack LIFO de paneles.

**Core:**
| Script | Ruta | Rol |
|--------|------|-----|
| [[UIManager]] | `UI/UIManager.cs` | Hub paneles + stack LIFO + router input + bus eventos UI static |
| [[UIInputs]] | `UI/UIInputs.cs` | Dueno action map UI (Navigate/Submit/Cancel stepped) |
| [[PanelTrigger]] | `Interactables/PanelTrigger.cs` | Bridge mundo UI (IInteractable abre panel) |

**Panel Controllers:**
| Script | Ruta | Rol |
|--------|------|-----|
| [[BreedingPanelUITK]] | `UI/BreedingPanelUITK.cs` | Panel breeding |
| [[BuildBrowserUITK]] | `UI/BuildBrowserUITK.cs` | Build browser muebles |
| [[CreatureGridUI]] | `UI/CreatureGridUI.cs` | Grid criaturas uGUI |
| [[CreatureGridUITK]] | `UI/CreatureGridUITK.cs` | Grid criaturas UITK |
| [[CreatureGridView]] | `UI/CreatureGridView.cs` | Vista grid base |
| [[CreatureVisualUI]] | `UI/CreatureVisualUI.cs` | Render 3D en UI |
| [[HotbarHUDUITK]] | `UI/HotbarHUDUITK.cs` | HUD hotbar (overlay) |
| [[InfoOverlayUITK]] | `UI/InfoOverlayUITK.cs` | Overlay contextual |
| [[MorimonchiDetailInfoUITK]] | `UI/MorimonchiDetailInfoUITK.cs` | Detalle criatura |
| [[StoragePanelUITK]] | `UI/StoragePanelUITK.cs` | Panel almacenamiento |
| [[StorePanelUITK]] | `UI/StorePanelUITK.cs` | Panel tienda |

**Reglas de Oro:**
- Jamas usar SetActive en UITK (destruye rootVisualElement). Usar style.display = None.
- Action Maps Player y UI son mutuamente excluyentes. Solo uno activo a la vez.
- Paneles siempre en GameObjects activos (pueden escuchar eventos aunque ocultos).

---

## Recetario UITK (S38 — lecciones del panel de lineup 3v3, aprobado por Juan)

> Leer ANTES de construir cualquier UI nueva. Todo esto salio de iterar la tab "Equipo 3v3" contra mockups de Juan; el resultado final quedo aprobado como referencia de calidad.

### Layout que llena la ventana (el bug clasico)
1. Dentro de un `TabView`, el contenido NO llena la altura salvo que `flex-grow: 1` este en **TRES** niveles: `.unity-tab-view__content-container`, **`.unity-tab`** (el que todos olvidan) y `.unity-tab__content-container`. Sin el del medio, cada tab mide su contenido y deja banda muerta abajo.
2. El root del tab ademas necesita `flex-grow: 1` **y** `height: 100%`.
3. Anclar una barra al fondo: `margin-top: auto` (soportado en Unity 6 UITK).

### El feedback loop de auto-medicion
Un contenedor centrado (`align-items: center` en el padre) **sin width definido** mide lo que mide su contenido. Si un calculo dinamico lee ese ancho para dimensionar el contenido → loop: contenido chico → contenedor chico → "no hay espacio" → contenido chico. Fix: `width: 100%` en el contenedor medido.

### Sizing dinamico (grillas/boards que se adaptan a la resolucion)
- NUNCA fijar px pensando en una resolucion (el Game view del editor suele ser 720p; el monitor de Juan no).
- Patron: `GeometryChangedEvent` en el contenedor → calcular tamano desde `resolvedStyle.width/height` → aplicar por **inline style** (pisa al USS, que queda como valor inicial) → guard anti-loop (`if (Mathf.Abs(nuevo - actual) < 1f) return;`).

### Drag & drop runtime (no existe API en UITK runtime)
Patron completo en [[CombatLineupUITK]]: `PointerDownEvent` (guardar candidato + `CapturePointer`) → `PointerMoveEvent` (umbral ~8px antes de arrancar; ghost con `PickingMode.Ignore` agregado al root, posicionado con `root.WorldToLocal(evt.position)`) → `PointerUpEvent` (hit-test por `worldBound.Contains`). **Quirk critico**: en el Up, `UnregisterCallback` ANTES de `ReleasePointer` — si no, el `PointerCaptureOutEvent` dispara el camino de cancelacion sobre un drop ya resuelto.
- Click derecho para inspeccion sin chocar con el drag: `if (evt.button == 1)` en el mismo `PointerDownEvent`.
- Click izquierdo "limpio" (sin superar umbral) se detecta en el Up con `!dragActive`.

### Scrollbars y rueda
- Scrollbar custom (fino, oscuro, sin flechas): estilizar `.unity-scroller--horizontal` scoped al contenedor + `display: none` a `__low-button`/`__high-button` + colores en `.unity-base-slider__tracker`/`__dragger`.
- Carrusel horizontal con rueda del mouse: `WheelEvent` → `scrollOffset.x += evt.delta.y * 20f` + `StopPropagation()`.

### Quirks de editor/workflow
- **Hot-reload de USS/UXML con Play corriendo huerfana el arbol**: UIDocument recrea `rootVisualElement` y TODAS las refs cacheadas (Q<>) mueren → panel vacio. No es bug del juego: reiniciar Play. Afecta a todos los paneles (guard `wired`).
- Tab nueva agregada AL FINAL del TabView queda fuera de la navegacion por teclado si el clamp del panel no la incluye — patron util para tabs WIP mouse-only sin tocar la navegacion. (El ejemplo vivo era `CombatPanelUITK`, borrado en S128.)
- Iterar diseno con Unity MCP: abrir el panel por codigo (`UIManager.RequestPanelSet` via reflection en `execute_code`) + `manage_camera screenshot` del Game view = ver el layout real antes de entregar. Los numeros "se ve bien" del USS mienten; el screenshot no.
- Componente de UI nuevo = MonoBehaviour hermano con su ref `UIDocument` serializada (patron F3/DevConsoles) — no engordar el partial del panel.

---

## Paleta y helpers compartidos (S93)

- **La paleta canonica ES `UI Toolkit/Theme.uss`**: 17 tokens `--mm-*` bajo `.mm-theme` (papel/tinta/coral/teal/gold/plum + good/warn/crit + scrim) que coinciden exacto con los 5 colores del kit "Diario del Pet Shop" de [[Index/14 - Art Prompts]]. Variante **`.mm-theme--night`** completa y **otra vez sin usar** desde que S128 borro el panel de combate. Inventario detallado de tokens, formas (3px `--mm-frame`, radios 8/10/16/22, `letter-spacing 4px`) y clases reutilizables por familia (`.panel*`, `.action*`, `.mm-swatch`, `.card*`, tabs pill, `.stat--*`, `.part-row`, `.combat-card*` huerfano del 3v3) en [[Index/21 - Combate v3 - Dragon RPS]] §9.0. Ningun color nuevo fuera del tema; rareza por `BodyPart.RarityColor`.
- **Arbol por codigo** (`EquipmentBackpackUITK`) exige `AddToClassList("mm-theme")` + `styleSheets.Add(themeStyleSheet)` o las `var(--mm-*)` no resuelven.
- **Helpers** (S93): `UI/UiPanels` (`RootOf(document)`, `SetActiveIndex(items, index, clase)`, `ClampSelection(count, index)` — usarlos en vez de repetir el idioma) · `UI/CreatureDisplay` (`StateOf(dna)` localizada UNICA, `RarityColor(r, palette)`, `ApplyIconVisual`, `ApplyRarityBorder`) · `UI/MonchiPortraitUI.Apply(elemento, dna)` para retratos (sin spawnear; `ApplyLive` solo con la criatura en el mundo).
- Show/hide de paneles: `UIManager.SetPanelShown` es el dueno; los paneles solo togglean sub-vistas propias (etiquetas de vacio, toasts). `BuildBrowserUITK` y `HotbarHUDUITK` no son paneles de `UIManager` a proposito.
- `PanelSettings`: `StandartPanelSettings.asset` (Scale With Screen Size, 1920x1080, match alto) para los 10 documentos de pantalla; `WorldUIPanelSettings.asset` solo para world-space (nametag, globo NPC).

## Kit v2 "Linterna de bosque" (S160) — cómo usarlo y lo aprendido

> Regla de trabajo (Juan S160): al terminar cada pantalla, sumar acá lo aprendido y compararse lado a lado con la referencia original; la vara es **igual o mejor** que Synty. Antes de diseñar una pantalla nueva, buscar qué juego ya resolvió esa tarea y copiar su distribución.

**Dónde vive:** `UI Toolkit/Skin/Skin.uss` (tokens + componentes, importado por `Theme.uss`), `Skin/Synty/` (sprites copiados de los packs, con su 9-slice), `Skin/Fonts/` (LT Museum = títulos, Grenze = secciones/números, Alegreya Sans = cuerpo; licencias OFL al lado). Pantalla modelo aprobada: `MorimonchiDetailInfoUITK`. Referencias renderizadas: `Captures/S160/ref/`. Propuesta de overhaul por pantalla (juego de referencia + esquema): artifact `claude.ai/artifact/N3UpoMexRkG49b9T2GmT44`.

**Dos registros:** menú de pantalla completa = raíz `mm-theme mm-skin mm-screen` (fondo pino **opaco**, sin degradados ni brillos: Juan los rechazó) + capa `mm-screen__vignette` + `mm-footer` con `mm-prompt`/`mm-key`; HUD sobre el mundo = clase `mm-hud` (píldoras cálidas translúcidas `Bar_Rounded`/`Box_Rounded`, ranuras marrones, burbuja crema `mm-bubble`), receta del HUD FarmingLife de Synty.

**Copiar una receta de Synty (lo que más rindió):** volcar la jerarquía del prefab con `execute_code` (sprite, tipo, color, tamaño y fuente por nodo) a un .txt y replicarla. Los prefabs están a 4K: dividir tamaños y fuentes por 2 para la referencia 1920×1080. Las escenas demo se renderizan en editor con su cámara a un RT; si el canvas es Overlay, pasarlo a ScreenSpaceCamera en memoria (sin guardar). Abrir **una escena por llamada**: los lotes grandes tumban el MCP.

**Capas en UITK (un solo fondo por elemento):** un marco de Synty = relleno (`*_Mask`, blanco → `-unity-background-image-tint-color`) en el propio elemento + hijos absolutos `mm-layer mm-panel__lip` y `mm-layer mm-panel__frame` como **primeros hijos** con `picking-mode="Ignore"`. Los marcos dorados se usan **nativos** (no recolorear: el gradient map los aplanaba). Bordes de 4K → `-unity-slice-scale` (0.25 marcos grandes, 0.35 chicos, 0.15 `mm-panel--compact`).

**Sprites:** `Assets/Synty/` está en .gitignore → nunca referenciarlo; copiar con `AssetDatabase.CopyAsset` a `Skin/Synty/` (conserva bordes 9-slice, GUID nuevo). Un USS importado **antes** de que exista el sprite muestra un triángulo de advertencia: reimportar el USS (`ImportAsset(..., ForceUpdate)`) y reiniciar Play. Mirar la forma del sprite antes de culpar al render (Ring_Large_01 es un arco parcial, no un círculo).

**Quirks de UITK:** `var()` en `style=""` del UXML rompe el `CloneTree` (NullReference en `StyleVariableResolver`) → colores por variable solo en clases (`mm-skin-chip--coral`). Tokens del skin: selector `.mm-skin, .mm-theme.mm-skin` (el @import queda antes y perdía contra `.mm-theme`). TabView 6.3: el header vive en `.unity-tab-view__content-viewport` (nombre engañoso) con `.unity-tab-view__next-button/__previous-button`; centrar con `justify-content` en ese viewport, `.unity-tab { flex-grow:1 }` para que la página ocupe el alto, seleccionado = `:checked`, subrayado = `.unity-tab__header-underline`. Fuentes: `-unity-font-definition: url("x.ttf")` funciona directo; Ortica no tiene "¿".

**Retrato en vivo:** el RT de `MonchiLivePortrait` es transparente; pedestal = elipse CSS (`border-radius:50%` + borde dorado) + disco oscuro aplastado detrás, subido hasta los pies.

**Verificación:** abrir paneles en Play con `UIManager.SelectCreature(dna, registry)` o `UIManager.RequestPanelSet(UIPanelType.X, true)` y capturar con `manage_camera screenshot`. Editar USS con Play corriendo huerfana el árbol: stop → refresh → play. Las capturas a veces salen "lavadas" (quirk S158): ante dudas, probar con un fondo opaco de prueba.

**Anti-slop (checklist de comparación):** cada dato = ícono + nombre + valor en cajitas (`mm-statbox`, `mm-row`, `mm-valuebox`), nunca párrafos tipo volcado; nada de placeholders visibles (cuadrados grises, botones lavados); sin espacio muerto; nada de rectángulos planos sin marco; jerarquía título blanco 38 / subtítulo dorado 23 / sección Grenze dorada 26 / cuerpo 20-22; comparar **recortes a la misma escala** contra la referencia y dar un veredicto honesto.

**Lo aprendido en S161 (por pantalla):** ranura de inventario canónica = receta FarmingLife (caja `Box_Rounded_Medium_01` #634B31 + runas `Tracery_Diamond_01` #24201A9A + ícono + píldora de tecla abajo; activa con `Frame_Rounded_02` tintado dorado) — la usan hotbar y almacén; los huecos vacíos muestran las runas, nunca gris. Ítems sin ícono de Synty: renderizar el prefab propio a PNG 512 transparente con cámara temporal (renderer 1, sin post) y recortar al bbox alfa (`ItemDefinitionSO.Icon`). Composiciones copiadas: Libro = Inventory 01 (grilla · vitrina · ficha), Crianza y PC = Crafting 01, Almacén = Inventory 02/cofre de Stardew, Bajada = PartyManagement 01, Regreso = Results 01, Venta = Popups 01. Pantallas con datos de la ficha reusan `DetailInfoTabPresenter` sobre su propio root (busca por nombre y tolera faltantes). Retícula y avisos contextuales: `PlayerFocusProbe` → `FocusPromptUITK`; un mueble con texto propio implementa `IFocusLabel` en vez de un TMP flotante. Texto en el mundo con TMP: fuente `Skin/Fonts/LTMuseum-Bold SDF.asset`. ScrollView con grilla: `flex-wrap` en `.x .unity-scroll-view__content-container` (descendiente, no `>`), ancho fijo para forzar columnas y scroller sobrante en `Hidden`.

**Subagentes:** el trabajo UXML/USS se paraleliza bien con una guía escrita (archivos disjuntos, prohibido tocar `.cs`/`Skin.uss`, reportar sprites y cambios de código); no pueden verificar a ojo → la verificación en Play la hago yo.
