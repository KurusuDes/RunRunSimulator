---
tags: [script, ui, expedition, return, uitk, navigable]
---

# ExpeditionReturnCardUITK.cs

**Ruta:** `UI/ExpeditionReturnCardUITK.cs`

**Responsabilidad:** Tarjeta de resultado al volver de una bajada. Escucha `GameEvents.OnExpeditionReturned`, muestra el título (ganada o perdida), la Minerita ganada, las salas superadas, la Minerita perdida en derrota, la lista del equipo con evolución o progreso de exploración y el aviso de Slime no explorable tras una derrota. Es presentación pura: no persiste ni toca la nube. Reemplaza el toast de retorno que tenía `InfoOverlayUITK`.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `document` | `UIDocument` | — | Root del panel (`UiPanels.RootOf`) |
| `panel` | `UIPanelType` | `ExpeditionReturn` | Clave de registro en `UIManager` |

## Elementos UXML

`ret-title`, `ret-minerita`, `ret-rooms`, `ret-lost`, `ret-noexploration`, `ret-team` (contenedor de tarjetas), `ret-continue` (botón de cierre).

## Métodos y Eventos

| Miembro | Descripción |
|---------|-------------|
| `OnEnable` / `OnDisable` | Suscribe y desuscribe `GameEvents.OnExpeditionReturned` |
| `OnExpeditionReturned(r)` | Guarda `pending` y arranca una corrutina que espera dos frames antes de mostrar |
| `Show(r)` | Llena labels, línea de pérdida (si `Lost` y `MineritaLost > 0`), equipo, línea de no exploración (si `Lost` y hay Slime) y llama `UIManager.RequestPanelSet(panel, true)` |
| `BuildMember(dna, grew, explorationsToEvolve)` | Tarjeta por MoriMochi. Si `EvolvedIds` contiene su `UniqueID`, clase `ret-card--grew` y badge `ui.return.grew`. Si no, y es Slime, pips de exploración |
| `OnUISubmit` / `Close` | Cierra con `RequestPanelSet(panel, false)` |
| `OnUICancel` | Devuelve false |

## Conexiones

- [[ExpeditionBridge]] — publica `ExpeditionReturned` con el payload completo
- [[ExpeditionHandoff]] — tipo `ExpeditionReturn`
- [[GameEvents]] — `OnExpeditionReturned`
- [[UIManager]] — `RequestPanelSet`, `RegisterNavigable`, `UnregisterNavigable`
- [[UiPanels]] — `RootOf`
- [[UIPanelType]] — `UIEnums.cs`, valor `ExpeditionReturn = 9`
- [[MonchiPortraitUI]] — retrato de cada tarjeta
- [[CreatureDNA]] — `Form`, `Explorations`, `CustomName`, `UniqueID`
- [[Loc]] — textos `ui.return.*`

## Notas

- Registro navegable en `Start`, desregistro en `OnDestroy`.
- El payload `ExpeditionReturn` (`Team`, `EvolvedIds`, `ExplorationsToEvolve`, `MineritaLost`) lo consume solo esta tarjeta.
- Si el evento llega antes de que `Start` enlace los elementos (`wired` false) y sigue sin enlazar tras dos frames, no muestra nada y deja `pending` guardado.
