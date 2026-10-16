using UnityEngine;
using UnityEngine.Localization.Settings;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class FocusPromptUITK : MonoBehaviour
{
    [SerializeField] private UIDocument document;

    private VisualElement crosshair;
    private VisualElement prompt;
    private Label titleLabel;
    private Label detailLabel;
    private FocusPrompt current;
    private bool uiFocused;

    private void OnEnable()
    {
        PlayerFocusProbe.Changed += HandleChanged;
        UIManager.OnUIFocusChanged += HandleUIFocus;
        SettingsService.Changed += HandleSettingsChanged;
        LocalizationSettings.SelectedLocaleChanged += HandleLocaleChanged;
        current = PlayerFocusProbe.Current;
        Refresh();
    }

    private void OnDisable()
    {
        PlayerFocusProbe.Changed -= HandleChanged;
        UIManager.OnUIFocusChanged -= HandleUIFocus;
        SettingsService.Changed -= HandleSettingsChanged;
        LocalizationSettings.SelectedLocaleChanged -= HandleLocaleChanged;
    }

    private void Start()
    {
        var root = UiPanels.RootOf(document);
        if (root == null) { Debug.LogWarning("[FocusPromptUITK] No UIDocument / root."); return; }

        crosshair = root.Q<VisualElement>("crosshair");
        prompt = root.Q<VisualElement>("focus-prompt");
        current = PlayerFocusProbe.Current;
        Refresh();
    }

    private void Update()
    {
        if (titleLabel != null) RefreshLabelText();
    }

    private void RefreshLabelText()
    {
        var focusLabel = PlayerFocusProbe.CurrentLabel;
        string title = focusLabel?.FocusTitle;
        string detail = focusLabel?.FocusDetail;

        if (titleLabel.text != (title ?? "")) titleLabel.text = title ?? "";
        titleLabel.style.display = string.IsNullOrEmpty(title) ? DisplayStyle.None : DisplayStyle.Flex;

        if (detailLabel.text != (detail ?? "")) detailLabel.text = detail ?? "";
        detailLabel.style.display = string.IsNullOrEmpty(detail) ? DisplayStyle.None : DisplayStyle.Flex;
    }

    private void HandleChanged(FocusPrompt value)
    {
        current = value;
        Refresh();
    }

    private void HandleUIFocus(bool focused)
    {
        uiFocused = focused;
        Refresh();
    }

    private void HandleSettingsChanged(GameSettings settings) => Refresh();

    private void HandleLocaleChanged(UnityEngine.Localization.Locale locale) => Refresh();

    private void Refresh()
    {
        if (crosshair != null)
        {
            crosshair.style.display = uiFocused ? DisplayStyle.None : DisplayStyle.Flex;
            crosshair.EnableInClassList("crosshair--target", current == FocusPrompt.Creature || current == FocusPrompt.Interactable);
        }

        if (prompt == null) return;

        var focusLabel = PlayerFocusProbe.CurrentLabel;
        bool hints = current != FocusPrompt.None && SettingsService.Current.ShowKeyHints;
        bool show = !uiFocused && (hints || focusLabel != null);
        prompt.EnableInClassList("focus-prompt--visible", show);
        titleLabel = null;
        detailLabel = null;
        if (!show) return;

        prompt.Clear();
        if (focusLabel != null)
        {
            titleLabel = new Label { pickingMode = PickingMode.Ignore };
            titleLabel.AddToClassList("focus-title");
            prompt.Add(titleLabel);

            detailLabel = new Label { pickingMode = PickingMode.Ignore };
            detailLabel.AddToClassList("focus-detail");
            prompt.Add(detailLabel);

            RefreshLabelText();
        }

        if (!hints) return;
        switch (current)
        {
            case FocusPrompt.Creature:
                AddRow("E", "ui.focus.pet");
                AddRow(Loc.Tr("ui.key.hold", "E"), "ui.focus.grab");
                break;
            case FocusPrompt.Interactable:
                AddRow("E", "ui.focus.use");
                break;
            case FocusPrompt.Carrying:
                AddRow("E", "ui.focus.drop");
                AddRow(Loc.Tr("ui.key.click"), "ui.focus.throw");
                break;
            case FocusPrompt.Item:
                AddRow(Loc.Tr("ui.key.click"), "ui.focus.useitem");
                AddRow(Loc.Tr("ui.key.hold", "E"), "ui.focus.throw");
                break;
        }
    }

    private void AddRow(string keyText, string actionKey)
    {
        var row = new VisualElement { pickingMode = PickingMode.Ignore };
        row.AddToClassList("focus-row");

        var key = new Label(keyText) { pickingMode = PickingMode.Ignore };
        key.AddToClassList("mm-hud-key");
        key.AddToClassList("focus-key");
        row.Add(key);

        var action = new Label(Loc.Tr(actionKey)) { pickingMode = PickingMode.Ignore };
        action.AddToClassList("focus-action");
        row.Add(action);

        prompt.Add(row);
    }
}
}
