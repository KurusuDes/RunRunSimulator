using System;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class DetailInfoTabPresenter
{
    private readonly CreatureDatabaseSO database;
    private readonly CareGateSO careGate;
    private readonly BrawlKitDatabaseSO kits;
    private readonly DetailEvolutionBlock evolutionBlock;

    private readonly VisualElement needHealthFill, needEnergyFill, needAffectFill;
    private readonly VisualElement needHealthRow, needEnergyRow, needAffectRow;
    private readonly Label needHealthValue, needEnergyValue, needAffectValue;
    private readonly Label exploreStatus, combatRoleTitle, subtitle;
    private readonly Label statState, statBorn, statBreeds, statBattles;
    private readonly Label personalityName, personalityDesc;
    private readonly VisualElement partsContainer, combatRole, combatRolePill, slotsLeft, slotsRight;
    private CreatureDNA lastDna;

    public DetailInfoTabPresenter(VisualElement root, CreatureDatabaseSO database, CareGateSO careGate, BrawlKitDatabaseSO kits,
        EvolutionEffectSO evolution, Func<CreatureRegistrySO> registry)
    {
        this.database = database;
        this.careGate = careGate;
        this.kits = kits;
        evolutionBlock = new DetailEvolutionBlock(kits, evolution, registry, () => Rebuild(lastDna));

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
        needHealthValue  = root.Q<Label>("need-health-value");
        needEnergyValue  = root.Q<Label>("need-energy-value");
        needAffectValue  = root.Q<Label>("need-affect-value");
        subtitle         = root.Q<Label>("subtitle");
        statState        = root.Q<Label>("stat-state-value");
        statBorn         = root.Q<Label>("stat-born-value");
        statBreeds       = root.Q<Label>("stat-breeds-value");
        statBattles      = root.Q<Label>("stat-battles-value");
        personalityName  = root.Q<Label>("personality-name");
        personalityDesc  = root.Q<Label>("personality-desc");
        slotsLeft        = root.Q<VisualElement>("slots-left");
        slotsRight       = root.Q<VisualElement>("slots-right");
        partsContainer   = root.Q<VisualElement>("parts");
    }

    public void Rebuild(CreatureDNA dna)
    {
        if (dna == null) return;
        lastDna = dna;

        SetNeedBar(needHealthFill, needHealthValue, NeedType.Health, dna.Needs.Health);
        SetNeedBar(needEnergyFill, needEnergyValue, NeedType.Energy, dna.Needs.Energy);
        SetNeedBar(needAffectFill, needAffectValue, NeedType.Affect, dna.Needs.Affect);

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

        if (subtitle != null)
            subtitle.text = $"{LocEnumMaps.GenderName(dna.Gender)} · {LocEnumMaps.RoleName(dna.Role)} · {LocEnumMaps.ElementName(dna.Element)}";

        if (statState != null) statState.text = CreatureDisplay.StateOf(dna);
        if (statBorn != null) statBorn.text = Born(dna);
        if (statBreeds != null) statBreeds.text = dna.BreedCount.ToString();
        if (statBattles != null) statBattles.text = dna.Battles.ToString();

        if (personalityName != null) personalityName.text = LocEnumMaps.RoleName(dna.Role);
        if (personalityDesc != null) personalityDesc.text = RoleDesc(dna.Role);

        var profile = BrawlKitProfile.Of(dna, kits, database);

        SetCombatRole(profile);
        BuildSlots(dna);
        BuildParts(dna, profile);
    }

    private static void SetNeedBar(VisualElement fill, Label valueLabel, NeedType need, float value)
    {
        if (valueLabel != null) valueLabel.text = Mathf.RoundToInt(NeedsDisplay.Fill01(need, value) * 100f) + "%";
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

        var action = evolutionBlock.BuildAction(dna);
        if (action != null) partsContainer.Add(action);

        if (database == null) return;

        AddPartRow(PartRole.Body, database.GetBodyShape(dna.BodyShapeID), evolutionBlock.Build(dna, PartRole.Body, null));
        AddSkillRow(PartRole.Horn, database.GetHorn(dna.HornID), profile.Horn, evolution: evolutionBlock.Build(dna, PartRole.Horn, profile.Horn?.Family));
        AddSkillRow(PartRole.Back, database.GetBack(dna.BackID), profile.Back, profile.BackLocked,
            profile.BackLocked ? null : evolutionBlock.Build(dna, PartRole.Back, profile.Back?.Family));
        AddWingRow(PartRole.Wing, database.GetWing(dna.WingID), profile.Wing, evolutionBlock.Build(dna, PartRole.Wing, null));
    }

    private void BuildSlots(CreatureDNA dna)
    {
        slotsLeft?.Clear();
        slotsRight?.Clear();
        if (database == null) return;

        slotsLeft?.Add(BuildSlot(PartRole.Horn, database.GetHorn(dna.HornID)));
        slotsLeft?.Add(BuildSlot(PartRole.Back, database.GetBack(dna.BackID)));
        slotsLeft?.Add(BuildSlot(PartRole.Wing, database.GetWing(dna.WingID)));
        slotsRight?.Add(BuildSlot(PartRole.Face, database.GetFace(dna.FaceID)));
        slotsRight?.Add(BuildSlot(PartRole.Body, database.GetBodyShape(dna.BodyShapeID)));
    }

    private static VisualElement BuildSlot(PartRole slot, BodyPart part)
    {
        var root = new VisualElement();
        root.AddToClassList("detail-slot");

        var box = new VisualElement();
        box.AddToClassList("mm-slot");
        box.AddToClassList("detail-slot__box");

        var vignette = new VisualElement { pickingMode = PickingMode.Ignore };
        vignette.AddToClassList("mm-layer");
        vignette.AddToClassList("mm-slot__vignette");
        box.Add(vignette);

        var icon = new VisualElement();
        icon.AddToClassList("detail-slot__icon");
        if (part != null && part.Icon != null)
        {
            icon.style.backgroundImage = new StyleBackground(part.Icon);
            switch (slot)
            {
                case PartRole.Horn: icon.AddToClassList("part-icon--horn"); break;
                case PartRole.Back: icon.AddToClassList("part-icon--back"); break;
                case PartRole.Wing: icon.AddToClassList("part-icon--wing"); break;
            }
        }
        else
        {
            icon.AddToClassList("detail-slot__icon--" + slot.ToString().ToLowerInvariant());
            if (part?.Set != null) icon.style.unityBackgroundImageTintColor = part.Set.Color;
        }
        box.Add(icon);

        var frame = new VisualElement { pickingMode = PickingMode.Ignore };
        frame.AddToClassList("mm-layer");
        frame.AddToClassList("mm-slot__frame");
        box.Add(frame);

        root.Add(box);

        var label = new Label(SlotName(slot));
        label.AddToClassList("detail-slot__label");
        root.Add(label);

        var name = new Label(part?.Name ?? "—");
        name.AddToClassList("detail-slot__name");
        root.Add(name);

        return root;
    }

    private void AddSkillRow(PartRole slot, BodyPart part, BrawlSkillSO skill, bool locked = false, VisualElement evolution = null)
    {
        if (locked) AddPowerPartRow(slot, part, Loc.Tr("ui.power.locked.title"), Loc.Tr("ui.power.locked.desc"), null, true, evolution);
        else if (skill != null) AddPowerPartRow(slot, part, skill.Title, skill.Description, skill.Role, evolution: evolution);
        else AddPowerPartRow(slot, part, null, null, null, evolution: evolution);
    }

    private void AddWingRow(PartRole slot, BodyPart part, BrawlWingKitSO wing, VisualElement evolution = null)
    {
        if (wing != null) AddPowerPartRow(slot, part, wing.Title, wing.Description, BrawlKitProfile.WingRole(wing), evolution: evolution);
        else AddPowerPartRow(slot, part, null, null, null, evolution: evolution);
    }

    private void AddPartRow(PartRole slot, BodyPart part, VisualElement evolution = null)
    {
        var row = new VisualElement();
        row.AddToClassList("part-row");
        row.Add(BuildPartSwatch(part, null));

        var text = new Label();
        text.AddToClassList("part-text");
        text.text = PartText(slot, part);

        if (evolution != null)
        {
            var body = new VisualElement();
            body.AddToClassList("part-body");
            body.Add(text);
            body.Add(evolution);
            row.Add(body);
        }
        else
        {
            row.Add(text);
        }

        partsContainer.Add(row);
    }

    private void AddPowerPartRow(PartRole slot, BodyPart part, string powerTitle, string powerDescription, BrawlSkillRole? powerRole, bool locked = false, VisualElement evolution = null)
    {
        var row = new VisualElement();
        row.AddToClassList("part-row");
        row.Add(BuildPartSwatch(part, powerRole));

        var body = new VisualElement();
        body.AddToClassList("part-body");

        var text = new Label();
        text.AddToClassList("part-text");
        text.text = PartText(slot, part);
        body.Add(text);

        if (powerRole.HasValue || locked)
        {
            var power = new VisualElement();
            power.AddToClassList("part-power");
            power.EnableInClassList("part-power--locked", locked);

            var title = new Label(powerTitle);
            title.AddToClassList("part-power__title");
            if (powerRole.HasValue) title.AddToClassList("mm-role-text--" + BrawlKitProfile.RoleClass(powerRole.Value));
            power.Add(title);

            var description = new Label(powerDescription);
            description.AddToClassList("part-power__desc");
            power.Add(description);

            body.Add(power);
        }

        if (evolution != null) body.Add(evolution);

        row.Add(body);
        partsContainer.Add(row);
    }

    private static string PartText(PartRole slot, BodyPart part) =>
        part != null ? $"{SlotName(slot)} · {part.Name}" : SlotName(slot);

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
            if (part != null) swatch.AddToClassList("detail-slot__icon--" + part.GetPartRole().ToString().ToLowerInvariant());
            swatch.style.unityBackgroundImageTintColor = setColor;
        }

        return swatch;
    }

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
        d.BirthDate == default ? "—" : d.BirthDate.ToLocalTime().ToString("dd/MM/yy");
}
}
