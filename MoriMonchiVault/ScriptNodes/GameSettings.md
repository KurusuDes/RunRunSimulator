---
tags: [script, data, settings, serializable]
---

# GameSettings.cs

**Ruta:** `Data/Settings/GameSettings.cs`

**Responsabilidad:** Contenedor de ajustes del jugador (idioma, video, interfaz, controles, audio). Clase serializable sin lógica salvo `Clone()` (copia superficial con `MemberwiseClone`). Se persiste como JSON en `PlayerPrefs` vía `SettingsService`. Incluye el enum `NameTagMode`.

## Campos publicos

| Grupo | Campos (default) |
|-------|------------------|
| Idioma | `LocaleCode` ("") |
| Video | `ScreenMode` (FullScreenWindow), `ResolutionWidth`/`Height` (0 = nativa), `VSync` (true), `FpsCap` (0 = sin límite), `QualityLevel` (-1 = el de Unity) |
| Interfaz | `NameTags` (WhenLooked), `HudScale` (1), `ShowKeyHints` (true) |
| Controles | `LookSensitivity` (1), `InvertY` (false), `FieldOfView` (0 = default), `CameraBob` (true) |
| Audio | `MasterVolume` (1), `MusicVolume` (0.8), `SfxVolume` (1), `AmbienceVolume` (0.8), `UiVolume` (1) |

## Enum NameTagMode

`Always`, `WhenLooked`, `Never`.

## Conexiones

- [[SettingsService]] — único dueño de la instancia activa; serializa y aplica
- [[SettingsRows]], [[ISettingsSection]] y las secciones `Settings*Section` — leen y escriben los campos del draft
- [[NameTag]] — respeta `NameTags`
- [[HudScaleApplier]] — aplica `HudScale`
