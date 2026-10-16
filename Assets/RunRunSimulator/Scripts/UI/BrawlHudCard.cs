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
    private readonly VisualElement damage;
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

        var portrait = Element("brawl-portrait");
        portrait.Add(Element("brawl-portrait__bg"));
        portrait.Add(Element("brawl-portrait__grad"));
        portrait.Add(Element("brawl-portrait__tracery"));
        var portraitImage = Element("brawl-portrait__img");
        MonchiPortraitUI.Apply(portraitImage, fighter.DNA);
        portrait.Add(portraitImage);
        damage = Element("brawl-portrait__damage");
        portrait.Add(damage);
        portrait.Add(Element("brawl-portrait__vignette"));
        portrait.Add(Element("brawl-portrait__frame"));
        portrait.Add(Element("brawl-portrait__detail"));
        hpLabel = MakeLabel("", "brawl-portrait__hp");
        portrait.Add(hpLabel);
        portrait.Add(MakeLabel(Loc.Tr("ui.brawl.card.ko"), "brawl-portrait__ko"));
        Root.Add(portrait);

        var info = Element("brawl-card__info");

        var head = Element("brawl-card__head");
        head.Add(MakeLabel(fighter.DisplayName, "brawl-card__name"));
        head.Add(MakeLabel(fighter.BodyLabel, "brawl-card__body"));
        info.Add(head);

        var hp = Element("brawl-hpbar");
        var track = Element("brawl-hpbar__track");
        hpFill = Element("brawl-hpbar__fill");
        hpShield = Element("brawl-hpbar__shield");
        track.Add(hpFill);
        track.Add(hpShield);
        hp.Add(track);
        hp.Add(Element("brawl-hpbar__heart"));
        info.Add(hp);

        var line = Element("brawl-card__line");
        line.Add(MakeLabel(fighter.Brain.PostureLabel, "brawl-card__posture"));
        intentLabel = MakeLabel("", "brawl-card__intent");
        line.Add(intentLabel);
        info.Add(line);

        var row = Element("brawl-card__slots");
        AddSlot(row, 0, fighter.WingTheme, fighter.WingKit != null, false);
        AddSlot(row, 1, fighter.HornTheme, fighter.HornSkill != null, false);
        AddSlot(row, 2, fighter.BackTheme, fighter.BackSkill != null, fighter.BackLocked);
        info.Add(row);

        Root.Add(info);

        Refresh();
    }

    public void PulseSkill(int slot)
    {
        int index = slot + 1;
        if (index < 1 || index >= SlotCount) return;
        radials[index]?.Pulse();
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
            damage.style.height = Length.Percent((1f - hp01) * 100f);
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

    private void AddSlot(VisualElement row, int index, BrawlTheme theme, bool active, bool locked)
    {
        var slot = Element("brawl-slot");
        if (locked) slot.AddToClassList("brawl-slot--locked");
        else if (!active) slot.AddToClassList("brawl-slot--empty");

        var box = Element("brawl-slot__box");

        if (locked)
        {
            box.Add(MakeLabel("?", "brawl-slot__lock"));
            box.Add(Element("brawl-slot__ring"));
            slot.Add(box);
            row.Add(slot);

            slots[index] = slot;
            slotActive[index] = false;
            return;
        }

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
        box.Add(Element("brawl-slot__ring"));

        slot.Add(box);
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
            case BrawlIntent.Engage: return Loc.Tr("ui.brawl.intent.engage");
            case BrawlIntent.Kite: return Loc.Tr("ui.brawl.intent.kite");
            case BrawlIntent.Hunt: return Loc.Tr("ui.brawl.intent.hunt");
            case BrawlIntent.Protect: return Loc.Tr("ui.brawl.intent.protect");
            case BrawlIntent.Heal: return Loc.Tr("ui.brawl.intent.heal");
            case BrawlIntent.Retreat: return Loc.Tr("ui.brawl.intent.retreat");
            case BrawlIntent.Cast: return Loc.Tr("ui.brawl.intent.cast");
            default: return Loc.Tr("ui.brawl.intent.idle");
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
