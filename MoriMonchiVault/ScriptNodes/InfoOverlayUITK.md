---
tags: [script, ui, overlay]
---

# InfoOverlayUITK.cs

**Ruta:** `UI/InfoOverlayUITK.cs`

**Responsabilidad:** Overlay siempre visible. Muestra el reloj (día, hora y bloque), el saldo de Dabloons y de Minerita, un toast de salida o adopción de criaturas, un aviso de la llamada del tío (**S149**), un aviso de encargo completado (**S151**), un aviso de meta cumplida (**S152**), la leyenda de controles (`hints`) y el selector de idioma EN/ES. Solo presenta: lee `GameClock`, `GameManager.CurrentInventory` y los payloads de eventos. El toast de retorno de expedición ya no vive aquí (S145): lo muestra `ExpeditionReturnCardUITK`.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del overlay |
| `hints` | `InputHint[]` | WASD, E, Click, Q, Rueda, B, Tab | Leyenda de controles (tecla + clave de acción de `Loc`); editable en inspector |
| `toastSeconds` | `float` | 6 | Duración del toast |

**Nota:** los hints por defecto incluyen `B` (`ui.overlay.hint.build`) y `Tab` (`ui.overlay.hint.catalog`). El modo construcción se retiró en S149; estos hints quedan en el default y conviene revisarlos.

## Elementos UXML

`date`, `dabloons`, `material` (saldo de Minerita), `expedition-toast` (reutilizado para el toast de criatura, el aviso del tío, el aviso de encargo y el aviso de meta), `hints` (contenedor de la leyenda).

## Eventos Suscritos (OnEnable / OnDisable)

| Evento | Manejador | Efecto |
|--------|-----------|--------|
| `GameEvents.OnInventoryChanged` / `OnInventoryReloaded` | `RefreshDabloons` | Actualiza Dabloons y Minerita |
| `GameEvents.OnCreatureDeparted` | `HandleCreatureDeparted` | Toast "adoptada" si `IsSold`, si no "perdida" |
| `GameEvents.OnRescueGiftSent` | `HandleRescueGiftSent` | **(S149)** Toast de la llamada del tío con el nombre de la caja |
| `GameEvents.OnOrderCompleted` | `HandleOrderCompleted` | **(S151)** Toast de encargo completado con la descripción y la recompensa |
| `GameEvents.OnGoalCompleted` | `HandleGoalCompleted` | **(S152)** Toast de meta cumplida con su título y recompensa en Dabloons |
| `GameEvents.OnDayBlockChanged` / `OnDayStarted` | `RefreshClock(force)` | Reloj |
| `LocalizationSettings.SelectedLocaleChanged` | `HandleLocaleChanged` | Reconstruye leyenda, reloj y saldos |
| `SettingsService.Changed` | `HandleSettingsChanged` | **(S151)** Muestra u oculta las filas de la leyenda según `ShowKeyHints` |

## Comportamiento

- **Reloj:** refresco cada 1 s (tiempo unscaled). Texto localizado (`ui.overlay.clock`) con día, hora, minuto y nombre del bloque.
- **Toast de criatura:** `ui.overlay.creature.adopted` o `ui.overlay.creature.lost`. Antes de mostrarlo quita las clases `toast--win`, `toast--lose` y `toast--draw`, que ya no se agregan.
- **Toast del tío (S149):** `ui.overlay.uncle.call` con `box.DisplayName`. Usa el mismo label y temporizador que el toast de criatura.
- **Toast de encargo (S151):** `ui.orders.done` con `order.Describe()` y `order.Reward`. Mismo label y temporizador.
- **Toast de meta (S152):** `ui.goal.done` con `Loc.Tr(goal.TitleKey)` y `goal.RewardDabloons`. Mismo label y temporizador.
- **Duración:** el toast se oculta a los `toastSeconds`, con timer en `Update`.
- **Saldos:** Dabloons con `ui.overlay.dabloons`; Minerita en el label "material" con `ui.overlay.material`.
- **Leyenda e idioma:** una fila por hint más los botones EN y ES (`Loc.SetLocale`). El idioma activo lleva `lang-btn--active`. Al construir la leyenda aplica `SettingsService.Current.ShowKeyHints` (S151).

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[GameClock]] — `Day`, `MinuteOfDay`, `Block`
- [[GameEvents]] — eventos de la tabla
- [[GameManager]] — `CurrentInventory`
- [[PlayerInventorySO]] — `Balance(Dabloons)`, `Balance(Minerita)`
- [[CreatureDNA]] — `CustomName`, `IsSold`, `ToStringID`
- [[CreatureBoxSO]] — `DisplayName` del regalo del tío (S149)
- [[UncleRescueService]] — emite `RescueGiftSent` (S149)
- [[ShopOrder]] — `Describe()` y `Reward` del toast de encargo (S151)
- [[OrderBoardService]] — emite `OrderCompleted` (S151)
- [[GoalSO]] — `TitleKey` y `RewardDabloons` del toast de meta (S152)
- [[GoalService]] — emite `GoalCompleted` (S152)
- [[SettingsService]], [[GameSettings]] — `ShowKeyHints` (S151)
- [[Loc]] — `Tr`, `SetLocale`, `ApplySavedLocale`, `CurrentCode`
- [[ExpeditionReturnCardUITK]] — tarjeta que reemplaza el toast de retorno
- [[UiPanels]] — `RootOf`

## Notas

- `Start` llama `Loc.ApplySavedLocale()` antes de leer los labels.
- Antes de asignar un toast se quitan las clases de resultado anteriores.
- S145: `OnExpeditionReturned` y el toast de retorno salieron de este script; el toast solo cubre salida y adopción de criaturas.
- S149: el toast del tío comparte el mismo label que el de criatura; si llegan dos avisos seguidos, el segundo reemplaza al primero.
- S151: el toast de encargo también comparte el label; el último aviso que llegue reemplaza al anterior.
- S152: el toast de meta también comparte el label; mismo criterio, el último aviso reemplaza al anterior.
