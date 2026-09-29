using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "ShopUpgrade", menuName = "RunRunSimulator/Store/Shop Upgrade")]
public class ShopUpgradeSO : SerializedScriptableObject
{
    [Title("Identity")]
    [Tooltip("Unique key saved in the world state. Must not contain '-'.")]
    public string Id;
    public string DisplayName;

    [Title("Levels")]
    [Tooltip("Dabloons price of each level. Count = max level.")]
    public List<int> LevelPrices = new List<int>();
    [MinValue(1)] public int BonusPerLevel = 1;

    public int MaxLevel => LevelPrices != null ? LevelPrices.Count : 0;

    public bool IsMaxed(int level) => level >= MaxLevel;

    public int PriceFor(int currentLevel) =>
        currentLevel >= 0 && currentLevel < MaxLevel ? LevelPrices[currentLevel] : 0;

    public int BonusAt(int level) => Mathf.Clamp(level, 0, MaxLevel) * BonusPerLevel;

    public int CurrentLevel
    {
        get
        {
            var world = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
            return world != null ? world.UpgradeLevel(Id) : 0;
        }
    }

    public int CurrentBonus => BonusAt(CurrentLevel);
}
}
