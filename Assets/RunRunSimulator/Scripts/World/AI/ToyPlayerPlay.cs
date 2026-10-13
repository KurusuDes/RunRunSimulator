using UnityEngine;
namespace MoriMonchiSimulator
{

internal class ToyPlayerPlay : IToyBehavior
{
    private enum PlayMode { None, FetchGo, FetchReturn, TugApproach, Tugging, Tease }

    private const float FaceTurnSpeed       = 360f;
    private const float EmoteInterval       = 1.5f;
    private const float DropToPlayerSpeed   = 1.5f;
    private const float TeaseJitterDegrees  = 50f;
    private const int   TeaseCandidates     = 4;

    private readonly MoriMochiAgent owner;
    private readonly AgentContext   ctx;
    private readonly AgentToyMotor  motor;

    private PlayMode  mode;
    private Toy       toy;
    private Transform mouth;
    private float     timer;
    private float     emoteTimer;
    private bool      tugHeld;

    internal ToyPlayerPlay(MoriMochiAgent owner, AgentContext ctx, AgentToyMotor motor)
    {
        this.owner = owner;
        this.ctx   = ctx;
        this.motor = motor;
    }

    public bool IsActive => mode != PlayMode.None;

    public CreatureIntent Intent => mode switch
    {
        PlayMode.None        => CreatureIntent.Wandering,
        PlayMode.FetchGo     => CreatureIntent.Approaching,
        PlayMode.TugApproach => CreatureIntent.Approaching,
        _                    => CreatureIntent.Playing,
    };

    public bool TryEngage(ToyTuningSO t)
    {
        var thrown = FindThrown(t);
        if (thrown != null)
        {
            owner.RequestReleaseStation();
            toy = thrown;
            Begin(PlayMode.FetchGo);
            motor.SetBoost(t.CarrySpeedMultiplier);
            owner.EmitEmote(EmoteKind.Jugando);
            return true;
        }

        var held = AgentToyMotor.HeldToyOfPlayer();
        if (held != null && held.IsCarriable && ctx.PlanarDistanceToPlayer() <= t.NoticeRadius)
        {
            owner.RequestReleaseStation();
            toy = held;
            Begin(PlayMode.TugApproach);
            return true;
        }

        return false;
    }

    public void Tick(ToyTuningSO t, float dt)
    {
        timer += dt;

        switch (mode)
        {
            case PlayMode.FetchGo:     TickFetchGo(t, dt);     break;
            case PlayMode.FetchReturn: TickFetchReturn(t, dt); break;
            case PlayMode.TugApproach: TickTugApproach(t, dt); break;
            case PlayMode.Tugging:     TickTugging(t, dt);     break;
            case PlayMode.Tease:       TickTease(t, dt);       break;
        }
    }

    public bool ReactToHit(Toy hitToy, MoriMochiAgent kicker) => false;

    public void Clear()
    {
        ReleaseTug();
        if (toy != null) motor.Drop(toy, owner.Velocity);
        toy  = null;
        mode = PlayMode.None;
    }

    private void End(bool completed)
    {
        Clear();
        motor.Finish(completed);
    }

    private void Begin(PlayMode newMode)
    {
        mode       = newMode;
        timer      = 0f;
        emoteTimer = 0f;
        motor.Enter();
    }

    private Toy FindThrown(ToyTuningSO t)
    {
        Toy best = null;
        float bestDist = t.NoticeRadius;
        var all = Toy.All;
        for (int i = 0; i < all.Count; i++)
        {
            var candidate = all[i];
            if (candidate == null || !candidate.ThrownByPlayer || !candidate.IsFree || candidate.Kind == ToyKind.Bubbles) continue;
            float d = motor.Planar(candidate.transform.position);
            if (d > bestDist) continue;
            bestDist = d;
            best     = candidate;
        }
        return best;
    }

    private Transform EnsureMouth(ToyTuningSO t)
    {
        if (mouth == null)
        {
            mouth = new GameObject("ToyFetchMouth").transform;
            mouth.SetParent(ctx.Body, false);
        }
        mouth.localPosition = t.MouthOffset;
        mouth.localRotation = Quaternion.identity;
        return mouth;
    }

    private void ReleaseTug()
    {
        if (!tugHeld) return;
        tugHeld = false;
        var tug = PlayerToyTug.Instance;
        if (tug != null) tug.Release(owner);
        ctx.SetStopped(false);
    }

    private void FacePlayer(float dt)
    {
        if (ctx.Player == null) return;
        Vector3 d = ctx.Player.position - ctx.Body.position; d.y = 0f;
        if (d.sqrMagnitude < 0.0001f) return;
        ctx.Body.rotation = Quaternion.RotateTowards(ctx.Body.rotation, Quaternion.LookRotation(d), FaceTurnSpeed * dt);
    }

    private void TickFetchGo(ToyTuningSO t, float dt)
    {
        if (toy == null || !toy.IsFree || ctx.Player == null || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (motor.Planar(toy.transform.position) <= t.KickRange)
        {
            if (!toy.TryAttach(owner, EnsureMouth(t), true)) { End(false); return; }
            mode  = PlayMode.FetchReturn;
            timer = 0f;
            owner.EmitEmote(EmoteKind.Feliz);
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(toy.transform.position);
    }

    private void TickFetchReturn(ToyTuningSO t, float dt)
    {
        if (toy == null || toy.Holder != owner)
        {
            toy = null;
            owner.EmitEmote(EmoteKind.Molesto);
            End(false);
            return;
        }

        if (ctx.Player == null || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (ctx.PlanarDistanceToPlayer() <= t.FetchDropRange)
        {
            Vector3 toPlayer = ctx.Player.position - ctx.Body.position; toPlayer.y = 0f;
            Vector3 dir = toPlayer.sqrMagnitude > 0.0001f ? toPlayer.normalized : ctx.Body.forward;
            motor.Drop(toy, dir * DropToPlayerSpeed);
            toy = null;
            owner.EmitEmote(EmoteKind.Corazon);
            ctx.Dna.Needs.AddAffect(t.FetchAffect);
            End(true);
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(ctx.Player.position);
    }

    private void TickTugApproach(ToyTuningSO t, float dt)
    {
        var held = AgentToyMotor.HeldToyOfPlayer();
        if (ctx.Player == null || held == null || !held.IsCarriable || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (ctx.PlanarDistanceToPlayer() <= t.TugRange)
        {
            var tug = PlayerToyTug.Instance;
            if (tug != null)
            {
                float boldness = Mathf.Clamp01(ctx.Dna.Boldness);
                if (tug.TryBegin(owner, t.TugPullPerSecond + t.TugBoldnessPull * boldness))
                {
                    tugHeld    = true;
                    mode       = PlayMode.Tugging;
                    timer      = 0f;
                    emoteTimer = 0f;
                    ctx.SetStopped(true);
                }
                return;
            }

            if (Random.value < t.SnatchChancePerSecond * dt) Snatch(t);
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(ctx.Player.position);
    }

    private void Snatch(ToyTuningSO t)
    {
        var hotbar = HotbarController.Instance;
        if (hotbar != null) hotbar.DropActive();
        StartTease(AgentToyMotor.NearestFreeCarriable(ctx.Player.position, t.SnatchRange * 2f), t);
    }

    private void StartTease(Toy stolen, ToyTuningSO t)
    {
        if (!motor.TryCarry(stolen, EmoteKind.Feliz, t)) { End(false); return; }

        toy   = stolen;
        mode  = PlayMode.Tease;
        timer = 0f;
        motor.SetBoost(t.TeaseSpeedMultiplier);
        PickAwayPoint(t);
    }

    private void TickTugging(ToyTuningSO t, float dt)
    {
        var tug = PlayerToyTug.Instance;
        if (tug == null || tug.Puller != owner) { End(false); return; }

        switch (tug.State)
        {
            case PlayerToyTug.TugState.Pulling:
                FacePlayer(dt);
                emoteTimer -= dt;
                if (emoteTimer <= 0f)
                {
                    emoteTimer = EmoteInterval;
                    owner.EmitEmote(EmoteKind.Jugando);
                }
                break;

            case PlayerToyTug.TugState.PlayerWon:
                owner.EmitEmote(EmoteKind.Feliz);
                ctx.Dna.Needs.AddAffect(t.TugWinAffect);
                End(true);
                break;

            case PlayerToyTug.TugState.CreatureWon:
                var hotbar = HotbarController.Instance;
                if (hotbar != null) hotbar.DropActive();
                var dropped = AgentToyMotor.NearestFreeCarriable(ctx.Player.position, t.TugRange * 2f);
                ReleaseTug();
                StartTease(dropped, t);
                break;

            default:
                End(false);
                break;
        }
    }

    private void TickTease(ToyTuningSO t, float dt)
    {
        if (toy == null) { End(false); return; }

        if (toy.Holder != owner || toy.IsHeldByPlayer)
        {
            var taker = toy.Holder;
            toy = null;
            if (taker != null && taker != owner)
            {
                owner.EmitEmote(EmoteKind.Molesto);
                End(false);
                return;
            }

            owner.EmitEmote(EmoteKind.Feliz);
            ctx.Dna.Needs.AddAffect(t.CaughtAffect);
            End(true);
            return;
        }

        if (timer >= t.TeaseDuration)
        {
            motor.Drop(toy, ctx.Body.forward * DropToPlayerSpeed);
            toy = null;
            End(true);
            return;
        }

        emoteTimer -= dt;
        if (emoteTimer <= 0f)
        {
            emoteTimer = EmoteInterval;
            owner.EmitEmote(EmoteKind.Jugando);
        }

        if (!motor.Repath(dt)) return;

        bool playerClose = ctx.PlanarDistanceToPlayer() < t.TeaseKeepAway;
        bool arrived = ctx.Agent.enabled && ctx.Agent.isOnNavMesh && !ctx.Agent.pathPending &&
                       ctx.Agent.remainingDistance <= ctx.Agent.stoppingDistance + 0.3f;
        if (playerClose || arrived) PickAwayPoint(t);
    }

    private void PickAwayPoint(ToyTuningSO t)
    {
        Vector3 from = ctx.Player != null ? ctx.Player.position : ctx.Body.position - ctx.Body.forward;
        Vector3 away = ctx.Body.position - from; away.y = 0f;
        away = away.sqrMagnitude > 0.0001f ? away.normalized : ctx.Body.forward;

        var area = toy != null ? toy.HomeArea : null;
        Vector3 best = ctx.Body.position;
        float bestSqr = -1f;

        for (int i = 0; i < TeaseCandidates; i++)
        {
            Vector3 p = area != null
                ? area.RandomPoint(1f)
                : ctx.Body.position + Quaternion.AngleAxis(Random.Range(-TeaseJitterDegrees, TeaseJitterDegrees), Vector3.up) * away * t.WanderRadius;

            Vector3 d = p - from; d.y = 0f;
            if (d.sqrMagnitude <= bestSqr) continue;
            bestSqr = d.sqrMagnitude;
            best    = p;
        }

        ctx.SetDestinationSafe(best);
    }
}
}
