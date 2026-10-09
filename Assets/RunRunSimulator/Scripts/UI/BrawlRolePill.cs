using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public static class BrawlRolePill
{
    public static VisualElement Build(in BrawlKitProfile profile)
    {
        var pill = NewPill();

        if (profile.Balanced)
        {
            pill.Add(Segment(Loc.Tr("ui.brawlrole.balanced"), "balanced", false));
            return pill;
        }

        pill.Add(Segment(profile.Primary, false));
        if (profile.HasSecondary) pill.Add(Segment(profile.Secondary, true));
        return pill;
    }

    public static VisualElement Build(BrawlSkillRole role)
    {
        var pill = NewPill();
        pill.Add(Segment(role, false));
        return pill;
    }

    private static VisualElement NewPill()
    {
        var pill = new VisualElement();
        pill.AddToClassList("mm-rolepill");
        return pill;
    }

    private static Label Segment(BrawlSkillRole role, bool minor) =>
        Segment(Loc.Tr(BrawlKitProfile.RoleKey(role)), BrawlKitProfile.RoleClass(role), minor);

    private static Label Segment(string text, string roleClass, bool minor)
    {
        var seg = new Label(text);
        seg.AddToClassList("mm-rolepill__seg");
        seg.AddToClassList("mm-role--" + roleClass);
        if (minor) seg.AddToClassList("mm-rolepill__seg--minor");
        return seg;
    }
}
}
