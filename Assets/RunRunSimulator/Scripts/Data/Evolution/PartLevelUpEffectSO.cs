using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "PartLevelUpEffect", menuName = "MoriMonchi/Evolution/Part Level Up")]
public class PartLevelUpEffectSO : EvolutionEffectSO
{
    private static readonly PartRole[] Evolvable = { PartRole.Body, PartRole.Horn, PartRole.Back, PartRole.Wing };
    private static readonly List<PartRole> Candidates = new();

    [Required] public BrawlKitDatabaseSO Kits;
    public List<int> CostPerLevel = new() { 30, 60, 100 };
    public int BattlesPerEvolution = 2;

    public override bool CanApply(CreatureDNA dna)
    {
        if (!IsEligible(dna)) return false;
        if (FillCandidates(dna) <= 0) return false;
        return dna.Battles >= RequiredBattles(dna);
    }

    public override int RequiredBattles(CreatureDNA dna)
    {
        if (dna == null) return 0;
        int done = 0;
        for (int i = 0; i < Evolvable.Length; i++) done += (int)dna.TierOf(Evolvable[i]) - 1;
        return BattlesPerEvolution * (done + 1);
    }

    public override int Cost(CreatureDNA dna)
    {
        int band = FillCandidates(dna);
        if (band <= 0 || CostPerLevel == null || CostPerLevel.Count == 0) return 0;
        return CostPerLevel[Mathf.Clamp(band - 1, 0, CostPerLevel.Count - 1)];
    }

    public override bool IsCandidate(CreatureDNA dna, PartRole role)
    {
        if (!IsEligible(dna)) return false;
        return FillCandidates(dna) > 0 && Candidates.Contains(role);
    }

    public override PartRole? Apply(CreatureDNA dna)
    {
        if (!CanApply(dna)) return null;
        var role = Candidates[Random.Range(0, Candidates.Count)];
        dna.SetTier(role, (Tier)((int)dna.TierOf(role) + 1));
        return role;
    }

    private bool IsEligible(CreatureDNA dna)
    {
        if (dna == null || dna.IsDead || dna.IsSold) return false;
        if (dna.Form != MonchiForm.Adult) return false;
        return Kits != null;
    }

    private int FillCandidates(CreatureDNA dna)
    {
        Candidates.Clear();
        if (dna == null || Kits == null) return 0;
        int band = int.MaxValue;
        for (int i = 0; i < Evolvable.Length; i++)
        {
            var role = Evolvable[i];
            int level = (int)dna.TierOf(role);
            if (level >= BrawlUpgrades.MaxLevel(Kits.Upgrades(dna, role))) continue;
            if (level < band)
            {
                band = level;
                Candidates.Clear();
            }
            if (level == band) Candidates.Add(role);
        }
        return Candidates.Count > 0 ? band : 0;
    }
}
}
