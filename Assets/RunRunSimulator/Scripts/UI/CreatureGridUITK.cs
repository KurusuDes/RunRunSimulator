using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class CreatureGridUITK : MonoBehaviour, IUINavigable
{
    [Header("UI Toolkit setup")]

    [SerializeField] private UIDocument document;

    [SerializeField] private UIPanelType panel = UIPanelType.CreatureGrid;

    [Header("Data")]

    [SerializeField] private CreatureDatabaseSO database;

    [SerializeField] private CareGateSO careGate;

    [SerializeField] private BrawlKitDatabaseSO kits;

    [SerializeField] private EvolutionEffectSO evolution;

    private enum GridFilter { All, Adult, Slime, Egg }

    private const string SelectedClass = "tile--selected";
    private const int Columns = 5;

    private ScrollView scroll;
    private Button closeButton;
    private Button openButton;
    private Label sideName, countLabel, emptyLabel;
    private VisualElement portrait;
    private DetailInfoTabPresenter presenter;
    private bool wired;

    private readonly List<VisualElement> tiles = new List<VisualElement>();
    private readonly List<Button> filterButtons = new List<Button>();
    private CreatureRegistrySO currentRegistry;
    private GridFilter filter = GridFilter.All;
    private int selectedIndex = -1;

    private void OnEnable()
    {
        GameEvents.OnRegistryChanged  += Rebuild;
        GameEvents.OnRegistryReloaded += Rebuild;
        UIManager.OnPanelVisibilityChanged += OnPanelVisibility;
    }

    private void OnDisable()
    {
        GameEvents.OnRegistryChanged  -= Rebuild;
        GameEvents.OnRegistryReloaded -= Rebuild;
        UIManager.OnPanelVisibilityChanged -= OnPanelVisibility;
    }

    private void Start()
    {
        Wire();
        UIManager.RegisterNavigable(panel, this);
    }

    private void OnDestroy()
    {
        if (closeButton != null) closeButton.clicked -= OnCloseClicked;
        if (openButton != null) openButton.clicked -= OpenSelected;
        UIManager.UnregisterNavigable(panel);
    }

    public void OnUINavigate(Vector2 dir)
    {
        if (tiles.Count == 0) return;
        int idx = selectedIndex < 0 ? 0 : selectedIndex;

        if      (dir.x >  0.5f) idx += 1;
        else if (dir.x < -0.5f) idx -= 1;
        else if (dir.y < -0.5f) idx += Columns;
        else if (dir.y >  0.5f) idx -= Columns;

        Select(idx);
    }

    public void OnUISubmit() => OpenSelected();

    public bool OnUICancel() => false;

    private void Wire()
    {
        if (wired) return;
        var root = UiPanels.RootOf(document);
        if (root == null) return;

        scroll       = root.Q<ScrollView>("grid-container");
        sideName     = root.Q<Label>("side-name");
        countLabel   = root.Q<Label>("grid-count");
        emptyLabel   = root.Q<Label>("grid-empty");
        portrait     = root.Q<VisualElement>("portrait");
        closeButton  = root.Q<Button>("close-button");
        openButton   = root.Q<Button>("open-detail");

        if (closeButton != null) closeButton.clicked += OnCloseClicked;
        if (openButton != null)
        {
            openButton.text = Loc.Tr("ui.prompt.open");
            openButton.clicked += OpenSelected;
        }

        SetLabelText(root, "grid-title", "ui.grid.title");
        SetLabelText(root, "grid-empty", "ui.grid.empty");
        SetLabelText(root, "care-title", "ui.detail.section.care");
        SetLabelText(root, "need-health-label", "ui.detail.need.health");
        SetLabelText(root, "need-energy-label", "ui.detail.need.energy");
        SetLabelText(root, "need-affect-label", "ui.detail.need.affect");
        SetLabelText(root, "prompt-move", "ui.prompt.move");
        SetLabelText(root, "prompt-open", "ui.prompt.open");
        SetLabelText(root, "prompt-close", "ui.prompt.close");

        BuildFilters(root.Q<VisualElement>("grid-filters"));

        presenter = new DetailInfoTabPresenter(root, database, careGate, kits, evolution, () => currentRegistry);
        wired = true;
    }

    private static void SetLabelText(VisualElement root, string name, string key)
    {
        var label = root.Q<Label>(name);
        if (label != null) label.text = Loc.Tr(key);
    }

    private void BuildFilters(VisualElement host)
    {
        if (host == null) return;
        host.Clear();
        filterButtons.Clear();

        AddFilter(host, GridFilter.All, "ui.grid.filter.all");
        AddFilter(host, GridFilter.Adult, "ui.grid.filter.adult");
        AddFilter(host, GridFilter.Slime, "ui.grid.filter.slime");
        AddFilter(host, GridFilter.Egg, "ui.grid.filter.egg");
        RefreshFilterButtons();
    }

    private void AddFilter(VisualElement host, GridFilter value, string key)
    {
        var button = new Button { text = Loc.Tr(key) };
        button.AddToClassList("mm-button");
        button.AddToClassList("mm-button--alt");
        button.AddToClassList("filter-button");
        button.clicked += () => SetFilter(value);
        button.userData = value;
        filterButtons.Add(button);
        host.Add(button);
    }

    private void RefreshFilterButtons()
    {
        foreach (var b in filterButtons)
            b.EnableInClassList("mm-button--selected", (GridFilter)b.userData == filter);
    }

    private void SetFilter(GridFilter value)
    {
        if (filter == value) return;
        filter = value;
        RefreshFilterButtons();
        selectedIndex = -1;
        Rebuild(currentRegistry);
    }

    private bool Passes(CreatureDNA dna) => filter switch
    {
        GridFilter.Adult => dna.Form == MonchiForm.Adult,
        GridFilter.Slime => dna.Form == MonchiForm.Slime,
        GridFilter.Egg   => dna.Form == MonchiForm.Egg,
        _                => true,
    };

    private void Rebuild(CreatureRegistrySO registry)
    {
        Wire();
        if (!wired || scroll == null || registry == null) return;

        currentRegistry = registry;
        scroll.Clear();
        tiles.Clear();

        foreach (var dna in registry.GetAll().Values.Where(Passes).OrderByDescending(d => d.BirthDate))
        {
            var tile = BuildTile(dna);
            tiles.Add(tile);
            scroll.Add(tile);
        }

        if (countLabel != null) countLabel.text = Loc.Tr("ui.grid.count", tiles.Count);
        if (emptyLabel != null) emptyLabel.style.display = tiles.Count == 0 ? DisplayStyle.Flex : DisplayStyle.None;

        Select(selectedIndex < 0 ? 0 : selectedIndex, scrollIntoView: false);
    }

    private VisualElement BuildTile(CreatureDNA dna)
    {
        var tile = new VisualElement { userData = dna };
        tile.AddToClassList("mm-slot");
        tile.AddToClassList("tile");

        var vignette = new VisualElement { pickingMode = PickingMode.Ignore };
        vignette.AddToClassList("mm-layer");
        vignette.AddToClassList("mm-slot__vignette");
        tile.Add(vignette);

        var icon = new VisualElement { pickingMode = PickingMode.Ignore };
        icon.AddToClassList("tile__icon");
        MonchiPortraitUI.Apply(icon, dna);
        tile.Add(icon);

        bool ready = careGate != null && CreatureAvailability.CanExplore(dna, careGate);
        var dot = new VisualElement { pickingMode = PickingMode.Ignore };
        dot.AddToClassList("tile__dot");
        dot.AddToClassList(ready ? "tile__dot--ready" : "tile__dot--blocked");
        tile.Add(dot);

        var frame = new VisualElement { pickingMode = PickingMode.Ignore };
        frame.AddToClassList("mm-layer");
        frame.AddToClassList("mm-slot__frame");
        frame.AddToClassList("tile__frame");
        tile.Add(frame);

        tile.RegisterCallback<ClickEvent>(evt =>
        {
            Select(tiles.IndexOf(tile));
            if (evt.clickCount == 2) OpenSelected();
        });

        return tile;
    }

    private void Select(int idx, bool scrollIntoView = true)
    {
        selectedIndex = UiPanels.ClampSelection(tiles.Count, idx);
        if (selectedIndex < 0)
        {
            if (sideName != null) sideName.text = string.Empty;
            return;
        }

        UiPanels.SetActiveIndex(tiles, selectedIndex, SelectedClass);

        if (scrollIntoView && scroll != null)
            scroll.ScrollTo(tiles[selectedIndex]);

        if (tiles[selectedIndex].userData is CreatureDNA dna)
            ShowSelected(dna);
    }

    private void ShowSelected(CreatureDNA dna)
    {
        if (sideName != null)
            sideName.text = string.IsNullOrEmpty(dna.CustomName) ? dna.ToStringID() : dna.CustomName;

        presenter?.Rebuild(dna);

        var root = UiPanels.RootOf(document);
        if (portrait != null && root != null && root.resolvedStyle.display != DisplayStyle.None)
            MonchiPortraitUI.ApplyLive(portrait, dna);
    }

    private void OnPanelVisibility(UIPanelType type, bool visible)
    {
        if (type != panel || !visible || portrait == null) return;
        if (selectedIndex < 0 || selectedIndex >= tiles.Count) return;
        if (tiles[selectedIndex].userData is CreatureDNA dna)
            MonchiPortraitUI.ApplyLive(portrait, dna);
    }

    private void OpenSelected()
    {
        if (selectedIndex < 0 || selectedIndex >= tiles.Count) return;
        if (tiles[selectedIndex].userData is CreatureDNA dna)
            UIManager.SelectCreature(dna, currentRegistry);
    }

    private void OnCloseClicked() => UIManager.RequestPanelToggle(panel);
}
}
