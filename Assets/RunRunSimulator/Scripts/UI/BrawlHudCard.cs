using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
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

    private string lastIntent;
    private float lastHp = -1f;
    private float lastShield = -1f;
    private int lastHpValue = -1;
    private bool lastAlive = true;

    public VisualElement Root { get; }

    public BrawlHudCard(BrawlFighter fighter, BrawlTuningSO tuning)
    {
        this.fighter = fighter;

        Root = Element("brawl-card");
        Root.AddToClassList(fighter.Team == ExpeditionTeam.Player ? "brawl-card--blue" : "brawl-card--red");
        Root.Add(Element("brawl-bg"));

        var head = Element("brawl-card__head");
        head.Add(MakeLabel(fighter.DisplayName, "brawl-card__name"));
        head.Add(MakeLabel(fighter.BodyLabel, "brawl-card__body"));
        Root.Add(head);

        var line = Element("brawl-card__line");
        line.Add(MakeLabel(fighter.Brain.PostureLabel, "brawl-card__posture"));
        intentLabel = MakeLabel("", "brawl-card__intent");
        line.Add(intentLabel);
        Root.Add(line);

        var hp = Element("brawl-hp");
        hpFill = Element("brawl-hp__fill");
        hpFill.style.backgroundColor = tuning.TeamColor(fighter.Team);
        hpShield = Element("brawl-hp__shield");
        hpLabel = MakeLabel("", "brawl-hp__label");
        hp.Add(hpFill);
        hp.Add(hpShield);
        hp.Add(hpLabel);
        hp.Add(MakeLabel("KO", "brawl-hp__ko"));
        Root.Add(hp);

        var row = Element("brawl-card__slots");
        AddSlot(row, 0, fighter.WingTheme, fighter.WingKit != null ? fighter.WingKit.Title : null, fighter.WingKit != null);
        AddSlot(row, 1, fighter.HornTheme, fighter.HornSkill != null ? fighter.HornSkill.Title : null, fighter.HornSkill != null);
        AddSlot(row, 2, fighter.BackTheme, fighter.BackSkill != null ? fighter.BackSkill.Title : null, fighter.BackSkill != null);
        Root.Add(row);

        Refresh();
    }

    public void PulseSkill(int slot)
    {
        int index = slot + 1;
        if (index < 1 || index >= SlotCount) return;
        radials[index].Pulse();
    }

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

    private void AddSlot(VisualElement row, int index, BrawlTheme theme, string title, bool active)
    {
        var slot = Element("brawl-slot");
        if (!active) slot.AddToClassList("brawl-slot--empty");

        var box = Element("brawl-slot__box");

        var icon = new Image { sprite = theme.Icon, scaleMode = ScaleMode.ScaleToFit, tintColor = theme.Color, pickingMode = PickingMode.Ignore };
        icon.AddToClassList("brawl-slot__icon");
        box.Add(icon);

        var radial = new RadialSlot
        {
            FillColor = new Color(theme.Color.r, theme.Color.g, theme.Color.b, FillAlpha),
            pickingMode = PickingMode.Ignore
        };
        radial.AddToClassList("brawl-slot__radial");
        box.Add(radial);

        slot.Add(box);
        slot.Add(MakeLabel(string.IsNullOrEmpty(title) ? "—" : title, "brawl-slot__label"));
        row.Add(slot);

        slots[index] = slot;
        radials[index] = radial;
        slotActive[index] = active;
    }

    private static bool Changed(float value, float last)
    {
        return Mathf.Abs(value - last) > 0.001f || (value <= 0f) != (last <= 0f);
    }

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

    private static VisualElement Element(string className)
    {
        var element = new VisualElement { pickingMode = PickingMode.Ignore };
        element.AddToClassList(className);
        return element;
    }

    private static Label MakeLabel(string text, string className)
    {
        var label = new Label(text) { pickingMode = PickingMode.Ignore };
        label.AddToClassList(className);
        return label;
    }
}
}
