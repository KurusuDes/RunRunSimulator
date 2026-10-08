---
tags: [script, ui, component]
---

# BrawlOverheads.cs

**Ruta:** `UI/BrawlOverheads.cs`

**Responsabilidad:** Plates overhead (HP + intención + bubble de skill) + floats (números que suben de daño/curación). Pool de floats reutilizable. Mantiene estado de cada fighter en `Plate`, renderiza en UIDocument overlay.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Nested Classes

### Plate (estado de fighter)

```csharp
private class Plate
{
    public BrawlFighter Fighter;
    public VisualElement Anchor;            // Contenedor (translado world→screen)
    public VisualElement Body;              // Nombre + barras
    public VisualElement Fill;              // Barra de HP (width %)
    public VisualElement Shield;            // Overlay de escudo
    public Label Status;                    // "aturdido", "provocado"
    public VisualElement Bubble;            // Bubble de skill casteo
    public Image BubbleIcon;                // Ícono en bubble
    public Label BubbleText;                // Título skill en bubble
    public Vector2 LastPos;                 // Cached para no reupdatear translate
    public float LastHp, LastShield = -1f;
    public float LastScale = 1f;
    public int LastStatus;
    public bool Shown;
    public bool Alive = true;
    public float BubbleStart, BubbleEnd = -1f;
}
```

### FloatText (pool de números flotantes)

```csharp
private class FloatText
{
    public VisualElement Anchor;            // Contenedor (translado)
    public Label Label;                     // Texto ("+500", "-300", "escudo")
    public string Variant;                  // Clase CSS (brawl-float--hit, --skill, --heal, etc.)
    public Vector3 World;                   // Posición world donde flotará
    public float Start;                     // Time.unscaledTime spawn
    public float Jitter;                    // Offset X aleatorio
    public float Lane;                      // Offset Y (0, 18, 36 para 3 lanes)
    public bool Active;                     // Si está en uso
}
```

## Campos Principales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | UIDocument | Root del documento UXML (overlay) |
| `tuning` | BrawlTuningSO | Colores de equipo |
| `headOffset` | float | Altura offset del head (1,5 = 1,5m sobre centro) |
| `plates` | Dictionary<BrawlFighter, Plate> | Map fighters → overhead plates |
| `pool` | FloatText[40] | Pool de números flotantes (reutilizable) |
| `layer` | VisualElement | Layer raíz de overheads |
| `platesGroup` | VisualElement | Contenedor de plates |
| `floatsGroup` | VisualElement | Contenedor de floats |

## Suscripciones de Evento

| Evento | Manejador | Descripción |
|--------|-----------|-------------|
| `BrawlMatch.OnRosterSpawned` | `HandleRoster()` | Recrea plates |
| `BrawlFighter.OnDamaged` | `HandleDamaged()` | Spawn float "-X" |
| `BrawlFighter.OnHealed` | `HandleHealed()` | Spawn float "+X" |
| `BrawlFighter.OnShielded` | `HandleShielded()` | Spawn float "escudo" |
| `BrawlSkillCaster.OnCastStarted` | `HandleCastStarted()` | Muestra bubble con skill |

## Métodos Principales

| Método | Descripción |
|--------|-------------|
| `TryBind()` | Busca root, recrea layer si no existe |
| `Unbind()` | Limpia plates, floats, elementos |
| `Rebuild()` | Limpia plates viejas, crea nuevas por fighters |
| `BuildPlate()` | Construye visual de plate para fighter |
| `BuildFloat()` | Construye slot de FloatText en pool |
| `UpdatePlate()` | LateUpdate: posición, HP, escudo, intención, bubble |
| `UpdateFloat()` | LateUpdate: posición floating, opacity fade |
| `SpawnFloat()` | Crea float desde pool, asigna posición y variante |
| `HandleDamaged()` | Dispara SpawnFloat("-X") |
| `HandleHealed()` | Dispara SpawnFloat("+X") |
| `HandleShielded()` | Dispara SpawnFloat("escudo") |
| `HandleCastStarted()` | Setea bubble icon, text, border, scale, timing |

## Flujo de Visualización (LateUpdate)

1. **Para cada Plate:**
   - Obtiene Fighter.Center + headOffset → world
   - Chequea camera frustum (visibilidad)
   - Transforma world → screen (RuntimePanelUtils.CameraTransformWorldToPanel)
   - Actualiza translate si cambió posición
   - Actualiza HP/Shield fill width
   - Actualiza Status label ("aturdido", "provocado")
   - Actualiza bubble (scale pop si en casting)

2. **Para cada FloatText activo:**
   - Calcula age desde spawn
   - Si age > FloatSeconds (0,8s), desactiva
   - Transforma world → screen
   - Calcula rise (curva de aceleración)
   - Setea opacity (fade out al final)
   - Setea translado con jitter + lane

## Constantes S142

```csharp
private const int PoolSize = 40;            // Max floats simultáneos
private const float AnchorHalf = 120f;      // Mitad de ancho anchor
private const float FloatSeconds = 0.8f;    // Vida del float
private const float FloatRise = 50f;        // Altura total subida
private const float FloatJitter = 34f;      // Offset X aleatorio
private const float FloatLane = 18f;        // Spacing Y entre lanes
private const float BigDamage = 1000f;      // Umbral para tamaño grande
private const float BubbleTail = 0.7f;      // Tiempo extra bubble tras windup
private const float PopHalf = 0.12f;        // Mitad de pop animation (0,12s cada mitad)
```

## Variantes de Float (Clases CSS)

| Variante | Condición | Color |
|----------|-----------|-------|
| `brawl-float--hit` | Daño básico < 1000 | Rojo oscuro |
| `brawl-float--skill` | Daño de skill | Rojo brillante |
| `brawl-float--big` | Daño >= 1000 | Grande, dorado |
| `brawl-float--heal` | Curación | Verde |
| `brawl-float--shield` | Escudo | Azul |

## Método SpawnFloat()

```csharp
private void SpawnFloat(Vector3 world, string text, string variant)
{
    if (layer == null) return;
    
    var item = pool[spawned % pool.Length];  // Reutiliza slot del pool
    spawned++;
    
    if (item.Variant != variant)
    {
        if (item.Variant != null) item.Label.RemoveFromClassList(item.Variant);
        item.Label.AddToClassList(variant);
        item.Variant = variant;
    }
    
    item.Label.text = text;
    item.Label.style.opacity = 0f;
    item.World = world;
    item.Start = Time.unscaledTime;
    item.Jitter = (Mathf.Repeat(spawned * 0.618034f, 1f) * 2f - 1f) * FloatJitter;  // Golden ratio
    item.Lane = (spawned % 3) * FloatLane;  // 3 lanes para evitar superposición
    item.Active = true;
}
```

**Golden ratio jitter:** Distribuye floats uniformemente sin patrón repetitivo.

## Método HandleCastStarted()

```csharp
private void HandleCastStarted(BrawlFighter fighter, BrawlSkillSO skill, Vector3 aim)
{
    if (skill == null || fighter == null || !plates.TryGetValue(fighter, out var plate)) return;
    
    var theme = fighter.HornSkill == skill ? fighter.HornTheme : fighter.BackTheme;
    
    plate.BubbleIcon.sprite = theme.Icon;
    plate.BubbleIcon.tintColor = theme.Color;
    plate.BubbleIcon.style.display = theme.Icon != null ? DisplayStyle.Flex : DisplayStyle.None;
    plate.BubbleText.text = skill.Title + "!";
    
    // Setea borders con color de tema
    var border = theme.Color;
    border.a = 1f;
    plate.Bubble.style.borderTopColor = border;
    // ... etc
    
    plate.LastScale = PopScale(0f);
    plate.Bubble.style.scale = new Scale(new Vector3(plate.LastScale, plate.LastScale, 1f));
    plate.BubbleStart = Time.unscaledTime;
    plate.BubbleEnd = plate.BubbleStart + skill.Windup + BubbleTail;  // Windup + 0,7s tail
    plate.Bubble.AddToClassList("brawl-bubble--show");
}
```

**PopScale:**
```csharp
private static float PopScale(float age)
{
    if (age < PopHalf) return Mathf.Lerp(0.6f, 1.1f, age / PopHalf);       // Expand 60% → 110%
    if (age < PopHalf * 2f) return Mathf.Lerp(1.1f, 1f, (age - PopHalf) / PopHalf);  // Shrink 110% → 100%
    return 1f;
}
```

Pop animation: pequeño (60%) → grande (110%) → normal (100%) en 0,24s.

## Dependencias

**Entrada:**
- `BrawlTuningSO` (colores de equipo)
- Eventos estáticos de `BrawlFighter`, `BrawlSkillCaster`
- UIDocument (overlay layer)

**Salida:**
- Renderiza plates + floats en UIDocument
- Camera.main para transformación world→screen

## Notas S142

- Pool de 40 floats permite ~50 floats/segundo (40 × 1,25 fps)
- FloatText reutiliza anchors en pool (no instantia, solo update state)
- Jitter usa golden ratio (0,618) para distribución pseudo-aleatoria determinista
- 3 lanes (Y offset) evita stack vertical (daño, curación, escudo no se superponen)
- Bubble muestra durante windup + 0,7s tail (visible "después" de casting)
- PopScale anima escala 0,6→1,1→1 para efecto "pop" (impacto visual)
- RuntimePanelUtils.CameraTransformWorldToPanel convierte world → screen space
- Frustum check (dot product) oculta plates fuera de vista cámara
- LastPos caché evita recomputar translate si fighter no se movió
