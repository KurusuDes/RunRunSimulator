---
tags: [script, ui, class]
---

# BrawlHudCard.cs

**Ruta:** `UI/BrawlHudCard.cs`

**Responsabilidad:** Card individual de fighter en HUD (no MonoBehaviour). Encapsula VisualElement root + estado (HP, intención, cooldowns de skill). Creado por `BrawlHud.RebuildCards()`, actualizado en loop por `BrawlHud.Refresh()`.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Estructura

```csharp
public class BrawlHudCard
{
    private const int SlotCount = 3;              // Wing, Horn, Back
    private const float ReadyCharge = 0.999f;    // Umbral "listo"
    private const float FillAlpha = 0.45f;       // Opacidad de radial fill
    
    private readonly BrawlFighter fighter;
    private readonly Label intentLabel;
    private readonly VisualElement hpFill;
    private readonly VisualElement hpShield;
    private readonly Label hpLabel;
    private readonly RadialSlot[] radials;
    private readonly VisualElement[] slots;
    private readonly bool[] slotActive;
    private readonly bool[] charging;
    
    public VisualElement Root { get; }
}
```

## Componentes Visuales

| Componente | Clase CSS | Descripción |
|-----------|-----------|-------------|
| Root | brawl-card / brawl-card--blue/--red | Card contenedora |
| Head | brawl-card__head | Nombre + label cuerpo |
| Line | brawl-card__line | Postura + intención |
| HP Bar | brawl-hp | Vida (lleno) + escudo (overlay) |
| Slots | brawl-card__slots | Wing + Horn + Back (3 slots) |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `BrawlHudCard(fighter, tuning)` | Constructor: arma visual + inicializa cached state |
| `Refresh()` | Actualiza HP, intención, slots, cargos (llamado por BrawlHud.Update) |
| `PulseSkill(int slot)` | Anima pulse en slot cuando skill castea (slot 0=Wing, 1=Horn, 2=Back) |

## Constructor

```csharp
public BrawlHudCard(BrawlFighter fighter, BrawlTuningSO tuning)
{
    // 1. Crea root (blue/red según team)
    Root = Element("brawl-card");
    Root.AddToClassList(fighter.Team == ExpeditionTeam.Player ? "brawl-card--blue" : "brawl-card--red");
    
    // 2. Head (nombre + cuerpo)
    head.Add(MakeLabel(fighter.DisplayName, "brawl-card__name"));
    head.Add(MakeLabel(fighter.BodyLabel, "brawl-card__body"));
    
    // 3. Line (postura + intención)
    line.Add(MakeLabel(fighter.Brain.PostureLabel, "brawl-card__posture"));
    intentLabel = MakeLabel("", "brawl-card__intent");
    line.Add(intentLabel);
    
    // 4. HP bar (fill + shield overlay)
    hpFill.style.backgroundColor = tuning.TeamColor(fighter.Team);
    hpShield = Element("brawl-hp__shield");
    hpLabel = MakeLabel("", "brawl-hp__label");
    
    // 5. Slots (Wing, Horn, Back)
    AddSlot(row, 0, fighter.WingTheme, title, active);  // Slot 0 = Wing
    AddSlot(row, 1, fighter.HornTheme, title, active);  // Slot 1 = Horn
    AddSlot(row, 2, fighter.BackTheme, title, active);  // Slot 2 = Back
}
```

## Método Refresh() (llamado cada frame desde BrawlHud)

```csharp
public void Refresh()
{
    if (fighter == null) return;
    
    // 1. Chequea vivo/muerto (cambia clase CSS)
    bool alive = fighter.IsAlive;
    if (alive != lastAlive)
        Root.EnableInClassList("brawl-card--ko", !alive);
    
    // 2. Actualiza barra de HP (width porcentaje)
    float hp01 = fighter.Hp01;
    if (Changed(hp01, lastHp))
        hpFill.style.width = Length.Percent(hp01 * 100f);
    
    // 3. Actualiza escudo (overlay sobre HP)
    float shield01 = fighter.MaxHp > 0f ? Mathf.Clamp01(fighter.Shield / fighter.MaxHp) : 0f;
    if (Changed(shield01, lastShield))
        hpShield.style.width = Length.Percent(shield01 * 100f);
    
    // 4. Actualiza label numérico de HP
    int hpValue = Mathf.CeilToInt(fighter.Hp);
    if (hpValue != lastHpValue)
        hpLabel.text = hpValue.ToString();
    
    // 5. Actualiza label de intención
    string intent = alive ? IntentText(fighter.Brain.Intent) : "";
    if (intent != lastIntent)
        intentLabel.text = intent;
    
    // 6. Actualiza cargos de skills (radiales)
    for (int i = 0; i < SlotCount; i++) RefreshSlot(i);
}
```

## Método RefreshSlot()

```csharp
private void RefreshSlot(int index)
{
    if (!slotActive[index]) return;
    
    float charge = index == 0 ? fighter.Wing.Mobility01 : fighter.Caster.Charge01(index - 1);
    radials[index].Charge01 = charge;
    
    bool isCharging = charge < ReadyCharge;  // 0,999 threshold
    if (isCharging == charging[index]) return;  // Sin cambio
    charging[index] = isCharging;
    slots[index].EnableInClassList("brawl-slot--charging", isCharging);
}
```

**Lógica:**
- Slot 0: Wing.Mobility01 (movilidad)
- Slot 1: Caster.Charge01(0) (cuerno)
- Slot 2: Caster.Charge01(1) (espalda)
- Si charge < 0,999 → en carga, aplicar clase "charging"
- RadialSlot muestra gráficamente el fill (0-1)

## Método IntentText()

```csharp
private static string IntentText(BrawlIntent intent)
{
    switch (intent)
    {
        case BrawlIntent.Engage: return "pelea";
        case BrawlIntent.Kite: return "dispara de lejos";
        case BrawlIntent.Hunt: return "caza";
        case BrawlIntent.Protect: return "protege";
        case BrawlIntent.Heal: return "cura";
        case BrawlIntent.Retreat: return "huye";
        case BrawlIntent.Cast: return "concentra";
        default: return "espera";
    }
}
```

Traduce BrawlIntent enum a texto legible (feedback de IA).

## Método PulseSkill()

```csharp
public void PulseSkill(int slot)
{
    int index = slot + 1;  // Convierte ClashSlot (0=Horn, 1=Back) a índice (1, 2)
    if (index < 1 || index >= SlotCount) return;
    radials[index].Pulse();
}
```

Anima pulse en radial cuando skill se castea.

## Método AddSlot()

```csharp
private void AddSlot(VisualElement row, int index, BrawlTheme theme, string title, bool active)
{
    var slot = Element("brawl-slot");
    if (!active) slot.AddToClassList("brawl-slot--empty");
    
    var box = Element("brawl-slot__box");
    
    // Ícono teñido con color de tema
    var icon = new Image { sprite = theme.Icon, tintColor = theme.Color };
    icon.AddToClassList("brawl-slot__icon");
    box.Add(icon);
    
    // Radial circular que muestra carga
    var radial = new RadialSlot
    {
        FillColor = new Color(theme.Color.r, theme.Color.g, theme.Color.b, FillAlpha)
    };
    radial.AddToClassList("brawl-slot__radial");
    box.Add(radial);
    
    slot.Add(box);
    slot.Add(MakeLabel(string.IsNullOrEmpty(title) ? "—" : title, "brawl-slot__label"));
    row.Add(slot);
}
```

## Optimizaciones

- `lastHp`, `lastShield`, `lastIntent`, etc. cacheadas para no recomputar si no cambió
- `Changed(value, last)` retorna true si delta > 0.001 o flip 0↔1 (evita dithering visual)
- `slotActive[index]` evita refresh de slots vacíos
- `charging[index]` caché para no re-aplicar clase CSS si ya activa

## Dependencias

**Entrada:**
- `BrawlFighter` (HP, intención, skills, cargos)
- `BrawlTuningSO` (colores de equipo)
- `BrawlTheme` (ícono, color de tema para slots)
- `RadialSlot` (custom element para charge radial)

**Salida:**
- VisualElement root integrado en BrawlHud (blueCards/redCards)

## Notas S142

- No es MonoBehaviour (pura clase de UI)
- SlotActive permite ocultar slots sin skill (ej. criatura sin cuerno)
- Radial muestra 0→1 suave (shader interpola)
- Intención es feedback de IA (texto dinámico según Brain.Intent)
- Color de slot teñido con BrawlTheme.Color (determinístico por parte)
- Pulse animation para feedback de casteo (opcional, puede no estar implementado aún)
