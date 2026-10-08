using UnityEngine;

namespace MoriMonchiSimulator
{

public static class BrawlTeamLook
{
    public static bool IsAlly(ExpeditionTeam team) => team == ExpeditionTeam.Player;

    public static Color Wash(Color color, ExpeditionTeam team)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null) return color;

        switch (team)
        {
            case ExpeditionTeam.Rival:
            {
                float alpha = color.a;
                Color washed = Color.Lerp(color, lib.FoeTint, lib.FoeWash);
                washed.a = alpha;
                return washed;
            }
            case ExpeditionTeam.Player:
            {
                Color.RGBToHSV(color, out float h, out float s, out float v);
                Color boosted = Color.HSVToRGB(h, Mathf.Min(1f, s * (1f + lib.AllySaturation)), Mathf.Max(v, lib.AllyMinValue));
                boosted.a = color.a;
                return boosted;
            }
            default:
                return color;
        }
    }

    public static BrawlTheme Wash(BrawlTheme theme, ExpeditionTeam team)
    {
        theme.Color = Wash(theme.Color, team);
        return theme;
    }

    public static float Size(ExpeditionTeam team)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null) return 1f;
        return team == ExpeditionTeam.Player ? lib.AllySizeBoost : 1f;
    }
}
}
