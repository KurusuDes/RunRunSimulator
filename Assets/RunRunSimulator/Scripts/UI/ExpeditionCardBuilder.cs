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
        public readonly string Description;
        public readonly bool Locked;

        public Power(BrawlTheme theme, BrawlSkillRole role, string title, string description, bool locked = false)
        {
            Theme = theme;
            Role = role;
            Title = title;
            Description = description;
            Locked = locked;
        }
    }

    public static VisualElement BuildCard(CreatureDNA dna, bool ok, BrawlKitProfile profile, CareGateSO careGate)
    {
        var card = new VisualElement();
        card.AddToClassList("exp-card");
        if (!ok) card.AddToClassList("exp-card--off");

        var icon = new VisualElement();
        icon.AddToClassList("exp-card__icon");
        MonchiPortraitUI.Apply(icon, dna);
        card.Add(icon);

        var name = new Label(dna.CustomName);
        name.AddToClassList("exp-card__name");
        card.Add(name);

        if (ok)
        {
            card.Add(RolePill(profile, "exp-card__role"));

            var powers = new VisualElement();
            powers.AddToClassList("exp-card__powers");
            for (int slot = 0; slot < PowerCount; slot++)
                powers.Add(PowerIcon(PowerAt(profile, slot), "exp-power"));
            card.Add(powers);
        }
        else
        {
            var state = new Label(StateTextFor(dna));
            state.AddToClassList("exp-card__state");
            card.Add(state);

            NeedType? weak = CreatureAvailability.WeakestNeed(dna, careGate);
            if (weak.HasValue)
            {
                var bars = new VisualElement();
                bars.AddToClassList("exp-card__bars");
                bars.Add(BuildBar(weak.Value, NeedValue(dna, weak.Value)));
                card.Add(bars);
            }
        }

        var check = new Label("✓");
        check.AddToClassList("exp-card__check");
        card.Add(check);

        return card;
    }

    public static void FillDetail(VisualElement detail, CreatureDNA dna, BrawlKitProfile profile)
    {
        detail.Clear();

        var head = new VisualElement();
        head.AddToClassList("exp-detail__head");

        var name = new Label(dna.CustomName);
        name.AddToClassList("exp-detail__name");
        head.Add(name);
        head.Add(RolePill(profile, "exp-detail__role"));
        detail.Add(head);

        for (int slot = 0; slot < PowerCount; slot++)
            detail.Add(DetailRow(PowerAt(profile, slot)));
    }

    public static void FillTeam(VisualElement team, IReadOnlyList<BrawlKitProfile> profiles, IReadOnlyList<bool> picked)
    {
        team.Clear();

        var row = new VisualElement();
        row.AddToClassList("exp-team__row");

        var title = new Label(Loc.Tr("ui.expedition.team"));
        title.AddToClassList("exp-team__title");
        row.Add(title);

        bool any = false;
        bool support = false;
        for (int i = 0; i < picked.Count; i++)
        {
            if (!picked[i]) continue;
            any = true;
            if (profiles[i].HasRole(BrawlSkillRole.Support)) support = true;
            row.Add(RolePill(profiles[i], "exp-team__pill"));
        }
        team.Add(row);

        if (any && !support)
        {
            var warn = new Label(Loc.Tr("ui.expedition.nosupport"));
            warn.AddToClassList("exp-team__warn");
            team.Add(warn);
        }

        team.style.visibility = any ? Visibility.Visible : Visibility.Hidden;
    }

    private static VisualElement DetailRow(Power power)
    {
        var row = new VisualElement();
        row.AddToClassList("exp-detail__row");
        row.Add(PowerIcon(power, "exp-detail__icon"));

        var text = new VisualElement();
        text.AddToClassList("exp-detail__text");

        var title = new Label(power.Title);
        title.AddToClassList("exp-detail__title");
        if (!power.Locked) title.AddToClassList("mm-role-text--" + BrawlKitProfile.RoleClass(power.Role));
        text.Add(title);

        var desc = new Label(power.Description);
        desc.AddToClassList("exp-detail__desc");
        text.Add(desc);

        row.Add(text);
        return row;
    }

    private static VisualElement RolePill(in BrawlKitProfile profile, string extraClass)
    {
        var pill = BrawlRolePill.Build(profile);
        pill.AddToClassList(extraClass);
        return pill;
    }

    private static VisualElement PowerIcon(Power power, string iconClass)
    {
        var icon = new VisualElement();
        icon.AddToClassList(iconClass);
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
            ? new Power(profile.WingTheme, BrawlKitProfile.WingRole(profile.Wing), profile.Wing.Title, profile.Wing.Description)
            : new Power(profile.WingTheme, BrawlSkillRole.Offense, string.Empty, string.Empty),
        1 => SkillPower(profile.HornTheme, profile.Horn),
        _ => profile.BackLocked
            ? new Power(default, BrawlSkillRole.Offense, Loc.Tr("ui.power.locked.title"), Loc.Tr("ui.power.locked.desc"), true)
            : SkillPower(profile.BackTheme, profile.Back),
    };

    private static Power SkillPower(BrawlTheme theme, BrawlSkillSO skill) =>
        skill != null
            ? new Power(theme, skill.Role, skill.Title, skill.Description)
            : new Power(theme, BrawlSkillRole.Offense, string.Empty, string.Empty);

    private static VisualElement BuildBar(NeedType need, float value)
    {
        var track = new VisualElement();
        track.AddToClassList("exp-card__bar-track");
        track.AddToClassList("exp-card__bar-track--weak");
        track.tooltip = Loc.Tr(NeedsLabelKey(need));

        var fill = new VisualElement();
        fill.AddToClassList("exp-card__bar-fill");
        fill.AddToClassList(NeedsDisplay.ColorClass(need, value));
        fill.style.width = new StyleLength(new Length(NeedsDisplay.Fill01(need, value) * 100f, LengthUnit.Percent));
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
