---
tags: [script, data, struct]
---

# BrawlTheme.cs

**Ruta:** `Data/Brawl/BrawlTheme.cs`

**Responsabilidad:** Struct serializable que encapsula identidad visual de parte para Brawl: ícono, color, etiqueta, firma. Factory estático `Resolve()` computa BrawlTheme a partir de BodyPart + overrides.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Estructura

```csharp
[System.Serializable]
public struct BrawlTheme
{
    public Sprite Icon;               // Ícono pixel art de parte
    public Color Color;               // Color del set (PartSetSO.Color)
    public string Label;              // Nombre de parte (BodyPart.Name)
    public BrawlSignature Signature;  // Firma visual (rainbow, storm, etc.)
}
```

## Método Factory: Resolve()

```csharp
public static BrawlTheme Resolve(BodyPart part, Sprite iconOverride, Color colorOverride, BrawlSignature signature = BrawlSignature.None)
{
    bool hasPart = part != null;
    Sprite icon = hasPart && part.Icon != null ? part.Icon : iconOverride;

    Color color;
    if (colorOverride.a > 0.01f) color = colorOverride;           // Override > Set > White
    else if (hasPart && part.Set != null) color = part.Set.Color;
    else color = Color.white;
    color.a = 1f;                                                   // Asegura alpha=1

    return new BrawlTheme
    {
        Icon = icon,
        Color = color,
        Label = hasPart ? part.Name : "",
        Signature = signature
    };
}
```

**Lógica:**
- **Ícono:** part.Icon si existe, sino iconOverride (fallback)
- **Color:** colorOverride (si alpha > 0.01) > part.Set.Color > Color.white
- **Label:** part.Name si part existe, sino vacío
- **Signature:** pasado como parámetro (determinado por skill/wing en BrawlSkillSO/BrawlWingKitSO)

## Casos de uso

| Contexto | Llamador | Parámetros |
|----------|----------|-----------|
| Wing básico | BrawlFighter.SetWing() | part=wing part, iconOverride=WingKitSO.IconOverride, colorOverride=WingKitSO.ColorOverride, signature=WingKitSO.Signature |
| Skill cuerno | BrawlFighter.SetHornSkill() | part=horn part, iconOverride=SkillSO.IconOverride, colorOverride=SkillSO.ColorOverride, signature=SkillSO.Signature |
| Skill espalda | BrawlFighter.SetBackSkill() | part=back part, iconOverride=SkillSO.IconOverride, colorOverride=SkillSO.ColorOverride, signature=SkillSO.Signature |

## Dependencias

**Entrada:**
- `BodyPart.Icon` (sprite del ícono)
- `BodyPart.Set` (PartSetSO para color)
- `BodyPart.Name` (etiqueta)
- `BrawlSkillSO.IconOverride`, `ColorOverride`, `Signature`
- `BrawlWingKitSO.IconOverride`, `ColorOverride`, `Signature`

**Salida:**
- Usada en `BrawlHudCard.AddSlot()` (tintado de slot, ícono)
- Usada en `BrawlOverheads.HandleCastStarted()` (bubble icon y border)
- Usada en `BrawlHud.HandleKnockedOut()` (ícono del feed)
- Usada en `BrawlVfx` (tintado de proyectiles, partículas)

## Notas S142

- Struct pequeño sin estado mutable
- Factory pattern permite lazy evaluation (no computa color hasta que se necesita)
- Color.a siempre 1f (asegura opacidad total en UI)
- Fallback a iconOverride para partes sin ícono propio (modelo sin render propio antes de S142)
