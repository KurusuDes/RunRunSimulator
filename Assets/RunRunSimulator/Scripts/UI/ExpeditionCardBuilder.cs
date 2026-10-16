using System.Collections.Generic;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public static class ExpeditionCardBuilder
{
    private const int PowerCount = 3;

    private readonly struct Power
    {
        public readonly BrawlTheme Theme;
        public readonly BrawlSkillRole Role;
        public readonly string Title;
        public readonly bool Locked;

        public Power(BrawlTheme theme, BrawlSkillRole role, string title, bool locked = false)
        {
            Theme = theme;
            Role = role;
            Title = title;
            Locked = locked;
        }
    }

    public static VisualElement BuildTile(CreatureDNA dna, bool ok, CareGateSO careGate)
    {
        var tile = new VisualElement();
        tile.AddToClassList("exp-tile");
        if (!ok) tile.AddToClassList("exp-tile--off");

        var slot = new VisualElement();
        slot.AddToClassList("mm-slot");
        slot.AddToClassList("exp-tile__slot");

        var icon = new VisualElement();
        icon.AddToClassList("exp-tile__icon");
        icon.pickingMode = PickingMode.Ignore;
        MonchiPortraitUI.Apply(icon, dna);
        slot.Add(icon);

        var check = new Label("✓");
        check.AddToClassList("exp-tile__check");
        check.pickingMode = PickingMode.Ignore;
        slot.Add(check);
        tile.Add(slot);

        var name = new Label(dna.CustomName);
        name.AddToClassList("exp-tile__name");
        name.pickingMode = PickingMode.Ignore;
        tile.Add(name);

        if (!ok)
        {
            var state = new Label(StateTextFor(dna));
            state.AddToClassList("exp-tile__state");
            state.pickingMode = PickingMode.Ignore;
            tile.Add(state);

            NeedType? weak = CreatureAvailability.WeakestNeed(dna, careGate);
            if (weak.HasValue) tile.Add(BuildBar(weak.Value, NeedValue(dna, weak.Value)));
        }

        return tile;
    }

    public static VisualElement BuildTeamCard(CreatureDNA dna, BrawlKitProfile profile)
    {
        var card = new VisualElement();
        card.AddToClassList("mm-panel");
        card.AddToClassList("exp-member");
        card.Add(Layer("mm-panel__lip"));
        card.Add(Layer("mm-panel__frame"));

        var stage = new VisualElement();
        stage.AddToClassList("exp-member__stage");
        stage.pickingMode = PickingMode.Ignore;

        var floor = new VisualElement();
        floor.AddToClassList("exp-member__floor");
        floor.pickingMode = PickingMode.Ignore;
        var ring = new VisualElement();
        ring.AddToClassList("exp-member__floor-ring");
        ring.pickingMode = PickingMode.Ignore;
        floor.Add(ring);
        stage.Add(floor);

        var portrait = new VisualElement();
        portrait.AddToClassList("exp-member__portrait");
        portrait.pickingMode = PickingMode.Ignore;
        MonchiPortraitUI.Apply(portrait, dna);
        stage.Add(portrait);
        card.Add(stage);

        var name = new Label(dna.CustomName);
        name.AddToClassList("exp-member__name");
        name.pickingMode = PickingMode.Ignore;
        card.Add(name);

        var pill = RolePill(profile, "exp-member__role");
        pill.pickingMode = PickingMode.Ignore;
        card.Add(pill);

        var powers = new VisualElement();
        powers.AddToClassList("exp-member__powers");
        powers.pickingMode = PickingMode.Ignore;
        for (int slot = 0; slot < PowerCount; slot++)
            powers.Add(PowerColumn(PowerAt(profile, slot)));
        card.Add(powers);

        return card;
    }

    public static VisualElement BuildEmptySlot()
    {
        var card = new VisualElement();
        card.AddToClassList("mm-panel");
        card.AddToClassList("exp-member");
        card.AddToClassList("exp-member--empty");
        card.Add(Layer("mm-panel__lip"));
        card.Add(Layer("mm-panel__frame"));

        var runes = new VisualElement();
        runes.AddToClassList("exp-member__runes");
        runes.pickingMode = PickingMode.Ignore;
        card.Add(runes);

        var label = new Label(Loc.Tr("ui.expedition.slot.empty"));
        label.AddToClassList("exp-member__hint");
        label.pickingMode = PickingMode.Ignore;
        card.Add(label);

        return card;
    }

    public static void FillTeam(VisualElement team, IReadOnlyList<CreatureDNA> dnas, IReadOnlyList<BrawlKitProfile> profiles, IReadOnlyList<int> order, int maxPick)
    {
        team.Clear();

        var title = new Label(Loc.Tr("ui.expedition.team"));
        title.AddToClassList("exp-team__title");
        team.Add(title);

        var count = new Label(Loc.Tr("ui.expedition.members", order.Count, maxPick));
        count.AddToClassList("exp-team__count");
        team.Add(count);

        bool support = false;
        for (int slot = 0; slot < maxPick; slot++)
        {
            if (slot >= order.Count)
            {
                team.Add(BuildTeamEmptyRow());
                continue;
            }

            var profile = profiles[order[slot]];
            if (profile.HasRole(BrawlSkillRole.Support)) support = true;
            team.Add(BuildTeamRow(dnas[order[slot]], profile));
        }

        if (order.Count > 0 && !support)
        {
            var warn = new Label(Loc.Tr("ui.expedition.nosupport"));
            warn.AddToClassList("exp-team__warn");
            team.Add(warn);
        }
    }

    private static VisualElement BuildTeamRow(CreatureDNA dna, BrawlKitProfile profile)
    {
        var row = new VisualElement();
        row.AddToClassList("mm-row");
        row.AddToClassList("exp-team__row");

        var portrait = new VisualElement();
        portrait.AddToClassList("exp-team__portrait");
        portrait.pickingMode = PickingMode.Ignore;
        MonchiPortraitUI.Apply(portrait, dna);
        row.Add(portrait);

        var name = new Label(dna.CustomName);
        name.AddToClassList("exp-team__name");
        name.pickingMode = PickingMode.Ignore;
        row.Add(name);

        row.Add(RolePill(profile, "exp-team__pill"));
        return row;
    }

    private static VisualElement BuildTeamEmptyRow()
    {
        var row = new VisualElement();
        row.AddToClassList("mm-row");
        row.AddToClassList("exp-team__row");
        row.AddToClassList("exp-team__row--empty");
        row.pickingMode = PickingMode.Ignore;

        var runes = new VisualElement();
        runes.AddToClassList("exp-team__runes");
        runes.pickingMode = PickingMode.Ignore;
        row.Add(runes);

        var hint = new Label(Loc.Tr("ui.expedition.slot.empty"));
        hint.AddToClassList("exp-team__hint");
        hint.pickingMode = PickingMode.Ignore;
        row.Add(hint);
        return row;
    }

    private static VisualElement Layer(string cls)
    {
        var layer = new VisualElement();
        layer.AddToClassList("mm-layer");
        layer.AddToClassList(cls);
        layer.pickingMode = PickingMode.Ignore;
        return layer;
    }

    private static VisualElement PowerColumn(Power power)
    {
        var column = new VisualElement();
        column.AddToClassList("exp-power-col");
        column.pickingMode = PickingMode.Ignore;
        column.Add(PowerIcon(power));

        var title = new Label(power.Title);
        title.AddToClassList("exp-power-col__title");
        title.pickingMode = PickingMode.Ignore;
        column.Add(title);
        return column;
    }

    private static VisualElement RolePill(in BrawlKitProfile profile, string extraClass)
    {
        var pill = BrawlRolePill.Build(profile);
        pill.AddToClassList(extraClass);
        return pill;
    }

    private static VisualElement PowerIcon(Power power)
    {
        var icon = new VisualElement();
        icon.AddToClassList("exp-power");
        icon.pickingMode = PickingMode.Ignore;
        if (power.Locked)
        {
            icon.AddToClassList("exp-power--locked");
            var lockMark = new Label("?");
            lockMark.AddToClassList("exp-power__lock");
            icon.Add(lockMark);
            return icon;
        }
        icon.AddToClassList("mm-role-ring--" + BrawlKitProfile.RoleClass(power.Role));
        if (power.Theme.Icon != null) icon.style.backgroundImage = new StyleBackground(power.Theme.Icon);
        else icon.style.backgroundColor = power.Theme.Color;
        return icon;
    }

    private static Power PowerAt(BrawlKitProfile profile, int slot) => slot switch
    {
        0 => profile.Wing != null
            ? new Power(profile.WingTheme, BrawlKitProfile.WingRole(profile.Wing), BrawlLoc.Title(profile.Wing))
            : new Power(profile.WingTheme, BrawlSkillRole.Offense, string.Empty),
        1 => SkillPower(profile.HornTheme, profile.Horn),
        _ => profile.BackLocked
            ? new Power(default, BrawlSkillRole.Offense, Loc.Tr("ui.power.locked.title"), true)
            : SkillPower(profile.BackTheme, profile.Back),
    };

    private static Power SkillPower(BrawlTheme theme, BrawlSkillSO skill) =>
        skill != null
            ? new Power(theme, skill.Role, BrawlLoc.Title(skill))
            : new Power(theme, BrawlSkillRole.Offense, string.Empty);

    private static VisualElement BuildBar(NeedType need, float value)
    {
        var track = new VisualElement();
        track.AddToClassList("exp-tile__bar-track");
        track.tooltip = Loc.Tr(NeedsLabelKey(need));
        track.pickingMode = PickingMode.Ignore;

        var fill = new VisualElement();
        fill.AddToClassList("exp-tile__bar-fill");
        fill.AddToClassList(NeedsDisplay.ColorClass(need, value));
        fill.style.width = new StyleLength(new Length(NeedsDisplay.Fill01(need, value) * 100f, LengthUnit.Percent));
        fill.pickingMode = PickingMode.Ignore;
        track.Add(fill);

        return track;
    }

    private static float NeedValue(CreatureDNA dna, NeedType need) => need switch
    {
        NeedType.Health => dna.Needs.Health,
        NeedType.Energy => dna.Needs.Energy,
        _ => dna.Needs.Affect,
    };

    private static string NeedsLabelKey(NeedType need) => need switch
    {
        NeedType.Health => "ui.expedition.needs.health",
        NeedType.Energy => "ui.expedition.needs.energy",
        _ => "ui.expedition.needs.affect",
    };

    private static string StateTextFor(CreatureDNA dna) =>
        Loc.Tr(dna.IsBusy ? "ui.expedition.busy" : "ui.expedition.notready");
}
}
