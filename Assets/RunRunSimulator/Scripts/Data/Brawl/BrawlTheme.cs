using UnityEngine;
namespace MoriMonchiSimulator
{

[System.Serializable]
public struct BrawlTheme
{
    public Sprite Icon;
    public Color Color;
    public string Label;
    public BrawlSignature Signature;

    public static BrawlTheme Resolve(BodyPart part, Sprite iconOverride, Color colorOverride, BrawlSignature signature = BrawlSignature.None)
    {
        bool hasPart = part != null;
        Sprite icon = hasPart && part.Icon != null ? part.Icon : iconOverride;

        Color color;
        if (colorOverride.a > 0.01f) color = colorOverride;
        else if (hasPart && part.Set != null) color = part.Set.Color;
        else color = Color.white;
        color.a = 1f;

        return new BrawlTheme
        {
            Icon = icon,
            Color = color,
            Label = hasPart ? part.Name : "",
            Signature = signature
        };
    }
}
}
