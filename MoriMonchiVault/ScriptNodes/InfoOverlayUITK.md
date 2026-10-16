---
tags: [script, ui, overlay]
---

# InfoOverlayUITK.cs

**Ruta:** `UI/InfoOverlayUITK.cs`

**Responsabilidad:** Overlay siempre visible. Muestra el reloj (día, hora y bloque), el saldo de Dabloons y de Minerita (solo número), un toast de salida o adopción de criaturas, un aviso de la llamada del tío (**S149**), un aviso de encargo completado (**S151**) y un aviso de meta cumplida (**S152**). Solo presenta: lee `GameClock`, `GameManager.CurrentInventory` y los payloads de eventos. El toast de retorno de expedición ya no vive aquí (S145): lo muestra `ExpeditionReturnCardUITK`.

**S161:** la leyenda de teclas (`hints`) y el selector de idioma EN/ES salieron del overlay. La leyenda vive ahora en `FocusPromptUITK` (avisos contextuales) y el overlay quedó solo con reloj, saldos y toasts.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del overlay |
| `toastSeconds` | `float` | 6 | Duración del toast |

## Elementos UXML

`date`, `dabloons`, `material` (saldo de Minerita), `expedition-toast` (reutilizado para el toast de criatura, el aviso del tío, el aviso de encargo y el aviso de meta).

## Eventos Suscritos (OnEnable / OnDisable)

| Evento | Manejador | Efecto |
|--------|-----------|--------|
| `GameEvents.OnInventoryChanged` / `OnInventoryReloaded` | `RefreshDabloons` | Actualiza Dabloons y Minerita |
| `GameEvents.OnCreatureDeparted` | `HandleCreatureDeparted` | Toast "adoptada" si `IsSold`, si no "perdida" |
| `GameEvents.OnRescueGiftSent` | `HandleRescueGiftSent` | **(S149)** Toast de la llamada del tío con el nombre de la caja |
| `GameEvents.OnOrderCompleted` | `HandleOrderCompleted` | **(S151)** Toast de encargo completado con la descripción y la recompensa |
| `GameEvents.OnGoalCompleted` | `HandleGoalCompleted` | **(S152)** Toast de meta cumplida con su título y recompensa en Dabloons |
| `GameEvents.OnDayBlockChanged` / `OnDayStarted` | `RefreshClock(force)` | Reloj |
| `LocalizationSettings.SelectedLocaleChanged` | `HandleLocaleChanged` | Reconstruye reloj y saldos |

## Comportamiento

- **Reloj:** refresco cada 1 s (tiempo unscaled). Texto localizado (`ui.overlay.clock`) con día, hora, minuto y nombre del bloque.
- **Toast de criatura:** `ui.overlay.creature.adopted` o `ui.overlay.creature.lost`. Antes de mostrarlo quita las clases `toast--win`, `toast--lose` y `toast--draw`.
- **Toast del tío (S149):** `ui.overlay.uncle.call` con `box.DisplayName`. Usa el mismo label y temporizador que el toast de criatura.
- **Toast de encargo (S151):** `ui.orders.done` con `order.Describe()` y `order.Reward`. Mismo label y temporizador.
- **Toast de meta (S152):** `ui.goal.done` con `Loc.Tr(goal.TitleKey)` y `goal.RewardDabloons`. Mismo label y temporizador.
- **Duración:** el toast se oculta a los `toastSeconds`, con timer en `Update`.
- **Saldos (S161):** Dabloons con `ui.overlay.dabloons`; Minerita en el label "material", solo con número (`N0`).

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[GameClock]] — `Day`, `MinuteOfDay`, `Block`
- [[GameEvents]] — eventos de la tabla
- [[GameManager]] — `CurrentInventory`
- [[PlayerInventorySO]] — `Balance(Dabloons)`, `Balance(Minerita)`
- [[CreatureDNA]] — `CustomName`, `IsSold`
- [[CreatureBoxSO]] — `DisplayName` del regalo del tío (S149)
- [[UncleRescueService]] — emite `RescueGiftSent` (S149)
- [[ShopOrder]] — `Describe()` y `Reward` del toast de encargo (S151)
- [[OrderBoardService]] — emite `OrderCompleted` (S151)
- [[GoalSO]] — `TitleKey` y `RewardDabloons` del toast de meta (S152)
- [[GoalService]] — emite `GoalCompleted` (S152)
- [[Loc]] — `Tr`, `ApplySavedLocale`
- [[ExpeditionReturnCardUITK]] — tarjeta que reemplaza el toast de retorno
- [[UiPanels]] — `RootOf`
- [[FocusPromptUITK]] — leyenda de teclas de gameplay (S161)

## Notas

- `Start` llama `Loc.ApplySavedLocale()` antes de leer los labels.
- Antes de asignar un toast se quitan las clases de resultado anteriores.
- S145: `OnExpeditionReturned` y el toast de retorno salieron de este script.
- S149: el toast del tío comparte el mismo label que el de criatura; si llegan dos avisos seguidos, el segundo reemplaza al primero.
- S151: el toast de encargo también comparte el label; el último aviso que llegue reemplaza al anterior.
- S152: el toast de meta también comparte el label; mismo criterio.
- S161: se quitaron `hints`, el selector EN/ES y la suscripción a `SettingsService.Changed`.
