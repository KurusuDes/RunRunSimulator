---
tags: [script, ui, uitk, settings, hud]
---

# HudScaleApplier.cs

**Ruta:** `UI/HudScaleApplier.cs`

**Responsabilidad:** Aplica el ajuste `HudScale` de los ajustes al `PanelSettings` de un UIDocument. Captura la escala y la resolución de referencia base la primera vez y las restaura al desactivarse. Reacciona a cambios de ajustes.

## Comportamiento

- `ScaleWithScreenSize`: divide `referenceResolution` por el factor (≥ 0.1).
- Otros modos: `panel.scale = baseScale * factor`.
- `OnEnable`: suscribe `SettingsService.Changed` y aplica el valor actual.
- `OnDisable`: desuscribe y restaura el panel base.

## Campos serializados

- `panel` (`PanelSettings`)

## Conexiones

- [[SettingsService]] — `Current` y evento `Changed`
- [[GameSettings]] — `HudScale`
- Presente en los HUD UITK (vía `UIDocument` con su `PanelSettings`)
