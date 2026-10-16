using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
public class BrawlRunPanel : MonoBehaviour
{
    [Required, SerializeField] private UIDocument document;
    [Required, SerializeField] private BrawlRunDirector director;
    [Required, SerializeField] private BrawlRoomGlyphsSO glyphs;

    private VisualElement boundRoot;
    private VisualElement root;
    private VisualElement cardWrap;
    private VisualElement cardRooms;
    private VisualElement teamRow;
    private Label title;
    private Label info;
    private Label minerita;
    private Button goButton;
    private Button leaveButton;

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
        if (docRoot == null || director == null || glyphs == null) return false;
        if (root != null && docRoot == boundRoot) return true;

        Unbind();
        var found = docRoot.Q("run-root");
        if (found == null) return false;

        boundRoot = docRoot;
        root = found;
        cardWrap = root.Q("run-card-wrap");
        cardRooms = root.Q("run-rooms");
        title = root.Q<Label>("run-title");
        teamRow = root.Q("run-team");
        info = root.Q<Label>("run-info");
        minerita = MakeLabel("", "run-minerita");
        info.parent.Insert(info.parent.IndexOf(info), minerita);
        goButton = root.Q<Button>("run-go");
        leaveButton = root.Q<Button>("run-leave");

        goButton.clicked += OnGoClicked;
        leaveButton.clicked += OnLeaveClicked;

        Refresh();
        return true;
    }

    private void Unbind()
    {
        if (root != null)
        {
            goButton.clicked -= OnGoClicked;
            leaveButton.clicked -= OnLeaveClicked;
            cardRooms.Clear();
            teamRow.Clear();
        }

        boundRoot = null;
        root = null;
    }

    private void HandleChanged()
    {
        if (TryBind()) Refresh();
    }

    private void OnGoClicked()
    {
        if (director.State == BrawlRunState.Planning) director.AcceptTramo();
    }

    private void OnLeaveClicked() => director.Leave();

    private void Refresh()
    {
        var run = director.Active ? director.Run : null;
        var state = director.State;
        bool show = run != null && run.Depth > 0 && (state == BrawlRunState.Planning || state == BrawlRunState.Over);
        SetVisible(cardWrap, show);
        if (!show) return;

        RefreshCard(run);
    }

    private void RefreshCard(BrawlRun run)
    {
        BuildChips(cardRooms, run);

        switch (director.State)
        {
            case BrawlRunState.Planning:
                title.text = Loc.Tr("ui.brawl.run.plan.title", run.Depth, run.Rooms.Count);
                minerita.text = Loc.Tr("ui.brawl.run.minerita", Minerita(run.Material));
                BuildTeam(run);
                goButton.text = Loc.Tr("ui.brawl.run.go");
                leaveButton.text = run.Depth == 1 && run.Material == 0 ? Loc.Tr("ui.brawl.run.leave.shop") : Loc.Tr("ui.brawl.run.leave.cash", Minerita(run.Material));
                SetVisible(teamRow, true);
                SetVisible(info, false);
                SetVisible(goButton, true);
                SetVisible(leaveButton, true);
                break;
            default:
                title.text = Loc.Tr("ui.brawl.run.lost.title");
                minerita.text = run.MaterialLost > 0
                    ? Loc.Tr("ui.brawl.run.lost.loot", Minerita(run.MaterialLost), Minerita(run.Material))
                    : Loc.Tr("ui.brawl.run.lost.none");
                leaveButton.text = Loc.Tr("ui.brawl.run.leave.shop");
                SetVisible(teamRow, false);
                SetVisible(info, false);
                SetVisible(goButton, false);
                SetVisible(leaveButton, true);
                break;
        }
    }

    private static int Minerita(int loot)
    {
        var rules = BrawlRunRulesSO.Current;
        return loot * (rules != null ? rules.MineritaPerLoot : 1);
    }

    private void BuildTeam(BrawlRun run)
    {
        teamRow.Clear();
        var team = director.Team;
        if (team == null) return;

        for (int i = 0; i < team.Count; i++)
        {
            var dna = team[i];
            if (dna == null) continue;
            float health = run.Health01(dna.UniqueID);

            var member = Element("run-member");
            if (health < 0.999f) member.AddToClassList("run-member--hurt");

            var portrait = Element("run-member__portrait");
            var photo = Element("run-member__photo");
            MonchiPortraitUI.Apply(photo, dna);
            portrait.Add(photo);
            portrait.Add(Element("run-member__frame"));
            member.Add(portrait);

            string name = string.IsNullOrEmpty(dna.CustomName) ? "MoriMochi" : dna.CustomName;
            member.Add(MakeLabel(name, "run-member__name"));

            var bar = Element("run-member__bar");
            var fill = Element("run-member__fill");
            fill.style.width = Length.Percent(health * 100f);
            bar.Add(fill);
            member.Add(bar);

            member.Add(MakeLabel(Mathf.RoundToInt(health * 100f) + " %", "run-member__pct"));
            teamRow.Add(member);
        }
    }

    private void BuildChips(VisualElement container, BrawlRun run)
    {
        container.Clear();
        var rooms = run.Rooms;
        for (int i = 0; i < rooms.Count; i++)
        {
            var room = rooms[i];

            var chip = Element("run-room");
            chip.AddToClassList(i < run.RoomIndex ? "run-room--done" : i == run.RoomIndex ? "run-room--current" : "run-room--upcoming");
            chip.Add(Element("run-room__runes"));
            chip.Add(Element("run-room__frame"));

            var glyph = Element("run-room__glyph");
            var sprite = glyphs.For(room);
            if (sprite != null) glyph.style.backgroundImage = new StyleBackground(sprite);
            glyph.AddToClassList(room.Kind switch
            {
                BrawlRoomKind.Combat => "run-glyph--foe",
                BrawlRoomKind.Dummies => "run-glyph--heal",
                _ => "run-glyph--mineral"
            });
            chip.Add(glyph);
            container.Add(chip);
        }
    }

    private static void SetVisible(VisualElement element, bool visible) =>
        element.style.display = visible ? DisplayStyle.Flex : DisplayStyle.None;

    private static VisualElement Element(string className)
    {
        var element = new VisualElement { pickingMode = PickingMode.Ignore };
        element.AddToClassList(className);
        return element;
    }

    private static Label MakeLabel(string text, string className)
    {
        var label = new Label(text) { pickingMode = PickingMode.Ignore };
        label.AddToClassList(className);
        return label;
    }
}
}
