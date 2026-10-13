---
tags: [script, ui, settings, audio]
---

# SettingsAudioSection.cs

**Ruta:** `UI/Settings/SettingsAudioSection.cs`

**Responsabilidad:** Pestaña "Audio": cinco sliders de volumen (master, música, sfx, ambiente, UI) en 0 a 1 con paso 0.01. Incluye una nota "pendiente" (`ui.settings.audio.pending`) porque los buses por grupo todavía no están conectados: hoy solo `MasterVolume` se aplica al motor (`AudioListener.volume`, en `SettingsService`).

## Campos que toca

- `MasterVolume`, `MusicVolume`, `SfxVolume`, `AmbienceVolume`, `UiVolume`

## Conexiones

- [[ISettingsSection]] — implementa
- [[SettingsRows]] — `AddSlider` y `AddNote`
- [[SettingsService]] — aplica `MasterVolume` al `AudioListener`
- [[GameSettings]] — modelo
