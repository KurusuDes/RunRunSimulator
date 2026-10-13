using System.Collections;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class GoalService : MonoBehaviour
{
    private const string SoldKey     = "sold";
    private const string DescentsKey = "descents";
    private const string OrdersKey   = "orders";
    private const string EarnedKey   = "earned";

    [SerializeField] private List<GoalSO> goals = new List<GoalSO>();
    [Required, SerializeField] private CloudSyncService cloudSync;
    [SerializeField] private float syncTimeoutSeconds = 20f;

    private bool ready;

    public static GoalService Instance { get; private set; }

    public IReadOnlyList<GoalSO> Goals => goals;

    private WorldStateSO World => GameManager.Instance != null ? GameManager.Instance.WorldState : null;

    private void Awake() => Instance = this;

    private void OnDestroy()
    {
        if (Instance == this) Instance = null;
    }

    private void OnEnable()
    {
        GameEvents.OnCustomerSold += OnCustomerSold;
        GameEvents.OnExpeditionReturned += OnExpeditionReturned;
        GameEvents.OnOrderCompleted += OnOrderCompleted;
        GameEvents.OnBreedingCompleted += OnBreedingCompleted;
        GameEvents.OnShopZoneOpened += OnShopZoneOpened;
        GameEvents.OnWorldStateReloaded += OnWorldStateReloaded;
    }

    private void OnDisable()
    {
        GameEvents.OnCustomerSold -= OnCustomerSold;
        GameEvents.OnExpeditionReturned -= OnExpeditionReturned;
        GameEvents.OnOrderCompleted -= OnOrderCompleted;
        GameEvents.OnBreedingCompleted -= OnBreedingCompleted;
        GameEvents.OnShopZoneOpened -= OnShopZoneOpened;
        GameEvents.OnWorldStateReloaded -= OnWorldStateReloaded;
    }

    private void Start() => StartCoroutine(FirstEvaluationRoutine());

    private IEnumerator FirstEvaluationRoutine()
    {
        float elapsed = 0f;
        while (cloudSync != null && !cloudSync.StartupSyncDone && elapsed < syncTimeoutSeconds)
        {
            elapsed += Time.unscaledDeltaTime;
            yield return null;
        }
        ready = true;
        Apply(false);
    }

    private void OnWorldStateReloaded(WorldStateSO world)
    {
        if (!ready) return;
        Apply(false);
    }

    private void OnCustomerSold(NpcAgent agent, CreatureDNA dna, int price)
    {
        var world = World;
        if (!ready || world == null) return;
        world.AddCounter(SoldKey, 1);
        if (price > 0) world.AddCounter(EarnedKey, price);
        Apply(true);
    }

    private void OnExpeditionReturned(ExpeditionReturn result)
    {
        var world = World;
        if (!ready || world == null) return;
        world.AddCounter(DescentsKey, 1);
        Apply(true);
    }

    private void OnOrderCompleted(ShopOrder order)
    {
        var world = World;
        if (!ready || world == null) return;
        world.AddCounter(OrdersKey, 1);
        Apply(true);
    }

    private void OnBreedingCompleted(CreatureDNA mother, CreatureDNA father, CreatureDNA child)
    {
        if (!ready) return;
        Apply(false);
    }

    private void OnShopZoneOpened(ShopUpgradeSO expansion, int level)
    {
        if (!ready) return;
        Apply(false);
    }

    public int Progress(GoalSO g)
    {
        var world = World;
        if (g == null || world == null) return 0;
        if (world.IsGoalDone(g.Id)) return g.Target;

        int value;
        switch (g.Kind)
        {
            case GoalKind.CreaturesSold:   value = world.Counter(SoldKey); break;
            case GoalKind.CreaturesBred:   value = world.BredTotal; break;
            case GoalKind.Descents:        value = world.Counter(DescentsKey); break;
            case GoalKind.OrdersCompleted: value = world.Counter(OrdersKey); break;
            case GoalKind.DabloonsEarned:  value = world.Counter(EarnedKey); break;
            case GoalKind.ExpansionOpened: value = world.UpgradeLevel(g.ExpansionId); break;
            default:                       value = 0; break;
        }
        return Mathf.Clamp(value, 0, g.Target);
    }

    public bool IsDone(GoalSO g)
    {
        var world = World;
        return g != null && world != null && world.IsGoalDone(g.Id);
    }

    public GoalSO LockingGoal(ShopUpgradeSO u)
    {
        if (u == null) return null;
        foreach (var g in goals)
        {
            if (g == null || IsDone(g) || g.UnlocksExpansions == null) continue;
            if (g.UnlocksExpansions.Contains(u)) return g;
        }
        return null;
    }

    public GoalSO LockingGoal(ItemDefinitionSO item)
    {
        if (item == null) return null;
        foreach (var g in goals)
        {
            if (g == null || IsDone(g) || g.UnlocksItems == null) continue;
            if (g.UnlocksItems.Contains(item)) return g;
        }
        return null;
    }

    private void Apply(bool countersChanged)
    {
        var world = World;
        if (world == null) return;

        bool changed = countersChanged;
        foreach (var g in goals)
        {
            if (g == null || string.IsNullOrEmpty(g.Id) || world.IsGoalDone(g.Id)) continue;
            if (Progress(g) < g.Target) continue;

            world.MarkGoalDone(g.Id);
            if (g.RewardDabloons > 0) Wallet.Add(Currency.Dabloons, g.RewardDabloons, "goal");
            GameEvents.GoalCompleted(g);
            changed = true;
        }

        if (changed) GameEvents.WorldStateChanged(world);
    }
}
}
