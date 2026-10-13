using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class TugMeterHUD : MonoBehaviour
{
    [SerializeField] private UIDocument document;

    private const string LosingClass = "tug-meter--losing";
    private const long ResultHideMs = 800;

    private VisualElement meter;
    private VisualElement fill;
    private Label label;
    private IVisualElementScheduledItem hideItem;

    private void OnEnable()
    {
        PlayerToyTug.TugStarted += OnTugStarted;
        PlayerToyTug.TugChanged += OnTugChanged;
        PlayerToyTug.TugEnded   += OnTugEnded;
    }

    private void OnDisable()
    {
        PlayerToyTug.TugStarted -= OnTugStarted;
        PlayerToyTug.TugChanged -= OnTugChanged;
        PlayerToyTug.TugEnded   -= OnTugEnded;
        hideItem?.Pause();
        hideItem = null;
    }

    private void Start() => Bind();

    private bool Bind()
    {
        if (meter != null) return true;
        var root = UiPanels.RootOf(document);
        if (root == null) return false;
        meter = root.Q<VisualElement>("tug-meter");
        if (meter == null) return false;
        fill  = meter.Q<VisualElement>(className: "tug-meter__fill");
        label = meter.Q<Label>(className: "tug-meter__label");
        meter.style.display = DisplayStyle.None;
        return true;
    }

    private void OnTugStarted()
    {
        if (!Bind()) return;
        hideItem?.Pause();
        hideItem = null;
        label.text = Loc.Tr("ui.toy.tug.mash");
        meter.RemoveFromClassList(LosingClass);
        SetFill(0f);
        meter.style.display = DisplayStyle.Flex;
    }

    private void OnTugChanged(float progress)
    {
        if (!Bind()) return;
        SetFill(progress);
        meter.EnableInClassList(LosingClass, progress < 0f);
    }

    private void OnTugEnded(bool playerWon)
    {
        if (!Bind()) return;
        label.text = Loc.Tr(playerWon ? "ui.toy.tug.won" : "ui.toy.tug.lost");
        hideItem?.Pause();
        hideItem = meter.schedule.Execute(Hide);
        hideItem.ExecuteLater(ResultHideMs);
    }

    private void Hide()
    {
        meter.style.display = DisplayStyle.None;
        hideItem = null;
    }

    private void SetFill(float progress)
    {
        fill.style.width = Length.Percent(Mathf.Clamp01((progress + 1f) * 0.5f) * 100f);
    }
}
}
