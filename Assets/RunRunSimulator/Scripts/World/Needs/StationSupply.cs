using System.Collections.Generic;
using MoreMountains.Feedbacks;
using TMPro;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class StationSupply : MonoBehaviour, IInteractable
{
    private static readonly List<StationSupply> all = new List<StationSupply>();
    public static IReadOnlyList<StationSupply> All => all;

    [SerializeField] private SupplyKind kind;
    [SerializeField, Min(1f)] private float max = 100f;
    [SerializeField, Min(0f)] private float usePerPoint = 0.25f;
    [SerializeField, Range(0f, 1f)] private float dirtyThreshold = 0.3f;
    [SerializeField] private TextMeshPro label;
    [SerializeField] private MMF_Player onRefill;
    [SerializeField] private MMF_Player onEmpty;

    private float level;
    private int lastBucket;
    private int lastPercent = -1;

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
        UnityEngine.Localization.Settings.LocalizationSettings.SelectedLocaleChanged += OnLocaleChanged;
    }

    private void OnDisable()
    {
        all.Remove(this);
        GameEvents.OnWorldStateReloaded -= OnWorldStateReloaded;
        UnityEngine.Localization.Settings.LocalizationSettings.SelectedLocaleChanged -= OnLocaleChanged;
    }

    private void Start() => ReadFrom(GameManager.Instance != null ? GameManager.Instance.WorldState : null);

    private void OnWorldStateReloaded(WorldStateSO world) => ReadFrom(world);

    private void ReadFrom(WorldStateSO world)
    {
        level = world != null && world.TryGetStationLevel(gameObject.name, out var saved)
            ? Mathf.Clamp(saved, 0f, max)
            : max;
        lastBucket = Bucket();
        UpdateLabel();
    }

    public void Interact()
    {
        Refill(max);
        Persist();
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
        UpdateLabel();

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

    private void OnLocaleChanged(UnityEngine.Localization.Locale locale)
    {
        lastPercent = -1;
        UpdateLabel();
    }

    private void UpdateLabel()
    {
        if (label == null) return;

        int percent = Mathf.RoundToInt(Level01 * 100f);
        if (percent == lastPercent) return;
        lastPercent = percent;

        string key = kind switch
        {
            SupplyKind.Food  => "ui.station.food",
            SupplyKind.Water => "ui.station.water",
            _                => "ui.station.clean",
        };
        label.text = Loc.Tr(key, percent);

        float t = Level01;
        label.color = t < 0.5f
            ? Color.Lerp(Color.red, Color.yellow, t * 2f)
            : Color.Lerp(Color.yellow, Color.green, (t - 0.5f) * 2f);
    }
}
}
