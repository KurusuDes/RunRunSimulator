using UnityEngine;

namespace MoriMonchiSimulator
{

public static class BrawlProjectileTrail
{
    private const float CometTime = 0.5f;
    private const float CometWidthScale = 1.6f;

    private static readonly Color[] CometPalette =
    {
        new Color(1f, 0.95f, 0.5f),
        new Color(1f, 0.55f, 0.15f),
        new Color(0.9f, 0.15f, 0.1f),
        new Color(0.9f, 0.15f, 0.1f)
    };

    private static readonly Gradient gradient = new();
    private static readonly GradientColorKey[] plainColors = new GradientColorKey[2];
    private static readonly GradientAlphaKey[] plainAlphas = new GradientAlphaKey[2];
    private static readonly GradientColorKey[] cometColors = new GradientColorKey[4];
    private static readonly GradientAlphaKey[] cometAlphas = new GradientAlphaKey[4];

    public static void Apply(TrailRenderer trail, BrawlShot shot, float plainTime, float width, Color color)
    {
        trail.endWidth = 0f;
        if (shot.Theme.Signature == BrawlSignature.Comet) ApplyComet(trail, shot.Team, width);
        else ApplyPlain(trail, plainTime, width, color);
    }

    private static void ApplyPlain(TrailRenderer trail, float time, float width, Color color)
    {
        trail.time = time;
        trail.startWidth = width;

        plainColors[0] = new GradientColorKey(color, 0f);
        plainColors[1] = new GradientColorKey(color, 1f);
        plainAlphas[0] = new GradientAlphaKey(color.a, 0f);
        plainAlphas[1] = new GradientAlphaKey(0f, 1f);
        gradient.SetKeys(plainColors, plainAlphas);
        trail.colorGradient = gradient;
    }

    private static void ApplyComet(TrailRenderer trail, ExpeditionTeam team, float width)
    {
        trail.time = CometTime;
        trail.startWidth = width * CometWidthScale;

        int last = CometPalette.Length - 1;
        for (int i = 0; i <= last; i++)
        {
            Color c = BrawlTeamLook.Wash(CometPalette[i], team);
            float at = i / (float)last;
            cometColors[i] = new GradientColorKey(c, at);
            cometAlphas[i] = new GradientAlphaKey(i == last ? 0f : c.a, at);
        }
        gradient.SetKeys(cometColors, cometAlphas);
        trail.colorGradient = gradient;
    }
}
}
