---
tags: [script, ui, settings, controls]
---

# SettingsControlsSection.cs

**Ruta:** `UI/Settings/SettingsControlsSection.cs`

**Responsabilidad:** Pestaña "Controles": sensibilidad de mirada (0.25 a 3, paso 0.05), invertir Y y campo de visión (0 = default, o 60 a 100). Escribe en el draft. Al dibujar el FOV elige la opción más cercana al valor guardado.

## Campos que toca

- `LookSensitivity`, `InvertY`, `FieldOfView`
- `CameraBob` existe en `ResetToDefaults` pero no tiene control en esta pestaña

## Conexiones

- [[ISettingsSection]] — implementa
- [[SettingsRows]] — slider, toggle y dropdown
- [[GameSettings]] — modelo
