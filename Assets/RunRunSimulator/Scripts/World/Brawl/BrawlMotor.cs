using System;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.AI;
namespace MoriMonchiSimulator
{

[RequireComponent(typeof(NavMeshAgent))]
public class BrawlMotor : MonoBehaviour
{
    private const float VelocitySmoothing = 25f;
    private const float LookAtMinDistance = 0.1f;
    private const float FaceMinSpeed = 0.2f;
    private const float RepathMoveDistance = 1f;
    private const float LeapSampleRadius = 2f;
    private const float KnockStopSpeed = 0.05f;
    private const float MinForcedSeconds = 0.05f;

    [Required, SerializeField] private NavMeshAgent agent;
    [SerializeField, Min(0f)] private float repathInterval = 0.15f;
    [SerializeField, Min(0f)] private float turnSpeed = 720f;
    [SerializeField, Min(0f)] private float knockDecay = 6f;
    [SerializeField, Min(0f)] private float knockSpeedPerUnit = 1f;

    private BrawlFighter owner;
    private Vector3 velocity;
    private Vector3 lastPosition;
    private Vector3 knockVelocity;
    private bool dashing;
    private Vector3 dashDirection;
    private float dashSpeed;
    private float dashSeconds;
    private float dashElapsed;
    private Action<Vector3> dashStep;
    private Action dashEnd;
    private bool leaping;
    private Vector3 leapStart;
    private Vector3 leapTarget;
    private float leapSeconds;
    private float leapHeight;
    private float leapElapsed;
    private Action leapLand;
    private bool hasDestination;
    private Vector3 lastDestination;
    private float lastRepathAt;

    public Vector3 Velocity => velocity;
    public bool IsDashing => dashing;
    public bool IsLeaping => leaping;
    public bool IsForced => dashing || leaping;
    public bool Rooted { get; set; }
    public Vector3? LookAt { get; set; }

    private void Awake()
    {
        if (agent == null) agent = GetComponent<NavMeshAgent>();
        lastPosition = transform.position;
    }

    public void Init(BrawlFighter owner)
    {
        this.owner = owner;
        agent.updateRotation = false;
        agent.autoBraking = true;
        agent.acceleration = 40f;
        agent.angularSpeed = 0f;
        agent.stoppingDistance = 0.2f;
        dashing = false;
        dashStep = null;
        dashEnd = null;
        leaping = false;
        leapLand = null;
        knockVelocity = Vector3.zero;
        velocity = Vector3.zero;
        lastPosition = transform.position;
        hasDestination = false;
        Rooted = false;
        LookAt = null;
        if (agent.isOnNavMesh) agent.isStopped = false;
    }

    public void Warp(Vector3 position)
    {
        agent.Warp(position);
        lastPosition = transform.position;
        velocity = Vector3.zero;
        hasDestination = false;
    }

    public void MoveTo(Vector3 point)
    {
        if (owner == null || !owner.IsAlive || IsForced || owner.IsStunned || Rooted || !agent.isOnNavMesh) return;

        bool moved = !hasDestination || (point - lastDestination).sqrMagnitude > RepathMoveDistance * RepathMoveDistance;
        if (!moved && Time.time - lastRepathAt < repathInterval) return;

        agent.SetDestination(point);
        lastDestination = point;
        lastRepathAt = Time.time;
        hasDestination = true;
    }

    public void Stop()
    {
        hasDestination = false;
        if (agent.isOnNavMesh) agent.ResetPath();
    }

    public void Dash(Vector3 direction, float distance, float seconds, Action<Vector3> onStep, Action onEnd)
    {
        if (owner == null || !owner.IsAlive || !agent.isOnNavMesh) return;

        direction.y = 0f;
        if (direction.sqrMagnitude < 0.0001f)
        {
            direction = transform.forward;
            direction.y = 0f;
        }

        if (leaping)
        {
            leaping = false;
            leapLand = null;
            owner.Lift = 0f;
        }

        dashDirection = direction.normalized;
        dashSeconds = Mathf.Max(seconds, MinForcedSeconds);
        dashSpeed = distance / dashSeconds;
        dashElapsed = 0f;
        dashStep = onStep;
        dashEnd = onEnd;
        dashing = true;
    }

    public void Leap(Vector3 target, float seconds, float height, Action onLand)
    {
        if (owner == null || !owner.IsAlive || !agent.isOnNavMesh) return;

        dashing = false;
        dashStep = null;
        dashEnd = null;

        leapStart = transform.position;
        leapTarget = ClampToNavMesh(leapStart, target);
        leapSeconds = Mathf.Max(seconds, MinForcedSeconds);
        leapHeight = height;
        leapElapsed = 0f;
        leapLand = onLand;
        leaping = true;
    }

    public void Knock(Vector3 direction, float strength)
    {
        direction.y = 0f;
        if (direction.sqrMagnitude < 0.0001f) return;
        knockVelocity += direction.normalized * (strength * knockSpeedPerUnit);
    }

    public void Halt()
    {
        dashing = false;
        dashStep = null;
        dashEnd = null;
        leaping = false;
        leapLand = null;
        knockVelocity = Vector3.zero;
        velocity = Vector3.zero;
        hasDestination = false;
        LookAt = null;
        if (owner != null) owner.Lift = 0f;
        if (agent.isOnNavMesh)
        {
            agent.ResetPath();
            agent.isStopped = true;
        }
    }

    private void Update()
    {
        if (owner == null || !owner.IsAlive || !agent.isOnNavMesh) return;

        float dt = Time.deltaTime;
        bool wasForced = IsForced;
        agent.speed = owner.BaseSpeed * owner.SpeedMultiplier;
        agent.isStopped = owner.IsStunned || owner.Frozen || Rooted || wasForced;

        if (leaping) StepLeap(dt);
        else if (dashing) StepDash(dt);

        DecayKnock(dt, !wasForced);
    }

    private void LateUpdate()
    {
        float dt = Time.deltaTime;
        if (dt <= 0f) return;

        Vector3 position = transform.position;
        Vector3 raw = position - lastPosition;
        raw.y = 0f;
        raw /= dt;
        velocity = Vector3.Lerp(velocity, raw, 1f - Mathf.Exp(-VelocitySmoothing * dt));
        lastPosition = position;

        if (owner == null || !owner.IsAlive) return;

        Vector3 desired = Vector3.zero;
        if (dashing)
        {
            desired = dashDirection;
        }
        else if (LookAt.HasValue)
        {
            Vector3 toLook = LookAt.Value - position;
            toLook.y = 0f;
            if (toLook.sqrMagnitude > LookAtMinDistance * LookAtMinDistance) desired = toLook;
        }

        if (desired.sqrMagnitude < 0.0001f && velocity.sqrMagnitude > FaceMinSpeed * FaceMinSpeed) desired = velocity;
        if (desired.sqrMagnitude < 0.0001f) return;

        Quaternion target = Quaternion.LookRotation(desired.normalized, Vector3.up);
        transform.rotation = Quaternion.RotateTowards(transform.rotation, target, turnSpeed * dt);
    }

    private void StepDash(float dt)
    {
        float step = Mathf.Min(dt, dashSeconds - dashElapsed);
        agent.Move(dashDirection * (dashSpeed * step));
        dashElapsed += step;
        dashStep?.Invoke(transform.position);

        if (!dashing || dashElapsed < dashSeconds - 0.0001f) return;

        dashing = false;
        var end = dashEnd;
        dashStep = null;
        dashEnd = null;
        end?.Invoke();
    }

    private void StepLeap(float dt)
    {
        leapElapsed += dt;
        float t = Mathf.Clamp01(leapElapsed / leapSeconds);
        Vector3 desired = Vector3.Lerp(leapStart, leapTarget, Mathf.SmoothStep(0f, 1f, t));
        Vector3 delta = desired - transform.position;
        delta.y = 0f;
        agent.Move(delta);
        owner.Lift = 4f * leapHeight * t * (1f - t);

        if (t < 1f) return;

        leaping = false;
        owner.Lift = 0f;
        var land = leapLand;
        leapLand = null;
        BrawlFx.Emit(new BrawlFxEvent
        {
            Kind = BrawlFxKind.Land,
            To = transform.position,
            Source = owner,
            Theme = owner.WingTheme,
            Team = owner.Team
        });
        land?.Invoke();
    }

    private void DecayKnock(float dt, bool apply)
    {
        if (knockVelocity.sqrMagnitude < KnockStopSpeed * KnockStopSpeed)
        {
            knockVelocity = Vector3.zero;
            return;
        }

        if (apply) agent.Move(knockVelocity * dt);
        knockVelocity *= Mathf.Exp(-knockDecay * dt);
    }

    private Vector3 ClampToNavMesh(Vector3 start, Vector3 target)
    {
        if (NavMesh.SamplePosition(target, out var sample, LeapSampleRadius, agent.areaMask)) target = sample.position;
        if (NavMesh.Raycast(start, target, out var edge, agent.areaMask)) target = edge.position;
        return target;
    }
}
}
