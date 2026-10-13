using System;
using UnityEngine;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class PlayerToyTug : MonoBehaviour
{
    public enum TugState { Idle, Pulling, PlayerWon, CreatureWon }

    public static PlayerToyTug Instance { get; private set; }

    public static event Action TugStarted;
    public static event Action<float> TugChanged;
    public static event Action<bool> TugEnded;

    [SerializeField] private ToyTuningSO tuning;

    private float pullPerSecond;
    private float elapsed;

    public TugState State { get; private set; } = TugState.Idle;
    public MoriMochiAgent Puller { get; private set; }
    public float Progress { get; private set; }
    public bool IsActive => State == TugState.Pulling;

    private void Awake() => Instance = this;
    private void OnDestroy() { if (Instance == this) Instance = null; }

    private void OnEnable() => PlayerInputs.InteractPressed += OnInteractPressed;

    private void OnDisable()
    {
        PlayerInputs.InteractPressed -= OnInteractPressed;
        ResetState();
    }

    public bool TryBegin(MoriMochiAgent puller, float pullPerSecond)
    {
        if (State != TugState.Idle || puller == null || tuning == null) return false;
        if (HeldCarriableToy() == null) return false;

        Puller = puller;
        this.pullPerSecond = pullPerSecond;
        Progress = 0f;
        elapsed = 0f;
        State = TugState.Pulling;
        TugStarted?.Invoke();
        TugChanged?.Invoke(Progress);
        return true;
    }

    public void Release(MoriMochiAgent puller)
    {
        if (State == TugState.Idle || puller != Puller) return;
        ResetState();
    }

    private void ResetState()
    {
        State = TugState.Idle;
        Puller = null;
        Progress = 0f;
        elapsed = 0f;
    }

    private static Toy HeldCarriableToy()
    {
        var hotbar = HotbarController.Instance;
        if (hotbar == null) return null;
        var held = hotbar.ActiveHeldObject;
        if (held == null) return null;
        var toy = held.GetComponentInChildren<Toy>();
        return toy != null && toy.IsCarriable ? toy : null;
    }

    private void OnInteractPressed()
    {
        if (State != TugState.Pulling) return;
        Progress = Mathf.Min(1f, Progress + tuning.TugPressPower);
        TugChanged?.Invoke(Progress);
        if (Progress >= 1f) Resolve(true);
    }

    private void Update()
    {
        if (State != TugState.Pulling) return;

        if (Puller == null || !Puller.gameObject.activeInHierarchy)
        {
            Resolve(true);
            return;
        }

        float dt = Time.deltaTime;
        elapsed += dt;
        Progress = Mathf.Max(-1f, Progress - pullPerSecond * dt);
        TugChanged?.Invoke(Progress);

        if (Progress <= -1f) { Resolve(false); return; }
        if (elapsed >= tuning.TugMaxSeconds) { Resolve(true); return; }

        Vector3 offset = Puller.transform.position - transform.position;
        offset.y = 0f;
        float maxDistance = tuning.TugRange * 2f;
        if (offset.sqrMagnitude > maxDistance * maxDistance) Resolve(true);
    }

    private void Resolve(bool playerWon)
    {
        State = playerWon ? TugState.PlayerWon : TugState.CreatureWon;
        TugEnded?.Invoke(playerWon);
    }
}
}
