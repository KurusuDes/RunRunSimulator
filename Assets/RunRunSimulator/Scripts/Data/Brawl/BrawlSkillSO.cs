using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "Skill", menuName = "MoriMonchi/Brawl/Skill")]
public class BrawlSkillSO : ScriptableObject
{
    [Title("Identidad")]
    public string PartId = "";
    public ClashSlot Slot = ClashSlot.Horn;
    public string Title = "";
    [TextArea] public string Description = "";
    public Sprite IconOverride;
    public Color ColorOverride = new Color(1f, 1f, 1f, 0f);
    public BrawlSignature Signature;

    [Title("Clasificación")]
    public BrawlSkillFamily Family = BrawlSkillFamily.Shot;
    public BrawlSkillRole Role = BrawlSkillRole.Offense;
    public BrawlSkillTarget Target = BrawlSkillTarget.Enemy;

    [Title("Lanzamiento")]
    [Min(0f)] public float Windup = 0.6f;
    [Min(0f)] public float Cooldown = 8f;
    [Range(0f, 1f)] public float FirstDelay = 0.5f;
    public bool RootWhileCasting = true;
    public bool TracksTarget = true;
    public string CastAnim = "Roar";
    public string FireAnim = "Fire";

    [Title("Alcance y área")]
    [Min(0f)] public float Range = 6f;
    [Min(0f)] public float Radius = 2f;
    [Range(0f, 360f)] public float Angle = 90f;

    [Title("Efecto")]
    [Min(0f)] public float Damage = 0f;
    [Min(0f)] public float Heal = 0f;
    [Min(0f)] public float Shield = 0f;
    [Min(0f)] public float Duration = 0f;
    [Min(0f)] public float Delay = 0f;
    [Min(0.05f)] public float TickSeconds = 0.5f;
    [Min(1)] public int Count = 1;
    [Min(0f)] public float Speed = 14f;
    [Min(0f)] public float Knockback = 0f;

    [Title("Estados")]
    [Range(0f, 0.9f)] public float Slow = 0f;
    [Min(0f)] public float SlowSeconds = 0f;
    [Min(0f)] public float StunSeconds = 0f;
    [Min(0f)] public float Haste = 0f;
    [Min(0f)] public float DamageBoost = 0f;
    [Min(0f)] public float Thorns = 0f;
    [Min(0f)] public float TauntSeconds = 0f;

    [Title("Proyectil y visual")]
    [Min(0)] public int Bounces = 0;
    public bool Pierce = false;
    [Min(0f)] public float ExplodeRadius = 0f;
    [Min(0f)] public float SpriteSize = 0.8f;
    public bool FollowCaster = false;
}
}
