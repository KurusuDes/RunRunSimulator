---
tags: [script, ui, settings, video]
---

# SettingsVideoSection.cs

**Ruta:** `UI/Settings/SettingsVideoSection.cs`

**Responsabilidad:** Pestaña "Vídeo": modo de pantalla (ventana, exclusiva, sin bordes), resolución (nativa + las de `SettingsService.Resolutions`), vsync, límite de FPS (0, 30, 60, 120, 144, 240) y calidad (nombres de `QualitySettings`). Escribe en el draft; los cambios se aplican al guardar.

## Campos que toca

- `ScreenMode`, `ResolutionWidth`, `ResolutionHeight`, `VSync`, `FpsCap`, `QualityLevel`

## Defaults (ResetToDefaults)

Usa `new GameSettings()` como referencia para los 6 campos de esta sección.

## Conexiones

- [[ISettingsSection]] — implementa
- [[SettingsRows]] — dropdowns y toggle
- [[SettingsService]] — `Resolutions`, `QualityNames`
- [[GameSettings]] — modelo
