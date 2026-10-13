using System;
using System.Collections.Generic;
namespace MoriMonchiSimulator
{

[Serializable]
public class ShopOrder
{
    public TasteKind Kind;
    public Role      Role;
    public string    SetName;
    public int       Reward;

    public CustomerTaste ToTaste(CreatureDatabaseSO db)
    {
        var taste = new CustomerTaste { Kind = Kind, Role = Role };
        if (Kind != TasteKind.PartSet) return taste;

        taste.Set = FindSet(db);
        return taste;
    }

    public string Describe() => Kind == TasteKind.PartSet
        ? Loc.Tr("ui.orders.set", SetName)
        : Loc.Tr("ui.orders.role", LocEnumMaps.RoleName(Role));

    private PartSetSO FindSet(CreatureDatabaseSO db)
    {
        if (db == null || string.IsNullOrEmpty(SetName)) return null;
        return Find(db.Horns?.PartsTable) ?? Find(db.Backs?.PartsTable) ?? Find(db.Wings?.PartsTable);
    }

    private PartSetSO Find<T>(List<T> parts) where T : BodyPart
    {
        if (parts == null) return null;
        foreach (var p in parts)
            if (p != null && p.Set != null && p.Set.Name == SetName) return p.Set;
        return null;
    }
}
}
