using UnityEngine;
namespace MoriMonchiSimulator
{

internal class ToyBuddyPlay : IToyBehavior
{
    private enum BuddyMode { None, GoToRope, Tugging, CarryAway, GoToPlush, CarryPlush, Hugging, Bubbles }

    private const float TugEngageFactor   = 1.5f;
    private const float TugBreakFactor    = 3f;
    private const float TugEmoteInterval  = 1f;
    private const float HugEmoteInterval  = 2f;
    private const float HugNeighborRadius = 2.5f;
    private const float PlushEngageChance = 0.5f;
    private const float BoldnessTugBias   = 0.25f;
    private const float ArriveMargin      = 0.3f;
    private const float MinCarryTime      = 0.5f;
    private const float DropForwardSpeed  = 1.5f;
    private const float FaceTurnSpeed     = 10f;

    private readonly MoriMochiAgent owner;
    private readonly AgentContext   ctx;
    private readonly AgentToyMotor  motor;

    private BuddyMode      mode;
    private Toy            toy;
    private MoriMochiAgent target;
    private Bubble         bubble;
    private float          timer;
    private float          duration;
    private float          emoteTimer;
    private int            pops;
    private bool           stopped;

    internal ToyBuddyPlay(MoriMochiAgent owner, AgentContext ctx, AgentToyMotor motor)
    {
        this.owner = owner;
        this.ctx   = ctx;
        this.motor = motor;
    }

    public bool IsActive => mode != BuddyMode.None;

    public CreatureIntent Intent => mode switch
    {
        BuddyMode.Tugging   => CreatureIntent.Playing,
        BuddyMode.CarryAway => CreatureIntent.Playing,
        BuddyMode.Hugging   => CreatureIntent.Playing,
        BuddyMode.Bubbles   => pops > 0 ? CreatureIntent.Playing : CreatureIntent.Approaching,
        BuddyMode.None      => CreatureIntent.Wandering,
        _                   => CreatureIntent.Approaching,
    };

    public bool TryEngage(ToyTuningSO t)
    {
        var rope = NearestCarriedRope(t);
        if (rope != null && Random.value < t.RopeTugChance)
        {
            owner.RequestReleaseStation();
            toy    = rope;
            target = rope.Holder;
            Begin(BuddyMode.GoToRope);
            motor.SetBoost(t.ChaseSpeedMultiplier);
            owner.EmitEmote(EmoteKind.Jugando);
            return true;
        }

        var plush = NearestFreePlush(t);
        if (plush != null && Random.value < PlushEngageChance)
        {
            owner.RequestReleaseStation();
            toy = plush;
            Begin(BuddyMode.GoToPlush);
            return true;
        }

        var next = NearestBubble(t, null);
        if (next != null)
        {
            owner.RequestReleaseStation();
            bubble = next;
            bubble.Claim(owner);
            pops = 0;
            Begin(BuddyMode.Bubbles);
            motor.SetBoost(t.ChaseSpeedMultiplier);
            return true;
        }

        return false;
    }

    public void Tick(ToyTuningSO t, float dt)
    {
        timer += dt;

        switch (mode)
        {
            case BuddyMode.GoToRope:   TickGoToRope(t, dt);   break;
            case BuddyMode.Tugging:    TickTugging(t, dt);    break;
            case BuddyMode.CarryAway:  TickCarryAway(t, dt);  break;
            case BuddyMode.GoToPlush:  TickGoToPlush(t, dt);  break;
            case BuddyMode.CarryPlush: TickCarryPlush(t, dt); break;
            case BuddyMode.Hugging:    TickHugging(t, dt);    break;
            case BuddyMode.Bubbles:    TickBubbles(t, dt);    break;
        }
    }

    public bool ReactToHit(Toy hitToy, MoriMochiAgent kicker) => false;

    public void Clear()
    {
        if (toy != null)
        {
            toy.ClearTugger(owner);
            motor.Drop(toy, owner.Velocity);
        }
        if (stopped) ctx.SetStopped(false);
        stopped = false;
        mode    = BuddyMode.None;
        toy     = null;
        target  = null;
        bubble  = null;
        pops    = 0;
    }

    private void End(bool completed)
    {
        Clear();
        motor.Finish(completed);
    }

    private void Begin(BuddyMode newMode)
    {
        mode       = newMode;
        timer      = 0f;
        emoteTimer = 0f;
        motor.Enter();
    }

    private void Hold()
    {
        motor.ClearBoost();
        ctx.SetStopped(true);
        stopped    = true;
        timer      = 0f;
        emoteTimer = 0f;
    }

    private void Face(Vector3 position)
    {
        Vector3 dir = position - ctx.Body.position; dir.y = 0f;
        if (dir.sqrMagnitude < 0.001f) return;
        ctx.Body.rotation = Quaternion.Slerp(
            ctx.Body.rotation, Quaternion.LookRotation(dir.normalized, Vector3.up), FaceTurnSpeed * Time.deltaTime);
    }

    private Toy NearestCarriedRope(ToyTuningSO t)
    {
        Toy best = null;
        float bestDist = t.NoticeRadius;
        var all = Toy.All;
        for (int i = 0; i < all.Count; i++)
        {
            var c = all[i];
            if (c == null || c.Kind != ToyKind.Rope || c.TuggedBy != null) continue;
            var holder = c.Holder;
            if (holder == null || holder == owner || holder.IsPenned) continue;
            float d = motor.Planar(c.transform.position);
            if (d >= bestDist) continue;
            bestDist = d;
            best     = c;
        }
        return best;
    }

    private Toy NearestFreePlush(ToyTuningSO t)
    {
        Toy best = null;
        float bestDist = t.NoticeRadius;
        var all = Toy.All;
        for (int i = 0; i < all.Count; i++)
        {
            var c = all[i];
            if (c == null || c.Kind != ToyKind.Plush || !c.IsFree) continue;
            float d = motor.Planar(c.transform.position);
            if (d >= bestDist) continue;
            bestDist = d;
            best     = c;
        }
        return best;
    }

    private Bubble NearestBubble(ToyTuningSO t, Bubble exclude)
    {
        Bubble best = null;
        float bestDist = t.NoticeRadius;
        var all = Bubble.All;
        for (int i = 0; i < all.Count; i++)
        {
            var c = all[i];
            if (c == null || c == exclude || c.Popped) continue;
            float d = motor.Planar(c.transform.position);
            if (d >= bestDist) continue;
            bestDist = d;
            best     = c;
        }
        return best;
    }

    private void RecordWith(MoriMochiAgent other, SocialInteractionKind kind)
    {
        if (other == null || other == owner || other.DNA == null || ctx.Dna == null) return;
        SocialGraphService.RecordInteraction(ctx.Dna.UniqueID, other.DNA.UniqueID, kind);
    }

    private void TickGoToRope(ToyTuningSO t, float dt)
    {
        if (toy == null || target == null || toy.Holder != target || target.IsPenned ||
            (toy.TuggedBy != null && toy.TuggedBy != owner) || timer >= t.ChaseDuration * 2f)
        {
            End(false);
            return;
        }

        if (motor.Planar(target.transform.position) <= t.StealRange * TugEngageFactor)
        {
            toy.SetTugger(owner);
            Hold();
            duration = Random.Range(t.RopeTugMin, t.RopeTugMax);
            mode     = BuddyMode.Tugging;
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(target.transform.position);
    }

    private void TickTugging(ToyTuningSO t, float dt)
    {
        if (toy == null || target == null || toy.Holder != target || target.IsPenned ||
            motor.Planar(target.transform.position) > t.StealRange * TugBreakFactor)
        {
            End(false);
            return;
        }

        Face(target.transform.position);

        emoteTimer -= dt;
        if (emoteTimer <= 0f)
        {
            owner.EmitEmote(EmoteKind.Jugando);
            emoteTimer = TugEmoteInterval;
        }

        if (timer >= duration) ResolveTug(t);
    }

    private void ResolveTug(ToyTuningSO t)
    {
        var rival = target;
        toy.ClearTugger(owner);

        ctx.Dna.Needs.AddAffect(t.RopeTugAffect);
        if (rival.DNA != null) rival.DNA.Needs.AddAffect(t.RopeTugAffect);
        RecordWith(rival, SocialInteractionKind.PlayChase);

        float myBold    = ctx.Dna.Boldness;
        float theirBold = rival.DNA != null ? rival.DNA.Boldness : 0.5f;
        float winChance = Mathf.Clamp01(0.5f + (myBold - theirBold) * BoldnessTugBias);

        ctx.SetStopped(false);
        stopped = false;

        if (Random.value < winChance)
        {
            toy.Detach(Vector3.zero);
            if (motor.TryCarry(toy, EmoteKind.Feliz, t))
            {
                target   = null;
                duration = Random.Range(t.CarryDurationMin, t.CarryDurationMax);
                mode     = BuddyMode.CarryAway;
                timer    = 0f;
                return;
            }
        }

        End(true);
    }

    private void TickCarryAway(ToyTuningSO t, float dt)
    {
        if (toy == null || toy.Holder != owner) { End(false); return; }

        if (timer >= duration)
        {
            motor.Drop(toy, ctx.Body.forward * DropForwardSpeed);
            End(true);
            return;
        }

        if (!motor.Repath(dt)) return;
        if (Arrived()) motor.PickWanderPoint(toy, t);
    }

    private bool Arrived() =>
        ctx.Agent.enabled && ctx.Agent.isOnNavMesh && !ctx.Agent.pathPending &&
        ctx.Agent.remainingDistance <= ctx.Agent.stoppingDistance + ArriveMargin;

    private void TickGoToPlush(ToyTuningSO t, float dt)
    {
        if (toy == null || !toy.IsFree || timer >= t.ChaseDuration * 2f) { End(false); return; }

        if (motor.Planar(toy.transform.position) <= t.KickRange)
        {
            if (!motor.TryCarry(toy, EmoteKind.Corazon, t)) { End(false); return; }
            mode  = BuddyMode.CarryPlush;
            timer = 0f;
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(toy.transform.position);
    }

    private void TickCarryPlush(ToyTuningSO t, float dt)
    {
        if (toy == null || toy.Holder != owner) { End(false); return; }

        bool arrived = timer >= MinCarryTime && Arrived();
        if (!arrived && timer < t.ChaseDuration * 2f) return;

        Hold();
        duration = Random.Range(t.HugDurationMin, t.HugDurationMax);
        mode     = BuddyMode.Hugging;
    }

    private void TickHugging(ToyTuningSO t, float dt)
    {
        if (toy == null || toy.Holder != owner) { End(false); return; }

        ctx.Dna.Needs.AddAffect(t.HugAffectPerSecond * dt);

        emoteTimer -= dt;
        if (emoteTimer <= 0f)
        {
            owner.EmitEmote(EmoteKind.Corazon);
            emoteTimer = HugEmoteInterval;
        }

        if (timer < duration) return;

        float sqrRadius = HugNeighborRadius * HugNeighborRadius;
        for (int i = 0; i < ctx.Percepts.Count; i++)
        {
            var p = ctx.Percepts[i];
            if (p.Kind != PerceivableKind.Monchi || p.SqrDistance > sqrRadius) continue;
            RecordWith(p.Source != null ? p.Source.Monchi : null, SocialInteractionKind.SleepTogether);
        }

        End(true);
    }

    private void TickBubbles(ToyTuningSO t, float dt)
    {
        if (timer >= t.ChaseDuration * 2f) { End(pops > 0); return; }

        if (bubble == null || bubble.Popped)
        {
            var next = pops >= t.PopsMax ? null : NearestBubble(t, bubble);
            if (next == null) { End(pops > 0); return; }
            bubble = next;
            bubble.Claim(owner);
            timer = 0f;
        }

        if (motor.Planar(bubble.transform.position) <= t.PopRange)
        {
            var others = bubble.Pop(owner);
            owner.EmitEmote(EmoteKind.Jugando);
            ctx.Dna.Needs.AddAffect(t.PopAffect);
            if (others != null)
                for (int i = 0; i < others.Count; i++) RecordWith(others[i], SocialInteractionKind.PlayChase);

            pops++;
            bubble = null;
            if (pops >= t.PopsMax) End(true);
            return;
        }

        if (motor.Repath(dt)) ctx.SetDestinationSafe(bubble.transform.position);
    }
}
}
