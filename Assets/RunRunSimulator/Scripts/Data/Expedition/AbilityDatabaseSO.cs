using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "AbilityDatabase", menuName = "RunRunSimulator/Expedition/Ability Database")]
public class AbilityDatabaseSO : ScriptableObject
{
    public List<AbilitySO> Abilities = new List<AbilitySO>();

    public AbilitySO[] Resolve(CreatureDNA dna, CreatureDatabaseSO parts)
    {
        return new[]
        {
            parts?.GetHorn(dna?.HornID)?.Ability ?? Pick(dna?.HornID, ClashSlot.Horn),
            parts?.GetWing(dna?.WingID)?.Ability ?? Pick(dna?.WingID, ClashSlot.Wings),
            parts?.GetBack(dna?.BackID)?.Ability ?? Pick(dna?.BackID, ClashSlot.Back),
        };
    }

    private AbilitySO Pick(string partId, ClashSlot slot)
    {
        var candidates = new List<AbilitySO>();
        foreach (var ability in Abilities)
            if (ability != null && ability.Slot == slot) candidates.Add(ability);

        if (candidates.Count == 0) return null;

        int index = StableHash(partId ?? "") % candidates.Count;
        return candidates[index];
    }

    private static int StableHash(string s)
    {
        unchecked
        {
            int h = 23;
            foreach (char c in s) h = h * 31 + c;
            return h & 0x7fffffff;
        }
    }
}
}
