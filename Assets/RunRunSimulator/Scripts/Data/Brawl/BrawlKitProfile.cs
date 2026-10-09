namespace MoriMonchiSimulator
{

public readonly struct BrawlKitProfile
{
    public readonly BrawlWingKitSO Wing;
    public readonly BrawlSkillSO Horn;
    public readonly BrawlSkillSO Back;
    public readonly BrawlTheme WingTheme;
    public readonly BrawlTheme HornTheme;
    public readonly BrawlTheme BackTheme;
    public readonly BrawlSkillRole Primary;
    public readonly bool HasSecondary;
    public readonly BrawlSkillRole Secondary;
    public readonly bool Balanced;
    public readonly bool BackLocked;

    private BrawlKitProfile(BrawlWingKitSO wing, BrawlSkillSO horn, BrawlSkillSO back, BrawlTheme wingTheme, BrawlTheme hornTheme, BrawlTheme backTheme, bool backLocked)
    {
        Wing = wing;
        Horn = horn;
        Back = back;
        WingTheme = wingTheme;
        HornTheme = hornTheme;
        BackTheme = backTheme;
        BackLocked = backLocked;

        Resolve(
            horn != null ? horn.Role : (BrawlSkillRole?)null,
            back != null ? back.Role : (BrawlSkillRole?)null,
            wing != null ? WingRole(wing) : (BrawlSkillRole?)null,
            out var primary, out var hasSecondary, out var secondary, out var balanced);
        Primary = primary;
        HasSecondary = hasSecondary;
        Secondary = secondary;
        Balanced = balanced;
    }

    public bool HasRole(BrawlSkillRole role)
    {
        return (Wing != null && WingRole(Wing) == role)
            || (Horn != null && Horn.Role == role)
            || (Back != null && Back.Role == role);
    }

    public static BrawlKitProfile Of(CreatureDNA dna, BrawlKitDatabaseSO kits, CreatureDatabaseSO parts)
    {
        BrawlWingKitSO wing = null;
        BrawlSkillSO horn = null;
        BrawlSkillSO back = null;
        bool locked = dna != null && dna.Form != MonchiForm.Adult;
        if (dna != null && kits != null)
        {
            wing = kits.Wing(dna.WingID);
            horn = kits.Skill(dna.HornID, ClashSlot.Horn);
            if (!locked)
                back = kits.Skill(dna.BackID, ClashSlot.Back);
        }

        BodyPart wingPart = dna != null && parts != null ? parts.GetWing(dna.WingID) : null;
        BodyPart hornPart = dna != null && parts != null ? parts.GetHorn(dna.HornID) : null;
        BodyPart backPart = dna != null && parts != null ? parts.GetBack(dna.BackID) : null;

        BrawlTheme wingTheme = wing != null
            ? BrawlTheme.Resolve(wingPart, wing.IconOverride, wing.ColorOverride, wing.Signature)
            : BrawlTheme.Resolve(wingPart, null, default);
        BrawlTheme hornTheme = horn != null
            ? BrawlTheme.Resolve(hornPart, horn.IconOverride, horn.ColorOverride, horn.Signature)
            : BrawlTheme.Resolve(hornPart, null, default);
        BrawlTheme backTheme = locked
            ? default
            : back != null
                ? BrawlTheme.Resolve(backPart, back.IconOverride, back.ColorOverride, back.Signature)
                : BrawlTheme.Resolve(backPart, null, default);

        return new BrawlKitProfile(wing, horn, back, wingTheme, hornTheme, backTheme, locked);
    }

    public static BrawlSkillRole WingRole(BrawlWingKitSO wing)
    {
        return wing != null && wing.AllyHeal > 0f ? BrawlSkillRole.Support : BrawlSkillRole.Offense;
    }

    private static void Resolve(BrawlSkillRole? horn, BrawlSkillRole? back, BrawlSkillRole? wing, out BrawlSkillRole primary, out bool hasSecondary, out BrawlSkillRole secondary, out bool balanced)
    {
        primary = BrawlSkillRole.Offense;
        secondary = BrawlSkillRole.Offense;
        hasSecondary = false;
        balanced = false;

        if (horn.HasValue && back.HasValue && wing.HasValue)
        {
            if (horn == back && back == wing) primary = horn.Value;
            else if (horn == back) { primary = horn.Value; secondary = wing.Value; hasSecondary = true; }
            else if (horn == wing) { primary = horn.Value; secondary = back.Value; hasSecondary = true; }
            else if (back == wing) { primary = back.Value; secondary = horn.Value; hasSecondary = true; }
            else { primary = horn.Value; balanced = true; }
            return;
        }

        BrawlSkillRole? first = horn ?? back ?? wing;
        BrawlSkillRole? second = horn.HasValue ? (back ?? wing) : (back.HasValue ? wing : null);
        if (!first.HasValue) return;

        primary = first.Value;
        if (second.HasValue && second.Value != first.Value)
        {
            secondary = second.Value;
            hasSecondary = true;
        }
    }

    public static string RoleKey(BrawlSkillRole role)
    {
        switch (role)
        {
            case BrawlSkillRole.Control: return "ui.brawlrole.control";
            case BrawlSkillRole.Support: return "ui.brawlrole.support";
            case BrawlSkillRole.Tank: return "ui.brawlrole.tank";
            default: return "ui.brawlrole.offense";
        }
    }

    public static string RoleClass(BrawlSkillRole role)
    {
        switch (role)
        {
            case BrawlSkillRole.Control: return "control";
            case BrawlSkillRole.Support: return "support";
            case BrawlSkillRole.Tank: return "tank";
            default: return "offense";
        }
    }
}
}
