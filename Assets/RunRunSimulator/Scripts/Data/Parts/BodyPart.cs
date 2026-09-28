using Sirenix.OdinInspector;
using Sirenix.Serialization;
using UnityEngine;
namespace MoriMonchiSimulator
{

public abstract class BodyPart : SerializedScriptableObject
{
    [HorizontalGroup("Header", Width = 65)]
    [PreviewField(55, ObjectFieldAlignment.Left), HideLabel]
    public Sprite Icon;

    [VerticalGroup("Header/Info"), LabelWidth(55)]
    [ReadOnly]
    public string ID;

    [VerticalGroup("Header/Info"), LabelWidth(55)]
    public string Name;

    [VerticalGroup("Header/Info"), LabelWidth(55)]
    [GUIColor(nameof(GetRarityColor))]
    public Rarity Rarity;

    [VerticalGroup("Header/Info"), LabelWidth(55)]
    public Tier Tier;

    [VerticalGroup("Header/Info"), LabelWidth(55)]
    [GUIColor(nameof(GetSetColor))]
    public PartSetSO Set;

    [BoxGroup("Stats"), LabelWidth(80), Range(0, 10)]
    public float HP     = 0f;
    [BoxGroup("Stats"), LabelWidth(80), Range(0, 10)]
    public float Attack = 0f;
    [BoxGroup("Stats"), LabelWidth(80), Range(0, 10)]
    public float Speed  = 0f;

    [BoxGroup("Combate")]
    [AssetsOnly]
    public AbilitySO Ability;

    public abstract PartRole GetPartRole();

    private Color GetRarityColor() => RarityColor(Rarity);
    private Color GetSetColor()    => Set != null ? Set.Color : Color.gray;

    public static Color RarityColor(Rarity rarity) => rarity switch
    {
        Rarity.Common    => Color.white,
        Rarity.Uncommon  => new Color(0.5f, 1f, 0.5f),
        Rarity.Rare      => new Color(0.4f, 0.65f, 1f),
        Rarity.Epic      => new Color(0.85f, 0.45f, 1f),
        Rarity.Legendary => new Color(1f, 0.75f, 0.2f),
        _                => Color.white
    };
}
}
