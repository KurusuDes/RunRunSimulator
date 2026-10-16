using System.Collections.Generic;
using MoreMountains.Feedbacks;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class StationSupply : MonoBehaviour, IInteractable, IFocusLabel
{
    private static readonly List<StationSupply> all = new List<StationSupply>();
    public static IReadOnlyList<StationSupply> All => all;

    [SerializeField] private SupplyKind kind;
    [SerializeField, Min(1f)] private float max = 100f;
    [SerializeField, Min(0f)] private float usePerPoint = 0.25f;
    [SerializeField, Range(0f, 1f)] private float dirtyThreshold = 0.3f;
    [SerializeField] private MMF_Player onRefill;
    [SerializeField] private MMF_Player onEmpty;

    private float level;
    private int lastBucket;

    public SupplyKind Kind => kind;
    public float Level01 => Mathf.Clamp01(level / max);
    public bool IsEmpty => kind != SupplyKind.Clean && level <= 0f;

    private void Awake()
    {
        level = max;
        lastBucket = Bucket();
    }

    private void OnEnable()
    {
        all.Add(this);
        GameEvents.OnWorldStateReloaded += OnWorldStateReloaded;
    }

    private void OnDisable()
    {
        all.Remove(this);
        GameEvents.OnWorldStateReloaded -= OnWorldStateReloaded;
    }

    private void Start() => ReadFrom(GameManager.Instance != null ? GameManager.Instance.WorldState : null);

    private void OnWorldStateReloaded(WorldStateSO world) => ReadFrom(world);

    private void ReadFrom(WorldStateSO world)
    {
        level = world != null && world.TryGetStationLevel(gameObject.name, out var saved)
            ? Mathf.Clamp(saved, 0f, max)
            : max;
        lastBucket = Bucket();
    }

    public void Interact()
    {
        Refill(max);
        Persist();
        GameEvents.StationRefilled(kind);
        onRefill?.PlayFeedbacks();
    }

    public void Refill(float amount)
    {
        if (amount <= 0f) return;
        SetLevel(level + amount);
    }

    public float Consume(float needPoints)
    {
        if (needPoints <= 0f) return IsEmpty ? 0f : 1f;

        float factor;
        if (kind == SupplyKind.Clean)
            factor = Level01 >= dirtyThreshold ? 1f : 0.5f;
        else
            factor = level > 0f ? 1f : 0f;

        if (factor <= 0f) return 0f;

        bool wasEmpty = IsEmpty;
        SetLevel(level - needPoints * usePerPoint);
        if (!wasEmpty && IsEmpty) onEmpty?.PlayFeedbacks();
        return factor;
    }

    private void SetLevel(float value)
    {
        level = Mathf.Clamp(value, 0f, max);

        int bucket = Bucket();
        if (bucket == lastBucket) return;
        lastBucket = bucket;
        Persist();
    }

    private int Bucket() => Mathf.FloorToInt(level / 10f);

    private void Persist()
    {
        var world = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
        if (world == null) return;
        world.SetStationLevel(gameObject.name, level);
        GameEvents.WorldStateChanged(world);
    }

    public string FocusTitle
    {
        get
        {
            string key = kind switch
            {
                SupplyKind.Food  => "ui.station.food",
                SupplyKind.Water => "ui.station.water",
                _                => "ui.station.clean",
            };
            return Loc.Tr(key, Mathf.RoundToInt(Level01 * 100f));
        }
    }

    public string FocusDetail => null;
}
}
