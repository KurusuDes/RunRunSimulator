---
tags: [script, ui, class]
---

# BrawlHudCard.cs

**Ruta:** `UI/BrawlHudCard.cs`

**Responsabilidad:** Card individual de fighter en HUD (no MonoBehaviour). Encapsula VisualElement root + estado (HP, escudo, intención, cargas de skill). Creado por `BrawlHud.RebuildCards()`, actualizado en loop por `BrawlHud.Update()`. Muestra el slot de espalda bloqueada como "?" cuando `BrawlFighter.BackLocked` es true.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Estructura

```csharp
public class BrawlHudCard
{
    private const int SlotCount = 3;
    private const float ReadyCharge = 0.999f;
    private const float FillAlpha = 0.45f;

    private readonly BrawlFighter fighter;
    private readonly Label intentLabel;
    private readonly VisualElement hpFill;
    private readonly VisualElement hpShield;
    private readonly Label hpLabel;
    private readonly RadialSlot[] radials = new RadialSlot[SlotCount];
    private readonly VisualElement[] slots = new VisualElement[SlotCount];
    private readonly bool[] slotActive = new bool[SlotCount];
    private readonly bool[] charging = new bool[SlotCount];

    public VisualElement Root { get; }
}
```

## Componentes Visuales

| Componente | Clase CSS | Descripción |
|-----------|-----------|-------------|
| Root | brawl-card / brawl-card--blue/--red (`--ko` si está caído) | Card contenedora |
| Head | brawl-card__head | Nombre + label cuerpo |
| Line | brawl-card__line | Postura + intención |
| HP Bar | brawl-hp | Vida (fill), escudo (overlay `brawl-hp__shield`), número (`brawl-hp__label`) y "KO" (`brawl-hp__ko`) |
| Slots | brawl-card__slots | Wing + Horn + Back (3 slots) |
| Slot activo | brawl-slot / brawl-slot__box | Icono teñido con el tema, radial de carga (`brawl-slot__radial`) y etiqueta con el título |
| Slot vacío | brawl-slot--empty | Parte sin kit: sin radial, etiqueta "—" |
| Slot bloqueado | brawl-slot--locked, brawl-slot__lock | Espalda bloqueada: caja con "?" y etiqueta "—" |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `BrawlHudCard(fighter, tuning)` | Constructor: arma visual + inicializa cached state |
| `Refresh()` | Actualiza HP, escudo, intención, slots y cargas (llamado por BrawlHud.Update) |
| `PulseSkill(int slot)` | Pulse en el radial de un skill al castear. `slot` es `ClashSlot`: 0 = cuerno, 1 = espalda; internamente el índice es `slot + 1` |

## Constructor

- Root según equipo (`brawl-card--blue` o `--red`), fondo `brawl-bg`.
- Head: nombre (`DisplayName`) y cuerpo (`BodyLabel`).
- Line: postura (`Brain.PostureLabel`) e intención.
- HP: fill con color de equipo (`tuning.TeamColor`), shield, label y KO.
- Slots, en orden: ala (índice 0, `WingKit`), cuerno (índice 1, `HornSkill`) y espalda (índice 2, `BackSkill`, con `BackLocked`). Luego `Refresh()`.

## Método Refresh() (llamado cada frame desde BrawlHud)

```csharp
public void Refresh()
{
    if (fighter == null) return;

    bool alive = fighter.IsAlive;
    if (alive != lastAlive)
    {
        lastAlive = alive;
        Root.EnableInClassList("brawl-card--ko", !alive);
    }

    float hp01 = fighter.Hp01;
    if (Changed(hp01, lastHp))
    {
        lastHp = hp01;
        hpFill.style.width = Length.Percent(hp01 * 100f);
    }

    float shield01 = fighter.MaxHp > 0f ? Mathf.Clamp01(fighter.Shield / fighter.MaxHp) : 0f;
    if (Changed(shield01, lastShield))
    {
        lastShield = shield01;
        hpShield.style.width = Length.Percent(shield01 * 100f);
    }

    int hpValue = Mathf.CeilToInt(fighter.Hp);
    if (hpValue != lastHpValue)
    {
        lastHpValue = hpValue;
        hpLabel.text = hpValue.ToString();
    }

    string intent = alive ? IntentText(fighter.Brain.Intent) : "";
    if (intent != lastIntent)
    {
        lastIntent = intent;
        intentLabel.text = intent;
    }

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

    bool isCharging = charge < ReadyCharge;
    if (isCharging == charging[index]) return;
    charging[index] = isCharging;
    slots[index].EnableInClassList("brawl-slot--charging", isCharging);
}
```

**Lógica:**
- Slot 0: `Wing.Mobility01` (movilidad).
- Slot 1: `Caster.Charge01(0)` (cuerno).
- Slot 2: `Caster.Charge01(1)` (espalda).
- Si charge < 0,999 → en carga, aplicar clase "charging".
- Los slots bloqueados o vacíos no se refrescan (`slotActive` false).

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

Traduce `BrawlIntent` a texto legible (feedback de IA).

## Método PulseSkill()

```csharp
public void PulseSkill(int slot)
{
    int index = slot + 1;
    if (index < 1 || index >= SlotCount) return;
    radials[index]?.Pulse();
}
```

El `?.` evita fallar si el slot no tiene radial (parte sin kit o espalda bloqueada).

## Método AddSlot()

`AddSlot(row, index, theme, title, active, locked)`:
- `locked` → clase `brawl-slot--locked`, caja con "?" (`brawl-slot__lock`), etiqueta "—". No crea radial ni icono.
- Si no está activo y no está bloqueado → clase `brawl-slot--empty`, sin radial.
- Si está activo → icono `Image` con `theme.Icon` teñido con `theme.Color`, `RadialSlot` con `FillColor` = color del tema a `FillAlpha`, y etiqueta con el título del skill (o "—").
- Guarda el slot en `slots[index]`, el radial en `radials[index]` (si hay) y `slotActive[index]`.

## Optimizaciones

- `lastHp`, `lastShield`, `lastIntent`, etc. cacheadas para no recomputar si no cambió
- `Changed(value, last)` retorna true si delta > 0.001 o flip 0↔1 (evita dithering visual)
- `slotActive[index]` evita refresh de slots vacíos o bloqueados
- `charging[index]` caché para no re-aplicar clase CSS si ya activa

## Dependencias

**Entrada:**
- `BrawlFighter` (HP, escudo, intención, skills, cargas, `BackLocked`)
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

## Notas S146

- Espalda bloqueada (forma no adulta): slot con "?" en lugar de icono y radial. Lo decide `BrawlFighter.BackLocked`, que viene de `BrawlKitProfile`.
- El pulse de skill está implementado sobre `RadialSlot.Pulse()`; ya no es opcional.
