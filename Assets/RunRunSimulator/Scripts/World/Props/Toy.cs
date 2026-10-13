using System.Collections.Generic;
using MoreMountains.Feedbacks;
using UnityEngine;
namespace MoriMonchiSimulator
{

[RequireComponent(typeof(Rigidbody))]
public class Toy : MonoBehaviour
{
    private static readonly List<Toy> all = new List<Toy>();
    public static IReadOnlyList<Toy> All => all;

    [SerializeField] private ToyKind kind;
    [SerializeField] private MMF_Player onCarryStart;
    [SerializeField] private MMF_Player onCarryEnd;
    [SerializeField] private MMF_Player onKick;
    [SerializeField] private MMF_Player onHitCreature;
    [SerializeField] private MMF_Player onReturnHome;
    [SerializeField] private MMF_Player onTug;
    [SerializeField] private float hitSpeedThreshold = 2.5f;
    [SerializeField, Min(1f)] private float returnHomeAfterSeconds = 25f;
    [SerializeField, Min(0f)] private float thrownMemorySeconds = 20f;

    private Rigidbody rb;
    private WorldPropInstance prop;
    private float outsideTimer;
    private bool wasHeldByPlayer;
    private bool thrownByPlayer;
    private float thrownTimer;

    public ToyKind Kind => kind;
    public bool IsKickable => Kind == ToyKind.Ball;
    public bool IsCarriable => Kind == ToyKind.Chew || Kind == ToyKind.Hose || Kind == ToyKind.Mop
        || Kind == ToyKind.Rope || Kind == ToyKind.Plush;
    public bool ThrownByPlayer => thrownByPlayer;
    public MoriMochiAgent TuggedBy { get; private set; }
    public MoriMochiAgent Holder { get; private set; }
    public MoriMochiAgent LastKicker { get; private set; }
    public bool IsHeldByPlayer => prop != null && prop.IsHeld;
    public bool IsFree => Holder == null && !IsHeldByPlayer;
    public ToyPlayArea HomeArea => ToyPlayArea.Nearest(transform.position);

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        prop = GetComponent<WorldPropInstance>();
    }

    private void Update()
    {
        TrackThrown();

        if (!IsFree || rb.isKinematic) { outsideTimer = 0f; return; }

        var area = HomeArea;
        if (area == null || area.Contains(transform.position) || rb.linearVelocity.sqrMagnitude >= 0.04f)
        {
            outsideTimer = 0f;
            return;
        }

        outsideTimer += Time.deltaTime;
        if (outsideTimer < returnHomeAfterSeconds) return;

        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
        rb.position = area.RandomPoint(1f) + Vector3.up * 0.5f;
        LastKicker = null;
        onReturnHome?.PlayFeedbacks();
        outsideTimer = 0f;
    }

    private void TrackThrown()
    {
        bool held = IsHeldByPlayer;

        if (held)
        {
            thrownByPlayer = false;
        }
        else if (wasHeldByPlayer)
        {
            thrownByPlayer = true;
            thrownTimer = 0f;
        }
        else if (thrownByPlayer)
        {
            thrownTimer += Time.deltaTime;
            if (thrownTimer >= thrownMemorySeconds) thrownByPlayer = false;
        }

        wasHeldByPlayer = held;
    }

    private void OnEnable() => all.Add(this);

    private void OnDisable()
    {
        all.Remove(this);
        Holder = null;
        TuggedBy = null;
        thrownByPlayer = false;
        wasHeldByPlayer = false;
    }

    public void SetTugger(MoriMochiAgent a)
    {
        if (a == null) return;

        TuggedBy = a;
        onTug?.PlayFeedbacks();
    }

    public void ClearTugger(MoriMochiAgent a)
    {
        if (TuggedBy == a) TuggedBy = null;
    }

    public bool TryAttach(MoriMochiAgent holder, Transform mouth, bool allowAnyKind = false)
    {
        bool allowed = IsCarriable || (allowAnyKind && Kind == ToyKind.Ball);
        if (!allowed || IsHeldByPlayer || holder == null || mouth == null) return false;

        thrownByPlayer = false;
        rb.isKinematic = true;
        transform.SetParent(mouth, false);
        transform.localPosition = Vector3.zero;
        transform.localRotation = Quaternion.identity;
        SetTrigger(true);
        Holder = holder;
        onCarryStart?.PlayFeedbacks();
        return true;
    }

    public void Detach(Vector3 velocity)
    {
        if (Holder == null) return;

        TuggedBy = null;
        transform.SetParent(null, true);
        SetTrigger(false);
        rb.isKinematic = false;
        rb.linearVelocity = velocity;
        Holder = null;
        onCarryEnd?.PlayFeedbacks();
    }

    public void Kick(MoriMochiAgent kicker, Vector3 impulse)
    {
        if (!IsKickable || Holder != null || IsHeldByPlayer) return;

        rb.AddForce(impulse, ForceMode.Impulse);
        LastKicker = kicker;
        onKick?.PlayFeedbacks();
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (!IsKickable || collision.relativeVelocity.magnitude < hitSpeedThreshold) return;

        var agent = collision.collider.GetComponentInParent<MoriMochiAgent>();
        if (agent == null || agent == LastKicker) return;

        agent.ReactToToyHit(this, LastKicker);
        onHitCreature?.PlayFeedbacks();
    }

    private void SetTrigger(bool value)
    {
        foreach (var col in GetComponentsInChildren<Collider>()) col.isTrigger = value;
    }
}
}
