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

    [Title("Traer")]
    [Min(0f)] public float FetchEngageChancePerSecond = 2f;
    [Min(0f)] public float FetchAffect = 8f;
    [Min(0f)] public float FetchDropRange = 1.4f;

    [Title("Tironeo con el jugador")]
    [Min(0f)] public float TugRange = 1.6f;
    [Min(0f)] public float TugPressPower = 0.12f;
    [Min(0f)] public float TugPullPerSecond = 0.3f;
    [Range(0f, 1f)] public float TugBoldnessPull = 0.25f;
    [Min(0f)] public float TugMaxSeconds = 8f;
    [Min(0f)] public float TugWinAffect = 10f;

    [Title("Pilla-pilla")]
    [Min(0f)] public float TeaseDuration = 8f;
    [Min(0f)] public float TeaseKeepAway = 3f;
    [Min(0.1f)] public float TeaseSpeedMultiplier = 1.5f;
    [Min(0f)] public float CaughtAffect = 6f;

    [Title("Cuerda entre monchis")]
    [Range(0f, 1f)] public float RopeTugChance = 0.7f;
    [Min(0f)] public float RopeTugMin = 2f;
    [Min(0f)] public float RopeTugMax = 5f;
    [Min(0f)] public float RopeTugAffect = 4f;

    [Title("Peluche")]
    [Min(0f)] public float HugChancePerSecond = 0.5f;
    [Min(0f)] public float HugDurationMin = 6f;
    [Min(0f)] public float HugDurationMax = 10f;
    [Min(0f)] public float HugAffectPerSecond = 3f;

    [Title("Burbujas")]
    [Min(0f)] public float PopRange = 0.9f;
    [Min(1)] public int PopsMax = 4;
    [Min(0f)] public float PopAffect = 2f;
}
}
