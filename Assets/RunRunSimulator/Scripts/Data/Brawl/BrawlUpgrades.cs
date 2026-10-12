using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public static class BrawlUpgrades
{
    public const int MaxSteps = 3;

    public static int MaxLevel(IReadOnlyList<BrawlUpgradeStep> steps) => 1 + Mathf.Min(steps?.Count ?? 0, MaxSteps);

    public static BrawlSkillSO Upgraded(BrawlSkillSO source, int level, List<Object> owned)
    {
        if (source == null || level <= 1 || source.Upgrades == null || source.Upgrades.Count == 0) return source;
        var copy = Object.Instantiate(source);
        copy.name = source.name;
        owned.Add(copy);
        int applied = Mathf.Min(level - 1, source.Upgrades.Count, MaxSteps);
        for (int i = 0; i < applied; i++)
        {
            var step = source.Upgrades[i];
            if (step == null || step.Mods == null) continue;
            for (int j = 0; j < step.Mods.Count; j++) Apply(copy, step.Mods[j]);
        }
        return copy;
    }

    public static BrawlWingKitSO Upgraded(BrawlWingKitSO source, int level, List<Object> owned)
    {
        if (source == null || level <= 1 || source.Upgrades == null || source.Upgrades.Count == 0) return source;
        var copy = Object.Instantiate(source);
        copy.name = source.name;
        owned.Add(copy);
        int applied = Mathf.Min(level - 1, source.Upgrades.Count, MaxSteps);
        for (int i = 0; i < applied; i++)
        {
            var step = source.Upgrades[i];
            if (step == null || step.Mods == null) continue;
            for (int j = 0; j < step.Mods.Count; j++) Apply(copy, step.Mods[j]);
        }
        return copy;
    }

    public static void Body(IReadOnlyList<BrawlUpgradeStep> steps, int level, out float hpMul, out float speedMul)
    {
        hpMul = 1f;
        speedMul = 1f;
        if (steps == null || level <= 1) return;
        int applied = Mathf.Min(level - 1, steps.Count, MaxSteps);
        for (int i = 0; i < applied; i++)
        {
            var step = steps[i];
            if (step == null || step.Mods == null) continue;
            for (int j = 0; j < step.Mods.Count; j++)
            {
                var mod = step.Mods[j];
                switch (mod.Stat)
                {
                    case BrawlUpgradeStat.Hp: hpMul = Combine(hpMul, mod); break;
                    case BrawlUpgradeStat.MoveSpeed: speedMul = Combine(speedMul, mod); break;
                }
            }
        }
    }

    private static float Combine(float current, BrawlUpgradeMod mod) =>
        Mathf.Max(0f, mod.Op == BrawlUpgradeOp.Add ? current + mod.Value : current * mod.Value);

    private static int CombineInt(int current, BrawlUpgradeMod mod) =>
        Mathf.RoundToInt(mod.Op == BrawlUpgradeOp.Add ? current + mod.Value : current * mod.Value);

    private static void Apply(BrawlSkillSO s, BrawlUpgradeMod mod)
    {
        switch (mod.Stat)
        {
            case BrawlUpgradeStat.Damage: s.Damage = Combine(s.Damage, mod); break;
            case BrawlUpgradeStat.Heal: s.Heal = Combine(s.Heal, mod); break;
            case BrawlUpgradeStat.Shield: s.Shield = Combine(s.Shield, mod); break;
            case BrawlUpgradeStat.Duration: s.Duration = Combine(s.Duration, mod); break;
            case BrawlUpgradeStat.Cooldown: s.Cooldown = Combine(s.Cooldown, mod); break;
            case BrawlUpgradeStat.Range: s.Range = Combine(s.Range, mod); break;
            case BrawlUpgradeStat.Radius: s.Radius = Combine(s.Radius, mod); break;
            case BrawlUpgradeStat.Angle: s.Angle = Mathf.Min(Combine(s.Angle, mod), 360f); break;
            case BrawlUpgradeStat.Count: s.Count = Mathf.Max(1, CombineInt(s.Count, mod)); break;
            case BrawlUpgradeStat.Knockback: s.Knockback = Combine(s.Knockback, mod); break;
            case BrawlUpgradeStat.Slow: s.Slow = Mathf.Clamp(Combine(s.Slow, mod), 0f, 0.9f); break;
            case BrawlUpgradeStat.SlowSeconds: s.SlowSeconds = Combine(s.SlowSeconds, mod); break;
            case BrawlUpgradeStat.StunSeconds: s.StunSeconds = Combine(s.StunSeconds, mod); break;
            case BrawlUpgradeStat.Haste: s.Haste = Combine(s.Haste, mod); break;
            case BrawlUpgradeStat.DamageBoost: s.DamageBoost = Combine(s.DamageBoost, mod); break;
            case BrawlUpgradeStat.Thorns: s.Thorns = Combine(s.Thorns, mod); break;
            case BrawlUpgradeStat.TauntSeconds: s.TauntSeconds = Combine(s.TauntSeconds, mod); break;
            case BrawlUpgradeStat.Bounces: s.Bounces = Mathf.Max(0, CombineInt(s.Bounces, mod)); break;
            case BrawlUpgradeStat.Pierce:
                if (mod.Op == BrawlUpgradeOp.Add && mod.Value > 0f) s.Pierce = true;
                break;
            case BrawlUpgradeStat.ExplodeRadius: s.ExplodeRadius = Combine(s.ExplodeRadius, mod); break;
        }
    }

    private static void Apply(BrawlWingKitSO w, BrawlUpgradeMod mod)
    {
        switch (mod.Stat)
        {
            case BrawlUpgradeStat.Damage: w.Damage = Combine(w.Damage, mod); break;
            case BrawlUpgradeStat.Range: w.Range = Combine(w.Range, mod); break;
            case BrawlUpgradeStat.Angle: w.Angle = Mathf.Min(Combine(w.Angle, mod), 360f); break;
            case BrawlUpgradeStat.Count: w.Count = Mathf.Max(1, CombineInt(w.Count, mod)); break;
            case BrawlUpgradeStat.Knockback: w.Knockback = Combine(w.Knockback, mod); break;
            case BrawlUpgradeStat.Slow: w.Slow = Mathf.Clamp(Combine(w.Slow, mod), 0f, 0.9f); break;
            case BrawlUpgradeStat.SlowSeconds: w.SlowSeconds = Combine(w.SlowSeconds, mod); break;
            case BrawlUpgradeStat.AllyHeal: w.AllyHeal = Combine(w.AllyHeal, mod); break;
            case BrawlUpgradeStat.Reload: w.Reload = Mathf.Max(0.05f, Combine(w.Reload, mod)); break;
            case BrawlUpgradeStat.HitRadius: w.HitRadius = Combine(w.HitRadius, mod); break;
            case BrawlUpgradeStat.MoveSpeed: w.MoveSpeed = Combine(w.MoveSpeed, mod); break;
            case BrawlUpgradeStat.MobilityCooldown: w.MobilityCooldown = Combine(w.MobilityCooldown, mod); break;
            case BrawlUpgradeStat.MobilityDamage: w.MobilityDamage = Combine(w.MobilityDamage, mod); break;
            case BrawlUpgradeStat.MobilityDistance: w.MobilityDistance = Combine(w.MobilityDistance, mod); break;
        }
    }
}
}
