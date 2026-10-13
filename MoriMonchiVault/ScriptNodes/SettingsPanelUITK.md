---
tags: [script, ui, uitk, settings, panel]
---

# SettingsPanelUITK.cs

**Ruta:** `UI/SettingsPanelUITK.cs`

**Responsabilidad:** Panel de ajustes UITK. Tiene navegación por pestañas (una `ISettingsSection` por pestaña), trabaja sobre un **draft** (copia de `SettingsService.Current`) y solo al pulsar Aplicar llama `SettingsService.Apply`. Permite restablecer la sección activa a sus defaults y volver.

## Secciones (orden de pestañas)

`SettingsGeneralSection`, `SettingsVideoSection`, `SettingsInterfaceSection`, `SettingsControlsSection`, `SettingsAudioSection`.

## Flujo

- `Open()` (al mostrar o al pedirlo por `UIManager`): clona `Current` en `draft` y refresca textos.
- Aplicar: `SettingsService.Apply(draft.Clone())` + mensaje de estado 2.5 s.
- Restablecer: `sections[activeSection].ResetToDefaults(draft)` y reconstruye contenido.
- Volver: si `UIManager.Present`, pide cerrar el panel; si no, oculta y dispara `Closed`.

## Eventos

- Públicos: `Closed` (Action), consumido por `PauseMenuUITK`.
- Suscritos: `UIManager.OnPanelToggleRequested`, `UIManager.OnPanelSetRequested`.

## Campos serializados

- `document` (`UIDocument`), `panel` (`UIPanelType`, default `Settings`)

## Conexiones

- [[SettingsService]] — `Current`, `Apply`
- [[GameSettings]] — draft
- [[ISettingsSection]] y `Settings*Section` — pestañas
- [[SettingsRows]] — helpers de fila (usados por las secciones)
- [[UIManager]] — eventos de visibilidad
- [[UiPanels]] — `RootOf`, `SetActiveIndex`
- [[PauseMenuUITK]] — lo abre desde pausa
