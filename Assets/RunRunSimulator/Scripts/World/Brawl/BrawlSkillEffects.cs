using UnityEngine;
namespace MoriMonchiSimulator
{

public static class BrawlSkillEffects
{
    public static void Execute(BrawlCast cast)
    {
        if (cast.Caster == null || cast.Skill == null) return;

        switch (cast.Skill.Family)
        {
            case BrawlSkillFamily.Dash:   BrawlSkillOffense.Dash(cast); break;
            case BrawlSkillFamily.Chain:  BrawlSkillOffense.Chain(cast); break;
            case BrawlSkillFamily.Cone:   BrawlSkillOffense.Cone(cast); break;
            case BrawlSkillFamily.Shot:   BrawlSkillOffense.Shot(cast); break;
            case BrawlSkillFamily.Nova:   BrawlSkillOffense.Nova(cast); break;
            case BrawlSkillFamily.Homing: BrawlSkillOffense.Homing(cast); break;
            case BrawlSkillFamily.Pull:   BrawlSkillSupport.Pull(cast); break;
            case BrawlSkillFamily.Zone:   BrawlSkillSupport.Zone(cast); break;
            case BrawlSkillFamily.Ward:   BrawlSkillSupport.Ward(cast); break;
            case BrawlSkillFamily.Mend:   BrawlSkillSupport.Mend(cast); break;
        }
    }

    internal static BrawlHit Hit(BrawlCast c, BrawlFighter victim, float amount, Vector3 knockDir, float knockback)
    {
        return new BrawlHit
        {
            Amount = amount,
            Source = c.Caster,
            Point = victim.Center,
            KnockDir = knockDir,
            Knockback = knockback,
            Theme = c.Theme,
            FromSkill = true,
        };
    }

    internal static void Control(BrawlSkillSO s, BrawlFighter victim)
    {
        if (s.Slow > 0f) victim.ApplySlow(s.Slow, s.SlowSeconds);
        if (s.StunSeconds > 0f) victim.ApplyStun(s.StunSeconds);
    }

    internal static BrawlShot NewShot(BrawlCast c)
    {
        var me = c.Caster;
        return new BrawlShot
        {
            Owner = me,
            Team = me.Team,
            Origin = me.Center,
            Direction = c.AimDir,
            Height = me.Center.y - me.Position.y,
            Theme = c.Theme,
            FromSkill = true,
        };
    }

    internal static BrawlFxEvent NewFx(BrawlFxKind kind, BrawlCast c)
    {
        return new BrawlFxEvent
        {
            Kind = kind,
            Theme = c.Theme,
            Team = c.Caster.Team,
            Source = c.Caster,
        };
    }

    internal static Vector3 PlanarDir(Vector3 from, Vector3 to)
    {
        var d = to - from;
        d.y = 0f;
        return d.sqrMagnitude > 0.0001f ? d.normalized : Vector3.zero;
    }
}

}
