using System.Collections.Generic;
namespace MoriMonchiSimulator
{

public static class BreedingAttribution
{
    public static string CreditFor(InheritanceOddsTableSO.Slot slot, bool motherSide, IReadOnlyList<BreedingDecorSO> decors)
    {
        if (decors == null) return "";

        var slotStat = StatOf(slot);
        string id = FirstWithBoost(decors, slotStat);
        if (!string.IsNullOrEmpty(id)) return id;

        bool ancestorSlot = slot == InheritanceOddsTableSO.Slot.Parent
                         || slot == InheritanceOddsTableSO.Slot.Grandparent
                         || slot == InheritanceOddsTableSO.Slot.GreatGrandparent;
        if (!ancestorSlot) return "";

        return FirstWithBoost(decors, motherSide ? BreedingStat.MotherBias : BreedingStat.FatherBias);
    }

    private static BreedingStat StatOf(InheritanceOddsTableSO.Slot slot) => slot switch
    {
        InheritanceOddsTableSO.Slot.Parent           => BreedingStat.ParentWeight,
        InheritanceOddsTableSO.Slot.Grandparent      => BreedingStat.GrandparentWeight,
        InheritanceOddsTableSO.Slot.GreatGrandparent => BreedingStat.GreatGrandparentWeight,
        InheritanceOddsTableSO.Slot.Mutation         => BreedingStat.MutationWeight,
        _                                            => BreedingStat.BaseWeight
    };

    private static string FirstWithBoost(IReadOnlyList<BreedingDecorSO> decors, BreedingStat stat)
    {
        foreach (var decor in decors)
        {
            if (decor == null || decor.Modifiers == null) continue;
            foreach (var mod in decor.Modifiers)
                if (mod.Stat == stat && mod.Delta > 0f) return decor.Id ?? "";
        }
        return "";
    }
}
}
