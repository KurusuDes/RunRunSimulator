---
tags: [script, ui, component]
---

# BrawlHud.cs

**Ruta:** `UI/BrawlHud.cs`

**Responsabilidad:** Hub de HUD para Brawl 3v3. Vincula UIDocument (BrawlHud.uxml), maneja fase/reloj/MVP, crea BrawlHudCard por fighter, feed de KOs, banners de evento, speedup buttons. Singleton implícito vía MonoBehaviour.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Campos Principales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | UIDocument | Root del documento UXML (BrawlHud.uxml) |
| `tuning` | BrawlTuningSO | Reference a tuneos (colores de equipo) |
| `clock` | ArenaClockControl | Optional, para control de velocidad |
| `palette` | ArenaPaletteApplier | Optional, para nombre del mapa |
| `cards` | Dictionary<BrawlFighter, BrawlHudCard> | Map de fighters → cards del HUD |
| `speedButtons` | Button[3] | Botones 1x, 2x, 4x velocidad |
| `speedHandlers` | Action[3] | Handlers para botones |
| `root` | VisualElement | Root del documento (brawl-root) |
| `timerLabel` | Label | Reloj (mm:ss o +mm:ss en muerte súbita) |
| `phaseLabel` | Label | Estado fase (PREPARADOS, PELEA, etc.) |
| `matchLabel` | Label | Info partida (número, semilla, bioma) |
| `banner` | Label | Banner principal (¡GANA!, ¡ÚLTIMO EN PIE!, etc.) |
| `bannerSub` | Label | Subtítulo del banner |
| `newButton` | Button | Botón "Nueva Partida" |
| `rematchButton` | Button | Botón "Revancha" |
| `feed` | VisualElement | Log de últimos 5 KOs |
| `blueCards` | VisualElement | Columna de cards azules (Player team) |
| `redCards` | VisualElement | Columna de cards rojas (Rival team) |
| `bannerBox` | VisualElement | Contenedor del banner |

## Métodos Públicos

Ninguno. Acceso vía eventos estáticos (`BrawlMatch.OnPhaseChanged`, etc.)

## Suscripciones de Evento (OnEnable/OnDisable)

| Evento | Manejador | Descripción |
|--------|-----------|-------------|
| `BrawlMatch.OnRosterSpawned` | `HandleRoster()` | Reconstruye cards cuando aparecen fighters |
| `BrawlMatch.OnPhaseChanged` | `HandlePhase()` | Muestra banners según fase |
| `BrawlMatch.OnMatchEnded` | `HandleEnded()` | Muestra ganador + MVP |
| `BrawlMatch.OnLastStand` | `HandleLastStand()` | Muestra "¡ÚLTIMO EN PIE!" + nombre |
| `BrawlFighter.OnKnockedOut` | `HandleKnockedOut()` | Agrega entry al feed |
| `BrawlSkillCaster.OnCastFired` | `HandleCastFired()` | Pulse en card cuando skill castea |

## Métodos Privados Principales

| Método | Descripción |
|--------|-------------|
| `TryBind()` | Busca elementos en doc; retorna false si no está listo |
| `Unbind()` | Limpia referencias y suscripciones |
| `RebuildCards()` | Crea BrawlHudCard por fighter (azul/rojo según equipo) |
| `RefreshClock()` | Actualiza timer (mm:ss, invierte a muerte súbita) |
| `RefreshPhase()` | Actualiza label de fase + rampa KO |
| `RefreshMatch()` | Actualiza número partida + semilla + bioma |
| `RefreshCountdown()` | Muestra countdown (3, 2, 1) |
| `RefreshSpeed()` | Actualiza estado de speedup buttons |
| `ShowBanner()` | Muestra banner con animación pop |
| `HideBanner()` | Oculta banner |
| `MvpText()` | Calcula texto MVP (daño máx, curaciones, KOs) |

## Flujo de Partida

1. **OnEnable:** Suscribe eventos, intenta bind
2. **OnRosterSpawned:** Crea cards por fighter
3. **OnPhaseChanged (Countdown):** Oculta banner anterior
4. **OnPhaseChanged (Fight):** Muestra "¡A PELEAR!"
5. **Update (cada frame):** RefreshClock, RefreshPhase, RefreshMatch, RefreshCountdown, RefreshSpeed
6. **OnPhaseChanged (SuddenDeath):** Muestra "¡MUERTE SÚBITA!"
7. **OnKnockedOut:** Agrega entry al feed (máx 5 visibles, auto-fade después 7s)
8. **OnLastStand:** Muestra "¡ÚLTIMO EN PIE!" + nombre survivor
9. **OnMatchEnded:** Muestra "¡GANA X!" + MVP
10. **Update:** Si 6s desde fin, oculta banner
11. **OnDisable:** Desuscribe, unbind

## Constantes S142

```csharp
private const int FeedMax = 5;              // Max entries visibles simultáneas
private const long FeedLifeMs = 7000;       // Vida de entry en feed (7s)
private const long PopReleaseMs = 60;       // Duración pop animation (60ms)
private const float FightHold = 0.9f;       // Tiempo mostrar "¡A PELEAR!"
private const float SuddenHold = 1.6f;      // Tiempo mostrar "¡MUERTE SÚBITA!"
```

## Referencia: Classes/Elements UXML S142

```
brawl-root
├── brawl-banner-box          (invisible al inicio)
│   └── brawl-banner          (label, pop animation)
│       └── brawl-banner-sub  (subtítulo)
├── brawl-row (info)
│   ├── brawl-timer           (reloj mm:ss)
│   ├── brawl-phase           (PREPARADOS, PELEA, MUERTE SÚBITA)
│   └── brawl-match           (Partida 42 · semilla 12345 · Bosque)
├── brawl-speed (si clock presente)
│   ├── brawl-speed-1         (botón 1x)
│   ├── brawl-speed-2         (botón 2x)
│   └── brawl-speed-4         (botón 4x)
├── brawl-grid
│   ├── brawl-cards-blue      (columna azul)
│   └── brawl-cards-red       (columna roja)
├── brawl-feed                (log de KOs)
└── brawl-actions
    ├── brawl-new             (Nueva Partida)
    └── brawl-rematch         (Revancha)
```

## Dependencias

**Entrada:**
- `BrawlTuningSO` (colores de equipo)
- `ArenaClockControl` (optional, speedup)
- `ArenaPaletteApplier` (optional, nombre mapa)
- Eventos estáticos de `BrawlMatch`, `BrawlFighter`, `BrawlSkillCaster`

**Salida:**
- Crea `BrawlHudCard` (uno por fighter)
- Llama `BrawlMatch.NewMatch()` / `Rematch()` vía botones
- Renderiza cards, feed, banners, labels en UIDocument

## Notas S142

- TryBind() retorna false si documento no listo (permite esperar a inicialización de UXML)
- Unbind() se llama en OnDisable y cuando documento cambia
- lastCount/lastSeconds/etc son optimizaciones para no recomputar si no cambió
- Feed es auto-scrolling (últimas 5 entries visibles, más viejas fadean)
- MVP calcula daño, curación, KOs (mostrado en ganador al fin)
- Speedup buttons solo visibles si ArenaClockControl presente (desarrollo)
- Banner tiene pop animation (pequeño → normal en 60ms)
- Colores de equipo vienen de tuning (editables sin modificar código)
