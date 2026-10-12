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
    [SerializeField] private float hitSpeedThreshold = 2.5f;

    private Rigidbody rb;
    private WorldPropInstance prop;

    public ToyKind Kind => kind;
    public bool IsCarriable => Kind != ToyKind.Ball;
    public MoriMochiAgent Holder { get; private set; }
    public MoriMochiAgent LastKicker { get; private set; }
    public bool IsHeldByPlayer => prop != null && prop.IsHeld;
    public bool IsFree => Holder == null && !IsHeldByPlayer;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        prop = GetComponent<WorldPropInstance>();
    }

    private void OnEnable() => all.Add(this);

    private void OnDisable()
    {
        all.Remove(this);
        Holder = null;
    }

    public bool TryAttach(MoriMochiAgent holder, Transform mouth)
    {
        if (!IsCarriable || IsHeldByPlayer || holder == null || mouth == null) return false;

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

        transform.SetParent(null, true);
        SetTrigger(false);
        rb.isKinematic = false;
        rb.linearVelocity = velocity;
        Holder = null;
        onCarryEnd?.PlayFeedbacks();
    }

    public void Kick(MoriMochiAgent kicker, Vector3 impulse)
    {
        if (Holder != null || IsHeldByPlayer) return;

        rb.AddForce(impulse, ForceMode.Impulse);
        LastKicker = kicker;
        onKick?.PlayFeedbacks();
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.relativeVelocity.magnitude < hitSpeedThreshold) return;

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
