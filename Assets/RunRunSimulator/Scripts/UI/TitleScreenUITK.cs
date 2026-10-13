using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;
#if UNITY_EDITOR
using UnityEditor;
#endif
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class TitleScreenUITK : MonoBehaviour
{
    [SerializeField] private UIDocument document;
    [SerializeField] private SettingsPanelUITK settings;

    private InputAction escape;
    private VisualElement root;
    private VisualElement menu;
    private VisualElement confirm;
    private Label taglineLabel;
    private Label confirmText;
    private Button continueButton;
    private Button newButton;
    private Button settingsButton;
    private Button quitButton;
    private Button confirmYesButton;
    private Button confirmNoButton;

    private VisualElement logo;
    private VisualElement fade;
    private Label versionLabel;
    private readonly List<Label> letters = new List<Label>();
    private IVisualElementScheduledItem waveItem;
    private IVisualElementScheduledItem breatheItem;

    private bool settingsOpen;
    private bool leaving;

    private static readonly string[] LogoLines = { "Mori", "Monchis" };
    private const long BreatheMs = 1300;
    private const string BreatheClass = "title-button--breathe";
    private const string HiddenClass = "title-slide--hidden";
    private const string SlideClass = "title-slide";
    private const long LogoStartMs = 300;
    private const long LetterStaggerMs = 50;
    private const long LetterTransitionMs = 550;
    private const long TaglineDelayMs = 700;
    private const long ButtonsGapMs = 250;
    private const long ButtonStaggerMs = 80;
    private const long SlideDoneMs = 600;
    private const long LeaveMs = 450;
    private const float WaveAmplitude = 6f;
    private const float WaveSpeed = 3f;
    private const float WavePhase = 0.55f;
    private const float EntryRotation = 20f;

    private void Awake()
    {
        escape = new InputAction("TitleCancel", InputActionType.Button, "<Keyboard>/escape");
        escape.performed += OnEscape;
    }

    private void OnEnable()
    {
        if (settings != null) settings.Closed += OnSettingsClosed;
        escape.Enable();
    }

    private void OnDisable()
    {
        if (settings != null) settings.Closed -= OnSettingsClosed;
        escape.Disable();
    }

    private void Start()
    {
        Time.timeScale = 1f;
        UnityEngine.Cursor.lockState = CursorLockMode.None;
        UnityEngine.Cursor.visible   = true;
        Resolve();
    }

    private void OnDestroy()
    {
        if (waveItem != null) waveItem.Pause();
        if (breatheItem != null) breatheItem.Pause();
        if (continueButton   != null) continueButton.clicked   -= OnContinueClicked;
        if (newButton        != null) newButton.clicked        -= OnNewClicked;
        if (settingsButton   != null) settingsButton.clicked   -= OnSettingsClicked;
        if (quitButton       != null) quitButton.clicked       -= OnQuitClicked;
        if (confirmYesButton != null) confirmYesButton.clicked -= OnConfirmYes;
        if (confirmNoButton  != null) confirmNoButton.clicked  -= HideConfirm;
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

        menu             = root.Q<VisualElement>("title-menu");
        confirm          = root.Q<VisualElement>("title-confirm");
        logo             = root.Q<VisualElement>("title-logo");
        fade             = root.Q<VisualElement>("title-fade");
        versionLabel     = root.Q<Label>("title-version");
        taglineLabel     = root.Q<Label>("title-tagline");
        confirmText      = root.Q<Label>("title-confirm-text");
        continueButton   = root.Q<Button>("title-continue");
        newButton        = root.Q<Button>("title-new");
        settingsButton   = root.Q<Button>("title-settings");
        quitButton       = root.Q<Button>("title-quit");
        confirmYesButton = root.Q<Button>("title-confirm-yes");
        confirmNoButton  = root.Q<Button>("title-confirm-no");

        if (continueButton   != null) continueButton.clicked   += OnContinueClicked;
        if (newButton        != null) newButton.clicked        += OnNewClicked;
        if (settingsButton   != null) settingsButton.clicked   += OnSettingsClicked;
        if (quitButton       != null) quitButton.clicked       += OnQuitClicked;
        if (confirmYesButton != null) confirmYesButton.clicked += OnConfirmYes;
        if (confirmNoButton  != null) confirmNoButton.clicked  += HideConfirm;

        if (confirm != null) confirm.style.display = DisplayStyle.None;
        if (versionLabel != null) versionLabel.text = Application.version;
        RefreshTexts();
        PlayIntro();
    }

    private void PlayIntro()
    {
        if (fade != null)
        {
            VisualElement f = fade;
            f.schedule.Execute(() => f.RemoveFromClassList("title-fade--black")).StartingIn(60);
        }

        BuildLogo();

        long taglineAt = LogoStartMs + TaglineDelayMs;
        Slide(taglineLabel, taglineAt);

        long buttonsAt = taglineAt + ButtonsGapMs;
        Button[] buttons = { continueButton, newButton, settingsButton, quitButton };
        for (int i = 0; i < buttons.Length; i++)
            Slide(buttons[i], buttonsAt + i * ButtonStaggerMs);

        if (continueButton != null)
        {
            VisualElement primary = continueButton;
            breatheItem = primary.schedule.Execute(() => primary.ToggleInClassList(BreatheClass))
                .StartingIn(buttonsAt + SlideDoneMs + 100).Every(BreatheMs);
        }
    }

    private void BuildLogo()
    {
        if (logo == null) return;
        logo.Clear();
        letters.Clear();

        int index = 0;
        for (int line = 0; line < LogoLines.Length; line++)
        {
            VisualElement row = new VisualElement();
            row.pickingMode = PickingMode.Ignore;
            row.AddToClassList("title-logo-row");
            row.AddToClassList("title-logo-row--" + (line + 1));
            logo.Add(row);

            string text = LogoLines[line];
            for (int c = 0; c < text.Length; c++, index++)
            {
                Label letter = new Label(text[c].ToString());
                letter.pickingMode = PickingMode.Ignore;
                letter.AddToClassList("title-letter");
                letter.AddToClassList(index % 2 == 0 ? "title-letter--a" : "title-letter--b");
                letter.style.rotate = new Rotate(Angle.Degrees(Random.Range(-EntryRotation, EntryRotation)));
                row.Add(letter);
                letters.Add(letter);

                Label l = letter;
                l.schedule.Execute(() =>
                {
                    l.style.rotate = StyleKeyword.Null;
                    l.AddToClassList("title-letter--in");
                }).StartingIn(LogoStartMs + index * LetterStaggerMs);
            }
        }

        long idleAt = LogoStartMs + (letters.Count - 1) * LetterStaggerMs + LetterTransitionMs + 50;
        logo.schedule.Execute(StartWave).StartingIn(idleAt);
    }

    private void StartWave()
    {
        for (int i = 0; i < letters.Count; i++) letters[i].AddToClassList("title-letter--idle");
        waveItem = logo.schedule.Execute(WaveTick).Every(16);
    }

    private void WaveTick()
    {
        float t = Time.unscaledTime * WaveSpeed;
        for (int i = 0; i < letters.Count; i++)
        {
            float y = Mathf.Sin(t + i * WavePhase) * WaveAmplitude;
            letters[i].style.translate = new Translate(new Length(0f), new Length(y));
        }
    }

    private void Slide(VisualElement element, long delayMs)
    {
        if (element == null) return;
        VisualElement e = element;
        e.schedule.Execute(() => e.RemoveFromClassList(HiddenClass)).StartingIn(delayMs);
        e.schedule.Execute(() => e.RemoveFromClassList(SlideClass)).StartingIn(delayMs + SlideDoneMs);
    }

    private void LeaveTo(System.Action go)
    {
        if (fade == null)
        {
            go();
            return;
        }
        fade.pickingMode = PickingMode.Position;
        fade.AddToClassList("title-fade--leave");
        fade.schedule.Execute(go).StartingIn(LeaveMs);
    }

    private void RefreshTexts()
    {
        if (taglineLabel     != null) taglineLabel.text     = Loc.Tr("ui.title.tagline");
        if (continueButton   != null) continueButton.text   = Loc.Tr("ui.title.continue");
        if (newButton        != null) newButton.text        = Loc.Tr("ui.title.new");
        if (settingsButton   != null) settingsButton.text   = Loc.Tr("ui.title.settings");
        if (quitButton       != null) quitButton.text       = Loc.Tr("ui.title.quit");
        if (confirmText      != null) confirmText.text      = Loc.Tr("ui.title.confirm");
        if (confirmYesButton != null) confirmYesButton.text = Loc.Tr("ui.title.confirm.yes");
        if (confirmNoButton  != null) confirmNoButton.text  = Loc.Tr("ui.title.confirm.no");
    }

    private void OnEscape(InputAction.CallbackContext c)
    {
        if (confirm != null && confirm.style.display == DisplayStyle.Flex)
            HideConfirm();
    }

    private void SetButtonsEnabled(bool value)
    {
        if (continueButton != null) continueButton.SetEnabled(value);
        if (newButton      != null) newButton.SetEnabled(value);
        if (settingsButton != null) settingsButton.SetEnabled(value);
        if (quitButton     != null) quitButton.SetEnabled(value);
    }

    private void OnContinueClicked()
    {
        if (leaving) return;
        leaving = true;
        SetButtonsEnabled(false);
        LeaveTo(SceneFlow.GoToStore);
    }

    private void OnNewClicked()
    {
        if (leaving || confirm == null) return;
        confirm.style.display = DisplayStyle.Flex;
    }

    private void HideConfirm()
    {
        if (leaving || confirm == null) return;
        confirm.style.display = DisplayStyle.None;
    }

    private void OnConfirmYes()
    {
        if (leaving) return;
        leaving = true;
        SetButtonsEnabled(false);
        if (confirmYesButton != null) confirmYesButton.SetEnabled(false);
        if (confirmNoButton  != null) confirmNoButton.SetEnabled(false);
        LeaveTo(SceneFlow.RequestNewGame);
    }

    private void OnSettingsClicked()
    {
        if (leaving || settings == null) return;
        settingsOpen = true;
        if (menu != null) menu.style.display = DisplayStyle.None;
        settings.Show();
    }

    private void OnSettingsClosed()
    {
        if (!settingsOpen) return;
        settingsOpen = false;
        if (menu != null) menu.style.display = DisplayStyle.Flex;
        RefreshTexts();
    }

    private void OnQuitClicked()
    {
#if UNITY_EDITOR
        EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }
}
}
