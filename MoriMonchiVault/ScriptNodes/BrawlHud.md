---
tags: [script, ui, component]
---

# BrawlHud.cs

**Ruta:** `UI/BrawlHud.cs`

**Responsabilidad:** Hub de HUD para Brawl 3v3. Vincula UIDocument (BrawlHud.uxml), maneja fase y MVP, crea BrawlHudCard por fighter, feed de KOs y banners de evento. Delega el reloj y los botones de velocidad a `BrawlHudClock`. Oculta la columna roja mientras hay una sala de prueba activa. Oculta los botones Nueva Partida y Revancha cuando la partida es `Driven` (bajada). En partidas `Driven` no muestra el cartel de ganador ni el MVP: al terminar solo oculta el banner, y el resultado lo muestran `BrawlRunHud` y `BrawlRunPanel`. Singleton implícito vía MonoBehaviour.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Campos Principales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | UIDocument | Root del documento UXML (BrawlHud.uxml) |
| `tuning` | BrawlTuningSO | Reference a tuneos (colores de equipo) |
| `clock` | ArenaClockControl | Optional; se pasa a `BrawlHudClock` para los botones de velocidad |
| `palette` | ArenaPaletteApplier | Optional, para nombre del mapa |
| `trial` | BrawlTrialRoom | Optional; mientras `Active`, oculta la columna roja y se pasa al reloj |
| `cards` | Dictionary<BrawlFighter, BrawlHudCard> | Map de fighters → cards del HUD |
| `hudClock` | BrawlHudClock | Reloj y velocidad; se crea y une en `TryBind` |
| `rivalHidden` | bool | Estado de la columna roja (evita reescribir el estilo) |
| `root` | VisualElement | Root del documento (brawl-root) |
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
| `BrawlMatch.OnMatchEnded` | `HandleEnded()` | Muestra ganador + MVP; en `Driven` solo oculta el banner |
| `BrawlMatch.OnLastStand` | `HandleLastStand()` | Muestra "¡ÚLTIMO EN PIE!" + nombre |
| `BrawlFighter.OnKnockedOut` | `HandleKnockedOut()` | Agrega entry al feed |
| `BrawlSkillCaster.OnCastFired` | `HandleCastFired()` | Pulse en card cuando skill castea |

## Métodos Privados Principales

| Método | Descripción |
|--------|-------------|
| `TryBind()` | Busca elementos en doc, crea y une `hudClock`; retorna false si no está listo |
| `Unbind()` | Limpia referencias, suscripciones y `hudClock` |
| `RebuildCards()` | Crea BrawlHudCard por fighter (azul/rojo según equipo); muestra u oculta Nueva/Revancha según `Driven` |
| `RefreshRivalCards()` | Oculta la columna roja mientras `trial.Active` y la vuelve a mostrar al terminar |
| `RefreshPhase()` | Actualiza label de fase + rampa KO |
| `RefreshMatch()` | Actualiza número partida + semilla + bioma |
| `RefreshCountdown()` | Muestra countdown (3, 2, 1) |
| `ShowBanner()` | Muestra banner con animación pop |
| `HideBanner()` | Oculta banner |
| `MvpText(BrawlMatch, ExpeditionTeam winner)` | Calcula texto MVP. **S147:** solo elige entre los fighters del equipo ganador; si el resultado es empate (`None`), considera a todos |

El reloj y la velocidad ya no los actualiza `BrawlHud`: los refresca `hudClock.Refresh(match)` (ver `BrawlHudClock`).

## Flujo de Partida

1. **OnEnable:** Suscribe eventos, intenta bind
2. **OnRosterSpawned:** Oculta banner, crea cards por fighter
3. **OnPhaseChanged (Countdown):** Oculta banner anterior; luego RefreshCountdown muestra 3, 2, 1
4. **OnPhaseChanged (Fight):** Muestra "¡A PELEAR!"
5. **Update (cada frame):** `hudClock.Refresh`, RefreshRivalCards, RefreshPhase, RefreshMatch, RefreshCountdown y Refresh de cada card
6. **OnPhaseChanged (SuddenDeath):** Muestra "¡MUERTE SÚBITA!"
7. **OnKnockedOut:** Agrega entry al feed (máx 5 visibles, auto-fade después 7s)
8. **OnLastStand:** Muestra "¡ÚLTIMO EN PIE!" + nombre survivor
9. **OnMatchEnded:** En partida normal muestra "¡GANA X!" (o "¡EMPATE!") + MVP con hold infinito. En `Driven` oculta el banner y no muestra MVP
10. **Próximo OnRosterSpawned o Countdown:** oculta el banner
11. **OnDisable:** Desuscribe, unbind

## Constantes S142

```csharp
private const int FeedMax = 5;
private const long FeedLifeMs = 7000;
private const long PopReleaseMs = 60;
private const float FightHold = 0.9f;
private const float SuddenHold = 1.6f;
```

Equivalen a: máximo de entradas en el feed, vida de cada entrada (7 s), duración del pop del banner (60 ms), tiempo de "¡A PELEAR!" y de "¡MUERTE SÚBITA!" / "¡ÚLTIMO EN PIE!".

## Referencia: Classes/Elements UXML S142

```
brawl-root
├── brawl-banner-box          (invisible al inicio)
│   └── brawl-banner          (label, pop animation)
│       └── brawl-banner-sub  (subtítulo)
├── brawl-row (info)
│   ├── brawl-timer           (reloj mm:ss; lo une BrawlHudClock)
│   ├── brawl-phase           (PREPARADOS, PELEA, MUERTE SÚBITA)
│   └── brawl-match           (Partida 42 · semilla 12345 · Bosque)
├── brawl-speed (si clock presente)
│   ├── brawl-speed-1         (botón 1x)
│   ├── brawl-speed-2         (botón 2x)
│   └── brawl-speed-4         (botón 4x)
├── brawl-grid
│   ├── brawl-cards-blue      (columna azul)
│   └── brawl-cards-red       (columna roja; se oculta durante la prueba)
├── brawl-feed                (log de KOs)
└── brawl-actions
    ├── brawl-new             (Nueva Partida; oculto si Driven)
    └── brawl-rematch         (Revancha; oculto si Driven)
```

## Dependencias

**Entrada:**
- `BrawlTuningSO` (colores de equipo)
- `ArenaClockControl` (optional, vía `BrawlHudClock`)
- `ArenaPaletteApplier` (optional, nombre mapa)
- `BrawlTrialRoom` (optional, `Active`)
- Eventos estáticos de `BrawlMatch`, `BrawlFighter`, `BrawlSkillCaster`
- `BrawlMatch.Current` (para `Driven` y MVP)

**Salida:**
- Crea `BrawlHudCard` (uno por fighter) y `BrawlHudClock`
- Llama `BrawlMatch.NewMatch()` / `Rematch()` vía botones
- Renderiza cards, feed, banners, labels en UIDocument

## Notas

- TryBind() retorna false si documento no listo (permite esperar a inicialización de UXML)
- Unbind() se llama en OnDisable y cuando documento cambia
- lastCount/lastPhase/etc son optimizaciones para no recomputar si no cambió
- Feed es auto-scrolling (últimas 5 entries visibles, más viejas fadean)
- MVP calcula daño, curación, KOs (mostrado en ganador al fin, solo en partidas no `Driven`)
- Banner tiene pop animation (pequeño → normal en 60ms)
- Colores de equipo vienen de tuning (editables sin modificar código)
- Textos de banner y feed hardcodeados en español (no pasan por `Loc`)

## Notas S144

- En partidas `Driven` (bajada Brawl, dirigidas por `BrawlRunDirector`) los botones Nueva Partida y Revancha quedan ocultos. Se decide en `RebuildCards()`, que corre en cada roster.

## Notas S145

- El reloj y los botones de velocidad salieron a `BrawlHudClock`; `BrawlHud` solo lo crea, lo une, lo desune y lo refresca.
- `RefreshRivalCards` oculta la columna roja con `trial.Active` (salas de muñecos y minerales) y la restaura al terminar la prueba.
- El banner de fin de partida muestra "¡EMPATE!" cuando el ganador es `None`. Para la bajada, ese empate cuenta como victoria en `BrawlRunDirector`.

## Notas S146

- En `Driven` el cierre de partida no muestra cartel ni MVP: `HandleEnded` solo oculta el banner. La bajada decide qué sigue (`BrawlRunDirector` pasa a `RoomResult` u `Over`), y lo muestran `BrawlRunHud` y `BrawlRunPanel`.

## Notas S147

- El MVP del banner de fin sale solo del equipo ganador (`MvpText` filtra por `Team == winner`). En empate (`None`) se evalúan todos los fighters. Antes el MVP era global.
