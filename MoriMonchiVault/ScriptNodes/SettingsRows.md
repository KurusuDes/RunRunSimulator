---
tags: [script, ui, uitk, settings, helpers, static]
---

# SettingsRows.cs

**Ruta:** `UI/Settings/SettingsRows.cs`

**Responsabilidad:** Helpers estáticos para construir filas del panel de ajustes (encabezado, nota, dropdown, slider, toggle). Cada fila es `label + control` con clases `set-row*`. No guarda estado; el cambio se comunica por callbacks `Action`.

## Métodos públicos

| Método | Descripción |
|--------|-------------|
| `Percent(float)` | Formato "NN %" |
| `AddHeader(content, titleKey)` | Título de sección (`set-header`) |
| `AddNote(content, noteKey)` | Nota (`set-note`) |
| `AddDropdown(content, labelKey, choices, index, onChange)` | `DropdownField` (`set-dropdown`); no hace nada si no hay opciones |
| `AddSlider(content, labelKey, min, max, step, value, format, onChange)` | `Slider` con snap al paso y etiqueta de valor |
| `AddToggle(content, labelKey, value, onChange)` | `Toggle` (`set-toggle`) |

## Conexiones

- Usadas por todas las `Settings*Section`
- [[ISettingsSection]] — contrato de las secciones
- [[Loc]] — `Loc.Tr` para etiquetas
