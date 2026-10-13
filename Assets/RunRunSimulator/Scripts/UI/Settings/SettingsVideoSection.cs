using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class SettingsVideoSection : ISettingsSection
{
    private static readonly FullScreenMode[] Modes =
        { FullScreenMode.Windowed, FullScreenMode.ExclusiveFullScreen, FullScreenMode.FullScreenWindow };

    private static readonly string[] ModeKeys =
    {
        "ui.settings.video.mode.windowed",
        "ui.settings.video.mode.fullscreen",
        "ui.settings.video.mode.borderless"
    };

    private static readonly int[] FpsOptions = { 0, 30, 60, 120, 144, 240 };

    public string TitleKey => "ui.settings.section.video";

    public void Build(VisualElement content, GameSettings draft)
    {
        SettingsRows.AddHeader(content, TitleKey);
        BuildMode(content, draft);
        BuildResolution(content, draft);
        SettingsRows.AddToggle(content, "ui.settings.video.vsync", draft.VSync, v => draft.VSync = v);
        BuildFpsCap(content, draft);
        BuildQuality(content, draft);
    }

    public void ResetToDefaults(GameSettings draft)
    {
        var defaults = new GameSettings();
        draft.ScreenMode       = defaults.ScreenMode;
        draft.ResolutionWidth  = defaults.ResolutionWidth;
        draft.ResolutionHeight = defaults.ResolutionHeight;
        draft.VSync            = defaults.VSync;
        draft.FpsCap           = defaults.FpsCap;
        draft.QualityLevel     = defaults.QualityLevel;
    }

    private static void BuildMode(VisualElement content, GameSettings draft)
    {
        var names = new List<string>(ModeKeys.Length);
        foreach (var key in ModeKeys) names.Add(Loc.Tr(key));

        int index = Array.IndexOf(Modes, draft.ScreenMode);
        if (index < 0) index = Modes.Length - 1;

        SettingsRows.AddDropdown(content, "ui.settings.video.mode", names, index, i => draft.ScreenMode = Modes[i]);
    }

    private static void BuildResolution(VisualElement content, GameSettings draft)
    {
        var resolutions = SettingsService.Resolutions;
        var names = new List<string> { Loc.Tr("ui.settings.video.resolution.native") };
        int index = 0;

        for (int i = 0; i < resolutions.Count; i++)
        {
            names.Add($"{resolutions[i].width} x {resolutions[i].height}");
            if (resolutions[i].width == draft.ResolutionWidth && resolutions[i].height == draft.ResolutionHeight)
                index = i + 1;
        }

        SettingsRows.AddDropdown(content, "ui.settings.video.resolution", names, index, i =>
        {
            draft.ResolutionWidth  = i == 0 ? 0 : resolutions[i - 1].width;
            draft.ResolutionHeight = i == 0 ? 0 : resolutions[i - 1].height;
        });
    }

    private static void BuildFpsCap(VisualElement content, GameSettings draft)
    {
        var names = new List<string>(FpsOptions.Length);
        foreach (int fps in FpsOptions)
            names.Add(fps == 0 ? Loc.Tr("ui.settings.video.fps.none") : fps.ToString());

        int index = Mathf.Max(0, Array.IndexOf(FpsOptions, draft.FpsCap));

        SettingsRows.AddDropdown(content, "ui.settings.video.fps", names, index, i => draft.FpsCap = FpsOptions[i]);
    }

    private static void BuildQuality(VisualElement content, GameSettings draft)
    {
        var names = SettingsService.QualityNames;
        if (names == null || names.Length == 0) return;

        int index = draft.QualityLevel < 0 ? QualitySettings.GetQualityLevel() : draft.QualityLevel;

        SettingsRows.AddDropdown(content, "ui.settings.video.quality", names, index, i => draft.QualityLevel = i);
    }
}
}
