using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public static class BreedingInheritanceView
{
    private static readonly PartRole[] Order =
    {
        PartRole.Horn, PartRole.Back, PartRole.Wing, PartRole.Face, PartRole.Body
    };

    public static void Build(VisualElement list, CreatureDatabaseSO database, CreatureDNA father, CreatureDNA mother)
    {
        if (list == null) return;
        list.Clear();
        foreach (var role in Order)
            list.Add(BuildRow(role, PartOf(database, father, role), PartOf(database, mother, role), father != null, mother != null));
    }

    private static VisualElement BuildRow(PartRole role, BodyPart fatherPart, BodyPart motherPart, bool hasFather, bool hasMother)
    {
        var row = new VisualElement();
        row.AddToClassList("mm-row");
        row.AddToClassList("inherit-row");

        var box = new VisualElement();
        box.AddToClassList("mm-statbox");
        box.AddToClassList("inherit-row__box");
        var icon = new VisualElement { pickingMode = PickingMode.Ignore };
        icon.AddToClassList("mm-icon");
        icon.AddToClassList("inherit-icon--" + role.ToString().ToLowerInvariant());
        box.Add(icon);
        row.Add(box);

        var name = new Label(Loc.Tr("ui.detail.slot." + role.ToString().ToLowerInvariant()));
        name.AddToClassList("inherit-row__role");
        row.Add(name);

        bool same = fatherPart != null && motherPart != null && fatherPart.Set != null && fatherPart.Set == motherPart.Set;
        row.Add(BuildCell(fatherPart, hasFather, same));
        row.Add(BuildCell(motherPart, hasMother, same));
        return row;
    }

    private static VisualElement BuildCell(BodyPart part, bool hasParent, bool same)
    {
        var cell = new VisualElement();
        cell.AddToClassList("inherit-cell");
        if (same) cell.AddToClassList("inherit-cell--same");

        var swatch = new VisualElement();
        swatch.AddToClassList("inherit-cell__swatch");
        if (part != null) swatch.style.backgroundColor = part.Set != null ? part.Set.Color : Color.gray;
        else swatch.style.display = DisplayStyle.None;
        cell.Add(swatch);

        var label = new Label(hasParent && part != null ? DataLoc.PartName(part) : "—");
        label.AddToClassList("inherit-cell__text");
        cell.Add(label);
        return cell;
    }

    private static BodyPart PartOf(CreatureDatabaseSO database, CreatureDNA dna, PartRole role)
    {
        if (database == null || dna == null) return null;
        switch (role)
        {
            case PartRole.Horn: return database.GetHorn(dna.HornID);
            case PartRole.Back: return database.GetBack(dna.BackID);
            case PartRole.Wing: return database.GetWing(dna.WingID);
            case PartRole.Face: return database.GetFace(dna.FaceID);
            default:            return database.GetBodyShape(dna.BodyShapeID);
        }
    }
}
}
