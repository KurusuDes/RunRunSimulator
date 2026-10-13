using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public enum GoalKind
{
    CreaturesSold,
    CreaturesBred,
    Descents,
    OrdersCompleted,
    DabloonsEarned,
    ExpansionOpened,
}

[CreateAssetMenu(fileName = "Goal", menuName = "RunRunSimulator/Progress/Goal")]
public class GoalSO : SerializedScriptableObject
{
    public string Id;
    public string TitleKey;
    public GoalKind Kind;
    [ShowIf("@Kind == GoalKind.ExpansionOpened")] public string ExpansionId;
    public int Target = 1;
    public int RewardDabloons;
    public List<ShopUpgradeSO> UnlocksExpansions = new List<ShopUpgradeSO>();
    public List<ItemDefinitionSO> UnlocksItems = new List<ItemDefinitionSO>();
}
}
