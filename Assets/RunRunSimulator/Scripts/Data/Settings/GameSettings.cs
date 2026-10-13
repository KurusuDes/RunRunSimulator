using System;
using UnityEngine;

namespace MoriMonchiSimulator
{
    public enum NameTagMode
    {
        Always,
        WhenLooked,
        Never
    }

    [Serializable]
    public class GameSettings
    {
        public string LocaleCode = "";

        public FullScreenMode ScreenMode = FullScreenMode.FullScreenWindow;
        public int ResolutionWidth = 0;
        public int ResolutionHeight = 0;
        public bool VSync = true;
        public int FpsCap = 0;
        public int QualityLevel = -1;

        public NameTagMode NameTags = NameTagMode.WhenLooked;
        public float HudScale = 1f;
        public bool ShowKeyHints = true;

        public float LookSensitivity = 1f;
        public bool InvertY = false;
        public float FieldOfView = 0f;
        public bool CameraBob = true;

        public float MasterVolume = 1f;
        public float MusicVolume = 0.8f;
        public float SfxVolume = 1f;
        public float AmbienceVolume = 0.8f;
        public float UiVolume = 1f;

        public GameSettings Clone()
        {
            return (GameSettings)MemberwiseClone();
        }
    }
}
