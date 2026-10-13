---
tags: [script, ui, settings, interface]
---

# ISettingsSection.cs

**Ruta:** `UI/Settings/ISettingsSection.cs`

**Responsabilidad:** Contrato de una pestaña del panel de ajustes. Cada sección dibuja sus filas sobre un `VisualElement` a partir de un `GameSettings` (draft) y sabe restablecer sus propios campos a los defaults.

## Miembros

| Miembro | Descripción |
|---------|-------------|
| `string TitleKey` | Clave de localización del título de la pestaña |
| `void Build(VisualElement content, GameSettings draft)` | Dibuja las filas y escribe cambios en el draft |
| `void ResetToDefaults(GameSettings draft)` | Restablece solo los campos de esta sección |

## Implementaciones

- [[SettingsGeneralSection]] — idioma
- [[SettingsVideoSection]] — modo, resolución, vsync, FPS, calidad
- [[SettingsInterfaceSection]] — nombres, escala HUD, pistas de teclas
- [[SettingsControlsSection]] — sensibilidad, invertir Y, FOV
- [[SettingsAudioSection]] — volúmenes

## Conexiones

- [[SettingsPanelUITK]] — dueño del array de secciones
- [[SettingsRows]] — helpers de construcción
- [[GameSettings]] — draft
