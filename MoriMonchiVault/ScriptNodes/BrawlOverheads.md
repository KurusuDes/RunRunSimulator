---
tags: [script, ui, component]
---

# BrawlOverheads.cs

**Ruta:** `UI/BrawlOverheads.cs`

**Responsabilidad:** Plates overhead (HP, escudo, estado y burbuja de skill) y floats (números que suben de daño, curación y escudo). Pool de floats reutilizable. Mantiene el estado de cada fighter en `Plate` y renderiza en una capa overlay del UIDocument. Los muñecos de sala de prueba no muestran nombre. Al caer un fighter, su plate pasa a `brawl-plate--ko` y se cierra su burbuja.

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
    public float LastHp = -1f;
    public float LastShield = -1f;
    public float LastScale = 1f;
    public int LastStatus;
    public bool Shown;
    public bool Alive = true;
    public float BubbleStart;
    public float BubbleEnd = -1f;
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
| `layer` | VisualElement | Capa raíz de overheads (`brawl-overheads`, clases `mm-theme mm-theme--night`) |
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
| `TryBind()` | Crea la capa `brawl-overheads` con sus dos grupos, llena el pool e insértala al inicio del documento. Retorna false si el documento no está listo |
| `Unbind()` | Limpia plates, quita la capa del documento y vacía el pool |
| `Rebuild()` | Limpia plates viejas, crea nuevas por fighters |
| `BuildPlate()` | Construye visual de plate para fighter; el nombre solo si no es `Dummy` |
| `BuildFloat()` | Construye slot de FloatText en pool |
| `UpdatePlate()` | LateUpdate: posición, vivo/KO, HP, escudo, estado y burbuja |
| `UpdateBubble()` | Cierra la burbuja al terminar el tiempo o si el fighter cae; si no, aplica el pop |
| `UpdateFloat()` | LateUpdate: posición floating, opacity fade |
| `SpawnFloat()` | Crea float desde pool, asigna posición y variante |
| `HandleDamaged()` | Dispara SpawnFloat("-X"); ignora drenaje (`IsDrain`) y daños que redondean a 0 |
| `HandleHealed()` | Dispara SpawnFloat("+X") |
| `HandleShielded()` | Dispara SpawnFloat("escudo") |
| `HandleCastStarted()` | Setea bubble icon, text, border, scale, timing |
| `Changed()` | Compara con umbral 0,001 o cruce de cero; evita reescribir el ancho de barra si no cambió |

## Flujo de Visualización (LateUpdate)

1. **Para cada Plate:**
   - Obtiene Fighter.Center + headOffset → world
   - Chequea frente de cámara (producto punto > 0,1) para mostrar u ocultar
   - Transforma world → screen (RuntimePanelUtils.CameraTransformWorldToPanel)
   - Actualiza translate si cambió posición
   - Actualiza clase `brawl-plate--ko` si cambió el estado vivo
   - Actualiza HP/Shield fill width
   - Actualiza Status label ("aturdido", "provocado")
   - Actualiza bubble (scale pop si en casting; cierre al terminar o al caer)

2. **Para cada FloatText activo:**
   - Calcula age desde spawn
   - Si age > FloatSeconds (0,8s), desactiva
   - Oculta si el punto está fuera del frente de cámara
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
    var border = theme.Color;
    border.a = 1f;

    plate.BubbleIcon.sprite = theme.Icon;
    plate.BubbleIcon.tintColor = theme.Color;
    plate.BubbleIcon.style.display = theme.Icon != null ? DisplayStyle.Flex : DisplayStyle.None;
    plate.BubbleText.text = skill.Title + "!";
    plate.Bubble.style.borderTopColor = border;
    plate.Bubble.style.borderRightColor = border;
    plate.Bubble.style.borderBottomColor = border;
    plate.Bubble.style.borderLeftColor = border;

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
- Frente de cámara (producto punto) oculta plates fuera de vista
- LastPos caché evita recomputar translate si fighter no se movió

## Notas S145

- Los muñecos (`Dummy`) no muestran nombre en su plate.
- Al caer (`IsAlive` falso), la plate recibe `brawl-plate--ko` y su burbuja se cierra.
- La capa lleva las clases de tema `mm-theme mm-theme--night`.
