using UnityEngine;
namespace MoriMonchiSimulator
{

internal class AgentToyMotor
{
    private const float BoostRefresh = 0.25f;

    private readonly MoriMochiAgent owner;
    private readonly AgentContext   ctx;

    private Transform mouth;
    private float     repathTimer;
    private float     cooldownUntil;
    private bool      boosting;

    internal AgentToyMotor(MoriMochiAgent owner, AgentContext ctx)
    {
        this.owner = owner;
        this.ctx   = ctx;
    }

    internal bool CooldownReady => Time.time >= cooldownUntil;

    internal bool CanPlay()
    {
        if (ctx.Dna == null) return false;
        if (ctx.CurrentContainer != null) return false;
        if (ctx.IsBreeding) return false;
        if (ctx.Dna.Form == MonchiForm.Egg) return false;
        if (owner.Team != ExpeditionTeam.None) return false;
        return true;
    }

    internal float Planar(Vector3 p)
    {
        Vector3 d = p - ctx.Body.position; d.y = 0f;
        return d.magnitude;
    }

    internal void Enter()
    {
        repathTimer = 0f;

        ctx.State                = AgentState.Playing;
        ctx.SetStopped(false);
        ctx.Agent.updateRotation = true;
    }

    internal void SetBoost(float multiplier)
    {
        boosting            = true;
        ctx.SpeedMultiplier = multiplier;
        ctx.SpeedBoostUntil = Time.time + BoostRefresh;
    }

    internal void RefreshBoost()
    {
        if (boosting) ctx.SpeedBoostUntil = Time.time + BoostRefresh;
    }

    internal void ClearBoost()
    {
        if (!boosting) return;
        boosting            = false;
        ctx.SpeedBoostUntil = 0f;
    }

    internal bool Repath(float dt)
    {
        repathTimer -= dt;
        if (repathTimer > 0f) return false;
        repathTimer = owner.repathInterval;
        return true;
    }

    internal void StartCooldown()
    {
        var t = owner.toyTuning;
        cooldownUntil = Time.time + (t != null ? t.Cooldown : 0f);
    }

    internal void Finish(bool completed)
    {
        if (completed) owner.EmitEmote(EmoteKind.Feliz);
        ClearBoost();
        StartCooldown();
        if (ctx.State == AgentState.Playing) owner.RequestRoam();
    }

    internal void Reset()
    {
        ClearBoost();
        repathTimer   = 0f;
        cooldownUntil = 0f;
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

    internal bool TryCarry(Toy carried, EmoteKind emote, ToyTuningSO t)
    {
        if (carried == null) return false;
        if (!carried.TryAttach(owner, EnsureMouth(t))) return false;

        Enter();
        SetBoost(t.CarrySpeedMultiplier);
        PickWanderPoint(carried, t);
        owner.EmitEmote(emote);
        return true;
    }

    internal void Drop(Toy toy, Vector3 velocity)
    {
        if (toy != null && toy.Holder == owner) toy.Detach(velocity);
    }

    internal void PickWanderPoint(Toy toy, ToyTuningSO t)
    {
        var area = toy != null ? toy.HomeArea : null;
        if (area != null)
        {
            ctx.SetDestinationSafe(area.RandomPoint(1f));
            return;
        }

        Vector2 r = Random.insideUnitCircle * t.WanderRadius;
        ctx.SetDestinationSafe(ctx.Body.position + new Vector3(r.x, 0f, r.y));
    }

    internal static Toy HeldToyOfPlayer()
    {
        var hotbar = HotbarController.Instance;
        if (hotbar == null) return null;
        var held = hotbar.ActiveHeldObject;
        return held != null ? held.GetComponentInChildren<Toy>() : null;
    }

    internal static Toy NearestFreeCarriable(Vector3 around, float radius)
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
}
}
