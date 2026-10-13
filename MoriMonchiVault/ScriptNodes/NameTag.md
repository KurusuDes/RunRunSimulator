---
tags: [script, ui, world-ui, creature-display]
---

# NameTag.cs

**Ruta:** `World/Creatures/NameTag.cs`

**Responsabilidad:** Placa flotante UITK sobre MoriMochi. Muestra nombre, gender, role, life stage, intent, precio (si está en venta), timer de cría (si está criando) y estado (muerto, en cría, frágil). Solo presenta; el modo de visibilidad viene de los ajustes (`SettingsService`).

**Historia breve:** S97 expone `ShowDistance`. S98 renderiza gestos y beating. S99 `ScreenSizeReferenceDistance` y colores de placa por team. S131 calcula la edad en días con `CreatureDNA.AgeDays(GameClock.Instance.Day)` para actualizar la etapa de vida en vivo. S149/S151: modo de visibilidad por ajustes, foco por mirada y estado "frágil".

## Campos Serializados

**Visibility:**
| Campo | Tipo | Propósito |
|-------|------|----------|
| `showDistance` | float | Distancia máxima para mostrar placa (default 8f) |
| `uprightOnly` | bool | Mantiene etiqueta vertical sin camera pitch (default true) |

**Focus (mirada):**
| Campo | Tipo | Propósito |
|-------|------|----------|
| `fadeUnlessLooked` | bool | Si la placa se atenúa cuando no se mira (default true) |
| `focusAngle` | float | Grados desde el forward de la cámara para contar como mirada (1–45, default 10) |
| `unfocusedOpacity` | float | Opacidad sin foco (default 0.35) |
| `focusFadeSpeed` | float | Velocidad del fade de foco (default 6) |
| `closeShrinkDistance` | float | Por debajo de esta distancia la placa se encoge (default 3) |
| `minCloseScale` | float | Escala mínima al encoger (0.1–1, default 0.55) |

**Pen Layout (breeding):**
| Campo | Tipo | Propósito |
|-------|------|----------|
| `penRaise` | float | Altura extra en m cuando penned (default 0.6) |
| `penScale` | float | Escala uniforme cuando penned (default 0.8) |
| `screenSizeReferenceDistance` | float | Escala adaptativa por distancia si > 0 (S99) |
| `allyNameColor` | Color | Color nombre si Team==Player (default verde pastel) |
| `rivalNameColor` | Color | Color nombre si Team==Rival (default rojo pastel) |
| `rivalRevealSpeed` | float | Velocidad fade-in de rival (default 4f) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `ShowDistance` | float | Getter/setter para `showDistance` (S97) |
| `ScreenSizeReferenceDistance` | float | Getter/setter para `screenSizeReferenceDistance` (S99) |
| `FadeUnlessLooked` | bool | Getter/setter para `fadeUnlessLooked` (ArenaSandbox la apaga en los elencos) |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Bind(CreatureDNA creature, MoriMochiAgent agent)` | Wireo de DNA y agente. Resuelve UXML, aplica nombre/color, llama Refresh |

## Visibilidad (ajustes)

- `nameTagMode` se toma de `SettingsService.Current.NameTags` al habilitarse y se actualiza con `SettingsService.Changed`.
- `Never`: la placa no se muestra.
- `WhenLooked` (default) y `Always`: se muestra dentro de `showDistance`. Con `Always` no hay atenuación por mirada.
- Un rival (Team == Rival) aparece con fade (`reveal`) solo cuando `ExpeditionNav.IsRevealing(agent.Intent)`.

## Métodos Privados (Refresh)

| Método | Descripción |
|--------|-------------|
| `Refresh()` | Selector: RefreshStore / RefreshPenned / RefreshDefault según estado |
| `RefreshStore()` | Muestra precio solo (`CustomerService.EstimateAverage`) |
| `RefreshPenned()` | Muestra gender/role/stage/breed/heart+timer si criando |
| `RefreshDefault()` | Muestra nombre, estado (muerto, en cría, frágil), intent o pista de caricia |
| `StatusOf(dna)` | Muerto → rojo; en cría → rosa; `CreatureFrailty.IsFrail` → gris "frágil" (S151) |
| `StageText(int ageDays)` | Etapa de vida desde días con `BreedingController.LifeStageTable`; sin tabla, muestra "Xd" |
| `CountdownText(long readyAtMinutes)` | Cuenta atrás hasta `BreedReadyAt` (en minutos de juego) |
| `NameColor(CreatureDNA)` | Elige color por team (allyNameColor / rivalNameColor / color de género) |

## Ciclo de Vida (LateUpdate)

1. Adquiere cámara (lazy ref a Camera.main)
2. Calcula distancia a cámara, determina visibilidad (modo de ajustes + `showDistance`)
3. Si cambió visibilidad, actualiza DisplayStyle
4. Revela rival y calcula foco por mirada; aplica opacidad al root
5. **Refresh:** actualiza contenido dinámico
6. Aplica escala pen + screen-size scaling + encogimiento de cerca
7. Posiciona (altura extra si penned) y rota hacia cámara (LookRotation con upright option)

## Cálculo de Etapa de Vida (S131)

```csharp
int today = GameClock.Instance != null ? GameClock.Instance.Day : 1;
stageLabel.text = StageText(dna.AgeDays(today));
```

**Dependencias:**
- `CreatureDNA.AgeDays(int today)` — `Max(0, today - BirthDay)`
- `GameClock.Instance.Day` — día actual del juego
- `CreatureLifeStageTableSO.GetStage(ageDays)` — mapea edad → LifeStage

## Campos Internos

| Campo | Tipo | Propósito |
|-------|------|----------|
| `document` | UIDocument | Componente del mismo GO |
| `root` | VisualElement | Raíz UXML |
| `nameLabel`, `stageLabel`, `breedLabel`, `timerLabel`, `statusLabel`, `intentLabel`, `petHintLabel`, `priceLabel`, `genderLabel`, `roleLabel`, `heartLabel` | Label | Labels |
| `agent`, `dna` | ref | Wireadas en Bind |
| `cam` | Transform | Camera.main para LOD |
| `shown` | bool | Bandera de visibilidad actual |
| `reveal`, `focus`, `lastOpacity` | float | Estado de fade (rival y mirada) |
| `baseLocalPos`, `baseLocalScale` | Vector3 | Guardadas para restaurar |

## Invariantes

- Si GameClock falta, fallback a día=1
- Si LifeStageTable falta, muestra solo "Xd"
- `root.pickingMode = Ignore`: la placa nunca bloquea el raycast del jugador

## Vinculado a

- [[Index/23 - Arena Sandbox & Expedicion (S102-S103)]]
- [[Index/09 - Active Context]]

## Conexiones

**Data:**
- [[CreatureDNA]] — lee `AgeDays(int)`, `IsDead`, `BusyState`
- [[CreatureFrailty]] — estado "frágil" (S151)
- [[SettingsService]], [[GameSettings]] — modo de visibilidad (`NameTags`)
- [[MoriMochiAgent]] — referencia para lógica (Team, Intent, IsPenned, IsForSale, IsBeingPetted)

**Sistemas:**
- [[GameClock]] — proporciona `Day` y `TotalMinutes`
- [[BreedingController]] — acceso a LifeStageTable para mapeo edad→etapa
- [[CreatureLifeStageTableSO]] — lookup etapa por edad
- [[CustomerService]] — precio promedio en tienda
- [[ExpeditionNav]] — `IsRevealing` para el fade de rivales
