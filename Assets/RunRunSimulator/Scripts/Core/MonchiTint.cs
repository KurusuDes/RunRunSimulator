using UnityEngine;

namespace MoriMonchiSimulator
{
public static class MonchiTint
{
    private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
    private static readonly int Shade1ColorId = Shader.PropertyToID("_1st_ShadeColor");
    private static readonly int Shade2ColorId = Shader.PropertyToID("_2nd_ShadeColor");
    private static readonly int RimColorId = Shader.PropertyToID("_RimLightColor");

    public static Color ColorFor(string rendererName, CreatureDNA dna, Color wing, Color accent)
    {
        if (rendererName.Length >= 11 && rendererName.StartsWith("Deco_") && ColorUtility.TryParseHtmlString("#" + rendererName.Substring(5, 6), out var decoColor))
            return decoColor;
        if (rendererName.StartsWith("Wing"))
            return wing;
        if (rendererName.StartsWith("Horn") || rendererName.StartsWith("Back"))
            return accent;
        if (rendererName == "Teech")
            return Color.Lerp(Color.white, dna.BaseColor, 0.12f);
        return dna.BaseColor;
    }

    public static void Fill(MaterialPropertyBlock mpb, Color color)
    {
        var palette = ColorGenetics.BuildFurPalette(color, ColorGenetics.DeriveSecondary(color));
        mpb.SetColor(BaseColorId, palette.Base);
        mpb.SetColor(Shade1ColorId, palette.Shade1);
        mpb.SetColor(Shade2ColorId, palette.Shade2);
        mpb.SetColor(RimColorId, Color.Lerp(color, Color.white, 0.65f));
    }
}
}
