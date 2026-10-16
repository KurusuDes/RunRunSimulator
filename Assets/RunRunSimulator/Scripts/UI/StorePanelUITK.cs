using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class StorePanelUITK : MonoBehaviour, IUINavigable
{
    [SerializeField] private UIDocument document;
    [SerializeField] private UIPanelType panel = UIPanelType.Store;
    [SerializeField] private StoreManager store;

    private static readonly StoreRows.Tab[] Tabs = (StoreRows.Tab[])Enum.GetValues(typeof(StoreRows.Tab));

    private const string CatActiveClass   = "store-cat--active";
    private const string TileSelectedClass = "store-tile--selected";

    private VisualElement   tabsContainer;
    private ScrollView      grid;
    private Label           emptyLabel;
    private Label           balanceLabel;
    private Label           notifyLabel;
    private Button          closeButton;
    private StoreDetailCard detail;

    private readonly List<VisualElement> tabEls  = new List<VisualElement>();
    private readonly List<VisualElement> tileEls = new List<VisualElement>();
    private readonly List<StoreRows.Row> rows    = new List<StoreRows.Row>();

    private int activeTab;
    private int selectedRow = -1;
    private bool discountActive;
    private Coroutine notifyCoroutine;

    private ShopCatalogSO Catalog => store != null ? store.Catalog : null;

    private void OnEnable()
    {
        UIManager.OnPanelToggleRequested += OnPanelToggle;
        UIManager.OnPanelSetRequested    += OnPanelSet;
        GameEvents.OnInventoryChanged    += OnInventoryChanged;
        GameEvents.OnInventoryReloaded   += OnInventoryChanged;
    }

    private void OnDisable()
    {
        UIManager.OnPanelToggleRequested -= OnPanelToggle;
        UIManager.OnPanelSetRequested    -= OnPanelSet;
        GameEvents.OnInventoryChanged    -= OnInventoryChanged;
        GameEvents.OnInventoryReloaded   -= OnInventoryChanged;
    }

    private void Start()
    {
        Resolve();
        BuildTabs();
        UIManager.RegisterNavigable(panel, this);

        var inv = GameManager.CurrentInventory;
        RefreshBalance(inv);
        Rebuild();
    }

    private void OnDestroy()
    {
        if (closeButton != null) closeButton.clicked -= OnCloseClicked;
        if (detail != null) detail.BuyButton.clicked -= BuySelected;
        UIManager.UnregisterNavigable(panel);
    }

    private void OnPanelToggle(UIPanelType p) { if (p == panel) ResetAndRebuild(); }
    private void OnPanelSet(UIPanelType p, bool show) { if (p == panel && show) ResetAndRebuild(); }

    private void OnInventoryChanged(PlayerInventorySO inv) => RefreshBalance(inv);

    private void ResetAndRebuild()
    {
        store?.RestockIfNeeded();
        activeTab = 0;
        selectedRow = 0;
        HighlightActiveTab();
        Rebuild();
    }

    public void OnUINavigate(Vector2 dir)
    {
        if      (dir.x >  0.5f) StepTab(1);
        else if (dir.x < -0.5f) StepTab(-1);
        else if (dir.y < -0.5f) StepRow(1);
        else if (dir.y >  0.5f) StepRow(-1);
    }

    public void OnUISubmit() => BuySelected();

    public bool OnUICancel() => false;

    private void RefreshBalance(PlayerInventorySO inv)
    {
        if (balanceLabel == null) return;
        balanceLabel.text = inv != null ? Loc.Tr("ui.store.balance", inv.Balance(Currency.Dabloons)) : "";
    }

    private void ShowNotify(string message)
    {
        if (notifyLabel == null) return;
        notifyLabel.text          = message;
        notifyLabel.style.display = DisplayStyle.Flex;
        if (notifyCoroutine != null) StopCoroutine(notifyCoroutine);
        notifyCoroutine = StartCoroutine(HideNotifyAfterDelay(2.5f));
    }

    private IEnumerator HideNotifyAfterDelay(float delay)
    {
        yield return new WaitForSecondsRealtime(delay);
        if (notifyLabel != null) notifyLabel.style.display = DisplayStyle.None;
        notifyCoroutine = null;
    }

    private void BuildTabs()
    {
        if (tabsContainer == null) return;
        tabsContainer.Clear();
        tabEls.Clear();

        for (int i = 0; i < Tabs.Length; i++)
        {
            int idx = i;
            var cat = new VisualElement();
            cat.AddToClassList("store-cat");

            var slot = new VisualElement { pickingMode = PickingMode.Ignore };
            slot.AddToClassList("mm-slot");
            slot.AddToClassList("store-cat__slot");
            var icon = new VisualElement { pickingMode = PickingMode.Ignore };
            icon.AddToClassList("store-icon");
            icon.AddToClassList("store-cat__icon");
            StoreTileView.ApplyIcon(icon, Tabs[i], null);
            slot.Add(icon);
            cat.Add(slot);

            var label = new Label(StoreRows.TabLabel(Tabs[i])) { pickingMode = PickingMode.Ignore };
            label.AddToClassList("store-cat__label");
            cat.Add(label);

            cat.RegisterCallback<ClickEvent>(_ => SetTab(idx));
            tabsContainer.Add(cat);
            tabEls.Add(cat);
        }
        HighlightActiveTab();
    }

    private void StepTab(int dir) =>
        SetTab(((activeTab + dir) % Tabs.Length + Tabs.Length) % Tabs.Length);

    private void SetTab(int idx)
    {
        activeTab = Mathf.Clamp(idx, 0, Tabs.Length - 1);
        selectedRow = 0;
        HighlightActiveTab();
        Rebuild();
    }

    private void HighlightActiveTab() => UiPanels.SetActiveIndex(tabEls, activeTab, CatActiveClass);

    private void Rebuild()
    {
        var container = ResolveGrid();
        if (container == null) return;

        container.Clear();
        tileEls.Clear();
        rows.Clear();

        var tab = (StoreRows.Tab)activeTab;
        StoreRows.Collect(tab, Catalog, store, rows);

        int today = GameClock.Instance != null ? GameClock.Instance.Day : 1;
        discountActive = Catalog?.IsDiscountActive(today) ?? false;

        for (int i = 0; i < rows.Count; i++)
        {
            int idx = i;
            var tile = StoreTileView.Build(tab, rows[i], discountActive, () => Select(idx), () => { Select(idx); BuySelected(); });
            tileEls.Add(tile);
            container.Add(tile);
        }

        if (emptyLabel != null)
        {
            emptyLabel.text = Loc.Tr(tab == StoreRows.Tab.Orders ? "ui.store.empty.orders" : "ui.store.empty");
            emptyLabel.style.display = rows.Count == 0 ? DisplayStyle.Flex : DisplayStyle.None;
        }

        Select(rows.Count == 0 ? -1 : Mathf.Clamp(selectedRow, 0, rows.Count - 1));
    }

    private void Purchase(StoreRows.Row row)
    {
        if (row.Buy == null) return;
        if (store == null) { Debug.LogWarning("[StorePanelUITK] No StoreManager assigned."); return; }

        var result = row.Buy.Invoke();
        switch (result)
        {
            case BuyResult.Success:
                Rebuild();
                break;
            case BuyResult.OutOfStock:
                ShowNotify(Loc.Tr("ui.store.toast.out_of_stock"));
                break;
            case BuyResult.InsufficientFunds:
                ShowNotify(Loc.Tr("ui.store.toast.insufficient_funds"));
                break;
            case BuyResult.AlreadyOwned:
                ShowNotify(Loc.Tr("ui.store.toast.already_owned"));
                break;
            case BuyResult.Locked:
                ShowNotify(Loc.Tr("ui.store.result.locked"));
                break;
        }
    }

    private void BuySelected()
    {
        if (selectedRow >= 0 && selectedRow < rows.Count) Purchase(rows[selectedRow]);
    }

    private void StepRow(int dir)
    {
        if (rows.Count == 0) return;
        Select(((selectedRow + dir) % rows.Count + rows.Count) % rows.Count);
    }

    private void Select(int idx)
    {
        selectedRow = UiPanels.ClampSelection(tileEls.Count, idx);
        if (selectedRow < 0)
        {
            detail?.SetEmpty();
            return;
        }
        UiPanels.SetActiveIndex(tileEls, selectedRow, TileSelectedClass);
        if (grid != null) grid.ScrollTo(tileEls[selectedRow]);
        detail?.Show((StoreRows.Tab)activeTab, rows[selectedRow], discountActive);
    }

    private void Resolve()
    {
        var root = UiPanels.RootOf(document);
        if (root == null) return;

        tabsContainer = root.Q<VisualElement>("tabs");
        grid          = root.Q<ScrollView>("grid");
        emptyLabel    = root.Q<Label>("empty");
        balanceLabel  = root.Q<Label>("balance");
        notifyLabel   = root.Q<Label>("notify");
        closeButton   = root.Q<Button>("close-button");
        detail        = new StoreDetailCard(root);

        SetText(root, "store-title", Loc.Tr("ui.store.title"));
        SetPrompt(root, "prompt-category", "ui.prompt.category");
        SetPrompt(root, "prompt-move", "ui.prompt.move");
        SetPrompt(root, "prompt-buy", "ui.prompt.buy");
        SetPrompt(root, "prompt-close", "ui.prompt.close");

        if (emptyLabel  != null) emptyLabel.text         = Loc.Tr("ui.store.empty");
        if (notifyLabel != null) notifyLabel.style.display = DisplayStyle.None;
        if (closeButton != null) closeButton.clicked     += OnCloseClicked;
        detail.BuyButton.clicked += BuySelected;
        detail.SetEmpty();
    }

    private static void SetText(VisualElement root, string className, string text)
    {
        var label = root.Q<Label>(className: className);
        if (label != null) label.text = text;
    }

    private static void SetPrompt(VisualElement root, string name, string key)
    {
        var label = root.Q<Label>(name);
        if (label != null) label.text = Loc.Tr(key);
    }

    private ScrollView ResolveGrid()
    {
        if (grid != null && grid.panel != null) return grid;
        var root = UiPanels.RootOf(document);
        if (root == null) return null;
        grid = root.Q<ScrollView>("grid");
        return grid;
    }

    private void OnCloseClicked() => UIManager.RequestPanelToggle(panel);
}
}
