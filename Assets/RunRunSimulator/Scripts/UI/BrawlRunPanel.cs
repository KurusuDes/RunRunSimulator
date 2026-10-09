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
                title.text = "Tramo " + run.Depth + " · " + run.Rooms.Count + " salas";
                minerita.text = "Minerita: " + Minerita(run.Material);
                info.text = HealthLine(run);
                goButton.text = "Enfrentar tramo";
                leaveButton.text = run.Depth == 1 && run.Material == 0 ? "Volver a la tienda" : "Salir con " + Minerita(run.Material) + " Minerita";
                SetVisible(info, true);
                SetVisible(goButton, true);
                SetVisible(leaveButton, true);
                break;
            default:
                title.text = "Perdiste el combate";
                minerita.text = run.MaterialLost > 0
                    ? "Se pierden " + Minerita(run.MaterialLost) + " Minerita · te llevas " + Minerita(run.Material)
                    : "Sin botín que perder";
                leaveButton.text = "Volver a la tienda";
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

    private string HealthLine(BrawlRun run)
    {
        var team = director.Team;
        if (team == null) return "";

        string line = "";
        for (int i = 0; i < team.Count; i++)
        {
            var dna = team[i];
            if (dna == null) continue;
            string name = string.IsNullOrEmpty(dna.CustomName) ? "MoriMochi" : dna.CustomName;
            if (line.Length > 0) line += " · ";
            line += name + " " + Mathf.RoundToInt(run.Health01(dna.UniqueID) * 100f) + " %";
        }
        return line;
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
