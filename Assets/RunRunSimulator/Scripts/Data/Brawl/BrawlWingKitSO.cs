using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "WingKit", menuName = "MoriMonchi/Brawl/Wing Kit")]
public class BrawlWingKitSO : ScriptableObject
{
    [Title("Identidad")]
    public string PartId = "";
    public string Title = "";
    [TextArea] public string Description = "";
    public Sprite IconOverride;
    public Color ColorOverride = new Color(1f, 1f, 1f, 0f);
    public BrawlSignature Signature;

    [Title("Movimiento")]
    public BrawlLocomotion Locomotion = BrawlLocomotion.Ground;
    [Min(0f)] public float MoveSpeed = 4f;

    [Title("Ataque básico")]
    public BrawlAttackKind Attack = BrawlAttackKind.Melee;
    [Min(0f)] public float Range = 5f;
    [Min(0f)] public float Damage = 600f;
    [Min(0f)] public float Windup = 0.15f;
    [Min(0.05f)] public float Reload = 1.2f;
    [Min(1)] public int Count = 1;
    [Min(0f)] public float Spread = 0f;
    [Range(0f, 360f)] public float Angle = 100f;
    [Min(0f)] public float ProjectileSpeed = 18f;
    [Min(0f)] public float HitRadius = 0.45f;
    [Min(0f)] public float Knockback = 0f;
    [Range(0f, 0.9f)] public float Slow = 0f;
    [Min(0f)] public float SlowSeconds = 0f;
    [Min(0f)] public float SpriteSize = 0.45f;
    public string AttackAnim = "Fire";

    [Title("Curación con el básico")]
    [Min(0f)] public float AllyHeal = 0f;
    [Range(0f, 1f)] public float HealBelow = 0.6f;

    [Title("Movilidad")]
    public BrawlMobilityKind Mobility = BrawlMobilityKind.Leap;
    [Min(0f)] public float MobilityDistance = 5f;
    [Min(0.05f)] public float MobilitySeconds = 0.4f;
    [Min(0f)] public float MobilityCooldown = 7f;
    [Min(0f)] public float MobilityDamage = 0f;
}
}
