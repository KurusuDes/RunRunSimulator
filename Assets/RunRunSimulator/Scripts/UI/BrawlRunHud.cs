using MoreMountains.Feedbacks;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
public class BrawlRunHud : MonoBehaviour
{
    [Required, SerializeField] private UIDocument document;
    [Required, SerializeField] private BrawlRunDirector director;
    [SerializeField] private BrawlTrialRoom trial;
    [SerializeField] private MMF_Player onLoot;
    [SerializeField, Min(0f)] private float countDelay = 0.75f;

    private VisualElement boundRoot;
    private VisualElement root;
    private VisualElement hud;
    private VisualElement leftPips;
    private Label bagCount;
    private Label leftText;
    private Label trialLabel;
    private IVisualElementScheduledItem lootItem;
    private bool lootPending;
    private int shownMinerita = -1;
    private bool lastTrialActive;
    private bool lastTrialStarted;
    private int lastTrialMaterial = -1;

    private void OnEnable()
    {
        if (director != null) director.Changed += HandleChanged;
        TryBind();
    }

    private void OnDisable()
    {
        if (director != null) director.Changed -= HandleChanged;
        Unbind();
    }

    private bool TryBind()
    {
        var docRoot = document != null ? document.rootVisualElement : null;
        if (docRoot == null || director == null) return false;
        if (root != null && docRoot == boundRoot) return true;

        Unbind();
        var found = docRoot.Q("run-root");
        if (found == null) return false;

        var foundHud = found.Q("run-hud");
        var foundPips = found.Q("run-left-pips");
        var foundBag = found.Q<Label>("run-bag-count");
        var foundLeft = found.Q<Label>("run-left-text");
        var foundTrial = found.Q<Label>("run-trial");
        if (foundHud == null || foundPips == null || foundBag == null || foundLeft == null || foundTrial == null) return false;

        boundRoot = docRoot;
        root = found;
        hud = foundHud;
        leftPips = foundPips;
        bagCount = foundBag;
        leftText = foundLeft;
        trialLabel = foundTrial;

        Refresh();
        return true;
    }

    private void Unbind()
    {
        if (lootItem != null) lootItem.Pause();
        lootItem = null;
        lootPending = false;
        if (leftPips != null) leftPips.Clear();

        boundRoot = null;
        root = null;
        shownMinerita = -1;
        lastTrialMaterial = -1;
    }

    private void HandleChanged()
    {
        if (TryBind()) Refresh();
    }

    private void Update()
    {
        if (!TryBind()) return;
        RefreshTrial();
    }

    private void Refresh()
    {
        var run = director.Active ? director.Run : null;
        var state = director.State;
        bool show = run != null && run.Depth > 0 && (state == BrawlRunState.Fighting || state == BrawlRunState.RoomResult);
        SetVisible(hud, show);

        lastTrialMaterial = -1;
        RefreshTrial();

        if (run == null)
        {
            shownMinerita = -1;
            return;
        }

        int target = Minerita(run.Material);
        if (!show)
        {
            SetBag(target);
            return;
        }

        RefreshLeft(run, state == BrawlRunState.Fighting);

        bool loot = state == BrawlRunState.RoomResult && director.LastRoomLoot > 0;
        if (loot && !lootPending && target != shownMinerita)
        {
            lootPending = true;
            if (onLoot != null) onLoot.PlayFeedbacks();
            lootItem = root.schedule.Execute(ApplyLoot).StartingIn((long)(countDelay * 1000f));
        }
        else if (!lootPending)
        {
            SetBag(target);
        }
    }

    private void ApplyLoot()
    {
        lootPending = false;
        var run = director != null && director.Active ? director.Run : null;
        if (run != null) SetBag(Minerita(run.Material));
    }

    private void SetBag(int value)
    {
        shownMinerita = value;
        bagCount.text = value.ToString();
    }

    private void RefreshLeft(BrawlRun run, bool fighting)
    {
        int count = run.Rooms.Count;
        int left = Mathf.Max(0, fighting ? count - run.RoomIndex - 1 : count - run.RoomIndex);
        leftText.text = left == 0 ? "Última sala" : left == 1 ? "Falta 1 sala" : "Faltan " + left + " salas";

        leftPips.Clear();
        for (int i = 0; i < count; i++)
        {
            var pip = new VisualElement { pickingMode = PickingMode.Ignore };
            pip.AddToClassList("run-pip");
            pip.AddToClassList(i < run.RoomIndex ? "run-pip--done" : fighting && i == run.RoomIndex ? "run-pip--current" : "run-pip--upcoming");
            leftPips.Add(pip);
        }
    }

    private void RefreshTrial()
    {
        bool fighting = trial != null && director.Active && director.State == BrawlRunState.Fighting;
        bool active = fighting && trial.Active;
        bool started = active && trial.Started;
        int material = active && trial.Kind == BrawlRoomKind.Minerals ? trial.Material : 0;
        if (active == lastTrialActive && started == lastTrialStarted && material == lastTrialMaterial) return;

        lastTrialActive = active;
        lastTrialStarted = started;
        lastTrialMaterial = material;
        SetVisible(trialLabel, active);
        if (!active) return;

        if (trial.Kind != BrawlRoomKind.Minerals) trialLabel.text = "Muñecos · pégales para curar al equipo";
        else if (!started) trialLabel.text = "Minerales · pégale al cristal para empezar";
        else trialLabel.text = "Minerales · +" + Minerita(material) + " Minerita";
    }

    private static int Minerita(int loot)
    {
        var rules = BrawlRunRulesSO.Current;
        return loot * (rules != null ? rules.MineritaPerLoot : 1);
    }

    private static void SetVisible(VisualElement element, bool visible) =>
        element.style.display = visible ? DisplayStyle.Flex : DisplayStyle.None;
}
}
