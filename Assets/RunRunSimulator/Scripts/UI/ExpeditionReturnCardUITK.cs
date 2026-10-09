using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class ExpeditionReturnCardUITK : MonoBehaviour, IUINavigable
{
    [SerializeField] private UIDocument document;
    [SerializeField] private UIPanelType panel = UIPanelType.ExpeditionReturn;

    private Label titleLabel;
    private Label mineritaLabel;
    private Label roomsLabel;
    private Label lostLabel;
    private Label noExplorationLabel;
    private VisualElement teamRow;
    private Button continueButton;

    private ExpeditionReturn? pending;
    private bool wired;

    private void OnEnable() => GameEvents.OnExpeditionReturned += OnExpeditionReturned;

    private void OnDisable() => GameEvents.OnExpeditionReturned -= OnExpeditionReturned;

    private void Start()
    {
        var root = UiPanels.RootOf(document);
        if (root == null) return;

        titleLabel = root.Q<Label>("ret-title");
        mineritaLabel = root.Q<Label>("ret-minerita");
        roomsLabel = root.Q<Label>("ret-rooms");
        lostLabel = root.Q<Label>("ret-lost");
        noExplorationLabel = root.Q<Label>("ret-noexploration");
        teamRow = root.Q<VisualElement>("ret-team");

        continueButton = root.Q<Button>("ret-continue");
        if (continueButton != null)
        {
            continueButton.text = Loc.Tr("ui.return.continue");
            continueButton.clicked += Close;
        }

        wired = true;
        UIManager.RegisterNavigable(panel, this);
    }

    private void OnDestroy()
    {
        if (continueButton != null) continueButton.clicked -= Close;
        UIManager.UnregisterNavigable(panel);
    }

    private void OnExpeditionReturned(ExpeditionReturn r)
    {
        pending = r;
        StartCoroutine(ShowNextFrames());
    }

    private IEnumerator ShowNextFrames()
    {
        yield return null;
        yield return null;

        if (!wired || !pending.HasValue) yield break;

        var r = pending.Value;
        pending = null;
        Show(r);
    }

    private void Show(ExpeditionReturn r)
    {
        titleLabel.text = Loc.Tr(r.Lost ? "ui.return.title.lost" : "ui.return.title.ok");
        titleLabel.EnableInClassList("ret-title--lost", r.Lost);

        mineritaLabel.text = Loc.Tr("ui.return.minerita", r.MineritaGained);
        roomsLabel.text = Loc.Tr("ui.return.rooms", r.Floors);

        lostLabel.text = Loc.Tr("ui.return.lost", r.MineritaLost);
        SetVisible(lostLabel, r.Lost && r.MineritaLost > 0);

        BuildTeam(r);

        noExplorationLabel.text = Loc.Tr("ui.return.noexploration");
        SetVisible(noExplorationLabel, r.Lost && HasSlime(r.Team));

        UIManager.RequestPanelSet(panel, true);
    }

    private void BuildTeam(ExpeditionReturn r)
    {
        teamRow.Clear();
        if (r.Team == null) return;

        foreach (var dna in r.Team)
        {
            if (dna == null) continue;
            bool grew = r.EvolvedIds != null && r.EvolvedIds.Contains(dna.UniqueID);
            teamRow.Add(BuildMember(dna, grew, r.ExplorationsToEvolve));
        }
    }

    private VisualElement BuildMember(CreatureDNA dna, bool grew, int explorationsToEvolve)
    {
        var card = new VisualElement();
        card.AddToClassList("ret-card");
        card.EnableInClassList("ret-card--grew", grew);

        var icon = new VisualElement();
        icon.AddToClassList("ret-card__icon");
        MonchiPortraitUI.Apply(icon, dna);
        card.Add(icon);

        var name = new Label(dna.CustomName);
        name.AddToClassList("ret-card__name");
        card.Add(name);

        if (grew)
        {
            var growth = new VisualElement();
            growth.AddToClassList("ret-card__growth");
            var badge = new Label(Loc.Tr("ui.return.grew"));
            badge.AddToClassList("ret-badge");
            growth.Add(badge);
            card.Add(growth);
        }
        else if (dna.Form == MonchiForm.Slime)
        {
            var growth = new VisualElement();
            growth.AddToClassList("ret-card__growth");
            growth.Add(BuildPips(dna.Explorations, explorationsToEvolve));
            card.Add(growth);
        }

        return card;
    }

    private static VisualElement BuildPips(int explorations, int explorationsToEvolve)
    {
        var pips = new VisualElement();
        pips.AddToClassList("ret-pips");

        int total = Mathf.Max(0, explorationsToEvolve);
        int filled = Mathf.Clamp(explorations, 0, total);
        for (int i = 0; i < total; i++)
        {
            var pip = new VisualElement();
            pip.AddToClassList("ret-pip");
            pip.EnableInClassList("ret-pip--on", i < filled);
            pips.Add(pip);
        }

        return pips;
    }

    private static bool HasSlime(List<CreatureDNA> team)
    {
        if (team == null) return false;
        foreach (var dna in team)
            if (dna != null && dna.Form == MonchiForm.Slime) return true;
        return false;
    }

    private static void SetVisible(VisualElement element, bool visible) =>
        element.style.display = visible ? DisplayStyle.Flex : DisplayStyle.None;

    private void Close() => UIManager.RequestPanelSet(panel, false);

    public void OnUINavigate(Vector2 dir) { }

    public void OnUISubmit()
    {
        if (!wired) return;
        Close();
    }

    public bool OnUICancel() => false;
}
}
