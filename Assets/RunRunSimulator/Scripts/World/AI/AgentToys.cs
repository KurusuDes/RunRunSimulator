using UnityEngine;
namespace MoriMonchiSimulator
{

internal class AgentToys
{
    private readonly MoriMochiAgent  owner;
    private readonly AgentContext    ctx;
    private readonly AgentToyMotor   motor;
    private readonly IToyBehavior[]  behaviors;

    private IToyBehavior active;

    internal AgentToys(MoriMochiAgent owner, AgentContext ctx)
    {
        this.owner = owner;
        this.ctx   = ctx;
        motor      = new AgentToyMotor(owner, ctx);
        behaviors  = new IToyBehavior[]
        {
            new ToyPlayerPlay(owner, ctx, motor),
            new ToyBuddyPlay(owner, ctx, motor),
            new ToyFreePlay(owner, ctx, motor),
        };
    }

    private bool InvitingToyNear(ToyTuningSO t, bool byPlayerOnly)
    {
        var all = Toy.All;
        for (int i = 0; i < all.Count; i++)
        {
            var toy = all[i];
            if (toy == null || motor.Planar(toy.transform.position) > t.NoticeRadius) continue;
            if (toy.ThrownByPlayer && toy.IsFree) return true;
            if (!byPlayerOnly && toy.Kind == ToyKind.Rope && toy.Holder != null && toy.Holder != owner && toy.TuggedBy == null) return true;
        }
        return false;
    }

    internal bool TryEngage()
    {
        var t = owner.toyTuning;
        if (t == null) return false;
        bool reacting = ctx.State == AgentState.Reacting;
        if (ctx.State != AgentState.Idle && ctx.State != AgentState.Roaming && !reacting) return false;
        bool byPlayer = InvitingToyNear(t, true);
        if (reacting && !byPlayer && AgentToyMotor.HeldToyOfPlayer() == null) return false;
        if (!byPlayer && !motor.CooldownReady) return false;
        bool invited = byPlayer || InvitingToyNear(t, false);
        if (!motor.CanPlay()) return false;
        if (ctx.Dna.Needs.Energy < t.MinEnergy) return false;
        float chance = invited ? t.FetchEngageChancePerSecond : t.EngageChancePerSecond;
        if (Random.value >= chance * Time.deltaTime) return false;

        if (TryBehavior(0, t)) return true;
        int rest   = behaviors.Length - 1;
        int offset = Random.Range(0, rest);
        for (int i = 0; i < rest; i++)
            if (TryBehavior(1 + (offset + i) % rest, t)) return true;

        return false;
    }

    private bool TryBehavior(int index, ToyTuningSO t)
    {
        if (!behaviors[index].TryEngage(t)) return false;
        active = behaviors[index];
        return true;
    }

    internal void TickPlaying()
    {
        var t = owner.toyTuning;
        if (t == null || ctx.Dna == null || active == null || !active.IsActive) { Abort(); return; }

        float dt = Time.deltaTime;
        ctx.Dna.Needs.AddAffect(t.AffectPerSecond * dt);
        motor.RefreshBoost();

        active.Tick(t, dt);
        if (!active.IsActive) active = null;
    }

    internal void TickAlways()
    {
        if (active == null) return;
        if (ctx.State == AgentState.Playing) return;

        active.Clear();
        active = null;
        motor.ClearBoost();
        motor.StartCooldown();
    }

    internal void ReactToHit(Toy hitToy, MoriMochiAgent kicker)
    {
        owner.EmitEmote(EmoteKind.Molesto);

        if (active != null)
        {
            active.ReactToHit(hitToy, kicker);
            return;
        }

        for (int i = 0; i < behaviors.Length; i++)
        {
            if (!behaviors[i].ReactToHit(hitToy, kicker)) continue;
            active = behaviors[i];
            return;
        }
    }

    internal CreatureIntent Intent => active != null ? active.Intent : CreatureIntent.Wandering;

    internal void ResetForReuse()
    {
        if (active != null) active.Clear();
        active = null;
        motor.Reset();
    }

    private void Abort()
    {
        if (active != null) active.Clear();
        active = null;
        motor.Finish(false);
    }
}
}
