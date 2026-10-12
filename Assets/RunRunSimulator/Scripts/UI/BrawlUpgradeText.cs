using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public static class BrawlUpgradeText
{
    public static string Describe(BrawlUpgradeStep step, BrawlSkillFamily? family)
    {
        if (step == null || step.Mods == null) return "";

        var parts = new List<string>(step.Mods.Count);
        foreach (var mod in step.Mods)
            parts.Add(Loc.Tr(Key(mod.Stat, family), ValueText(mod)));

        return string.Join(" · ", parts);
    }

    private static string Key(BrawlUpgradeStat stat, BrawlSkillFamily? family)
    {
        string key = "ui.upgrade.stat." + stat.ToString().ToLowerInvariant();
        if (stat != BrawlUpgradeStat.Count || !family.HasValue) return key;

        return family.Value switch
        {
            BrawlSkillFamily.Chain => key + ".chain",
            BrawlSkillFamily.Nova  => key + ".nova",
            BrawlSkillFamily.Ward  => key + ".ward",
            _                      => key,
        };
    }

    private static string ValueText(BrawlUpgradeMod mod)
    {
        if (mod.Op == BrawlUpgradeOp.Multiply)
            return Signed(Mathf.Round((mod.Value - 1f) * 100f), "0") + " %";

        switch (mod.Stat)
        {
            case BrawlUpgradeStat.Duration:
            case BrawlUpgradeStat.SlowSeconds:
            case BrawlUpgradeStat.StunSeconds:
            case BrawlUpgradeStat.TauntSeconds:
                return Signed(mod.Value, "0.#") + " s";
            case BrawlUpgradeStat.Slow:
            case BrawlUpgradeStat.Haste:
            case BrawlUpgradeStat.DamageBoost:
                return Signed(mod.Value * 100f, "0") + " %";
            case BrawlUpgradeStat.Count:
            case BrawlUpgradeStat.Bounces:
                return Signed(mod.Value, "0");
            default:
                return Signed(mod.Value, "0.#");
        }
    }

    private static string Signed(float value, string format) =>
        (value < 0f ? "−" : "+") + Mathf.Abs(value).ToString(format);
}
}
