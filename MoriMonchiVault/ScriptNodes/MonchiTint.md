---
tags: [script, genetics, color, core]
---

# MonchiTint.cs

**Ruta:** `Core/MonchiTint.cs`

**Responsabilidad:** Utilidad estática que mapea colores genéticos a renderers y rellena MaterialPropertyBlocks con la paleta de colores. **S136 NUEVO.** Extraída de MonchiVisualizer para reutilización en EggLabAssembler. Dos métodos: `ColorFor()` determinista (por nombre renderer + DNA + harmonic colors), `Fill()` que arma el MPB con los 4 colores del toon shader (Base, Shade1, Shade2, Rim).

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `ColorFor(string rendererName, CreatureDNA dna, Color wing, Color accent)` | `Color` | Mapeo determinista: Deco_* (parsea hex), Wing* (harmonic wing), Horn/Back (harmonic accent), Teech (blend white), default (base color). |
| `Fill(MaterialPropertyBlock mpb, Color color)` | `void` | Llena MPB con `_BaseColor`, `_1st_ShadeColor`, `_2nd_ShadeColor`, `_RimLightColor` usando `ColorGenetics.BuildFurPalette()` + rim derivado. |

## Método ColorFor()

**Firma:**
```csharp
public static Color ColorFor(string rendererName, CreatureDNA dna, Color wing, Color accent)
```

**Lógica (por orden de evaluación):**
1. Si rendererName comienza con "Deco_" y tiene 11+ caracteres → intenta parsear hex 6-dígitos (índices 5-10, ej. "Deco_FF00AA") → retorna ese color
   - Ej: "Deco_FF00AA" → new Color(1, 0, 2/3)
   - Fallback: Si TryParseHtmlString falla, continúa evaluación
2. Si rendererName comienza con "Wing" → retorna `wing` (harmonic del BuildHarmony)
3. Si rendererName comienza con "Horn" o "Back" → retorna `accent` (harmonic del BuildHarmony)
4. Si rendererName es exactamente "Teech" → retorna `Color.Lerp(Color.white, dna.BaseColor, 0.12f)` (casi blanco, 12% base)
5. Default → retorna `dna.BaseColor` (cuerpo principal)

**Determinismo:**
- Mismo rendererName + DNA → mismo color siempre
- Harmonic wing/accent ya son deterministas vía FNV-1a hash en `ColorGenetics.BuildHarmony()`

## Método Fill()

**Firma:**
```csharp
public static void Fill(MaterialPropertyBlock mpb, Color color)
```

**Flujo:**
1. Genera paleta desde color vía `ColorGenetics.BuildFurPalette(color, ColorGenetics.DeriveSecondary(color))`
   - Base = color pasado
   - Shade1 = tonalidad oscura
   - Shade2 = tonalidad media
   - Rim = Lerp(color, white, 65%) + ajuste final
2. Escribe 4 propiedades Shader:
   - `_BaseColor` = palette.Base
   - `_1st_ShadeColor` = palette.Shade1
   - `_2nd_ShadeColor` = palette.Shade2
   - `_RimLightColor` = Lerp(color, white, 0.65f) (rim final)

**Invariante:** Rim NO es sobrescrito si existe rimOverride (ese es responsabilidad del caller, MonchiVisualizer.Tint())

## IDs Shader Cacheados

```csharp
private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
private static readonly int Shade1ColorId = Shader.PropertyToID("_1st_ShadeColor");
private static readonly int Shade2ColorId = Shader.PropertyToID("_2nd_ShadeColor");
private static readonly int RimColorId = Shader.PropertyToID("_RimLightColor");
```

Obtenidos una sola vez en inicialización estática; evita búsquedas repetidas.

## Cambios S136

**Extracción de lógica de MonchiVisualizer:**
- Antes: MonchiVisualizer tenía inline `ColorFor()` y `Fill()`
- Ahora: Ambos métodos movidos a MonchiTint.cs como utilidad estática reutilizable
- EggLabAssembler, MonchiVisualizer y futuros visualizadores comparten la misma regla de color

**Línea 12-23 ColorFor() equivalente a MonchiVisualizer.ApplyLook() lógica vieja:**
```csharp
// Viejo inline en MonchiVisualizer:
if (name.StartsWith("Deco_") && ...) { ... }
if (name.StartsWith("Wing")) { ... }
// ...

// Nuevo: MonchiTint.ColorFor()
```

**Línea 25-32 Fill() equivalente a MonchiVisualizer.Tint() lógica vieja:**
```csharp
// Viejo inline en MonchiVisualizer.Tint():
var palette = ColorGenetics.BuildFurPalette(...);
mpb.SetColor(_BaseColorId, palette.Base);
// ...

// Nuevo: MonchiTint.Fill()
```

## Notas S136

- Utilidad sin estado (static)
- Cacheado PropertyToID (performance)
- Usado por MonchiVisualizer.ApplyLook() y EggLabAssembler.Build()
- ColorFor() respeta identidad de partes genéticas (Wing/Horn/Back/Teech/Body)
- Rim final es derivado, NO genético (ese cálculo completo queda en ColorGenetics)

## Vinculado a

- [[ColorGenetics]] — BuildFurPalette(), BuildHarmony(), DeriveSecondary()
- [[MonchiVisualizer]] — **S136 MODIFICADO** usa MonchiTint.ColorFor() y MonchiTint.Fill()
- [[EggLabAssembler]] — **S136 NUEVO** usa MonchiTint en Build()
- [[Index/10 - Visualization]]

## Conexiones

**Llamadores:**
- `MonchiVisualizer.ApplyLook()` → ColorFor + Fill
- `MonchiVisualizer.Tint()` → Fill
- `EggLabAssembler.Build()` → ColorFor + Fill

**Dependencias:**
- ColorGenetics (BuildFurPalette, DeriveSecondary, BuildHarmony)
- CreatureDNA (BaseColor, BodyShapeID, etc.)
