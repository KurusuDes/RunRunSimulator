using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class DetailInfoTabPresenter
{
    private readonly CreatureDatabaseSO database;
    private readonly CareGateSO careGate;
    private readonly BrawlKitDatabaseSO kits;

    private readonly VisualElement needHealthFill, needEnergyFill, needAffectFill;
    private readonly VisualElement needHealthRow, needEnergyRow, needAffectRow;
    private readonly Label exploreStatus, combatRoleTitle, identityLabel, roleElementLabel, progressionLabel;
    private readonly VisualElement partsContainer, combatRole, combatRolePill;

    public DetailInfoTabPresenter(VisualElement root, CreatureDatabaseSO database, CareGateSO careGate, BrawlKitDatabaseSO kits)
    {
        this.database = database;
        this.careGate = careGate;
        this.kits = kits;

        needHealthRow    = root.Q<VisualElement>("need-health");
        needEnergyRow    = root.Q<VisualElement>("need-energy");
        needAffectRow    = root.Q<VisualElement>("need-affect");
        needHealthFill   = root.Q<VisualElement>("need-health-fill");
        needEnergyFill   = root.Q<VisualElement>("need-energy-fill");
        needAffectFill   = root.Q<VisualElement>("need-affect-fill");
        exploreStatus    = root.Q<Label>("explore-status");
        combatRole       = root.Q<VisualElement>("combat-role");
        combatRoleTitle  = root.Q<Label>("combat-role-title");
        combatRolePill   = root.Q<VisualElement>("combat-role-pill");
        identityLabel   = root.Q<Label>("identity");
        roleElementLabel = root.Q<Label>("role-element");
        partsContainer   = root.Q<VisualElement>("parts");
        progressionLabel = root.Q<Label>("progression");
    }

    public void Rebuild(CreatureDNA dna)
    {
        if (dna == null) return;

        SetNeedBar(needHealthFill, NeedType.Health, dna.Needs.Health);
        SetNeedBar(needEnergyFill, NeedType.Energy, dna.Needs.Energy);
        SetNeedBar(needAffectFill, NeedType.Affect, dna.Needs.Affect);

        bool canExplore = careGate != null && CreatureAvailability.CanExplore(dna, careGate);
        NeedType? weakest = careGate != null ? CreatureAvailability.WeakestNeed(dna, careGate) : null;

        SetNeedHighlight(needHealthRow, weakest == NeedType.Health);
        SetNeedHighlight(needEnergyRow, weakest == NeedType.Energy);
        SetNeedHighlight(needAffectRow, weakest == NeedType.Affect);

        if (exploreStatus != null)
        {
            exploreStatus.text = canExplore ? Loc.Tr("ui.detail.explore.ready") : Loc.Tr("ui.detail.explore.blocked");
            exploreStatus.EnableInClassList("explore-status--ready", canExplore);
            exploreStatus.EnableInClassList("explore-status--blocked", !canExplore);
        }

        if (identityLabel != null)
            identityLabel.text = Loc.Tr("ui.detail.identity", LocEnumMaps.GenderName(dna.Gender), CreatureDisplay.StateOf(dna), Born(dna));

        if (roleElementLabel != null)
            roleElementLabel.text = Loc.Tr("ui.detail.roleline", LocEnumMaps.RoleName(dna.Role), LocEnumMaps.ElementName(dna.Element), RoleDesc(dna.Role));

        var profile = BrawlKitProfile.Of(dna, kits, database);

        SetCombatRole(profile);
        BuildParts(dna, profile);

        if (progressionLabel != null)
            progressionLabel.text = Loc.Tr("ui.detail.progression", dna.BreedCount);
    }

    private static void SetNeedBar(VisualElement fill, NeedType need, float value)
    {
        if (fill == null) return;
        fill.style.width = Length.Percent(NeedsDisplay.Fill01(need, value) * 100f);
        fill.RemoveFromClassList("exp-bar--good");
        fill.RemoveFromClassList("exp-bar--warn");
        fill.RemoveFromClassList("exp-bar--crit");
        fill.AddToClassList(NeedsDisplay.ColorClass(need, value));
    }

    private static void SetNeedHighlight(VisualElement row, bool highlight) =>
        row?.EnableInClassList("detail-need--blocked", highlight);

    private void SetCombatRole(in BrawlKitProfile profile)
    {
        if (combatRole == null) return;

        if (combatRoleTitle != null) combatRoleTitle.text = Loc.Tr("ui.detail.combatrole.suggested");
        if (combatRolePill != null)
        {
            combatRolePill.Clear();
            combatRolePill.Add(BrawlRolePill.Build(profile));
        }
        combatRole.style.display = kits != null ? DisplayStyle.Flex : DisplayStyle.None;
    }

    private void BuildParts(CreatureDNA dna, BrawlKitProfile profile)
    {
        if (partsContainer == null) return;
        partsContainer.Clear();
        if (database == null) return;

        AddPartRow(PartRole.Body, database.GetBodyShape(dna.BodyShapeID));
        AddSkillRow(PartRole.Horn, database.GetHorn(dna.HornID), profile.Horn);
        AddSkillRow(PartRole.Back, database.GetBack(dna.BackID), profile.Back);
        AddWingRow(PartRole.Wing, database.GetWing(dna.WingID), profile.Wing);
        AddPartRow(PartRole.Face, database.GetFace(dna.FaceID));
    }

    private void AddSkillRow(PartRole slot, BodyPart part, BrawlSkillSO skill)
    {
        if (skill != null) AddPowerPartRow(slot, part, skill.Title, skill.Description, skill.Role);
        else AddPowerPartRow(slot, part, null, null, null);
    }

    private void AddWingRow(PartRole slot, BodyPart part, BrawlWingKitSO wing)
    {
        if (wing != null) AddPowerPartRow(slot, part, wing.Title, wing.Description, BrawlKitProfile.WingRole(wing));
        else AddPowerPartRow(slot, part, null, null, null);
    }

    private void AddPartRow(PartRole slot, BodyPart part)
    {
        var row = new VisualElement();
        row.AddToClassList("part-row");
        row.Add(BuildPartSwatch(part, null));

        var text = new Label();
        text.AddToClassList("part-text");
        text.text = PartLine(slot, part);
        row.Add(text);

        partsContainer.Add(row);
    }

    private void AddPowerPartRow(PartRole slot, BodyPart part, string powerTitle, string powerDescription, BrawlSkillRole? powerRole)
    {
        var row = new VisualElement();
        row.AddToClassList("part-row");
        row.Add(BuildPartSwatch(part, powerRole));

        var body = new VisualElement();
        body.AddToClassList("part-body");

        var text = new Label();
        text.AddToClassList("part-text");
        text.text = PartLine(slot, part);
        body.Add(text);

        if (powerRole.HasValue)
        {
            var power = new VisualElement();
            power.AddToClassList("part-power");

            var title = new Label(powerTitle);
            title.AddToClassList("part-power__title");
            title.AddToClassList("mm-role-text--" + BrawlKitProfile.RoleClass(powerRole.Value));
            power.Add(title);

            var description = new Label(powerDescription);
            description.AddToClassList("part-power__desc");
            power.Add(description);

            body.Add(power);
        }

        row.Add(body);
        partsContainer.Add(row);
    }

    private static string PartLine(PartRole slot, BodyPart part) =>
        part != null
            ? Loc.Tr("ui.detail.partrow", SlotName(slot), part.Name, SetName(part), LocEnumMaps.RarityName(part.Rarity))
            : Loc.Tr("ui.detail.partrow.empty", SlotName(slot));

    private static VisualElement BuildPartSwatch(BodyPart part, BrawlSkillRole? ringRole)
    {
        var swatch = new VisualElement();
        swatch.AddToClassList("part-swatch");

        if (ringRole.HasValue)
        {
            swatch.AddToClassList("part-swatch--ring");
            swatch.AddToClassList("mm-role-ring--" + BrawlKitProfile.RoleClass(ringRole.Value));
        }

        Color setColor = part?.Set != null ? part.Set.Color : Color.gray;

        if (part != null && part.Icon != null)
        {
            swatch.AddToClassList("part-icon");
            swatch.style.backgroundImage = new StyleBackground(part.Icon);
            swatch.style.backgroundColor = new Color(0f, 0f, 0f, 0f);
            switch (part.GetPartRole())
            {
                case PartRole.Horn: swatch.AddToClassList("part-icon--horn"); break;
                case PartRole.Back: swatch.AddToClassList("part-icon--back"); break;
                case PartRole.Wing: swatch.AddToClassList("part-icon--wing"); break;
            }
        }
        else
        {
            swatch.style.backgroundColor = setColor;
        }

        return swatch;
    }

    private static string SetName(BodyPart part) => part?.Set != null ? part.Set.Name : "—";

    private static string SlotName(PartRole r) => r switch
    {
        PartRole.Body => Loc.Tr("ui.detail.slot.body"),
        PartRole.Horn => Loc.Tr("ui.detail.slot.horn"),
        PartRole.Back => Loc.Tr("ui.detail.slot.back"),
        PartRole.Wing => Loc.Tr("ui.detail.slot.wing"),
        PartRole.Face => Loc.Tr("ui.detail.slot.face"),
        _             => r.ToString(),
    };

    private static string RoleDesc(Role r) => r switch
    {
        Role.Protector => Loc.Tr("ui.detail.roledesc.protector"),
        Role.Agresivo  => Loc.Tr("ui.detail.roledesc.agresivo"),
        Role.Empatico  => Loc.Tr("ui.detail.roledesc.empatico"),
        _              => "",
    };

    private static string Born(CreatureDNA d) =>
        d.BirthDate == default ? "—" : d.BirthDate.ToLocalTime().ToString("dd/MM/yyyy HH:mm");
}
}
