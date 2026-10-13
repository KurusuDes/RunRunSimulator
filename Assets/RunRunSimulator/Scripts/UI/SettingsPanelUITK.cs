using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class SettingsPanelUITK : MonoBehaviour
{
    [SerializeField] private UIDocument document;
    [SerializeField] private UIPanelType panel = UIPanelType.Settings;

    public event Action Closed;

    private const string TabClass       = "set-tab";
    private const string TabActiveClass = "set-tab--active";

    private readonly ISettingsSection[] sections =
    {
        new SettingsGeneralSection(),
        new SettingsVideoSection(),
        new SettingsInterfaceSection(),
        new SettingsControlsSection(),
        new SettingsAudioSection()
    };

    private readonly List<VisualElement> tabEls = new List<VisualElement>();

    private VisualElement root;
    private VisualElement nav;
    private ScrollView    content;
    private Label         titleLabel;
    private Label         statusLabel;
    private Button        applyButton;
    private Button        resetButton;
    private Button        backButton;

    private GameSettings draft;
    private int activeSection;

    private void OnEnable()
    {
        UIManager.OnPanelToggleRequested += OnPanelToggle;
        UIManager.OnPanelSetRequested    += OnPanelSet;
    }

    private void OnDisable()
    {
        UIManager.OnPanelToggleRequested -= OnPanelToggle;
        UIManager.OnPanelSetRequested    -= OnPanelSet;
    }

    private void Start()
    {
        Resolve();
        draft = SettingsService.Current.Clone();
        RefreshTexts();
        if (!UIManager.Present) SetVisible(false);
    }

    private void OnDestroy()
    {
        if (applyButton != null) applyButton.clicked -= OnApplyClicked;
        if (resetButton != null) resetButton.clicked -= OnResetClicked;
        if (backButton  != null) backButton.clicked  -= OnBackClicked;
    }

    public void Show()
    {
        Open();
        SetVisible(true);
    }

    public void Hide() => SetVisible(false);

    private void OnPanelToggle(UIPanelType p) { if (p == panel) Open(); }
    private void OnPanelSet(UIPanelType p, bool show) { if (p == panel && show) Open(); }

    private void Open()
    {
        if (root == null) return;
        draft = SettingsService.Current.Clone();
        if (statusLabel != null) statusLabel.style.display = DisplayStyle.None;
        RefreshTexts();
    }

    private void OnApplyClicked()
    {
        SettingsService.Apply(draft.Clone());
        RefreshTexts();
        ShowStatus(Loc.Tr("ui.settings.applied"));
    }

    private void OnResetClicked()
    {
        sections[activeSection].ResetToDefaults(draft);
        BuildContent();
    }

    private void OnBackClicked()
    {
        if (UIManager.Present)
        {
            UIManager.RequestPanelSet(panel, false);
            return;
        }
        Hide();
        Closed?.Invoke();
    }

    private void RefreshTexts()
    {
        if (root == null) return;
        if (titleLabel  != null) titleLabel.text  = Loc.Tr("ui.settings.title");
        if (applyButton != null) applyButton.text = Loc.Tr("ui.settings.apply");
        if (resetButton != null) resetButton.text = Loc.Tr("ui.settings.reset");
        if (backButton  != null) backButton.text  = Loc.Tr("ui.settings.back");
        BuildNav();
        BuildContent();
    }

    private void BuildNav()
    {
        if (nav == null) return;
        nav.Clear();
        tabEls.Clear();

        for (int i = 0; i < sections.Length; i++)
        {
            int idx = i;
            var tab = new Label(Loc.Tr(sections[i].TitleKey));
            tab.AddToClassList(TabClass);
            tab.RegisterCallback<ClickEvent>(_ => SetSection(idx));
            nav.Add(tab);
            tabEls.Add(tab);
        }
        UiPanels.SetActiveIndex(tabEls, activeSection, TabActiveClass);
    }

    private void SetSection(int idx)
    {
        activeSection = Mathf.Clamp(idx, 0, sections.Length - 1);
        UiPanels.SetActiveIndex(tabEls, activeSection, TabActiveClass);
        BuildContent();
    }

    private void BuildContent()
    {
        if (content == null || draft == null) return;
        content.Clear();
        sections[activeSection].Build(content.contentContainer, draft);
    }

    private void ShowStatus(string message)
    {
        if (statusLabel == null) return;
        statusLabel.text = message;
        statusLabel.style.display = DisplayStyle.Flex;
        statusLabel.schedule.Execute(() => statusLabel.style.display = DisplayStyle.None).StartingIn(2500);
    }

    private void SetVisible(bool visible)
    {
        if (root != null) root.style.display = visible ? DisplayStyle.Flex : DisplayStyle.None;
    }

    private void Resolve()
    {
        root = UiPanels.RootOf(document);
        if (root == null) return;

        nav         = root.Q<VisualElement>("nav");
        content     = root.Q<ScrollView>("content");
        titleLabel  = root.Q<Label>("title");
        statusLabel = root.Q<Label>("status");
        applyButton = root.Q<Button>("apply-button");
        resetButton = root.Q<Button>("reset-button");
        backButton  = root.Q<Button>("back-button");

        if (statusLabel != null) statusLabel.style.display = DisplayStyle.None;
        if (applyButton != null) applyButton.clicked += OnApplyClicked;
        if (resetButton != null) resetButton.clicked += OnResetClicked;
        if (backButton  != null) backButton.clicked  += OnBackClicked;
    }
}
}
