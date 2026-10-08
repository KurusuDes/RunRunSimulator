using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public static class BrawlSkillJudge
{
    private const float BoldLine = 0.5f;
    private const float ZoneBoldLine = 0.6f;
    private const float RelaxedBoldness = 0.6f;
    private const float PeelRange = 3f;
    private const float WeakFoeHp = 0.5f;
    private const float CrowdRadius = 3f;
    private const float BuffThreatRange = 8f;
    private const float NovaReach = 0.8f;
    private const float WardHpBold = 0.8f;
    private const float WardHpCautious = 0.9f;
    private const float WardSelfHurtSeconds = 1.2f;
    private const float WardNearFoe = 4f;
    private const float WardAllyHurtSeconds = 1.5f;
    private const float AnyHp = 1.01f;

    private static readonly List<BrawlFighter> buffer = new();

    public static bool Want(BrawlFighter me, BrawlBrain brain, int slot, BrawlTuningSO tuning, out BrawlFighter target, out Vector3 aim)
    {
        target = null;
        aim = me.Position;
        var skill = me.Caster.Skill(slot);
        if (skill == null) return false;
        float b = brain.Impatient(slot) ? Mathf.Max(brain.Boldness, RelaxedBoldness) : brain.Boldness;
        switch (skill.Family)
        {
            case BrawlSkillFamily.Mend:
                return WantMend(me, brain, skill, tuning, out target, out aim);
            case BrawlSkillFamily.Ward:
                return WantWard(me, brain, skill, tuning, out target, out aim);
            case BrawlSkillFamily.Zone:
                return WantZone(me, brain, skill, b, tuning, out target, out aim);
            case BrawlSkillFamily.Pull:
                return WantControl(me, skill, b, out target, out aim);
            case BrawlSkillFamily.Cone:
                return skill.Role == BrawlSkillRole.Control
                    ? WantControl(me, skill, b, out target, out aim)
                    : WantCone(me, skill, b, out target, out aim);
            case BrawlSkillFamily.Nova:
                return WantNova(me, skill, b, out target, out aim);
            default:
                return skill.Role == BrawlSkillRole.Control
                    ? WantControl(me, skill, b, out target, out aim)
                    : WantSingle(me, brain, skill, b, out target, out aim);
        }
    }

    private static bool WantSingle(BrawlFighter me, BrawlBrain brain, BrawlSkillSO skill, float b, out BrawlFighter target, out Vector3 aim)
    {
        aim = me.Position;
        target = ReachableFoe(me, brain, skill.Range);
        if (target == null) return false;
        aim = target.Position;
        if (b < BoldLine && target.Hp01 >= WeakFoeHp && BrawlQuery.FoesWithin(target.Position, CrowdRadius, me.Team) < 2)
            return false;
        bool straight = skill.Family == BrawlSkillFamily.Shot || skill.Family == BrawlSkillFamily.Dash;
        if (straight && skill.Bounces <= 0 && !BrawlQuery.HasLineOfSight(me.Position, target.Position))
            return false;
        return true;
    }

    private static bool WantCone(BrawlFighter me, BrawlSkillSO skill, float b, out BrawlFighter target, out Vector3 aim)
    {
        aim = me.Position;
        target = null;
        int need = b >= BoldLine ? 1 : 2;
        BrawlQuery.FoesWithin(me.Position, skill.Range, me.Team, buffer);
        int bestCount = 0;
        float bestDistance = float.MaxValue;
        for (int i = 0; i < buffer.Count; i++)
        {
            var candidate = buffer[i];
            Vector3 dir = candidate.Position - me.Position;
            int count = 0;
            for (int j = 0; j < buffer.Count; j++)
                if (BrawlQuery.InCone(me.Position, dir, skill.Range, skill.Angle * 0.5f, buffer[j])) count++;
            float distance = BrawlQuery.Planar(me.Position, candidate.Position);
            if (count > bestCount || (count == bestCount && count > 0 && distance < bestDistance))
            {
                bestCount = count;
                bestDistance = distance;
                target = candidate;
            }
        }
        if (target == null || bestCount < need) return false;
        aim = target.Position;
        return true;
    }

    private static bool WantNova(BrawlFighter me, BrawlSkillSO skill, float b, out BrawlFighter target, out Vector3 aim)
    {
        aim = me.Position;
        target = null;
        int need = b >= BoldLine ? 1 : 2;
        int count = BrawlQuery.FoesWithin(me.Position, skill.Range * NovaReach, me.Team, buffer);
        if (count < need) return false;
        target = Nearest(me.Position, buffer);
        if (target != null) aim = target.Position;
        return true;
    }

    private static bool WantControl(BrawlFighter me, BrawlSkillSO skill, float b, out BrawlFighter target, out Vector3 aim)
    {
        aim = me.Position;
        float reach = skill.Family == BrawlSkillFamily.Pull ? skill.Radius : skill.Range;
        target = BrawlQuery.NearestFoe(me, reach);
        if (target == null) return false;
        if (b < BoldLine && !Peel(me)) return false;
        aim = target.Position;
        return true;
    }

    private static bool WantZone(BrawlFighter me, BrawlBrain brain, BrawlSkillSO skill, float b, BrawlTuningSO tuning, out BrawlFighter target, out Vector3 aim)
    {
        target = null;
        aim = me.Position;
        bool foeCentered = skill.Target == BrawlSkillTarget.Enemy || skill.Target == BrawlSkillTarget.EnemyCluster;
        if (!foeCentered && skill.Heal > 0f)
            return WantMend(me, brain, skill, tuning, out target, out aim);
        int need = b >= ZoneBoldLine ? 1 : 2;
        if (!foeCentered)
            return BrawlQuery.FoesWithin(me.Position, skill.Radius, me.Team) >= need;
        Vector3 point = BrawlQuery.FoeClusterPoint(me, skill.Radius, skill.Range, out int count);
        bool peeled = skill.Role == BrawlSkillRole.Control && count >= 1 && Peel(me);
        if (count < need && !peeled) return false;
        target = BrawlQuery.NearestFoeTo(point, me.Team, skill.Radius + 1f);
        aim = point;
        return true;
    }

    private static bool WantMend(BrawlFighter me, BrawlBrain brain, BrawlSkillSO skill, BrawlTuningSO tuning, out BrawlFighter target, out Vector3 aim)
    {
        target = null;
        aim = me.Position;
        float threshold = Mathf.Lerp(tuning.HealThreshold.x, tuning.HealThreshold.y, brain.Sociability);
        bool buffOnly = skill.Heal <= 0f;
        if (skill.Target == BrawlSkillTarget.LowestAlly)
        {
            var ally = BrawlQuery.LowestAlly(me, skill.Range, false, threshold);
            if (ally == null && buffOnly) ally = PressedAlly(me, skill.Range);
            if (ally == null) return false;
            target = ally;
            aim = ally.Position;
            return true;
        }
        BrawlQuery.AlliesWithin(me.Position, skill.Radius, me.Team, buffer);
        BrawlFighter weakest = null;
        float weakestHp = threshold;
        if (me.Hp01 < weakestHp)
        {
            weakest = me;
            weakestHp = me.Hp01;
        }
        bool company = false;
        for (int i = 0; i < buffer.Count; i++)
        {
            var ally = buffer[i];
            if (ally == me || !ally.IsAlive) continue;
            company = true;
            if (ally.Hp01 < weakestHp)
            {
                weakest = ally;
                weakestHp = ally.Hp01;
            }
        }
        if (weakest != null)
        {
            aim = weakest.Position;
            return true;
        }
        return buffOnly && company && BrawlQuery.NearestFoe(me, BuffThreatRange) != null;
    }

    private static bool WantWard(BrawlFighter me, BrawlBrain brain, BrawlSkillSO skill, BrawlTuningSO tuning, out BrawlFighter target, out Vector3 aim)
    {
        target = null;
        aim = me.Position;
        if (skill.Target == BrawlSkillTarget.LowestAlly)
        {
            float threshold = Mathf.Lerp(tuning.HealThreshold.x, tuning.HealThreshold.y, brain.Sociability);
            BrawlQuery.AlliesWithin(me.Position, skill.Range, me.Team, buffer);
            if (!buffer.Contains(me)) buffer.Add(me);
            BrawlFighter best = null;
            float bestHp = threshold;
            for (int i = 0; i < buffer.Count; i++)
            {
                var ally = buffer[i];
                if (!ally.IsAlive || ally.Hp01 >= bestHp) continue;
                if (Time.time - ally.LastHurtAt > WardAllyHurtSeconds) continue;
                best = ally;
                bestHp = ally.Hp01;
            }
            if (best == null) return false;
            target = best;
            aim = best.Position;
            return true;
        }
        float limit = brain.Boldness >= BoldLine ? WardHpBold : WardHpCautious;
        if (me.Hp01 >= limit) return false;
        return Time.time - me.LastHurtAt < WardSelfHurtSeconds || BrawlQuery.NearestFoe(me, WardNearFoe) != null;
    }

    private static BrawlFighter ReachableFoe(BrawlFighter me, BrawlBrain brain, float reach)
    {
        var foe = brain.Target;
        if (foe == null || !foe.IsAlive || !BrawlQuery.AreFoes(me, foe) || BrawlQuery.Planar(me.Position, foe.Position) > reach + foe.Radius)
            foe = BrawlQuery.NearestFoe(me, reach + 1f);
        if (foe == null || BrawlQuery.Planar(me.Position, foe.Position) > reach + foe.Radius) return null;
        return foe;
    }

    private static bool Peel(BrawlFighter me)
    {
        if (BrawlQuery.NearestFoe(me, PeelRange) != null) return true;
        var weakest = BrawlQuery.LowestAlly(me, float.PositiveInfinity, false, AnyHp);
        return weakest != null && BrawlQuery.NearestFoeTo(weakest.Position, me.Team, PeelRange) != null;
    }

    private static BrawlFighter PressedAlly(BrawlFighter me, float range)
    {
        BrawlQuery.AlliesWithin(me.Position, range, me.Team, buffer);
        BrawlFighter best = null;
        float bestHp = float.MaxValue;
        for (int i = 0; i < buffer.Count; i++)
        {
            var ally = buffer[i];
            if (ally == me || !ally.IsAlive || ally.Hp01 >= bestHp) continue;
            if (BrawlQuery.NearestFoeTo(ally.Position, me.Team, BuffThreatRange) == null) continue;
            best = ally;
            bestHp = ally.Hp01;
        }
        return best;
    }

    private static BrawlFighter Nearest(Vector3 point, List<BrawlFighter> fighters)
    {
        BrawlFighter best = null;
        float bestDistance = float.MaxValue;
        for (int i = 0; i < fighters.Count; i++)
        {
            float distance = BrawlQuery.Planar(point, fighters[i].Position);
            if (distance >= bestDistance) continue;
            best = fighters[i];
            bestDistance = distance;
        }
        return best;
    }
}

}
