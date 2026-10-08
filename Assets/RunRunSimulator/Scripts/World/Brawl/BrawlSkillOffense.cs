using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public static class BrawlSkillOffense
{
    private const float DashFallbackSeconds = 0.35f;
    private const float ChainFalloff = 0.8f;
    private const float ChainReach = 1f;
    private const float NovaProjectileRadius = 0.4f;
    private const float NovaRingRadius = 1.5f;
    private const float HomingFanStep = 25f;
    private const float HomingTurnSpeed = 300f;
    private const float HomingRangeFactor = 1.6f;
    private const float HomingProjectileRadius = 0.45f;
    private const float ShotSpin = 360f;

    private static readonly List<BrawlFighter> Temp = new();
    private static readonly List<BrawlFighter> Linked = new();

    public static void Dash(BrawlCast c)
    {
        var me = c.Caster;
        var s = c.Skill;
        var start = me.Position;
        var dir = c.AimDir;
        var struck = new HashSet<BrawlFighter>();

        me.Motor.Dash(dir, s.Range, s.Duration > 0f ? s.Duration : DashFallbackSeconds,
            pos => DashStep(c, pos, start, dir, struck), null);

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Dash, c);
        fx.From = start;
        fx.To = start + dir * s.Range;
        BrawlFx.Emit(fx);
    }

    public static void Chain(BrawlCast c)
    {
        var me = c.Caster;
        var s = c.Skill;
        Linked.Clear();

        var target = ChainStart(c);
        if (target == null)
        {
            var miss = BrawlSkillEffects.NewFx(BrawlFxKind.Lightning, c);
            miss.Path = new[] { me.Center, me.Center + c.AimDir * s.Range };
            BrawlFx.Emit(miss);
            return;
        }

        var previous = me.Position;
        var damage = s.Damage;
        var links = Mathf.Max(1, s.Count);
        for (var i = 0; i < links && target != null; i++)
        {
            Linked.Add(target);
            var knock = BrawlSkillEffects.PlanarDir(previous, target.Position);
            if (damage > 0f) target.TakeDamage(BrawlSkillEffects.Hit(c, target, damage, knock, s.Knockback));
            BrawlSkillEffects.Control(s, target);
            previous = target.Position;
            damage *= ChainFalloff;
            target = i + 1 < links ? NextLink(me, target, s.Radius) : null;
        }

        var path = new Vector3[Linked.Count + 1];
        path[0] = me.Center;
        for (var i = 0; i < Linked.Count; i++) path[i + 1] = Linked[i].Center;

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Lightning, c);
        fx.Path = path;
        BrawlFx.Emit(fx);
    }

    public static void Cone(BrawlCast c)
    {
        var me = c.Caster;
        var s = c.Skill;
        var origin = me.Position;
        BrawlQuery.FoesWithin(origin, s.Range, me.Team, Temp);
        for (var i = 0; i < Temp.Count; i++)
        {
            var f = Temp[i];
            if (!BrawlQuery.InCone(origin, c.AimDir, s.Range, s.Angle * 0.5f, f)) continue;
            var knock = BrawlSkillEffects.PlanarDir(origin, f.Position);
            if (s.Damage > 0f) f.TakeDamage(BrawlSkillEffects.Hit(c, f, s.Damage, knock, s.Knockback));
            BrawlSkillEffects.Control(s, f);
        }

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Slash, c);
        fx.From = origin;
        fx.To = origin + c.AimDir;
        fx.Radius = s.Range;
        fx.Angle = s.Angle;
        BrawlFx.Emit(fx);
    }

    public static void Shot(BrawlCast c)
    {
        var s = c.Skill;
        var shot = BrawlSkillEffects.NewShot(c);
        shot.Speed = s.Speed;
        shot.Range = s.Range;
        shot.Damage = s.Damage;
        shot.Radius = s.Radius;
        shot.Knockback = s.Knockback;
        shot.Slow = s.Slow;
        shot.SlowSeconds = s.SlowSeconds;
        shot.StunSeconds = s.StunSeconds;
        shot.Bounces = s.Bounces;
        shot.Pierce = s.Pierce;
        shot.ExplodeRadius = s.ExplodeRadius;
        shot.SpriteSize = s.SpriteSize;
        shot.Spin = ShotSpin;
        BrawlProjectile.Fire(shot);

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Muzzle, c);
        fx.From = shot.Origin;
        fx.To = shot.Origin + c.AimDir;
        BrawlFx.Emit(fx);
    }

    public static void Nova(BrawlCast c)
    {
        var s = c.Skill;
        var me = c.Caster;
        var count = Mathf.Max(1, s.Count);
        var step = 360f / count;
        var offset = Random.value * 360f;
        for (var i = 0; i < count; i++)
        {
            var shot = BrawlSkillEffects.NewShot(c);
            shot.Direction = Quaternion.Euler(0f, offset + step * i, 0f) * Vector3.forward;
            shot.Speed = s.Speed;
            shot.Range = s.Range;
            shot.Radius = NovaProjectileRadius;
            shot.Damage = s.Damage;
            shot.Knockback = s.Knockback;
            shot.Slow = s.Slow;
            shot.SlowSeconds = s.SlowSeconds;
            shot.Pierce = s.Pierce;
            shot.SpriteSize = s.SpriteSize;
            BrawlProjectile.Fire(shot);
        }

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Ring, c);
        fx.To = me.Position;
        fx.Radius = NovaRingRadius;
        BrawlFx.Emit(fx);
    }

    public static void Homing(BrawlCast c)
    {
        var s = c.Skill;
        var me = c.Caster;
        var count = Mathf.Max(1, s.Count);
        BrawlQuery.FoesWithin(me.Position, s.Range, me.Team, Temp);
        SortByDistance(Temp, me.Position);

        for (var i = 0; i < count; i++)
        {
            var shot = BrawlSkillEffects.NewShot(c);
            shot.Direction = Quaternion.Euler(0f, (i - (count - 1) * 0.5f) * HomingFanStep, 0f) * c.AimDir;
            shot.Homing = Temp.Count > 0 ? Temp[i % Temp.Count] : null;
            shot.HomingTurn = HomingTurnSpeed;
            shot.Speed = s.Speed;
            shot.Range = s.Range * HomingRangeFactor;
            shot.Radius = HomingProjectileRadius;
            shot.Damage = s.Damage;
            shot.SpriteSize = s.SpriteSize;
            BrawlProjectile.Fire(shot);
        }

        var fx = BrawlSkillEffects.NewFx(BrawlFxKind.Muzzle, c);
        fx.From = me.Center;
        fx.To = me.Center + c.AimDir;
        fx.Angle = (count - 1) * HomingFanStep;
        BrawlFx.Emit(fx);
    }

    private static void DashStep(BrawlCast c, Vector3 pos, Vector3 start, Vector3 dir, HashSet<BrawlFighter> struck)
    {
        var s = c.Skill;
        BrawlQuery.FoesWithin(pos, s.Radius, c.Caster.Team, Temp);
        for (var i = 0; i < Temp.Count; i++)
        {
            var f = Temp[i];
            if (!struck.Add(f)) continue;

            var rel = f.Position - start;
            rel.y = 0f;
            var lateral = rel - dir * Vector3.Dot(rel, dir);
            var knock = (dir + lateral.normalized).normalized;
            if (s.Damage > 0f) f.TakeDamage(BrawlSkillEffects.Hit(c, f, s.Damage, knock, s.Knockback));
            BrawlSkillEffects.Control(s, f);
        }
    }

    private static BrawlFighter ChainStart(BrawlCast c)
    {
        var me = c.Caster;
        var reach = c.Skill.Range + ChainReach;
        if (c.Target != null && c.Target.IsAlive && BrawlQuery.Planar(me.Position, c.Target.Position) <= reach)
            return c.Target;
        return BrawlQuery.NearestFoeTo(c.AimPoint, me.Team, reach);
    }

    private static BrawlFighter NextLink(BrawlFighter me, BrawlFighter last, float radius)
    {
        BrawlQuery.FoesWithin(last.Position, radius, me.Team, Temp);
        BrawlFighter best = null;
        var bestDistance = float.MaxValue;
        for (var i = 0; i < Temp.Count; i++)
        {
            var f = Temp[i];
            if (Linked.Contains(f)) continue;
            var d = BrawlQuery.Planar(last.Position, f.Position);
            if (d >= bestDistance) continue;
            bestDistance = d;
            best = f;
        }
        return best;
    }

    private static void SortByDistance(List<BrawlFighter> list, Vector3 origin)
    {
        for (var i = 1; i < list.Count; i++)
        {
            var item = list[i];
            var d = BrawlQuery.Planar(origin, item.Position);
            var j = i - 1;
            while (j >= 0 && BrawlQuery.Planar(origin, list[j].Position) > d)
            {
                list[j + 1] = list[j];
                j--;
            }
            list[j + 1] = item;
        }
    }
}

}
