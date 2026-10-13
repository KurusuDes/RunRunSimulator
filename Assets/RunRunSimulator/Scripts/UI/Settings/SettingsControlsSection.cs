using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class SettingsControlsSection : ISettingsSection
{
    private static readonly int[] FovOptions = { 0, 60, 70, 80, 90, 100 };

    public string TitleKey => "ui.settings.section.controls";

    public void Build(VisualElement content, GameSettings draft)
    {
        SettingsRows.AddHeader(content, TitleKey);
        SettingsRows.AddSlider(content, "ui.settings.controls.sensitivity", 0.25f, 3f, 0.05f, draft.LookSensitivity,
            SettingsRows.Percent, v => draft.LookSensitivity = v);
        SettingsRows.AddToggle(content, "ui.settings.controls.invert", draft.InvertY, v => draft.InvertY = v);
        BuildFieldOfView(content, draft);
    }

    public void ResetToDefaults(GameSettings draft)
    {
        var defaults = new GameSettings();
        draft.LookSensitivity = defaults.LookSensitivity;
        draft.InvertY         = defaults.InvertY;
        draft.FieldOfView     = defaults.FieldOfView;
        draft.CameraBob       = defaults.CameraBob;
    }

    private static void BuildFieldOfView(VisualElement content, GameSettings draft)
    {
        var names = new List<string>(FovOptions.Length);
        foreach (int fov in FovOptions)
            names.Add(fov == 0 ? Loc.Tr("ui.settings.controls.fov.default") : fov.ToString());

        SettingsRows.AddDropdown(content, "ui.settings.controls.fov", names, NearestFov(draft.FieldOfView),
            i => draft.FieldOfView = FovOptions[i]);
    }

    private static int NearestFov(float value)
    {
        int best = 0;
        float bestDistance = float.MaxValue;
        for (int i = 0; i < FovOptions.Length; i++)
        {
            float distance = Mathf.Abs(FovOptions[i] - value);
            if (distance < bestDistance) { bestDistance = distance; best = i; }
        }
        return best;
    }
}
}
