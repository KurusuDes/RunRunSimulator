---
tags: [script, ui, overlay]
---

# InfoOverlayUITK.cs

**Ruta:** `UI/InfoOverlayUITK.cs`

**Responsabilidad:** Overlay siempre visible. Muestra el reloj (día, hora y bloque), el saldo de Dabloons y de Minerita, un toast de retorno de expedición o de salida/adopción de criaturas, la leyenda de controles (`hints`) y el selector de idioma EN/ES. Solo presenta: lee `GameClock`, `GameManager.CurrentInventory` y los payloads de eventos.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del overlay |
| `hints` | `InputHint[]` | WASD, E, Click, Q, Rueda, B, Tab | Leyenda de controles (tecla + clave de acción de `Loc`); editable en inspector |
| `toastSeconds` | `float` | 6 | Duración del toast |

## Elementos UXML

`date`, `dabloons`, `material`, `expedition-toast`, `hints` (contenedor de la leyenda).

## Eventos Suscritos (OnEnable / OnDisable)

| Evento | Manejador | Efecto |
|--------|-----------|--------|
| `GameEvents.OnInventoryChanged` / `OnInventoryReloaded` | `RefreshDabloons` | Actualiza Dabloons y Minerita |
| `GameEvents.OnExpeditionReturned` | `HandleExpeditionReturned` | Toast de retorno; si el label aún no existe, queda pendiente |
| `GameEvents.OnCreatureDeparted` | `HandleCreatureDeparted` | Toast "adoptada" si `IsSold`, si no "perdida" |
| `GameEvents.OnDayBlockChanged` / `OnDayStarted` | `RefreshClock(force)` | Reloj |
| `LocalizationSettings.SelectedLocaleChanged` | `HandleLocaleChanged` | Reconstruye leyenda, reloj y saldos |

## Comportamiento

- **Reloj:** refresco cada 1 s (tiempo unscaled). Texto localizado (`ui.overlay.clock`) con día, hora, minuto y nombre del bloque.
- **Toast de retorno:** si `Lost`, clase `toast--lose` y texto `ui.overlay.expedition.lost` (pisos, minerita). Si no, texto `ui.overlay.expedition.return` (pisos, minerita, caídos) con clase según `Winner` (win, lose o draw).
- **Toast de criatura:** `ui.overlay.creature.adopted` o `ui.overlay.creature.lost`.
- **Duración:** el toast se oculta a los `toastSeconds`, con timer en `Update`.
- **Saldos:** Dabloons con `ui.overlay.dabloons`; Minerita en el label "material" con `ui.overlay.material`.
- **Leyenda e idioma:** una fila por hint más los botones EN y ES (`Loc.SetLocale`). El idioma activo lleva `lang-btn--active`.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[GameClock]] — `Day`, `MinuteOfDay`, `Block`
- [[GameEvents]] — eventos de la tabla
- [[GameManager]] — `CurrentInventory`
- [[PlayerInventorySO]] — `Balance(Dabloons)`, `Balance(Minerita)`
- [[Loc]] — `Tr`, `SetLocale`, `ApplySavedLocale`, `CurrentCode`
- [[ExpeditionBridge]] — origen de `ExpeditionReturned`
- [[UiPanels]] — `RootOf`

## Notas

- Si `ExpeditionReturned` llega antes de que exista el label del toast (antes de `Start`), se guarda en `pendingToast` y se muestra al arrancar.
- `Start` llama `Loc.ApplySavedLocale()` antes de leer los labels.
- Antes de asignar un toast se quitan las clases de resultado anteriores.
