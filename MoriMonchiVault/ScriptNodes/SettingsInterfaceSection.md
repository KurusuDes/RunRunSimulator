---
tags: [script, ui, settings, interface]
---

# SettingsInterfaceSection.cs

**Ruta:** `UI/Settings/SettingsInterfaceSection.cs`

**Responsabilidad:** Pestaña "Interfaz": modo de etiquetas de nombre (siempre, al mirar, nunca), escala del HUD (0.75 a 1.5, paso 0.05) y pistas de teclas. Escribe en el draft.

## Campos que toca

- `NameTags` (`NameTagMode`), `HudScale`, `ShowKeyHints`

## Conexiones

- [[ISettingsSection]] — implementa
- [[SettingsRows]] — dropdown, slider y toggle
- [[GameSettings]] — modelo
- [[NameTag]] — consumidor de `NameTags` (vía ajustes)
- [[HudScaleApplier]] — consumidor de `HudScale`
