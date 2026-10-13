using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;
#if UNITY_EDITOR
using UnityEditor;
#endif
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class PauseMenuUITK : MonoBehaviour
{
    [SerializeField] private UIDocument document;
    [SerializeField] private SettingsPanelUITK settings;

    private InputAction escape;
    private VisualElement root;
    private Button resumeButton;
    private Button settingsButton;
    private Button skipTutorialButton;
    private Button titleButton;
    private Button quitButton;
    private Label titleLabel;

    private bool uiFocused;
    private bool paused;
    private bool settingsOpen;
    private bool quitting;
    private CursorLockMode previousLock;
    private bool previousVisible;

    private void Awake()
    {
        escape = new InputAction("PauseToggle", InputActionType.Button, "<Keyboard>/escape");
        escape.performed += OnEscape;
    }

    private void OnEnable()
    {
        UIManager.OnPanelVisibilityChanged += OnPanelVisibility;
        UIManager.OnUIFocusChanged         += OnUIFocusChanged;
        if (settings != null) settings.Closed += OnSettingsClosed;
        RefreshEscape();
    }

    private void OnDisable()
    {
        UIManager.OnPanelVisibilityChanged -= OnPanelVisibility;
        UIManager.OnUIFocusChanged         -= OnUIFocusChanged;
        if (settings != null) settings.Closed -= OnSettingsClosed;
        escape.Disable();
        if (paused) ApplyPaused(false);
    }

    private void Start()
    {
        Resolve();
        if (!UIManager.Present && root != null) root.style.display = DisplayStyle.None;
        RefreshEscape();
    }

    private void OnDestroy()
    {
        if (resumeButton   != null) resumeButton.clicked   -= OnResumeClicked;
        if (settingsButton != null) settingsButton.clicked -= OnSettingsClicked;
        if (skipTutorialButton != null) skipTutorialButton.clicked -= OnSkipTutorialClicked;
        if (titleButton    != null) titleButton.clicked    -= OnTitleClicked;
        if (quitButton     != null) quitButton.clicked     -= OnQuitClicked;
        if (escape != null)
        {
            escape.performed -= OnEscape;
            escape.Dispose();
        }
    }

    private void Resolve()
    {
        root = UiPanels.RootOf(document);
        if (root == null) return;

        titleLabel     = root.Q<Label>("pause-title");
        resumeButton   = root.Q<Button>("pause-resume");
        settingsButton = root.Q<Button>("pause-settings");
        skipTutorialButton = root.Q<Button>("pause-skiptutorial");
        titleButton    = root.Q<Button>("pause-totitle");
        quitButton     = root.Q<Button>("pause-quit");

        if (resumeButton   != null) resumeButton.clicked   += OnResumeClicked;
        if (settingsButton != null) settingsButton.clicked += OnSettingsClicked;
        if (skipTutorialButton != null) skipTutorialButton.clicked += OnSkipTutorialClicked;
        if (titleButton    != null) titleButton.clicked    += OnTitleClicked;
        if (quitButton     != null) quitButton.clicked     += OnQuitClicked;
        RefreshTexts();
    }

    private void RefreshTexts()
    {
        if (titleLabel     != null) titleLabel.text     = Loc.Tr("ui.pause.title");
        if (resumeButton   != null) resumeButton.text   = Loc.Tr("ui.pause.resume");
        if (settingsButton != null) settingsButton.text = Loc.Tr("ui.pause.settings");
        if (skipTutorialButton != null) skipTutorialButton.text = Loc.Tr("ui.pause.skiptutorial");
        if (titleButton    != null) titleButton.text    = Loc.Tr("ui.pause.totitle");
        if (quitButton     != null) quitButton.text     = Loc.Tr("ui.pause.quit");
        RefreshSkipTutorial();
    }

    private void RefreshSkipTutorial()
    {
        if (skipTutorialButton == null) return;
        bool tutorialActive = TutorialDirector.Instance != null && TutorialDirector.Instance.Active;
        skipTutorialButton.style.display = tutorialActive ? DisplayStyle.Flex : DisplayStyle.None;
    }

    private void OnSkipTutorialClicked()
    {
        if (TutorialDirector.Instance != null) TutorialDirector.Instance.Skip();
        RefreshSkipTutorial();
    }

    private void RefreshEscape()
    {
        if (escape == null) return;
        bool shouldEnable = !UIManager.Present || !uiFocused;
        if (shouldEnable && !escape.enabled) escape.Enable();
        else if (!shouldEnable && escape.enabled) escape.Disable();
    }

    private void OnUIFocusChanged(bool focused)
    {
        uiFocused = focused;
        RefreshEscape();
    }

    private void OnPanelVisibility(UIPanelType panel, bool shown)
    {
        if (panel == UIPanelType.Pause) ApplyPaused(shown);
    }

    private void OnEscape(InputAction.CallbackContext c)
    {
        if (UIManager.Present)
        {
            if (!paused) UIManager.RequestPanelSet(UIPanelType.Pause, true);
            return;
        }

        if (settingsOpen)
        {
            settings.Hide();
            OnSettingsClosed();
            return;
        }

        if (paused) ClosePause();
        else        OpenPause();
    }

    private void OpenPause()
    {
        if (root != null) root.style.display = DisplayStyle.Flex;
        previousLock    = UnityEngine.Cursor.lockState;
        previousVisible = UnityEngine.Cursor.visible;
        UnityEngine.Cursor.lockState = CursorLockMode.None;
        UnityEngine.Cursor.visible   = true;
        ApplyPaused(true);
    }

    private void ClosePause()
    {
        if (root != null) root.style.display = DisplayStyle.None;
        ApplyPaused(false);
        UnityEngine.Cursor.lockState = previousLock;
        UnityEngine.Cursor.visible   = previousVisible;
    }

    private void ApplyPaused(bool value)
    {
        paused = value;
        Time.timeScale = value ? 0f : 1f;
        if (value) RefreshTexts();
        if (!value) settingsOpen = false;
    }

    private void OnResumeClicked()
    {
        if (UIManager.Present) UIManager.RequestPanelSet(UIPanelType.Pause, false);
        else                   ClosePause();
    }

    private void OnSettingsClicked()
    {
        if (UIManager.Present)
        {
            UIManager.RequestPanelSet(UIPanelType.Settings, true);
            return;
        }

        if (settings == null) return;
        settingsOpen = true;
        if (root != null) root.style.display = DisplayStyle.None;
        settings.Show();
    }

    private void OnSettingsClosed()
    {
        if (UIManager.Present || !settingsOpen) return;
        settingsOpen = false;
        if (paused && root != null) root.style.display = DisplayStyle.Flex;
    }

    private async void OnTitleClicked()
    {
        if (quitting) return;
        quitting = true;
        if (titleButton != null) titleButton.SetEnabled(false);
        if (quitButton != null) quitButton.SetEnabled(false);

        if (GameManager.Instance != null)
        {
            try { await GameManager.Instance.FlushToCloudAsync(); }
            catch (System.Exception e) { Debug.LogException(e); }
        }

        if (UIManager.Present) UIManager.RequestPanelSet(UIPanelType.Pause, false);
        else                   ClosePause();
        SceneFlow.GoToTitle();
    }

    private async void OnQuitClicked()
    {
        if (quitting) return;
        quitting = true;
        if (quitButton != null) quitButton.SetEnabled(false);

        if (GameManager.Instance != null)
        {
            try { await GameManager.Instance.FlushToCloudAsync(); }
            catch (System.Exception e) { Debug.LogException(e); }
        }

#if UNITY_EDITOR
        EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }
}
}
