using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "BrawlKitDatabase", menuName = "MoriMonchi/Brawl/Kit Database")]
public class BrawlKitDatabaseSO : ScriptableObject
{
    public List<BrawlWingKitSO> Wings = new();
    public List<BrawlSkillSO> Skills = new();

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
