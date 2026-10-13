using System;
using System.Collections.Generic;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class SettingsInterfaceSection : ISettingsSection
{
    private static readonly NameTagMode[] Modes = { NameTagMode.Always, NameTagMode.WhenLooked, NameTagMode.Never };

    private static readonly string[] ModeKeys =
    {
        "ui.settings.interface.nametags.always",
        "ui.settings.interface.nametags.looked",
        "ui.settings.interface.nametags.never"
    };

    public string TitleKey => "ui.settings.section.interface";

    public void Build(VisualElement content, GameSettings draft)
    {
        SettingsRows.AddHeader(content, TitleKey);

        var names = new List<string>(ModeKeys.Length);
        foreach (var key in ModeKeys) names.Add(Loc.Tr(key));
        int index = Math.Max(0, Array.IndexOf(Modes, draft.NameTags));

        SettingsRows.AddDropdown(content, "ui.settings.interface.nametags", names, index, i => draft.NameTags = Modes[i]);
        SettingsRows.AddSlider(content, "ui.settings.interface.hudscale", 0.75f, 1.5f, 0.05f, draft.HudScale,
            SettingsRows.Percent, v => draft.HudScale = v);
        SettingsRows.AddToggle(content, "ui.settings.interface.keyhints", draft.ShowKeyHints, v => draft.ShowKeyHints = v);
    }

    public void ResetToDefaults(GameSettings draft)
    {
        var defaults = new GameSettings();
        draft.NameTags     = defaults.NameTags;
        draft.HudScale     = defaults.HudScale;
        draft.ShowKeyHints = defaults.ShowKeyHints;
    }
}
}
