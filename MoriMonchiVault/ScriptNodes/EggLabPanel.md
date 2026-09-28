---
tags: [script, ui, uitk, creature]
---

# EggLabPanel.cs

**Ruta:** `UI/EggLabPanel.cs`

**Responsabilidad:** UI UITK para laboratorio de huevos. **S136 NUEVO.** Presenta grilla de botones numéricas (1-N) sobre los huevos en mundo 3D (screen-space), card detail al seleccionar (nombre, padres, progreso, costo), portrait renderizado via EggLabPortrait.

## Campos Serializados (Required)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `builder` | `EggLabBuilder` | Orquestador; se suscribe a eventos |
| `portrait` | `EggLabPortrait` | Renderizador de portrait 3D |
| `worldCamera` | `Camera` | Cámara world (para convertir posiciones 3D a panel) |

## Constantes

| Constante | Valor | Descripción |
|-----------|-------|-------------|
| `TealFill` | RGB(51, 191, 166) | Color teal para RadialSlot (progreso) |

## Elementos UIElements (Descubiertos via Query)

| Query | Tipo | Descripción |
|-------|------|-------------|
| `#egg-lab__labels` | VisualElement | Contenedor de botones numéricas (botones flotantes 3D) |
| `#egg-lab__rearm` | Button | Botón "Regenerar" huevos |
| `#egg-lab__card` | VisualElement | Card detail (oculta hasta seleccionar) |
| `#egg-lab__card-close` | Button | Cerrar card |
| `#egg-lab__card-title` | Label | "Huevo #N" |
| `#egg-lab__portrait` | VisualElement | Background image renderizada |
| `#egg-lab__mother-swatch` | VisualElement | Cuadrado color madre (backgroundColor) |
| `#egg-lab__mother-name` | Label | Nombre madre ("♀ NombreX") |
| `#egg-lab__father-swatch` | VisualElement | Cuadrado color padre (backgroundColor) |
| `#egg-lab__father-name` | Label | Nombre padre ("♂ NombreY") |
| `#egg-lab__radial` | VisualElement | Contenedor del RadialSlot |
| `#egg-lab__cost` | Label | "Minerita XXX" |

## Ciclo de Vida

| Evento | Acción |
|--------|--------|
| `OnEnable()` | Obtiene UIDocument root, descubre elementos, se suscribe a eventos de builder, crea RadialSlot, llama RebuildLabels() y CloseCard() |
| `OnDisable()` | Desuscribe eventos, limpia number buttons |
| `LateUpdate()` | Convierte posiciones 3D de huevos a screen-space y posiciona botones numéricos (WorldToPanel) |

## Métodos Públicos

**Ninguno.** Solo comportamiento interno.

## Métodos Privados

### OnRebuilt()

Llamado cuando EggLabBuilder.Rebuilt se dispara.

**Acción:**
- CloseCard()
- RebuildLabels()

### RebuildLabels()

Recrea botones numéricos desde lista de entries.

**Flujo:**
1. ClearNumberButtons()
2. Si builder es null o labelsContainer es null → return
3. Para cada entry en builder.Entries:
   - Crea nuevo Button con lambda capturada: `() => builder.Select(capturedEntry)`
   - Text = entry.Number.ToString()
   - AddToClassList("egg-lab__num") para estilos CSS
   - Agrega al labelsContainer
   - Almacena tupla (button, entry) en numberButtons

**Notas:** Captura `capturedEntry` para evitar closure sobre variable del loop

### ClearNumberButtons()

Limpia labelsContainer (Clear()) y lista numberButtons.

### OnRearmClicked()

Callback del botón Rearm.

**Acción:** `builder.Rebuild()`

### OnSelected(EggLabEntry entry)

Callback cuando builder.Selected se dispara.

**Flujo:**
1. Si card es null o entry es null → return
2. Abre card: `card.style.display = DisplayStyle.Flex`
3. Actualiza title: "Huevo #X"
4. Renderiza portrait:
   - `portrait.Show(entry.Root)` → obtiene RenderTexture
   - Asigna como backgroundImage de portraitElement
   - Fondo transparent, size Contain
5. Actualiza swatches padres:
   - SetParent(motherSwatch, motherName, entry.Mother, "♀")
   - SetParent(fatherSwatch, fatherName, entry.Father, "♂")
6. Actualiza radial:
   - `radial.Charge01 = entry.Progress01`
   - `radialPercent.text` = "¡Listo!" si Progress01 >= 1, sino "X%"
7. Actualiza costo: "Minerita X"

### SetParent(VisualElement, Label, CreatureDNA, string glyph)

Método estático auxiliar.

**Acción:**
- Si swatch: `backgroundColor = dna.BaseColor` (si dna no null, else transparente)
- Si label: `text = glyph + " " + dna.CustomName` (si dna existe, else "?")
- Ej: "♀ Ember", "♂ Frost"

### CloseCard()

Cierra card de detalle.

**Acción:**
- `portrait.Hide()`
- `card.style.display = DisplayStyle.None`

### LateUpdate()

**Responsabilidad:** Mantener botones numéricos alineados con huevos en mundo 3D.

**Flujo cada frame:**
1. Si root es null o worldCamera es null → return
2. Obtiene panel del UIDocument: `root.panel`
3. Si panel es null → return
4. Para cada (button, entry) en numberButtons:
   - Si button o entry.Root es null → continúa
   - Calcula posición mundo: `worldPos = entry.Root.position + Vector3.up * 0.42f` (sobre el huevo)
   - Valida si está frente a cámara (dot product)
   - Si está detrás: `DisplayStyle.None`
   - Sino: `DisplayStyle.Flex` + convierte a panel-space vía `RuntimePanelUtils.CameraTransformWorldToPanel()`
   - Setea left/top del button

**Impacto:** Botones flotantes siguen huevos en tiempo real

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `root` | `VisualElement` | Root del UIDocument |
| `labelsContainer` | `VisualElement` | Contenedor de botones numéricos |
| `rearmButton` | `Button` | Botón regenerar |
| `card` | `VisualElement` | Card detail |
| `cardCloseButton` | `Button` | Cerrar card |
| `cardTitle` | `Label` | Título card |
| `portraitElement` | `VisualElement` | Background para portrait |
| `motherSwatch`, `fatherSwatch` | `VisualElement` | Colores padres |
| `motherName`, `fatherName` | `Label` | Nombres padres |
| `radialContainer` | `VisualElement` | Contenedor radial |
| `radial` | `RadialSlot` | Widget de carga circular (S123 MODIFICADO) |
| `radialPercent` | `Label` | Texto "X%" o "¡Listo!" |
| `costLabel` | `Label` | "Minerita X" |
| `numberButtons` | `List<(Button, EggLabEntry)>` | Tuplas de botón + entry |

## Cambios S136

**Nuevo script de UI del laboratorio:**
- Integración UITK con mundo 3D
- Botones screen-space (world-to-panel conversion)
- Portrait renderizado en tiempo real via EggLabPortrait
- Swatches de color genético de padres

**Flujo de eventos:**
- builder.Rebuilt → EggLabPanel actualiza labels
- builder.Selected → EggLabPanel actualiza card
- Button click → builder.Select()
- Raycast mundo → builder.Select() → panel se actualiza

**RadialSlot (S123 MODIFICADO):**
- Cargado dinámicamente en OnEnable
- FillColor = TealFill
- Charge01 = entry.Progress01

## Notas S136

- Card no es destructivo al cerrar (solo DisplayStyle.None)
- Portrait se actualiza cada selección (Show llama Hide del anterior)
- Botones numéricos son screen-space (no siguen huevos en escena directamente)
- LateUpdate se ejecuta cada frame para mantener alineación (puede optimizarse si N > 100)
- No hay animación de apertura/cierre de card (nítido)
- Colores padres son backgroundColor directo (no texto, solo color)

## Invariantes

- Cada entry tiene un botón único numerado (1-based)
- Card abierta = portrait activo; card cerrada = portrait detenido
- WorldToPanel requiere que root.panel sea válido (no null después de OnEnable)
- Botones detrás de cámara nunca se hacen clic (culling implícito)

## Vinculado a

- [[Index/31 - EggLab & Incubadora]]
- [[Resources/Scenes/EggLab.unity]] — escena única
- [[EggLabBuilder]], [[EggLabPortrait]], [[EggLabEntry]]
- [[RadialSlot]] — **S123 MODIFICADO**

## Conexiones

**Entrada:**
- EggLabBuilder.Rebuilt event → actualiza labels
- EggLabBuilder.Selected event → actualiza card
- Mouse clicks en botones numéricos
- EggLabPortrait.Show() para renderización

**Salida:**
- Card UI con padre/madre/progreso/costo
- Portrait 3D renderizado
- Botones flotantes aligned con mundo
