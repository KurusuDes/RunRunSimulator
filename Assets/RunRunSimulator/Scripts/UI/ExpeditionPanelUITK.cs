using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class ExpeditionPanelUITK : MonoBehaviour, IUINavigable
{
    [SerializeField] private UIDocument document;
    [SerializeField] private UIPanelType panel = UIPanelType.Expedition;
    [SerializeField, Min(1)] private int maxPick = 3;
    [SerializeField] private CareGateSO careGate;
    [SerializeField] private CreatureDatabaseSO database;
    [SerializeField] private BrawlKitDatabaseSO kits;

    private Label emptyLabel;
    private Label subtitleLabel;
    private ScrollView list;
    private VisualElement detail;
    private VisualElement team;
    private Button closeButton;
    private Button goButton;

    private readonly List<VisualElement> cards = new List<VisualElement>();
    private readonly List<CreatureDNA> dnas = new List<CreatureDNA>();
    private readonly List<BrawlKitProfile> profiles = new List<BrawlKitProfile>();
    private readonly List<bool> eligible = new List<bool>();
    private readonly List<bool> picked = new List<bool>();
    private int focused = -1;
    private bool wired;

    private void OnEnable()
    {
        UIManager.OnPanelSetRequested    += OnPanelSet;
        UIManager.OnPanelToggleRequested += OnPanelToggle;
        GameEvents.OnDayBlockChanged     += OnDayBlockChanged;
    }

    private void OnDisable()
    {
        UIManager.OnPanelSetRequested    -= OnPanelSet;
        UIManager.OnPanelToggleRequested -= OnPanelToggle;
        GameEvents.OnDayBlockChanged     -= OnDayBlockChanged;
    }

    private static bool ExpeditionOpen =>
        GameClock.Instance == null || GameClock.Instance.Block == null || GameClock.Instance.Block.ExpeditionOpen;

    private void OnDayBlockChanged(DayBlockDef block) => RefreshScheduleUI();

    private void Start()
    {
        var root = UiPanels.RootOf(document);
        if (root == null) return;

        root.Q<Label>("exp-title").text = Loc.Tr("ui.expedition.title");
        subtitleLabel = root.Q<Label>("exp-subtitle");

        emptyLabel = root.Q<Label>("exp-empty");
        list = root.Q<ScrollView>("exp-list");
        detail = root.Q<VisualElement>("exp-detail");
        team = root.Q<VisualElement>("exp-team");

        closeButton = root.Q<Button>("exp-close");
        if (closeButton != null)
        {
            closeButton.text = Loc.Tr("ui.expedition.close");
            closeButton.clicked += Close;
        }

        goButton = root.Q<Button>("exp-go");
        if (goButton != null) goButton.clicked += Depart;

        wired = true;
        UIManager.RegisterNavigable(panel, this);
        Rebuild();
    }

    private void OnDestroy()
    {
        if (closeButton != null) closeButton.clicked -= Close;
        if (goButton != null) goButton.clicked -= Depart;
        UIManager.UnregisterNavigable(panel);
    }

    private void OnPanelSet(UIPanelType p, bool show)
    {
        if (p == panel && show && wired) Rebuild();
    }

    private void OnPanelToggle(UIPanelType p)
    {
        if (p != panel || !wired) return;
        var root = UiPanels.RootOf(document);
        root?.schedule.Execute(() => { if (root.resolvedStyle.display != DisplayStyle.None) Rebuild(); });
    }

    private void Rebuild()
    {
        list?.Clear();
        cards.Clear();
        dnas.Clear();
        profiles.Clear();
        eligible.Clear();
        picked.Clear();

        var gm = GameManager.Instance;
        var registry = gm != null ? gm.Registry : null;

        var entries = new List<CreatureDNA>();
        if (registry != null)
        {
            foreach (var dna in registry.GetAll().Values)
            {
                if (dna.IsDead || dna.IsSold) continue;
                entries.Add(dna);
            }
        }

        entries.Sort(CompareEntries);

        foreach (var dna in entries)
        {
            bool ok = CreatureAvailability.CanExplore(dna, careGate);
            var profile = BrawlKitProfile.Of(dna, kits, database);
            var card = ExpeditionCardBuilder.BuildCard(dna, ok, profile, careGate);

            int index = cards.Count;
            card.RegisterCallback<ClickEvent>(_ => ToggleAt(index));
            card.RegisterCallback<PointerEnterEvent>(_ => HoverAt(index));

            cards.Add(card);
            dnas.Add(dna);
            profiles.Add(profile);
            eligible.Add(ok);
            picked.Add(false);
            list?.Add(card);
        }

        if (emptyLabel != null)
        {
            emptyLabel.text = Loc.Tr("ui.expedition.empty");
            emptyLabel.style.display = eligible.Contains(true) ? DisplayStyle.None : DisplayStyle.Flex;
        }

        SetFocus(cards.Count == 0 ? -1 : FirstEligible());
        RefreshTeam();
        RefreshScheduleUI();
    }

    private void RefreshScheduleUI()
    {
        if (subtitleLabel != null)
            subtitleLabel.text = ExpeditionOpen ? Loc.Tr("ui.expedition.subtitle", maxPick) : Loc.Tr("ui.expedition.night_only");
        UpdateGoButton();
    }

    private int CompareEntries(CreatureDNA a, CreatureDNA b)
    {
        bool ea = CreatureAvailability.CanExplore(a, careGate);
        bool eb = CreatureAvailability.CanExplore(b, careGate);
        if (ea != eb) return ea ? -1 : 1;
        return b.Needs.Health.CompareTo(a.Needs.Health);
    }

    private int FirstEligible()
    {
        for (int i = 0; i < eligible.Count; i++)
            if (eligible[i]) return i;
        return 0;
    }

    private void HoverAt(int index)
    {
        if (index != focused) SetFocus(index, false);
    }

    private void ToggleAt(int index)
    {
        SetFocus(index);
        if (index < 0 || index >= eligible.Count || !eligible[index]) return;
        if (!picked[index] && CountPicked() >= maxPick) return;
        picked[index] = !picked[index];
        cards[index].EnableInClassList("exp-card--on", picked[index]);
        UpdateGoButton();
        RefreshTeam();
    }

    private int CountPicked()
    {
        int n = 0;
        for (int i = 0; i < picked.Count; i++)
            if (picked[i]) n++;
        return n;
    }

    private void SetFocus(int index, bool scroll = true)
    {
        focused = UiPanels.ClampSelection(cards.Count, index);
        UiPanels.SetActiveIndex(cards, focused, "exp-card--focus");
        if (scroll && focused >= 0) list?.ScrollTo(cards[focused]);
        RefreshDetail();
    }

    private void RefreshDetail()
    {
        if (detail == null) return;
        detail.style.display = focused >= 0 ? DisplayStyle.Flex : DisplayStyle.None;
        if (focused >= 0) ExpeditionCardBuilder.FillDetail(detail, dnas[focused], profiles[focused]);
    }

    private void RefreshTeam()
    {
        if (team != null) ExpeditionCardBuilder.FillTeam(team, profiles, picked);
    }

    private void UpdateGoButton()
    {
        int count = CountPicked();
        if (goButton != null)
        {
            int cost = BrawlRunRulesSO.Current != null ? BrawlRunRulesSO.Current.DescentCost : 0;
            goButton.text = Loc.Tr("ui.expedition.go", count, maxPick) + (cost > 0 ? " · " + Loc.Tr("ui.expedition.cost", cost) : "");
            goButton.SetEnabled(count >= 1 && ExpeditionOpen && Wallet.Balance(Currency.Dabloons) >= cost);
        }
    }

    private void Depart()
    {
        if (CountPicked() < 1) return;

        var ids = new List<string>();
        for (int i = 0; i < picked.Count; i++)
            if (picked[i]) ids.Add(dnas[i].UniqueID);

        Close();
        ExpeditionBridge.RequestDeparture(ids);
    }

    private void Close() => UIManager.RequestPanelSet(panel, false);

    public void OnUINavigate(Vector2 dir)
    {
        if (!wired) return;
        if (dir.x > 0.5f) SetFocus(focused + 1);
        else if (dir.x < -0.5f) SetFocus(focused - 1);
    }

    public void OnUISubmit()
    {
        if (!wired || focused < 0) return;
        ToggleAt(focused);
    }

    public bool OnUICancel() => false;
}
}
