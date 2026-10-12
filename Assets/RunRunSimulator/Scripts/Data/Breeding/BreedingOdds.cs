using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BreedingOdds
{
    public float Parent;
    public float Grandparent;
    public float GreatGrandparent;
    public float Mutation;
    public float Base;
    public float MotherSide = 1f;
    public float FatherSide = 1f;

    public static BreedingOdds From(InheritanceOddsTableSO table, IEnumerable<BreedingModifier> mods)
    {
        var odds = new BreedingOdds
        {
            Parent           = table.ParentWeight,
            Grandparent      = table.GrandparentWeight,
            GreatGrandparent = table.GreatGrandparentWeight,
            Mutation         = table.MutationWeight,
            Base             = table.BaseWeight,
        };

        if (mods != null)
            foreach (var mod in mods)
                switch (mod.Stat)
                {
                    case BreedingStat.ParentWeight:           odds.Parent           += mod.Delta; break;
                    case BreedingStat.GrandparentWeight:      odds.Grandparent      += mod.Delta; break;
                    case BreedingStat.GreatGrandparentWeight: odds.GreatGrandparent += mod.Delta; break;
                    case BreedingStat.MutationWeight:         odds.Mutation         += mod.Delta; break;
                    case BreedingStat.BaseWeight:             odds.Base             += mod.Delta; break;
                    case BreedingStat.MotherBias:             odds.MotherSide       += mod.Delta; break;
                    case BreedingStat.FatherBias:             odds.FatherSide       += mod.Delta; break;
                }

        odds.Parent           = Mathf.Max(0f, odds.Parent);
        odds.Grandparent      = Mathf.Max(0f, odds.Grandparent);
        odds.GreatGrandparent = Mathf.Max(0f, odds.GreatGrandparent);
        odds.Mutation         = Mathf.Max(0f, odds.Mutation);
        odds.Base             = Mathf.Max(0f, odds.Base);
        odds.MotherSide       = Mathf.Max(0f, odds.MotherSide);
        odds.FatherSide       = Mathf.Max(0f, odds.FatherSide);
        return odds;
    }

    public InheritanceOddsTableSO.Slot Roll()
    {
        float total = Parent + Grandparent + GreatGrandparent + Mutation + Base;
        if (total <= 0f) return InheritanceOddsTableSO.Slot.Parent;

        float roll = Random.Range(0f, total);
        float c    = 0f;

        c += Parent;            if (roll < c) return InheritanceOddsTableSO.Slot.Parent;
        c += Grandparent;       if (roll < c) return InheritanceOddsTableSO.Slot.Grandparent;
        c += GreatGrandparent;  if (roll < c) return InheritanceOddsTableSO.Slot.GreatGrandparent;
        c += Mutation;          if (roll < c) return InheritanceOddsTableSO.Slot.Mutation;
        return InheritanceOddsTableSO.Slot.Base;
    }

    public bool PickMotherSide()
    {
        float total = MotherSide + FatherSide;
        if (total <= 0f) return Random.value < 0.5f;
        return Random.Range(0f, total) < MotherSide;
    }
}
}
