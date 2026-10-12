using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "ToyTuning", menuName = "RunRunSimulator/World/Toy Tuning")]
public class ToyTuningSO : ScriptableObject
{
    [Title("Enganche")]
    [Min(0f)] public float NoticeRadius = 8f;
    [Min(0f)] public float EngageChancePerSecond = 0.25f;
    [Range(0f, 100f)] public float MinEnergy = 30f;
    [Min(0f)] public float Cooldown = 12f;
    [Min(0f)] public float AffectPerSecond = 1.5f;

    [Title("Pelota")]
    [Min(0f)] public float KickRange = 0.9f;
    [Min(0f)] public float KickForce = 2.5f;
    [Min(0f)] public float KickUp = 0.6f;
    [Min(1)] public int KicksMin = 2;
    [Min(1)] public int KicksMax = 5;

    [Title("Llevar en la boca")]
    [Min(0f)] public float CarryDurationMin = 5f;
    [Min(0f)] public float CarryDurationMax = 9f;
    [Min(0.1f)] public float CarrySpeedMultiplier = 1.4f;
    [Min(0.5f)] public float WanderRadius = 5f;
    public Vector3 MouthOffset = new Vector3(0f, 0.55f, 0.45f);

    [Title("Robo entre monchis")]
    [Min(0f)] public float StealRange = 0.8f;
    [Range(0f, 1f)] public float StealChance = 0.5f;
    [Min(0f)] public float ChaseDuration = 5f;
    [Min(0.1f)] public float ChaseSpeedMultiplier = 1.5f;

    [Title("Robo al jugador")]
    [Min(0f)] public float SnatchRange = 1.3f;
    [Min(0f)] public float SnatchChancePerSecond = 0.08f;
}
}
