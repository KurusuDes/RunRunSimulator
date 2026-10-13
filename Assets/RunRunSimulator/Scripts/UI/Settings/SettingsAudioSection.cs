using System;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class SettingsAudioSection : ISettingsSection
{
    public string TitleKey => "ui.settings.section.audio";

    public void Build(VisualElement content, GameSettings draft)
    {
        SettingsRows.AddHeader(content, TitleKey);
        SettingsRows.AddNote(content, "ui.settings.audio.pending");
        AddVolume(content, "ui.settings.audio.master",   draft.MasterVolume,   v => draft.MasterVolume   = v);
        AddVolume(content, "ui.settings.audio.music",    draft.MusicVolume,    v => draft.MusicVolume    = v);
        AddVolume(content, "ui.settings.audio.sfx",      draft.SfxVolume,      v => draft.SfxVolume      = v);
        AddVolume(content, "ui.settings.audio.ambience", draft.AmbienceVolume, v => draft.AmbienceVolume = v);
        AddVolume(content, "ui.settings.audio.ui",       draft.UiVolume,       v => draft.UiVolume       = v);
    }

    public void ResetToDefaults(GameSettings draft)
    {
        var defaults = new GameSettings();
        draft.MasterVolume   = defaults.MasterVolume;
        draft.MusicVolume    = defaults.MusicVolume;
        draft.SfxVolume      = defaults.SfxVolume;
        draft.AmbienceVolume = defaults.AmbienceVolume;
        draft.UiVolume       = defaults.UiVolume;
    }

    private static void AddVolume(VisualElement content, string labelKey, float value, Action<float> onChange) =>
        SettingsRows.AddSlider(content, labelKey, 0f, 1f, 0.01f, value, SettingsRows.Percent, onChange);
}
}
