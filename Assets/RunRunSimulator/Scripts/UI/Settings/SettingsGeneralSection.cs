using System.Collections.Generic;
using UnityEngine.Localization;
using UnityEngine.Localization.Settings;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class SettingsGeneralSection : ISettingsSection
{
    public string TitleKey => "ui.settings.section.general";

    public void Build(VisualElement content, GameSettings draft)
    {
        SettingsRows.AddHeader(content, TitleKey);

        var locales = LocalizationSettings.AvailableLocales != null
            ? LocalizationSettings.AvailableLocales.Locales
            : null;
        if (locales == null || locales.Count == 0) return;

        string activeCode = string.IsNullOrEmpty(draft.LocaleCode) ? Loc.CurrentCode : draft.LocaleCode;

        var names = new List<string>(locales.Count);
        int index = 0;
        for (int i = 0; i < locales.Count; i++)
        {
            names.Add(NativeName(locales[i]));
            if (locales[i].Identifier.Code == activeCode) index = i;
        }

        SettingsRows.AddDropdown(content, "ui.settings.general.language", names, index,
            i => draft.LocaleCode = locales[i].Identifier.Code);
    }

    public void ResetToDefaults(GameSettings draft) => draft.LocaleCode = new GameSettings().LocaleCode;

    private static string NativeName(Locale locale)
    {
        var culture = locale.Identifier.CultureInfo;
        string name = culture != null ? culture.NativeName : locale.LocaleName;
        return string.IsNullOrEmpty(name) ? name : char.ToUpper(name[0]) + name.Substring(1);
    }
}
}
