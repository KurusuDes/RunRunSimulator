using System;
using System.Collections.Generic;
using UnityEngine;
using Random = UnityEngine.Random;
namespace MoriMonchiSimulator
{

public class OrderBoardService : MonoBehaviour
{
    private const int OrdersPerDay = 3;
    private const int RoleReward   = 15;
    private const int SetReward    = 20;
    private const int MaxAttempts  = 40;

    public static OrderBoardService Instance { get; private set; }

    private static WorldStateSO World => GameManager.Instance != null ? GameManager.Instance.WorldState : null;

    public IReadOnlyList<ShopOrder> Active => World != null ? World.Orders : (IReadOnlyList<ShopOrder>)Array.Empty<ShopOrder>();

    private void Awake()
    {
        Instance = this;
    }

    private void OnDestroy()
    {
        if (Instance == this) Instance = null;
    }

    private void OnEnable()
    {
        GameEvents.OnWorldStateReloaded += OnWorldStateReloaded;
        GameEvents.OnDayStarted += OnDayStarted;
        GameEvents.OnCustomerSold += OnCustomerSold;
    }

    private void OnDisable()
    {
        GameEvents.OnWorldStateReloaded -= OnWorldStateReloaded;
        GameEvents.OnDayStarted -= OnDayStarted;
        GameEvents.OnCustomerSold -= OnCustomerSold;
    }

    private void OnWorldStateReloaded(WorldStateSO world)
    {
        if (world != null) RollIfNeeded(world, world.Day);
    }

    private void OnDayStarted(int day)
    {
        var world = World;
        if (world != null) RollIfNeeded(world, day);
    }

    private void RollIfNeeded(WorldStateSO world, int day)
    {
        if (world.OrdersDay == day) return;

        var db = GameManager.Instance != null ? GameManager.Instance.Database : null;
        world.Orders = Roll(db);
        world.OrdersDay = day;
        GameEvents.WorldStateChanged(world);
    }

    private static List<ShopOrder> Roll(CreatureDatabaseSO db)
    {
        var sets = new List<string>();
        CollectSetNames(sets, db?.Horns?.PartsTable);
        CollectSetNames(sets, db?.Backs?.PartsTable);
        CollectSetNames(sets, db?.Wings?.PartsTable);

        var roles = (Role[])Enum.GetValues(typeof(Role));
        var orders = new List<ShopOrder>(OrdersPerDay);

        for (int attempt = 0; attempt < MaxAttempts && orders.Count < OrdersPerDay; attempt++)
        {
            ShopOrder order;
            if (sets.Count > 0 && Random.value < 0.5f)
                order = new ShopOrder { Kind = TasteKind.PartSet, SetName = sets[Random.Range(0, sets.Count)], Reward = SetReward };
            else
                order = new ShopOrder { Kind = TasteKind.Role, Role = roles[Random.Range(0, roles.Length)], Reward = RoleReward };

            if (!Contains(orders, order)) orders.Add(order);
        }
        return orders;
    }

    private static bool Contains(List<ShopOrder> orders, ShopOrder candidate)
    {
        foreach (var o in orders)
        {
            if (o.Kind != candidate.Kind) continue;
            if (o.Kind == TasteKind.Role ? o.Role == candidate.Role : o.SetName == candidate.SetName) return true;
        }
        return false;
    }

    private static void CollectSetNames<T>(List<string> names, List<T> parts) where T : BodyPart
    {
        if (parts == null) return;
        foreach (var p in parts)
            if (p != null && p.Set != null && !string.IsNullOrEmpty(p.Set.Name) && !names.Contains(p.Set.Name)) names.Add(p.Set.Name);
    }

    private void OnCustomerSold(NpcAgent agent, CreatureDNA dna, int price)
    {
        var world = World;
        if (world == null || dna == null) return;

        var db = GameManager.Instance.Database;
        var orders = world.Orders;
        for (int i = 0; i < orders.Count; i++)
        {
            var order = orders[i];
            if (order.ToTaste(db).Match(dna, db) < 1f) continue;

            orders.RemoveAt(i);
            Wallet.Add(Currency.Dabloons, order.Reward, "order");
            GameEvents.WorldStateChanged(world);
            GameEvents.OrderCompleted(order);
            return;
        }
    }
}
}
