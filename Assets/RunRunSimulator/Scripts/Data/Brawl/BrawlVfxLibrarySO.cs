using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "BrawlVfxLibrary", menuName = "MoriMonchi/Brawl/Vfx Library")]
public class BrawlVfxLibrarySO : ScriptableObject
{
    public static BrawlVfxLibrarySO Current { get; private set; }

    public static void Activate(BrawlVfxLibrarySO library) => Current = library;

    public static void Deactivate(BrawlVfxLibrarySO library)
    {
        if (Current == library) Current = null;
    }

    [Title("Materiales")]
    public Material SpriteMaterial;
    public Material ParticleMaterial;
    public Material ParticleAdditiveMaterial;
    public Material LineMaterial;

    [Title("Sprites")]
    public Sprite SparkSprite;

    [Title("Prefabs")]
    public GameObject HitFx;
    public GameObject KnockOutFx;
    public GameObject DustFx;

    [Title("Proyectiles")]
    [Min(0f)] public float ProjectileTrailTime = 0.25f;

    [Title("Lectura de equipo")]
    public Color FoeTint = new Color(1f, 0.22f, 0.18f);
    public float FoeWash = 0.7f;
    public float AllySaturation = 0.25f;
    public float AllyMinValue = 0.85f;
    public float AllySizeBoost = 1.2f;
    public Sprite GlowSprite;
}
}
