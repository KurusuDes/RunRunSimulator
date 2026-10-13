using System;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class DetailInheritancePresenter
{
    private readonly Func<CreatureRegistrySO> getRegistry;

    private readonly Label title;
    private readonly VisualElement list;

    public DetailInheritancePresenter(VisualElement root, Func<CreatureRegistrySO> getRegistry)
    {
        this.getRegistry = getRegistry;

        title = root.Q<Label>("inherit-title");
        list = root.Q<VisualElement>("inherit-list");
    }

    public void Rebuild(CreatureDNA dna)
    {
        if (list == null || dna == null) return;
        list.Clear();

        bool any = dna.Origins != null && dna.Origins.Count > 0;
        var display = any ? DisplayStyle.Flex : DisplayStyle.None;
        list.style.display = display;
        if (title != null)
        {
            title.style.display = display;
            title.text = Loc.Tr("ui.detail.inherit.title");
        }
        if (!any) return;

        foreach (var origin in dna.Origins)
            if (origin != null) list.Add(BuildLine(origin));
    }

    private VisualElement BuildLine(PartOrigin origin)
    {
        var line = new VisualElement();
        line.AddToClassList("inherit-line");

        var part = new Label(Loc.Tr("ui.detail.slot." + origin.Role.ToString().ToLowerInvariant()));
        part.AddToClassList("inherit-line__part");
        line.Add(part);

        var text = new Label(OriginText(origin));
        text.AddToClassList("inherit-line__text");
        line.Add(text);
        return line;
    }

    private string OriginText(PartOrigin origin)
    {
        string text = Loc.Tr("ui.detail.inherit.sep") + SlotText(origin);

        var decor = DecorOf(origin.DecorID);
        if (decor != null) text += Loc.Tr("ui.detail.inherit.by", decor.DisplayName);
        return text;
    }

    private string SlotText(PartOrigin origin)
    {
        switch (origin.Slot)
        {
            case InheritanceOddsTableSO.Slot.Mutation: return Loc.Tr("ui.detail.inherit.mutation");
            case InheritanceOddsTableSO.Slot.Base:     return Loc.Tr("ui.detail.inherit.random");
        }

        CreatureDNA ancestor = null;
        var registry = getRegistry();
        if (registry != null && !string.IsNullOrEmpty(origin.AncestorID))
            registry.TryGet(origin.AncestorID, out ancestor);

        string name = ancestor != null ? ancestor.CustomName : "";
        bool female = ancestor != null && ancestor.Gender == CreatureGender.Female;
        string who = female ? "f" : "m";
        string side = origin.MotherSide ? "mother" : "father";

        string kind = origin.Slot == InheritanceOddsTableSO.Slot.Parent ? "parent"
            : origin.Slot == InheritanceOddsTableSO.Slot.Grandparent ? "grand" : "great";

        string key = kind == "parent"
            ? "ui.detail.inherit.parent." + side
            : "ui.detail.inherit." + kind + "." + who + "." + side;

        return Loc.Tr(key, name ?? "").Trim();
    }

    private static BreedingDecorSO DecorOf(string id)
    {
        if (string.IsNullOrEmpty(id)) return null;
        var controller = BreedingController.Instance;
        return controller != null && controller.DecorDatabase != null ? controller.DecorDatabase.Get(id) : null;
    }
}
}
