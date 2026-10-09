using System.Globalization;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
public class BrawlRunPanel : MonoBehaviour
{
    private static readonly string[] RivalClasses = { "run-room--vs0", "run-room--vs1", "run-room--vs2", "run-room--vs3" };
    private static readonly NumberFormatInfo GroupFormat = new NumberFormatInfo { NumberGroupSeparator = "." };

    [Required, SerializeField] private UIDocument document;
    [Required, SerializeField] private BrawlRunDirector director;
    [SerializeField] private BrawlTrialRoom trial;
    [SerializeField] private Sprite combatIcon;
    [SerializeField] private Sprite dummiesIcon;
    [SerializeField] private Sprite mineralsIcon;

    private VisualElement boundRoot;
    private VisualElement root;
    private VisualElement strip;
    private VisualElement stripRooms;
    private VisualElement card;
    private VisualElement cardRooms;
    private Label stripTitle;
    private Label stripTrial;
    private Label title;
    private Label info;
    private Button goButton;
    private Button leaveButton;
    private bool lastTrialActive;
    private int lastTrialSeconds = -1;
    private int lastTrialDamage = -1;

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

        boundRoot = docRoot;
        root = found;
        strip = root.Q("run-strip");
        stripRooms = root.Q("run-strip-rooms");
        stripTitle = root.Q<Label>("run-strip-title");
        stripTrial = root.Q<Label>("run-strip-trial");
        card = root.Q("run-card");
        cardRooms = root.Q("run-rooms");
        title = root.Q<Label>("run-title");
        info = root.Q<Label>("run-info");
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
            stripRooms.Clear();
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
        else if (director.State == BrawlRunState.RoomResult) director.NextRoom();
    }

    private void OnLeaveClicked() => director.Leave();

    private void Update()
    {
        if (!TryBind()) return;
        RefreshTrial();
    }

    private void Refresh()
    {
        var run = director.Active ? director.Run : null;
        bool show = run != null && run.Depth > 0;
        SetVisible(root, show);
        if (!show) return;

        bool fighting = director.State == BrawlRunState.Fighting;
        SetVisible(strip, fighting);
        SetVisible(card, !fighting);
        if (fighting) RefreshStrip(run);
        else RefreshCard(run);
    }

    private void RefreshStrip(BrawlRun run)
    {
        int count = run.Rooms.Count;
        int shown = Mathf.Clamp(run.RoomIndex + 1, 1, Mathf.Max(1, count));
        stripTitle.text = "Tramo " + run.Depth + " · Sala " + shown + "/" + count;
        BuildChips(stripRooms, run, true);

        lastTrialSeconds = -1;
        RefreshTrial();
    }

    private void RefreshTrial()
    {
        if (trial == null || !director.Active || director.State != BrawlRunState.Fighting) return;

        bool active = trial.Active;
        int seconds = active ? Mathf.CeilToInt(trial.TimeLeft) : 0;
        int damage = active && trial.Kind == BrawlRoomKind.Minerals ? Mathf.RoundToInt(trial.Damage) : 0;
        if (active == lastTrialActive && seconds == lastTrialSeconds && damage == lastTrialDamage) return;

        lastTrialActive = active;
        lastTrialSeconds = seconds;
        lastTrialDamage = damage;
        SetVisible(stripTrial, active);
        if (!active) return;

        stripTrial.text = trial.Kind == BrawlRoomKind.Minerals
            ? "Minerales: " + seconds + " s · daño " + damage.ToString("N0", GroupFormat)
            : "Muñecos: " + seconds + " s";
    }

    private void RefreshCard(BrawlRun run)
    {
        BuildChips(cardRooms, run, false);

        switch (director.State)
        {
            case BrawlRunState.Planning:
                title.text = "Tramo " + run.Depth + " · " + run.Rooms.Count + " salas";
                info.text = "Botín: " + run.Material + "\n" + HealthLine(run);
                goButton.text = "Enfrentar tramo";
                leaveButton.text = run.Depth == 1 && run.Material == 0 ? "Volver a la tienda" : "Salir con " + run.Material + " de botín";
                SetVisible(goButton, true);
                SetVisible(leaveButton, true);
                break;
            case BrawlRunState.RoomResult:
                title.text = director.LastRoomSummary;
                info.text = "Botín: " + run.Material + "\n" + HealthLine(run);
                goButton.text = run.TramoDone ? "Ver el próximo tramo" : "Siguiente sala";
                SetVisible(goButton, true);
                SetVisible(leaveButton, false);
                break;
            default:
                title.text = "Perdiste el combate";
                info.text = "Se pierden " + run.MaterialLost + " de botín · te llevás " + run.Material;
                leaveButton.text = "Volver a la tienda";
                SetVisible(goButton, false);
                SetVisible(leaveButton, true);
                break;
        }
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

    private void BuildChips(VisualElement container, BrawlRun run, bool small)
    {
        container.Clear();
        var rooms = run.Rooms;
        for (int i = 0; i < rooms.Count; i++)
        {
            var room = rooms[i];
            bool combat = room.Kind == BrawlRoomKind.Combat;

            var chip = Element("run-room");
            if (small) chip.AddToClassList("run-room--small");
            chip.AddToClassList(i < run.RoomIndex ? "run-room--done" : i == run.RoomIndex ? "run-room--current" : "run-room--upcoming");
            chip.AddToClassList(RivalClasses[combat ? Mathf.Clamp(room.Rivals, 1, 3) : 0]);

            var icons = Element("run-room__icons");
            switch (room.Kind)
            {
                case BrawlRoomKind.Combat:
                    AddIcons(icons, combatIcon, Mathf.Max(1, room.Rivals));
                    break;
                case BrawlRoomKind.Dummies:
                    AddIcons(icons, dummiesIcon, 1);
                    break;
                default:
                    AddIcons(icons, mineralsIcon, 1);
                    break;
            }
            chip.Add(icons);

            string label = room.Kind switch
            {
                BrawlRoomKind.Combat => "VS " + room.Rivals,
                BrawlRoomKind.Dummies => "Muñecos",
                _ => "Minerales"
            };
            chip.Add(MakeLabel(label, "run-room__label"));
            container.Add(chip);
        }
    }

    private static void AddIcons(VisualElement icons, Sprite sprite, int count)
    {
        for (int i = 0; i < count; i++)
        {
            var icon = Element("run-room__icon");
            if (sprite != null) icon.style.backgroundImage = new StyleBackground(sprite);
            else icon.AddToClassList("run-room__icon--empty");
            icons.Add(icon);
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
