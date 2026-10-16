using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class StoragePanelUITK : MonoBehaviour, IUINavigable
{
    [SerializeField] private UIDocument document;
    [SerializeField] private UIPanelType panel = UIPanelType.Storage;
    [SerializeField] private ItemDatabaseSO database;

    private const int Columns         = 8;
    private const int MinRows         = 2;
    private const string SlotClass         = "storage-slot";
    private const string SlotFilledClass   = "storage-slot--filled";
    private const string SlotSelectedClass = "storage-slot--selected";

    private sealed class SlotView
    {
        public VisualElement Root;
        public VisualElement Icon;
        public Label Name;
        public Label Count;
    }

    private ScrollView grid;
    private VisualElement hotbarHost;
    private Label subtitle;
    private Button closeButton;

    private readonly List<VisualElement> filledSlots = new List<VisualElement>();
    private readonly List<string> slotIds = new List<string>();
    private int selectedIndex = -1;
    private PlayerInventorySO inventory;

    private void OnEnable()
    {
        inventory = GameManager.CurrentInventory;
        GameEvents.OnInventoryChanged  += Rebuild;
        GameEvents.OnInventoryReloaded += Rebuild;
        HotbarController.OnHotbarChanged += RebuildHotbar;
    }

    private void OnDisable()
    {
        GameEvents.OnInventoryChanged  -= Rebuild;
        GameEvents.OnInventoryReloaded -= Rebuild;
        HotbarController.OnHotbarChanged -= RebuildHotbar;
    }

    private void Start()
    {
        WireChrome();
        UIManager.RegisterNavigable(panel, this);
        RebuildFromInventory();
    }

    private void OnDestroy()
    {
        if (closeButton != null) closeButton.clicked -= OnCloseClicked;
        UIManager.UnregisterNavigable(panel);
    }

    public void OnUINavigate(Vector2 dir)
    {
        if (filledSlots.Count == 0) return;
        int idx = selectedIndex < 0 ? 0 : selectedIndex;
        if      (dir.x >  0.5f) idx += 1;
        else if (dir.x < -0.5f) idx -= 1;
        else if (dir.y < -0.5f) idx += Columns;
        else if (dir.y >  0.5f) idx -= Columns;
        Select(idx);
    }

    public void OnUISubmit() => EjectSelected();

    public bool OnUICancel() => false;

    private void Rebuild(PlayerInventorySO inv) { inventory = inv; RebuildFromInventory(); }

    private void RebuildFromInventory()
    {
        RebuildGrid();
        RebuildHotbar();
    }

    private void RebuildGrid()
    {
        var container = ResolveGrid();
        if (container == null) return;

        container.Clear();
        filledSlots.Clear();
        slotIds.Clear();

        var counts = new Dictionary<string, int>();
        var order  = new List<string>();
        if (inventory != null)
        {
            foreach (var id in inventory.WorldPropsStored)
            {
                if (string.IsNullOrEmpty(id)) continue;
                if (!counts.ContainsKey(id)) { counts[id] = 0; order.Add(id); }
                counts[id]++;
            }
        }

        foreach (var id in order)
        {
            var view = BuildSlot();
            Fill(view, id, counts[id]);
            string captured = id;
            view.Root.AddToClassList(SlotFilledClass);
            view.Root.RegisterCallback<ClickEvent>(_ => Eject(captured));
            filledSlots.Add(view.Root);
            slotIds.Add(id);
            container.Add(view.Root);
        }

        int rows  = Mathf.Max(MinRows, Mathf.CeilToInt(order.Count / (float)Columns));
        int total = rows * Columns;
        for (int i = order.Count; i < total; i++)
            container.Add(BuildSlot().Root);

        if (subtitle != null)
            subtitle.text = order.Count == 1 ? Loc.Tr("ui.storage.count.one") : Loc.Tr("ui.storage.count.many", order.Count);

        Select(filledSlots.Count == 0 ? -1 : Mathf.Clamp(selectedIndex, 0, filledSlots.Count - 1));
    }

    private void RebuildHotbar()
    {
        var host = ResolveHotbar();
        if (host == null) return;

        host.Clear();
        for (int i = 0; i < PlayerInventorySO.HotbarSize; i++)
        {
            var view = BuildSlot();
            string id = inventory != null ? inventory.GetHotbarSlot(i) : null;
            if (!string.IsNullOrEmpty(id)) Fill(view, id, 0);
            host.Add(view.Root);
        }
    }

    private static SlotView BuildSlot()
    {
        var root = new VisualElement();
        root.AddToClassList(SlotClass);

        var box = new VisualElement();
        box.AddToClassList("storage-slot__box");
        box.pickingMode = PickingMode.Ignore;
        root.Add(box);

        var runes = new VisualElement();
        runes.AddToClassList("storage-slot__runes");
        runes.pickingMode = PickingMode.Ignore;
        box.Add(runes);

        var icon = new VisualElement();
        icon.AddToClassList("storage-slot__icon");
        icon.pickingMode = PickingMode.Ignore;
        box.Add(icon);

        var name = new Label("");
        name.AddToClassList("storage-slot__name");
        name.pickingMode = PickingMode.Ignore;
        box.Add(name);

        var count = new Label("");
        count.AddToClassList("storage-slot__count");
        count.pickingMode = PickingMode.Ignore;
        box.Add(count);

        var frame = new VisualElement();
        frame.AddToClassList("storage-slot__frame");
        frame.pickingMode = PickingMode.Ignore;
        box.Add(frame);

        return new SlotView { Root = root, Icon = icon, Name = name, Count = count };
    }

    private void Fill(SlotView view, string id, int count)
    {
        var def = database != null ? database.GetByID(id) : null;
        if (def != null && def.Icon != null)
            view.Icon.style.backgroundImage = new StyleBackground(def.Icon);
        else
            view.Name.text = def != null ? DataLoc.ItemName(def) : id;

        if (count > 0) view.Count.text = $"×{count}";
    }

    private void Eject(string id)
    {
        if (StorageContainer.Instance == null)
        {
            Debug.LogWarning("[StoragePanelUITK] No StorageContainer in scene to eject from.");
            return;
        }
        StorageContainer.Instance.Eject(id);
    }

    private void EjectSelected()
    {
        if (selectedIndex >= 0 && selectedIndex < slotIds.Count)
            Eject(slotIds[selectedIndex]);
    }

    private void Select(int idx)
    {
        selectedIndex = UiPanels.ClampSelection(filledSlots.Count, idx);
        if (selectedIndex < 0) return;
        UiPanels.SetActiveIndex(filledSlots, selectedIndex, SlotSelectedClass);
    }

    private void WireChrome()
    {
        var root = UiPanels.RootOf(document);
        if (root == null) return;
        closeButton = root.Q<Button>("close-button");
        subtitle    = root.Q<Label>("subtitle");

        SetLabelText(root, "title", "ui.storage.title");
        SetLabelText(root, "section-box", "ui.storage.section.box");
        SetLabelText(root, "section-hotbar", "ui.storage.section.hotbar");
        SetLabelText(root, "prompt-move", "ui.prompt.move");
        SetLabelText(root, "prompt-take", "ui.storage.prompt.take");
        SetLabelText(root, "prompt-close", "ui.prompt.close");

        if (closeButton != null) closeButton.clicked += OnCloseClicked;
    }

    private static void SetLabelText(VisualElement root, string name, string key)
    {
        var label = root.Q<Label>(name);
        if (label != null) label.text = Loc.Tr(key);
    }

    private void OnCloseClicked() => UIManager.RequestPanelToggle(panel);

    private ScrollView ResolveGrid()
    {
        if (grid != null && grid.panel != null) return grid;
        var root = UiPanels.RootOf(document);
        if (root == null) return null;
        grid = root.Q<ScrollView>("grid");
        return grid;
    }

    private VisualElement ResolveHotbar()
    {
        if (hotbarHost != null && hotbarHost.panel != null) return hotbarHost;
        var root = UiPanels.RootOf(document);
        if (root == null) return null;
        hotbarHost = root.Q<VisualElement>("hotbar");
        return hotbarHost;
    }
}
}
