using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "BrawlRunRules", menuName = "MoriMonchi/Brawl/Run Rules")]
public class BrawlRunRulesSO : ScriptableObject
{
    public static BrawlRunRulesSO Current { get; private set; }

    public static void Activate(BrawlRunRulesSO rules) => Current = rules;

    public static void Deactivate(BrawlRunRulesSO rules)
    {
        if (Current == rules) Current = null;
    }

    [Title("Bajada")]
    [Min(0)] public int DescentCost = 10;
    [Min(1)] public int MineritaPerLoot = 5;
    [Range(0f, 1f)] public float LossFraction = 0.5f;
    [Range(0f, 1f)] public float HealAfterCombat = 0.4f;

    [Title("Tramos")]
    [Min(1)] public int MinRooms = 2;
    [Min(1)] public int MaxRooms = 5;
    [Min(1)] public int FirstTramoMaxRivals = 2;
    [Min(1)] public int HardFromDepth = 3;

    [Title("Rivales")]
    [Min(0.05f)] public float RivalPowerBase = 0.85f;
    [Min(0f)] public float RivalPowerPerDepth = 0.1f;
    [Min(0.05f)] public float RivalPowerMax = 1.5f;
    [Min(0)] public int MaterialPerRival = 1;

    [Title("Salas de prueba")]
    [Range(0f, 1f)] public float DummiesChance = 0.15f;
    [Range(0f, 1f)] public float MineralsChance = 0.15f;
    [Min(1f)] public float TrialSeconds = 20f;
    [Min(0.05f)] public float DummyPower = 2f;
    [Range(0f, 1f)] public float DummyHealFraction = 0.3f;
    [Min(1f)] public float MineralDamagePerMaterial = 4000f;
    [Min(0)] public int MineralBaseLoot = 1;
    [Min(0f)] public float TrialStartGrace = 6f;

    [Title("Ritmo")]
    [Min(0f)] public float LootBeatSeconds = 1.6f;
    [Min(0f)] public float VeilCoverSeconds = 1.1f;

    public float RivalPower(int depth) => Mathf.Min(RivalPowerMax, RivalPowerBase + RivalPowerPerDepth * Mathf.Max(0, depth - 1));
}
}
