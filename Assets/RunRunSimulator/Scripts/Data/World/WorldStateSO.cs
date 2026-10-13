using System;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[Serializable]
public class WorldStateData
{
    public int   Day          = 1;
    public float MinuteOfDay  = 360f;
    public int   TutorialStep = 0;
    public Dictionary<string, int> UpgradeLevels = new Dictionary<string, int>();
    public Dictionary<string, int> ShopStock = new Dictionary<string, int>();
    public int LastRestockDay = 0;
    public int BredTotal = 0;
    public Dictionary<string, string> DecorSlots = new Dictionary<string, string>();
    public Dictionary<string, float> StationLevels = new Dictionary<string, float>();
    public List<ShopOrder> Orders = new List<ShopOrder>();
    public int OrdersDay = 0;
    public Dictionary<string, int> Counters = new Dictionary<string, int>();
    public List<string> CompletedGoals = new List<string>();
}

[CreateAssetMenu(fileName = "WorldState", menuName = "RunRunSimulator/World/World State")]
public class WorldStateSO : ScriptableObject
{
    [Title("World State (runtime)")]
    [SerializeField, ReadOnly] private int   day          = 1;
    [SerializeField, ReadOnly] private float minuteOfDay  = 360f;
    [SerializeField, ReadOnly] private int   tutorialStep = 0;

    public int   Day          { get => day;          set => day = value; }
    public float MinuteOfDay  { get => minuteOfDay;  set => minuteOfDay = value; }
    public int   TutorialStep { get => tutorialStep; set => tutorialStep = value; }

    [ShowInInspector, ReadOnly] private Dictionary<string, int> upgradeLevels = new Dictionary<string, int>();

    public int UpgradeLevel(string id) =>
        !string.IsNullOrEmpty(id) && upgradeLevels.TryGetValue(id, out var level) ? level : 0;

    public void SetUpgradeLevel(string id, int level)
    {
        if (string.IsNullOrEmpty(id)) return;
        upgradeLevels[id] = level;
    }

    [ShowInInspector, ReadOnly] private Dictionary<string, int> shopStock = new Dictionary<string, int>();
    [SerializeField, ReadOnly] private int lastRestockDay = 0;

    public int LastRestockDay { get => lastRestockDay; set => lastRestockDay = value; }
    public IReadOnlyDictionary<string, int> ShopStock => shopStock;

    public void SetShopStock(Dictionary<string, int> stock)
    {
        shopStock = stock != null ? new Dictionary<string, int>(stock) : new Dictionary<string, int>();
    }

    [SerializeField, ReadOnly] private int bredTotal = 0;

    public int BredTotal { get => bredTotal; set => bredTotal = value; }

    [ShowInInspector, ReadOnly] private Dictionary<string, string> decorSlots = new Dictionary<string, string>();

    public IReadOnlyDictionary<string, string> DecorSlots => decorSlots;

    public string GetDecorSlot(string slotId) =>
        !string.IsNullOrEmpty(slotId) && decorSlots.TryGetValue(slotId, out var decorId) ? decorId : null;

    public void SetDecorSlot(string slotId, string decorId)
    {
        if (string.IsNullOrEmpty(slotId)) return;
        if (string.IsNullOrEmpty(decorId)) decorSlots.Remove(slotId);
        else decorSlots[slotId] = decorId;
    }

    [ShowInInspector, ReadOnly] private Dictionary<string, float> stationLevels = new Dictionary<string, float>();

    public bool TryGetStationLevel(string id, out float level)
    {
        level = 0f;
        return !string.IsNullOrEmpty(id) && stationLevels.TryGetValue(id, out level);
    }

    public void SetStationLevel(string id, float level)
    {
        if (string.IsNullOrEmpty(id)) return;
        stationLevels[id] = level;
    }

    [ShowInInspector, ReadOnly] private List<ShopOrder> orders = new List<ShopOrder>();
    [SerializeField, ReadOnly] private int ordersDay = 0;

    public List<ShopOrder> Orders { get => orders; set => orders = value ?? new List<ShopOrder>(); }
    public int OrdersDay { get => ordersDay; set => ordersDay = value; }

    [ShowInInspector, ReadOnly] private Dictionary<string, int> counters = new Dictionary<string, int>();
    [ShowInInspector, ReadOnly] private List<string> completedGoals = new List<string>();

    public int Counter(string key) =>
        !string.IsNullOrEmpty(key) && counters.TryGetValue(key, out var value) ? value : 0;

    public void AddCounter(string key, int amount)
    {
        if (string.IsNullOrEmpty(key)) return;
        counters[key] = Counter(key) + amount;
    }

    public bool IsGoalDone(string id) => !string.IsNullOrEmpty(id) && completedGoals.Contains(id);

    public void MarkGoalDone(string id)
    {
        if (string.IsNullOrEmpty(id) || completedGoals.Contains(id)) return;
        completedGoals.Add(id);
    }

    public WorldStateData GetData() => new WorldStateData
    {
        Day            = day,
        MinuteOfDay    = minuteOfDay,
        TutorialStep   = tutorialStep,
        UpgradeLevels  = new Dictionary<string, int>(upgradeLevels),
        ShopStock      = new Dictionary<string, int>(shopStock),
        LastRestockDay = lastRestockDay,
        BredTotal      = bredTotal,
        DecorSlots     = new Dictionary<string, string>(decorSlots),
        StationLevels  = new Dictionary<string, float>(stationLevels),
        Orders         = new List<ShopOrder>(orders),
        OrdersDay      = ordersDay,
        Counters       = new Dictionary<string, int>(counters),
        CompletedGoals = new List<string>(completedGoals),
    };

    public void LoadFrom(WorldStateData data)
    {
        day          = data?.Day ?? 1;
        minuteOfDay  = data?.MinuteOfDay ?? 360f;
        tutorialStep = data?.TutorialStep ?? 0;
        upgradeLevels = data?.UpgradeLevels != null
            ? new Dictionary<string, int>(data.UpgradeLevels)
            : new Dictionary<string, int>();
        shopStock = data?.ShopStock != null
            ? new Dictionary<string, int>(data.ShopStock)
            : new Dictionary<string, int>();
        lastRestockDay = data?.LastRestockDay ?? 0;
        bredTotal = data?.BredTotal ?? 0;
        decorSlots = data?.DecorSlots != null
            ? new Dictionary<string, string>(data.DecorSlots)
            : new Dictionary<string, string>();
        stationLevels = data?.StationLevels != null
            ? new Dictionary<string, float>(data.StationLevels)
            : new Dictionary<string, float>();
        orders = data?.Orders != null
            ? new List<ShopOrder>(data.Orders)
            : new List<ShopOrder>();
        ordersDay = data?.OrdersDay ?? 0;
        counters = data?.Counters != null
            ? new Dictionary<string, int>(data.Counters)
            : new Dictionary<string, int>();
        completedGoals = data?.CompletedGoals != null
            ? new List<string>(data.CompletedGoals)
            : new List<string>();
    }
}
}
