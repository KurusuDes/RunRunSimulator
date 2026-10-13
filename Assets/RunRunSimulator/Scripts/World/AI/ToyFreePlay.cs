using UnityEngine;
namespace MoriMonchiSimulator
{

internal class ToyFreePlay : IToyBehavior
{
    private enum ToyMode { None, GoToBall, Kicking, GoToCarry, Carrying, Chasing }

    private const float KickNoiseDegrees = 25f;
    private const float DropForwardSpeed = 1.5f;
    private const float FaceTurnSpeed    = 360f;

    private readonly MoriMochiAgent owner;
    private readonly AgentContext   ctx;
    private readonly AgentToyMotor  motor;

    private ToyMode        mode;
    private Toy            toy;
    private MoriMochiAgent target;
    private float          timer;
    private float          duration;
    private float          kickTimer;
    private int            kicksLeft;
    private bool           tugPaused;

    internal ToyFreePlay(MoriMochiAgent owner, AgentContext ctx, AgentToyMotor motor)
    {
        this.owner = owner;
        this.ctx   = ctx;
        this.motor = motor;
    }

    public bool IsActive => mode != ToyMode.None;

    public CreatureIntent Intent => mode switch
    {
        ToyMode.Kicking   => CreatureIntent.Playing,
        ToyMode.Carrying  => CreatureIntent.Playing,
        ToyMode.None      => CreatureIntent.Wandering,
        _                 => CreatureIntent.Approaching,
    };

    public bool TryEngage(ToyTuningSO t)
    {
        Toy stealable = null;
        Toy free      = null;
        float bestSteal = t.NoticeRadius;
        float bestFree  = t.NoticeRadius;

        var all = Toy.All;
        for (int i = 0; i < all.Count; i++)
        {
            var candidate = all[i];
            if (candidate == null) continue;

            float d = motor.Planar(candidate.transform.position);
            if (d > t.NoticeRadius) continue;

            if (candidate.IsCarriable && candidate.Holder != null && candidate.Holder != owner)
            {
                if (d < bestSteal) { bestSteal = d; stealable = candidate; }
            }
            else if (candidate.IsFree && (candidate.IsKickable || candidate.IsCarriable) && d < bestFree)
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
            Begin(free.IsKickable ? ToyMode.GoToBall : ToyMode.GoToCarry);
            return true;
        }

        return false;
    }

    public void Tick(ToyTuningSO t, float dt)
    {
        timer += dt;

        switch (mode)
        {
            case ToyMode.GoToBall:  TickGoToBall(t, dt);  break;
            case ToyMode.Kicking:   TickKicking(t, dt);   break;
            case ToyMode.GoToCarry: TickGoToCarry(t, dt); break;
            case ToyMode.Carrying:  TickCarrying(t, dt);  break;
            case ToyMode.Chasing:   TickChasing(t, dt);   break;
        }
    }

    public bool ReactToHit(Toy hitToy, MoriMochiAgent kicker)
    {
        var t = owner.toyTuning;
        if (t == null || kicker == null || kicker == owner) return false;
        if (toy != null) return false;
        if (!motor.CanPlay()) return false;
        if (ctx.State != AgentState.Idle && ctx.State != AgentState.Roaming && ctx.State != AgentState.Playing) return false;

        owner.RequestReleaseStation();
        BeginChase(kicker, null, t);
        return true;
    }

    public void Clear()
    {
        DropToy();
        Reset();
    }

    private void Reset()
    {
        if (tugPaused) { tugPaused = false; ctx.SetStopped(false); }
        mode   = ToyMode.None;
        toy    = null;
        target = null;
    }

    private void DropToy()
    {
        motor.Drop(toy, owner.Velocity);
        toy = null;
    }

    private void End(bool completed)
    {
        Clear();
        motor.Finish(completed);
    }

    private void Begin(ToyMode newMode)
    {
        mode      = newMode;
        timer     = 0f;
        kickTimer = 0f;
        tugPaused = false;
        motor.Enter();
    }

    private void BeginChase(MoriMochiAgent who, Toy stealToy, ToyTuningSO t)
    {
        target   = who;
        toy      = stealToy;
        duration = t.ChaseDuration;
        Begin(ToyMode.Chasing);
        motor.SetBoost(t.ChaseSpeedMultiplier);
    }

    private bool BeginCarry(Toy carried, EmoteKind emote, ToyTuningSO t)
    {
        if (!motor.TryCarry(carried, emote, t)) return false;

        toy      = carried;
        target   = null;
        duration = Random.Range(t.CarryDurationMin, t.CarryDurationMax);
        mode     = ToyMode.Carrying;
        timer    = 0f;
        kickTimer = 0f;
        return true;
    }

    private void TickGoToBall(ToyTuningSO t, float dt)
    {
        if (toy == null || !toy.IsFree || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (motor.Planar(toy.transform.position) <= t.KickRange)
        {
            kicksLeft = Random.Range(t.KicksMin, t.KicksMax + 1);
            mode      = ToyMode.Kicking;
            timer     = 0f;
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(toy.transform.position);
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

        if (kickTimer <= 0f && motor.Planar(ballPos) <= t.KickRange)
        {
            Vector3 dir = ballPos - ctx.Body.position; dir.y = 0f;
            dir = dir.sqrMagnitude > 0.0001f ? dir.normalized : ctx.Body.forward;
            var area = toy.HomeArea;
            if (area != null && !area.Contains(ballPos))
            {
                Vector3 home = area.Center - ballPos; home.y = 0f;
                if (home.sqrMagnitude > 0.0001f) dir = home.normalized;
            }
            else
            {
                dir = Quaternion.AngleAxis(Random.Range(-KickNoiseDegrees, KickNoiseDegrees), Vector3.up) * dir;
            }

            toy.Kick(owner, dir * t.KickForce + Vector3.up * t.KickUp);
            owner.EmitEmote(EmoteKind.Jugando);
            kicksLeft--;
            kickTimer = owner.repathInterval * 2f;
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(ballPos);
    }

    private void TickGoToCarry(ToyTuningSO t, float dt)
    {
        if (toy == null || !toy.IsFree || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (motor.Planar(toy.transform.position) <= t.KickRange)
        {
            if (!BeginCarry(toy, EmoteKind.Jugando, t)) End(false);
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(toy.transform.position);
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

        var tugger = toy.TuggedBy;
        if (tugger != null)
        {
            timer -= dt;
            if (!tugPaused)
            {
                tugPaused = true;
                ctx.SetStopped(true);
            }
            FaceTowards(tugger.transform.position, dt);
            return;
        }

        if (tugPaused)
        {
            tugPaused = false;
            ctx.SetStopped(false);
            motor.PickWanderPoint(toy, t);
        }

        if (timer >= duration)
        {
            motor.Drop(toy, ctx.Body.forward * DropForwardSpeed);
            toy = null;
            End(true);
            return;
        }

        if (!motor.Repath(dt)) return;
        if (ctx.Agent.enabled && ctx.Agent.isOnNavMesh && !ctx.Agent.pathPending &&
            ctx.Agent.remainingDistance <= ctx.Agent.stoppingDistance + 0.3f)
            motor.PickWanderPoint(toy, t);
    }

    private void TickChasing(ToyTuningSO t, float dt)
    {
        if (target == null || target.IsPenned || timer >= duration) { End(false); return; }
        if (toy != null && (toy.Holder != target)) { End(false); return; }

        if (!motor.Repath(dt)) return;

        if (motor.Planar(target.transform.position) <= t.StealRange)
        {
            if (toy == null)
            {
                owner.EmitEmote(EmoteKind.Molesto);
                End(true);
                return;
            }
            var victim = target;
            if (Random.value < t.StealChance && BeginCarry(toy, EmoteKind.Feliz, t))
            {
                if (ctx.Dna != null && victim.DNA != null)
                    SocialGraphService.RecordInteraction(ctx.Dna.UniqueID, victim.DNA.UniqueID, SocialInteractionKind.PlayChase);
                return;
            }
        }

        ctx.SetDestinationSafe(target.transform.position);
    }

    private void FaceTowards(Vector3 point, float dt)
    {
        Vector3 d = point - ctx.Body.position; d.y = 0f;
        if (d.sqrMagnitude < 0.0001f) return;
        ctx.Body.rotation = Quaternion.RotateTowards(ctx.Body.rotation, Quaternion.LookRotation(d), FaceTurnSpeed * dt);
    }

    private void TickSnatching(ToyTuningSO t, float dt)
    {
        var heldToy = AgentToyMotor.HeldToyOfPlayer();
        if (ctx.Player == null || heldToy == null || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (ctx.PlanarDistanceToPlayer() <= t.SnatchRange)
        {
            if (Random.value < t.SnatchChancePerSecond * dt)
            {
                HotbarController.Instance.DropActive();
                if (!BeginCarry(AgentToyMotor.NearestFreeCarriable(ctx.Player.position, t.SnatchRange * 2f), EmoteKind.Feliz, t)) End(false);
            }
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(ctx.Player.position);
    }
}
}
