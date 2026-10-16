using UnityEngine;
using UnityEngine.Localization.Settings;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class OrdersHudUITK : MonoBehaviour
{
    private const string TitleKey = "ui.orders.hud.title";

    [SerializeField] private UIDocument document;

    private VisualElement block;
    private Label title;
    private VisualElement list;
    private bool uiFocused;

    private void OnEnable()
    {
        GameEvents.OnWorldStateChanged += HandleWorldState;
        GameEvents.OnWorldStateReloaded += HandleWorldState;
        GameEvents.OnDayStarted += HandleDayStarted;
        GameEvents.OnOrderCompleted += HandleOrderCompleted;
        UIManager.OnUIFocusChanged += HandleUIFocus;
        LocalizationSettings.SelectedLocaleChanged += HandleLocaleChanged;
    }

    private void OnDisable()
    {
        GameEvents.OnWorldStateChanged -= HandleWorldState;
        GameEvents.OnWorldStateReloaded -= HandleWorldState;
        GameEvents.OnDayStarted -= HandleDayStarted;
        GameEvents.OnOrderCompleted -= HandleOrderCompleted;
        UIManager.OnUIFocusChanged -= HandleUIFocus;
        LocalizationSettings.SelectedLocaleChanged -= HandleLocaleChanged;
    }

    private void Start()
    {
        var root = UiPanels.RootOf(document);
        if (root == null) { Debug.LogWarning("[OrdersHudUITK] No UIDocument / root."); return; }

        block = root.Q<VisualElement>("orders");
        title = root.Q<Label>("orders-title");
        list = root.Q<VisualElement>("orders-list");
        Refresh();
    }

    private void HandleWorldState(WorldStateSO state) => Refresh();

    private void HandleDayStarted(int day) => Refresh();

    private void HandleOrderCompleted(ShopOrder order) => Refresh();

    private void HandleLocaleChanged(UnityEngine.Localization.Locale locale) => Refresh();

    private void HandleUIFocus(bool focused)
    {
        uiFocused = focused;
        Refresh();
    }

    private void Refresh()
    {
        if (block == null || list == null) return;

        var board = OrderBoardService.Instance;
        var orders = board != null ? board.Active : null;
        if (uiFocused || orders == null || orders.Count == 0)
        {
            block.style.display = DisplayStyle.None;
            return;
        }

        if (title != null) title.text = Loc.Tr(TitleKey);
        list.Clear();
        foreach (var order in orders)
        {
            if (order != null) list.Add(BuildRow(order));
        }
        block.style.display = list.childCount > 0 ? DisplayStyle.Flex : DisplayStyle.None;
    }

    private static VisualElement BuildRow(ShopOrder order)
    {
        var row = new VisualElement { pickingMode = PickingMode.Ignore };
        row.AddToClassList("orders-row");

        var bullet = new VisualElement { pickingMode = PickingMode.Ignore };
        bullet.AddToClassList("orders-bullet");
        row.Add(bullet);

        var text = new Label(order.Describe()) { pickingMode = PickingMode.Ignore };
        text.AddToClassList("orders-text");
        row.Add(text);

        var reward = new VisualElement { pickingMode = PickingMode.Ignore };
        reward.AddToClassList("orders-reward");

        var amount = new Label("+" + order.Reward) { pickingMode = PickingMode.Ignore };
        amount.AddToClassList("orders-reward__amount");
        reward.Add(amount);

        var coin = new VisualElement { pickingMode = PickingMode.Ignore };
        coin.AddToClassList("orders-reward__coin");
        reward.Add(coin);

        row.Add(reward);
        return row;
    }
}
}
