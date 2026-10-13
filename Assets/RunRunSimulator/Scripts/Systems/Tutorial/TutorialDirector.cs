using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class TutorialDirector : MonoBehaviour
{
    public static TutorialDirector Instance { get; private set; }

    public static event Action<int, int, string> StepChanged;
    public static event Action StepCompleted;
    public static event Action Finished;

    private const float CompleteDelaySeconds = 0.6f;

    [SerializeField] private List<TutorialStep> steps = new List<TutorialStep>();
    [SerializeField] private Transform player;
    [SerializeField] private CloudSyncService cloudSync;
    [SerializeField] private float syncTimeoutSeconds = 20f;
    [SerializeField] private float moveDistance = 3f;

    private int activeIndex = -1;
    private int lastSeen = -1;
    private bool ready;
    private bool completing;
    private bool oldSaveChecked;
    private Vector3 startPos;

    public bool Active => activeIndex >= 0;
    public int Index => activeIndex;
    public int Total => steps.Count;
    public TutorialStep Current => Active ? steps[activeIndex] : default;

    private void Awake() => Instance = this;

    private void OnDestroy()
    {
        if (Instance == this) Instance = null;
    }

    private void OnEnable()
    {
        GameEvents.OnWorldStateReloaded += OnWorldStateReloaded;
        GameEvents.OnWorldStateChanged += OnWorldStateChanged;
        GameEvents.OnCreatureBoxOrdered += OnBoxOrdered;
        GameEvents.OnStationRefilled += OnStationRefilled;
        GameEvents.OnRegistryChanged += OnRegistryChanged;
        GameEvents.OnExpeditionReturned += OnExpeditionReturned;
        UIManager.OnPanelVisibilityChanged += OnPanelVisibility;
    }

    private void OnDisable()
    {
        GameEvents.OnWorldStateReloaded -= OnWorldStateReloaded;
        GameEvents.OnWorldStateChanged -= OnWorldStateChanged;
        GameEvents.OnCreatureBoxOrdered -= OnBoxOrdered;
        GameEvents.OnStationRefilled -= OnStationRefilled;
        GameEvents.OnRegistryChanged -= OnRegistryChanged;
        GameEvents.OnExpeditionReturned -= OnExpeditionReturned;
        UIManager.OnPanelVisibilityChanged -= OnPanelVisibility;
    }

    private void Start() => StartCoroutine(BootRoutine());

    private IEnumerator BootRoutine()
    {
        float elapsed = 0f;
        while (cloudSync != null && !cloudSync.StartupSyncDone && elapsed < syncTimeoutSeconds)
        {
            elapsed += Time.unscaledDeltaTime;
            yield return null;
        }
        yield return null;
        ready = true;
        Evaluate();
    }

    private void Update()
    {
        if (!ready || !Active || completing || player == null) return;

        var step = steps[activeIndex];
        if (step.Signal == TutorialSignal.Moved)
        {
            if (FlatDistance(player.position, startPos) >= moveDistance) Complete(TutorialSignal.Moved);
        }
        else if (step.Signal == TutorialSignal.ReachTarget && step.Target != null)
        {
            if (FlatDistance(player.position, step.Target.position) < step.Radius) Complete(TutorialSignal.ReachTarget);
        }
    }

    public void Skip()
    {
        if (!ready || GameManager.Instance == null || GameManager.Instance.WorldState == null) return;
        SetValue(GameManager.Instance.WorldState, Total + 1);
    }

    private void OnWorldStateReloaded(WorldStateSO world)
    {
        if (ready) Evaluate();
    }

    private void OnWorldStateChanged(WorldStateSO world)
    {
        if (!ready || world == null || world.TutorialStep == lastSeen) return;
        Evaluate();
    }

    private void OnBoxOrdered(CreatureBoxSO box) => Complete(TutorialSignal.BoxOrdered);

    private void OnStationRefilled(SupplyKind kind)
    {
        if (kind == SupplyKind.Food) Complete(TutorialSignal.FoodRefilled);
    }

    private void OnRegistryChanged(CreatureRegistrySO registry)
    {
        if (HasLiving(registry)) Complete(TutorialSignal.CreatureArrived);
    }

    private void OnExpeditionReturned(ExpeditionReturn r) => Complete(TutorialSignal.ExpeditionReturned);

    private void OnPanelVisibility(UIPanelType panel, bool show)
    {
        if (show && panel == UIPanelType.Store) Complete(TutorialSignal.StorePanelOpened);
    }

    private void Evaluate()
    {
        var gm = GameManager.Instance;
        var world = gm != null ? gm.WorldState : null;
        if (world == null) return;

        int value = world.TutorialStep;
        lastSeen = value;

        if (value <= 0)
        {
            activeIndex = -1;
            return;
        }

        if (value > Total)
        {
            bool wasActive = Active;
            activeIndex = -1;
            if (wasActive) Finished?.Invoke();
            return;
        }

        if (value == 1 && !oldSaveChecked)
        {
            oldSaveChecked = true;
            var registry = gm.Registry;
            if (registry != null && (registry.Count > 0 || registry.Departed.Count > 0))
            {
                SetValue(world, Total + 1);
                return;
            }
        }

        int index = value - 1;
        if (index == activeIndex) return;
        Activate(index, world);
    }

    private void Activate(int index, WorldStateSO world)
    {
        var step = steps[index];
        if ((step.Signal == TutorialSignal.BoxOrdered || step.Signal == TutorialSignal.CreatureArrived)
            && HasLiving(GameManager.Instance.Registry))
        {
            SetValue(world, index + 2);
            return;
        }

        completing = false;
        activeIndex = index;
        startPos = player != null ? player.position : Vector3.zero;
        Debug.Log($"[Tutorial] paso {index + 1}/{Total}");
        StepChanged?.Invoke(index, Total, step.TextKey);
    }

    private void Complete(TutorialSignal signal)
    {
        if (!ready || !Active || completing || steps[activeIndex].Signal != signal) return;
        completing = true;
        StepCompleted?.Invoke();
        StartCoroutine(AdvanceRoutine(activeIndex));
    }

    private IEnumerator AdvanceRoutine(int index)
    {
        yield return new WaitForSecondsRealtime(CompleteDelaySeconds);
        if (activeIndex != index) yield break;
        completing = false;
        var world = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
        if (world != null) SetValue(world, index + 2);
    }

    private void SetValue(WorldStateSO world, int value)
    {
        world.TutorialStep = value;
        lastSeen = value;
        GameEvents.WorldStateChanged(world);
        Evaluate();
    }

    private static bool HasLiving(CreatureRegistrySO registry)
    {
        if (registry == null) return false;
        foreach (var dna in registry.GetAll().Values)
            if (dna != null && !dna.IsDead && !dna.IsSold) return true;
        return false;
    }

    private static float FlatDistance(Vector3 a, Vector3 b)
    {
        a.y = 0f;
        b.y = 0f;
        return Vector3.Distance(a, b);
    }
}
}
