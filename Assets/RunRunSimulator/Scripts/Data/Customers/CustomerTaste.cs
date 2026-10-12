using System;
using System.Collections.Generic;
using UnityEngine;
using Random = UnityEngine.Random;

namespace MoriMonchiSimulator
{
public struct CustomerTaste
{
    private const float ColorMatchDistance = 0.35f;

    public TasteKind Kind;
    public Role Role;
    public Color Color;
    public PartSetSO Set;

    public float Match(CreatureDNA dna, CreatureDatabaseSO db)
    {
        if (Kind == TasteKind.None) return 0.5f;
        if (dna == null) return 0f;

        switch (Kind)
        {
            case TasteKind.Role:
                return dna.Role == Role ? 1f : 0f;
            case TasteKind.Color:
            {
                var a = dna.BaseColor;
                float dr = a.r - Color.r, dg = a.g - Color.g, db2 = a.b - Color.b;
                return Mathf.Sqrt(dr * dr + dg * dg + db2 * db2) < ColorMatchDistance ? 1f : 0f;
            }
            case TasteKind.PartSet:
            {
                if (Set == null || db == null) return 0f;
                return db.GetHorn(dna.HornID)?.Set == Set
                    || db.GetBack(dna.BackID)?.Set == Set
                    || db.GetWing(dna.WingID)?.Set == Set ? 1f : 0f;
            }
        }
        return 0f;
    }

    public string Describe()
    {
        switch (Kind)
        {
            case TasteKind.Role:    return Loc.Tr("npc.taste.role", LocEnumMaps.RoleName(Role));
            case TasteKind.Color:   return Loc.Tr("npc.taste.color");
            case TasteKind.PartSet: return Set != null ? Loc.Tr("npc.taste.set", Set.Name) : Loc.Tr("npc.taste.none");
            default:                return Loc.Tr("npc.taste.none");
        }
    }

    public static CustomerTaste Roll(CustomerArchetypeSO archetype, IReadOnlyList<CreatureDNA> onDisplay, CreatureDatabaseSO db)
    {
        var taste = new CustomerTaste { Kind = archetype != null ? archetype.Taste : TasteKind.None };
        if (taste.Kind == TasteKind.None) return taste;

        bool fromDisplay = onDisplay != null && onDisplay.Count > 0
                        && Random.value < archetype.TasteFromDisplayChance;

        if (fromDisplay && TryCopy(ref taste, onDisplay[Random.Range(0, onDisplay.Count)], db))
            return taste;

        RollRandom(ref taste, onDisplay, db);
        return taste;
    }

    private static bool TryCopy(ref CustomerTaste taste, CreatureDNA source, CreatureDatabaseSO db)
    {
        if (source == null) return false;
        switch (taste.Kind)
        {
            case TasteKind.Role:
                taste.Role = source.Role;
                return true;
            case TasteKind.Color:
                taste.Color = source.BaseColor;
                return true;
            case TasteKind.PartSet:
            {
                var sets = new List<PartSetSO>(3);
                AddSet(sets, db?.GetHorn(source.HornID));
                AddSet(sets, db?.GetBack(source.BackID));
                AddSet(sets, db?.GetWing(source.WingID));
                if (sets.Count == 0) return false;
                taste.Set = sets[Random.Range(0, sets.Count)];
                return true;
            }
        }
        return false;
    }

    private static void AddSet(List<PartSetSO> sets, BodyPart part)
    {
        if (part != null && part.Set != null) sets.Add(part.Set);
    }

    private static void RollRandom(ref CustomerTaste taste, IReadOnlyList<CreatureDNA> onDisplay, CreatureDatabaseSO db)
    {
        switch (taste.Kind)
        {
            case TasteKind.Role:
                var roles = (Role[])Enum.GetValues(typeof(Role));
                taste.Role = roles[Random.Range(0, roles.Length)];
                break;
            case TasteKind.Color:
                taste.Color = onDisplay != null && onDisplay.Count > 0 && Random.value < 0.5f
                    ? onDisplay[Random.Range(0, onDisplay.Count)].BaseColor
                    : Color.HSVToRGB(Random.value, 0.7f, 0.9f);
                break;
            case TasteKind.PartSet:
                var sets = new List<PartSetSO>();
                CollectSets(sets, db?.Horns?.PartsTable);
                CollectSets(sets, db?.Backs?.PartsTable);
                CollectSets(sets, db?.Wings?.PartsTable);
                if (sets.Count > 0) taste.Set = sets[Random.Range(0, sets.Count)];
                else taste.Kind = TasteKind.None;
                break;
        }
    }

    private static void CollectSets<T>(List<PartSetSO> sets, List<T> parts) where T : BodyPart
    {
        if (parts == null) return;
        foreach (var p in parts)
            if (p != null && p.Set != null && !sets.Contains(p.Set)) sets.Add(p.Set);
    }
}
}
