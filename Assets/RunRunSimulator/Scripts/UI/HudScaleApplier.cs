using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class HudScaleApplier : MonoBehaviour
{
    [SerializeField] private PanelSettings panel;

    private float baseScale;
    private Vector2Int baseReferenceResolution;
    private bool captured;

    private void OnEnable()
    {
        if (panel == null) return;
        if (!captured)
        {
            baseScale = panel.scale;
            baseReferenceResolution = panel.referenceResolution;
            captured = true;
        }
        SettingsService.Changed += OnSettingsChanged;
        Apply(SettingsService.Current.HudScale);
    }

    private void OnDisable()
    {
        SettingsService.Changed -= OnSettingsChanged;
        if (panel == null || !captured) return;
        panel.scale = baseScale;
        panel.referenceResolution = baseReferenceResolution;
    }

    private void OnSettingsChanged(GameSettings settings) => Apply(settings.HudScale);

    private void Apply(float hudScale)
    {
        float factor = Mathf.Max(0.1f, hudScale);
        if (panel.scaleMode == PanelScaleMode.ScaleWithScreenSize)
        {
            panel.referenceResolution = new Vector2Int(
                Mathf.RoundToInt(baseReferenceResolution.x / factor),
                Mathf.RoundToInt(baseReferenceResolution.y / factor));
        }
        else
        {
            panel.scale = baseScale * factor;
        }
    }
}
}
