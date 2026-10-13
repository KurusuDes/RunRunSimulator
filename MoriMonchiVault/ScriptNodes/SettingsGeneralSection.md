---
tags: [script, ui, settings, locale]
---

# SettingsGeneralSection.cs

**Ruta:** `UI/Settings/SettingsGeneralSection.cs`

**Responsabilidad:** Pestaña "General" de ajustes: selector de idioma. Lista los locales disponibles de `LocalizationSettings` con su nombre nativo (capitalizado) y escribe el `LocaleCode` elegido en el draft. Los cambios efectivos ocurren al aplicar (`SettingsService.Apply`).

## Campos que toca

- `draft.LocaleCode`

## Conexiones

- [[ISettingsSection]] — implementa
- [[SettingsRows]] — `AddDropdown`
- [[SettingsService]] — aplica el idioma al guardar
- [[Loc]] — código activo (`Loc.CurrentCode`)
