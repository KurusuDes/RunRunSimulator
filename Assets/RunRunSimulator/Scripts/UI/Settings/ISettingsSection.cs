using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public interface ISettingsSection
{
    string TitleKey { get; }
    void Build(VisualElement content, GameSettings draft);
    void ResetToDefaults(GameSettings draft);
}
}
