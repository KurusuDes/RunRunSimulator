using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "BrawlKitDatabase", menuName = "MoriMonchi/Brawl/Kit Database")]
public class BrawlKitDatabaseSO : ScriptableObject
{
    public List<BrawlWingKitSO> Wings = new();
    public List<BrawlSkillSO> Skills = new();
    public List<BrawlUpgradeStep> BodyUpgrades = new();

    private static readonly IReadOnlyList<BrawlUpgradeStep> NoUpgrades = new List<BrawlUpgradeStep>().AsReadOnly();

    public IReadOnlyList<BrawlUpgradeStep> Upgrades(CreatureDNA dna, PartRole role)
    {
        if (dna == null) return NoUpgrades;
        IReadOnlyList<BrawlUpgradeStep> steps = null;
        switch (role)
        {
            case PartRole.Body: steps = BodyUpgrades; break;
            case PartRole.Horn: steps = Skill(dna.HornID, ClashSlot.Horn)?.Upgrades; break;
            case PartRole.Back: steps = Skill(dna.BackID, ClashSlot.Back)?.Upgrades; break;
            case PartRole.Wing: steps = Wing(dna.WingID)?.Upgrades; break;
        }
        return steps ?? NoUpgrades;
    }

    public BrawlWingKitSO Wing(string partId)
    {
        for (int i = 0; i < Wings.Count; i++)
        {
            var kit = Wings[i];
            if (kit != null && kit.PartId == partId) return kit;
        }
        return Wings.Count > 0 ? Wings[0] : null;
    }

    public BrawlSkillSO Skill(string partId, ClashSlot slot)
    {
        for (int i = 0; i < Skills.Count; i++)
        {
            var skill = Skills[i];
            if (skill != null && skill.PartId == partId) return skill;
        }
        for (int i = 0; i < Skills.Count; i++)
        {
            var skill = Skills[i];
            if (skill != null && skill.Slot == slot) return skill;
        }
        return null;
    }
}
}
