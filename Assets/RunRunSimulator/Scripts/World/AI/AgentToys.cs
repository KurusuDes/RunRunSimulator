using UnityEngine;
namespace MoriMonchiSimulator
{

internal class AgentToys
{
    private enum ToyMode { None, GoToBall, Kicking, GoToCarry, Carrying, Chasing, Snatching }

    private const float KickNoiseDegrees = 25f;
    private const float BoostRefresh     = 0.25f;
    private const float DropForwardSpeed = 1.5f;

    private readonly MoriMochiAgent owner;
    private readonly AgentContext   ctx;

    private ToyMode        mode;
    private Toy            toy;
    private MoriMochiAgent target;
    private Transform      mouth;
    private float          timer;
    private float          duration;
    private float          repathTimer;
    private float          kickTimer;
    private float          cooldownUntil;
    private int            kicksLeft;
    private bool           boosting;

    internal AgentToys(MoriMochiAgent owner, AgentContext ctx)
    {
        this.owner = owner;
        this.ctx   = ctx;
    }

    private bool CanPlay()
    {
        if (ctx.Dna == null) return false;
        if (ctx.CurrentContainer != null) return false;
        if (ctx.IsBreeding) return false;
        if (ctx.Dna.Form == MonchiForm.Egg) return false;
        if (owner.Team != ExpeditionTeam.None) return false;
        return true;
    }

    private float Planar(Vector3 p)
    {
        Vector3 d = p - ctx.Body.position; d.y = 0f;
        return d.magnitude;
    }

    internal bool TryEngage()
    {
        var t = owner.toyTuning;
        if (t == null) return false;
        if (ctx.State != AgentState.Idle && ctx.State != AgentState.Roaming) return false;
        if (Time.time < cooldownUntil) return false;
        if (!CanPlay()) return false;
        if (ctx.Dna.Needs.Energy < t.MinEnergy) return false;
        if (Random.value >= t.EngageChancePerSecond * Time.deltaTime) return false;

        Toy stealable = null;
        Toy free      = null;
        float bestSteal = t.NoticeRadius;
        float bestFree  = t.NoticeRadius;

        var all = Toy.All;
        for (int i = 0; i < all.Count; i++)
        {
            var candidate = all[i];
            if (candidate == null) continue;

            float d = Planar(candidate.transform.position);
            if (d > t.NoticeRadius) continue;

            if (candidate.IsCarriable && candidate.Holder != null && candidate.Holder != owner)
            {
                if (d < bestSteal) { bestSteal = d; stealable = candidate; }
            }
            else if (candidate.IsFree && d < bestFree)
            {
                bestFree = d;
                free     = candidate;
            }
        }

        if (stealable != null)
        {
            owner.RequestReleaseStation();
            BeginChase(stealable.Holder, stealable, t);
            owner.EmitEmote(EmoteKind.Jugando);
            return true;
        }

        if (free != null)
        {
            owner.RequestReleaseStation();
            toy = free;
            Enter(free.Kind == ToyKind.Ball ? ToyMode.GoToBall : ToyMode.GoToCarry);
            return true;
        }

        if (HeldToyOfPlayer() != null && ctx.PlanarDistanceToPlayer() <= t.NoticeRadius)
        {
            owner.RequestReleaseStation();
            Enter(ToyMode.Snatching);
            return true;
        }

        return false;
    }

    private static Toy HeldToyOfPlayer()
    {
        var hotbar = HotbarController.Instance;
        if (hotbar == null) return null;
        var held = hotbar.ActiveHeldObject;
        return held != null ? held.GetComponentInChildren<Toy>() : null;
    }

    private void Enter(ToyMode newMode)
    {
        mode        = newMode;
        timer       = 0f;
        repathTimer = 0f;
        kickTimer   = 0f;

        ctx.State                = AgentState.Playing;
        ctx.SetStopped(false);
        ctx.Agent.updateRotation = true;
    }

    private void SetBoost(float multiplier)
    {
        boosting              = true;
        ctx.SpeedMultiplier   = multiplier;
        ctx.SpeedBoostUntil   = Time.time + BoostRefresh;
    }

    private void ClearBoost()
    {
        if (!boosting) return;
        boosting            = false;
        ctx.SpeedBoostUntil = 0f;
    }

    private void BeginChase(MoriMochiAgent who, Toy stealToy, ToyTuningSO t)
    {
        target   = who;
        toy      = stealToy;
        duration = t.ChaseDuration;
        Enter(ToyMode.Chasing);
        SetBoost(t.ChaseSpeedMultiplier);
    }

    private Transform EnsureMouth(ToyTuningSO t)
    {
        if (mouth == null)
        {
            mouth = new GameObject("ToyMouth").transform;
            mouth.SetParent(ctx.Body, false);
        }
        mouth.localPosition = t.MouthOffset;
        mouth.localRotation = Quaternion.identity;
        return mouth;
    }

    private bool BeginCarry(Toy carried, EmoteKind emote, ToyTuningSO t)
    {
        if (carried == null) return false;
        if (!carried.TryAttach(owner, EnsureMouth(t))) return false;

        toy      = carried;
        target   = null;
        duration = Random.Range(t.CarryDurationMin, t.CarryDurationMax);
        Enter(ToyMode.Carrying);
        SetBoost(t.CarrySpeedMultiplier);
        PickWanderPoint(t);
        owner.EmitEmote(emote);
        return true;
    }

    private void PickWanderPoint(ToyTuningSO t)
    {
        Vector2 r = Random.insideUnitCircle * t.WanderRadius;
        ctx.SetDestinationSafe(ctx.Body.position + new Vector3(r.x, 0f, r.y));
    }

    internal void TickPlaying()
    {
        var t = owner.toyTuning;
        if (t == null || ctx.Dna == null || mode == ToyMode.None) { End(false); return; }

        float dt = Time.deltaTime;
        timer += dt;
        ctx.Dna.Needs.AddAffect(t.AffectPerSecond * dt);
        if (boosting) ctx.SpeedBoostUntil = Time.time + BoostRefresh;

        switch (mode)
        {
            case ToyMode.GoToBall:  TickGoToBall(t);  break;
            case ToyMode.Kicking:   TickKicking(t, dt); break;
            case ToyMode.GoToCarry: TickGoToCarry(t); break;
            case ToyMode.Carrying:  TickCarrying(t, dt); break;
            case ToyMode.Chasing:   TickChasing(t, dt);  break;
            case ToyMode.Snatching: TickSnatching(t, dt); break;
        }
    }

    private bool Repath(float dt)
    {
        repathTimer -= dt;
        if (repathTimer > 0f) return false;
        repathTimer = owner.repathInterval;
        return true;
    }

    private void TickGoToBall(ToyTuningSO t)
    {
        if (toy == null || !toy.IsFree || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (Planar(toy.transform.position) <= t.KickRange)
        {
            kicksLeft = Random.Range(t.KicksMin, t.KicksMax + 1);
            mode      = ToyMode.Kicking;
            timer     = 0f;
            return;
        }

        if (Repath(Time.deltaTime)) ctx.SetDestinationSafe(toy.transform.position);
    }

    private void TickKicking(ToyTuningSO t, float dt)
    {
        if (toy == null || !toy.IsFree || kicksLeft <= 0 || timer >= t.CarryDurationMax * 2f)
        {
            End(kicksLeft <= 0);
            return;
        }

        kickTimer -= dt;
        Vector3 ballPos = toy.transform.position;

        if (kickTimer <= 0f && Planar(ballPos) <= t.KickRange)
        {
            Vector3 dir = ballPos - ctx.Body.position; dir.y = 0f;
            dir = dir.sqrMagnitude > 0.0001f ? dir.normalized : ctx.Body.forward;
            dir = Quaternion.AngleAxis(Random.Range(-KickNoiseDegrees, KickNoiseDegrees), Vector3.up) * dir;

            toy.Kick(owner, dir * t.KickForce + Vector3.up * t.KickUp);
            owner.EmitEmote(EmoteKind.Jugando);
            kicksLeft--;
            kickTimer = owner.repathInterval * 2f;
            return;
        }

        if (Repath(dt)) ctx.SetDestinationSafe(ballPos);
    }

    private void TickGoToCarry(ToyTuningSO t)
    {
        if (toy == null || !toy.IsFree || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (Planar(toy.transform.position) <= t.KickRange)
        {
            if (!BeginCarry(toy, EmoteKind.Jugando, t)) End(false);
            return;
        }

        if (Repath(Time.deltaTime)) ctx.SetDestinationSafe(toy.transform.position);
    }

    private void TickCarrying(ToyTuningSO t, float dt)
    {
        if (toy == null || toy.Holder != owner)
        {
            var lost  = toy;
            var thief = lost != null ? lost.Holder : null;
            toy = null;
            owner.EmitEmote(EmoteKind.Molesto);
            if (thief != null && thief != owner) BeginChase(thief, lost, t);
            else End(false);
            return;
        }

        if (timer >= duration)
        {
            toy.Detach(ctx.Body.forward * DropForwardSpeed);
            toy = null;
            End(true);
            return;
        }

        if (!Repath(dt)) return;
        if (ctx.Agent.enabled && ctx.Agent.isOnNavMesh && !ctx.Agent.pathPending &&
            ctx.Agent.remainingDistance <= ctx.Agent.stoppingDistance + 0.3f)
            PickWanderPoint(t);
    }

    private void TickChasing(ToyTuningSO t, float dt)
    {
        if (target == null || target.IsPenned || timer >= duration) { End(false); return; }
        if (toy != null && (toy.Holder != target)) { End(false); return; }

        if (!Repath(dt)) return;

        if (Planar(target.transform.position) <= t.StealRange)
        {
            if (toy == null)
            {
                owner.EmitEmote(EmoteKind.Molesto);
                End(true);
                return;
            }
            if (Random.value < t.StealChance && BeginCarry(toy, EmoteKind.Feliz, t)) return;
        }

        ctx.SetDestinationSafe(target.transform.position);
    }

    private void TickSnatching(ToyTuningSO t, float dt)
    {
        var heldToy = HeldToyOfPlayer();
        if (ctx.Player == null || heldToy == null || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (ctx.PlanarDistanceToPlayer() <= t.SnatchRange)
        {
            if (Random.value < t.SnatchChancePerSecond * dt)
            {
                HotbarController.Instance.DropActive();
                if (!BeginCarry(NearestFreeCarriable(ctx.Player.position, t.SnatchRange * 2f), EmoteKind.Feliz, t)) End(false);
            }
            return;
        }

        if (Repath(dt)) ctx.SetDestinationSafe(ctx.Player.position);
    }

    private static Toy NearestFreeCarriable(Vector3 around, float radius)
    {
        Toy best = null;
        float bestSqr = radius * radius;
        var all = Toy.All;
        for (int i = 0; i < all.Count; i++)
        {
            var candidate = all[i];
            if (candidate == null || !candidate.IsCarriable || !candidate.IsFree) continue;
            float sqr = (candidate.transform.position - around).sqrMagnitude;
            if (sqr > bestSqr) continue;
            bestSqr = sqr;
            best    = candidate;
        }
        return best;
    }

    internal void ReactToHit(Toy hitToy, MoriMochiAgent kicker)
    {
        owner.EmitEmote(EmoteKind.Molesto);

        var t = owner.toyTuning;
        if (t == null || kicker == null || kicker == owner) return;
        if (toy != null) return;
        if (!CanPlay()) return;
        if (ctx.State != AgentState.Idle && ctx.State != AgentState.Roaming && ctx.State != AgentState.Playing) return;

        owner.RequestReleaseStation();
        BeginChase(kicker, null, t);
    }

    internal void TickAlways()
    {
        if (mode == ToyMode.None) return;
        if (ctx.State == AgentState.Playing) return;

        DropToy();
        Clear();
    }

    internal void DropToy()
    {
        if (toy != null && toy.Holder == owner) toy.Detach(owner.Velocity);
        toy = null;
    }

    private void Clear()
    {
        ClearBoost();
        mode   = ToyMode.None;
        toy    = null;
        target = null;
        var t = owner.toyTuning;
        cooldownUntil = Time.time + (t != null ? t.Cooldown : 0f);
    }

    private void End(bool completed)
    {
        if (completed) owner.EmitEmote(EmoteKind.Feliz);
        DropToy();
        Clear();
        if (ctx.State == AgentState.Playing) owner.RequestRoam();
    }

    internal CreatureIntent Intent => mode switch
    {
        ToyMode.Kicking   => CreatureIntent.Playing,
        ToyMode.Carrying  => CreatureIntent.Playing,
        ToyMode.None      => CreatureIntent.Wandering,
        _                 => CreatureIntent.Approaching,
    };

    internal void ResetForReuse()
    {
        DropToy();
        ClearBoost();
        mode          = ToyMode.None;
        toy           = null;
        target        = null;
        timer         = 0f;
        repathTimer   = 0f;
        kickTimer     = 0f;
        cooldownUntil = 0f;
    }
}
}
