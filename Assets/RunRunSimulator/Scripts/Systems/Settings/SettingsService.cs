using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Localization.Settings;

namespace MoriMonchiSimulator
{
    public static class SettingsService
    {
        const string PrefKey = "mm.settings";

        static GameSettings current;
        static List<Resolution> resolutions;

        public static event Action<GameSettings> Changed;

        public static GameSettings Current
        {
            get
            {
                if (current == null) current = Load();
                return current;
            }
        }

        public static IReadOnlyList<Resolution> Resolutions
        {
            get
            {
                if (resolutions == null) resolutions = BuildResolutions();
                return resolutions;
            }
        }

        public static string[] QualityNames => QualitySettings.names;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void ApplyOnStartup()
        {
            ApplyToEngine(Current);
        }

        public static void Apply(GameSettings s)
        {
            if (s == null) return;
            current = s.Clone();
            PlayerPrefs.SetString(PrefKey, JsonUtility.ToJson(current));
            PlayerPrefs.Save();
            ApplyToEngine(current);
            Changed?.Invoke(current);
        }

        static GameSettings Load()
        {
            var json = PlayerPrefs.GetString(PrefKey, "");
            if (string.IsNullOrEmpty(json)) return new GameSettings();
            try
            {
                return JsonUtility.FromJson<GameSettings>(json) ?? new GameSettings();
            }
            catch (Exception)
            {
                return new GameSettings();
            }
        }

        static void ApplyToEngine(GameSettings s)
        {
            if (s.QualityLevel >= 0 && s.QualityLevel < QualitySettings.names.Length)
                QualitySettings.SetQualityLevel(s.QualityLevel, true);

            QualitySettings.vSyncCount = s.VSync ? 1 : 0;
            Application.targetFrameRate = s.FpsCap > 0 ? s.FpsCap : -1;

            if (s.ResolutionWidth > 0 && s.ResolutionHeight > 0)
                Screen.SetResolution(s.ResolutionWidth, s.ResolutionHeight, s.ScreenMode);
            else if (Screen.fullScreenMode != s.ScreenMode)
                Screen.fullScreenMode = s.ScreenMode;

            AudioListener.volume = Mathf.Clamp01(s.MasterVolume);

            ApplyLocale(s.LocaleCode);
        }

        static void ApplyLocale(string code)
        {
            if (string.IsNullOrEmpty(code)) return;

            var init = LocalizationSettings.InitializationOperation;
            if (init.IsDone)
            {
                SelectLocale(code);
                return;
            }
            init.Completed += _ => SelectLocale(code);
        }

        static void SelectLocale(string code)
        {
            if (code == Loc.CurrentCode) return;
            Loc.SetLocale(code);
        }

        static List<Resolution> BuildResolutions()
        {
            var list = new List<Resolution>();
            var seen = new HashSet<long>();
            foreach (var r in Screen.resolutions)
            {
                if (seen.Add(((long)r.width << 32) | (uint)r.height)) list.Add(r);
            }
            list.Sort((a, b) => a.width != b.width ? b.width.CompareTo(a.width) : b.height.CompareTo(a.height));
            return list;
        }
    }
}
