using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class TutorialHintUITK : MonoBehaviour
{
    private const string ShownClass = "hint--shown";
    private const string DoneClass = "hint--done";
    private const string PopClass = "hint--pop";

    [SerializeField] private UIDocument document;

    private VisualElement hintRoot;
    private VisualElement pill;
    private Label badge;
    private Label text;

    private bool active;
    private bool uiFocused;
    private bool hasStep;
    private int stepIndex;
    private int stepTotal;
    private string stepKey;

    private void OnEnable()
    {
        TutorialDirector.StepChanged   += OnStepChanged;
        TutorialDirector.StepCompleted += OnStepCompleted;
        TutorialDirector.Finished      += OnFinished;
        UIManager.OnUIFocusChanged     += OnUIFocusChanged;
    }

    private void OnDisable()
    {
        TutorialDirector.StepChanged   -= OnStepChanged;
        TutorialDirector.StepCompleted -= OnStepCompleted;
        TutorialDirector.Finished      -= OnFinished;
        UIManager.OnUIFocusChanged     -= OnUIFocusChanged;
    }

    private void Start()
    {
        VisualElement root = UiPanels.RootOf(document);
        if (root == null) return;

        hintRoot = root.Q<VisualElement>("hint-root");
        pill     = root.Q<VisualElement>("hint-pill");
        badge    = root.Q<Label>("hint-badge");
        text     = root.Q<Label>("hint-text");
        if (hintRoot != null) hintRoot.style.display = DisplayStyle.None;

        if (active && hasStep) ShowStep();
    }

    private void OnStepChanged(int index, int total, string textKey)
    {
        active = true;
        hasStep = true;
        stepIndex = index;
        stepTotal = total;
        stepKey = textKey;
        if (pill != null) ShowStep();
    }

    private void OnStepCompleted()
    {
        if (badge == null) return;
        badge.text = "✓";
        badge.AddToClassList(DoneClass);
        badge.AddToClassList(PopClass);
        badge.schedule.Execute(() => badge.RemoveFromClassList(PopClass)).StartingIn(140);
    }

    private void OnFinished()
    {
        active = false;
        hasStep = false;
        if (pill == null) return;
        pill.RemoveFromClassList(ShownClass);
        pill.schedule.Execute(ApplyVisibility).StartingIn(450);
    }

    private void OnUIFocusChanged(bool focused)
    {
        uiFocused = focused;
        ApplyVisibility();
    }

    private void ShowStep()
    {
        pill.RemoveFromClassList(ShownClass);
        badge.RemoveFromClassList(DoneClass);
        badge.RemoveFromClassList(PopClass);
        badge.text = (stepIndex + 1) + "/" + stepTotal;
        text.text = Loc.Tr(stepKey);
        ApplyVisibility();
        pill.schedule.Execute(() =>
        {
            if (active) pill.AddToClassList(ShownClass);
        }).StartingIn(60);
    }

    private void ApplyVisibility()
    {
        if (hintRoot == null) return;
        bool visible = active && !uiFocused;
        hintRoot.style.display = visible ? DisplayStyle.Flex : DisplayStyle.None;
    }
}
}
