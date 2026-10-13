---
tags: [script, systems, settings, persistence, static]
---

# SettingsService.cs

**Ruta:** `Systems/Settings/SettingsService.cs`

**Responsabilidad:** Servicio estático de ajustes. Dueño de la instancia activa de `GameSettings`: la carga desde `PlayerPrefs` (JSON), la aplica al motor (calidad, vsync, FPS, resolución/modo de pantalla, volumen global, idioma) y la notifica. Aplica también al arrancar la escena (`RuntimeInitializeOnLoadMethod AfterSceneLoad`).

## Eventos (static)

| Evento | Payload | Cuándo |
|--------|---------|--------|
| `Changed` | `GameSettings` (copia activa) | Tras `Apply` |

## Propiedades y métodos públicos

| Miembro | Descripción |
|---------|-------------|
| `Current` | Instancia activa (carga perezosa desde PlayerPrefs) |
| `Resolutions` | Resoluciones de `Screen.resolutions` sin duplicados, ordenadas de mayor a menor (cache) |
| `QualityNames` | `QualitySettings.names` |
| `Apply(GameSettings s)` | Clona, persiste en `PlayerPrefs` (clave `mm.settings`), aplica al motor y dispara `Changed` |

## Invariantes

- Si el JSON falla o no existe, devuelve `new GameSettings()` (defaults).
- Idioma: si la localización no está inicializada, espera `InitializationOperation.Completed`; cambia con `Loc.SetLocale` solo si difiere de `Loc.CurrentCode`.
- Es el único lugar que escribe `PlayerPrefs` de ajustes.

## Conexiones

- [[GameSettings]] — modelo
- [[SettingsPanelUITK]] — pide `Current`, llama `Apply`
- [[HudScaleApplier]] — escucha `Changed` para escalar el HUD
- [[Loc]] — cambio de idioma
- Secciones `Settings*Section` — leen `Resolutions` y `QualityNames`
