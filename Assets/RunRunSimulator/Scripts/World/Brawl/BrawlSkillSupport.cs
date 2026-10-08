using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public static class BrawlSkillSupport
{
    private const float BuddyShieldFactor = 0.6f;
    private const float BeamSeconds = 0.6f;
    private const float MinLobBlastRadius = 1.2f;

    private static readonly List<BrawlFighter> Temp = new();

    public static void Pull(BrawlCast c)
    {
        var me = c.Caster;
        var s = c.Skill;
        BrawlQuery.FoesWithin(me.Position, s.Radius, me.Team, Temp);
        for (var i = 0; i < Temp.Count; i++)
        {
            var f = Temp[i];
            var toMe = BrawlSkillEffects.PlanarDir(f.Position, me.Position);
            f.Motor.Knock(toMe, s.Knockback);
            if (s.Damage > 0f) f.TakeDamage(BrawlSkillEffects.Hit(c, f, s.Damage, toMe, 0f));
            if (s.TauntSeconds > 0f) f.ApplyTaunt(me, s.TauntSeconds);
            if (s.Slow > 0f) f.ApplySlow(s.Slow, s.SlowSeconds);
        }

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Pull, c);
        fx.To = me.Position;
        fx.Radius = s.Radius;
        BrawlFx.Emit(fx);
    }

    public static void Zone(BrawlCast c)
    {
        var me = c.Caster;
        var s = c.Skill;
        var center = ZoneCenter(c);
        BrawlZone.Spawn(new BrawlZoneSpec
        {
            Owner = me,
            Team = me.Team,
            Center = center,
            Radius = s.Radius,
            Delay = s.Delay,
            Duration = s.Duration,
            TickSeconds = s.TickSeconds,
            DamagePerTick = s.Damage,
            HealPerTick = s.Heal,
            Slow = s.Slow,
            SlowSeconds = s.SlowSeconds,
            StunSeconds = s.StunSeconds,
            Knockback = s.Knockback,
            Pull = 0f,
            FollowOwner = s.FollowCaster,
            HitOnArm = s.Duration <= 0f,
            Theme = c.Theme,
        });

        if (s.Delay <= 0f) return;
        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Throw, c);
        fx.From = me.Center;
        fx.To = center;
        fx.Radius = s.Radius;
        fx.Duration = s.Delay;
        BrawlFx.Emit(fx);
    }

    public static void Ward(BrawlCast c)
    {
        var me = c.Caster;
        var s = c.Skill;
        var target = s.Target == BrawlSkillTarget.LowestAlly && c.Target != null && c.Target.IsAlive ? c.Target : me;

        Protect(c, target, s.Shield, true);
        if (s.Count > 1)
        {
            var buddy = NearestAllyTo(target, s.Radius, me.Team);
            if (buddy != null) Protect(c, buddy, s.Shield * BuddyShieldFactor, false);
        }

        if (s.TauntSeconds <= 0f) return;
        BrawlQuery.FoesWithin(me.Position, s.Radius, me.Team, Temp);
        for (var i = 0; i < Temp.Count; i++) Temp[i].ApplyTaunt(me, s.TauntSeconds);

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Pull, c);
        fx.To = me.Position;
        fx.Radius = s.Radius;
        BrawlFx.Emit(fx);
    }

    public static void Mend(BrawlCast c)
    {
        if (c.Skill.Target == BrawlSkillTarget.LowestAlly) MendOne(c);
        else MendArea(c);
    }

    private static Vector3 ZoneCenter(BrawlCast c)
    {
        switch (c.Skill.Target)
        {
            case BrawlSkillTarget.Self:
                return c.Caster.Position;
            case BrawlSkillTarget.LowestAlly:
            case BrawlSkillTarget.AlliesAround:
                return c.Target != null ? c.Target.Position : c.Caster.Position;
            default:
                return c.AimPoint;
        }
    }

    private static void Protect(BrawlCast c, BrawlFighter f, float shield, bool full)
    {
        var s = c.Skill;
        if (shield > 0f) f.AddShield(shield, s.Duration);
        if (full)
        {
            if (s.Thorns > 0f) f.ApplyThorns(s.Thorns, s.Duration);
            if (s.Haste > 0f) f.ApplyHaste(s.Haste, s.Duration);
        }

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Ward, c);
        fx.To = f.Position;
        fx.Target = f;
        fx.Duration = s.Duration;
        BrawlFx.Emit(fx);
    }

    private static BrawlFighter NearestAllyTo(BrawlFighter anchor, float radius, ExpeditionTeam team)
    {
        BrawlQuery.AlliesWithin(anchor.Position, radius, team, Temp);
        BrawlFighter best = null;
        var bestDistance = float.MaxValue;
        for (var i = 0; i < Temp.Count; i++)
        {
            var f = Temp[i];
            if (f == anchor) continue;
            var d = BrawlQuery.Planar(anchor.Position, f.Position);
            if (d >= bestDistance) continue;
            bestDistance = d;
            best = f;
        }
        return best;
    }

    private static void MendOne(BrawlCast c)
    {
        var me = c.Caster;
        var s = c.Skill;
        var ally = c.Target != null && c.Target.IsAlive ? c.Target : BrawlQuery.LowestAlly(me, s.Range, false);
        if (ally == null) return;

        if (s.Delay > 0f)
        {
            var shot = BrawlSkillEffects.NewShot(c);
            shot.Lob = true;
            shot.LobTarget = ally.Position;
            shot.LobSeconds = s.Delay;
            shot.Heal = s.Heal;
            shot.HealsAllies = true;
            shot.Damage = 0f;
            shot.ExplodeRadius = Mathf.Max(MinLobBlastRadius, s.Radius);
            shot.SpriteSize = s.SpriteSize;
            BrawlProjectile.Fire(shot);
            return;
        }

        Boost(s, me, ally);

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Beam, c);
        fx.From = me.Center;
        fx.To = ally.Center;
        fx.Duration = BeamSeconds;
        fx.Target = ally;
        BrawlFx.Emit(fx);
    }

    private static void MendArea(BrawlCast c)
    {
        var me = c.Caster;
        var s = c.Skill;
        BrawlQuery.AlliesWithin(me.Position, s.Radius, me.Team, Temp);
        for (var i = 0; i < Temp.Count; i++) Boost(s, me, Temp[i]);

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Pulse, c);
        fx.To = me.Position;
        fx.Radius = s.Radius;
        BrawlFx.Emit(fx);
    }

    private static void Boost(BrawlSkillSO s, BrawlFighter source, BrawlFighter ally)
    {
        if (s.Heal > 0f) ally.Heal(s.Heal, source);
        if (s.Haste > 0f) ally.ApplyHaste(s.Haste, s.Duration);
        if (s.DamageBoost > 0f) ally.ApplyDamageBoost(s.DamageBoost, s.Duration);
    }
}

}
