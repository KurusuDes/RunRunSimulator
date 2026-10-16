using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class StoreDetailCard
{
    private readonly VisualElement content;
    private readonly VisualElement icon;
    private readonly Label         nameLabel;
    private readonly Label         categoryLabel;
    private readonly VisualElement facts;
    private readonly Label         lockLabel;

    public Button BuyButton { get; }

    public StoreDetailCard(VisualElement root)
    {
        content       = root.Q<VisualElement>("detail-content");
        icon          = root.Q<VisualElement>("detail-icon");
        nameLabel     = root.Q<Label>("detail-name");
        categoryLabel = root.Q<Label>("detail-category");
        facts         = root.Q<VisualElement>("detail-facts");
        lockLabel     = root.Q<Label>("detail-lock");
        BuyButton     = root.Q<Button>("detail-buy");
    }

    public void SetEmpty()
    {
        content.style.display = DisplayStyle.None;
        BuyButton.SetEnabled(false);
    }

    public void Show(StoreRows.Tab tab, StoreRows.Row row, bool discountActive)
    {
        content.style.display = DisplayStyle.Flex;
        StoreTileView.ApplyIcon(icon, tab, row.Icon);
        nameLabel.text     = row.Name;
        categoryLabel.text = StoreRows.TabLabel(tab);

        bool locked = !string.IsNullOrEmpty(row.LockedBy);
        lockLabel.text          = row.LockedBy;
        lockLabel.style.display = locked ? DisplayStyle.Flex : DisplayStyle.None;

        facts.Clear();
        BuildFacts(row, discountActive);

        BuyButton.text = StorePrice.IsMaxed(row) ? Loc.Tr("ui.store.max") : Loc.Tr("ui.store.buy");
        BuyButton.SetEnabled(StorePrice.CanBuy(row));
    }

    private void BuildFacts(StoreRows.Row row, bool discountActive)
    {
        if (row.Buy == null)
        {
            if (!string.IsNullOrEmpty(row.Reward)) AddFact("store-fact__icon--coin", row.Reward, null, "store-fact__value");
            return;
        }

        if (row.Upgrade != null)
            AddFact("store-fact__icon--level", Loc.Tr("ui.store.level", row.Upgrade.CurrentLevel, row.Upgrade.MaxLevel), null, "store-fact__value");

        if (!StorePrice.IsMaxed(row))
        {
            var info = StorePrice.Resolve(row, discountActive);
            AddFact(info.Minerita ? "store-fact__icon--minerita" : "store-fact__icon--coin",
                    StorePrice.Text(info.Final, info.Minerita),
                    info.Discounted ? StorePrice.Text(info.Was, info.Minerita) : null,
                    info.Discounted ? "store-fact__value--sale" : "store-fact__value");
        }

        var shop = row.Shop;
        if (row.Upgrade == null && shop != null && !shop.IsUnlimited)
        {
            bool empty = shop.CurrentStock <= 0;
            string text = empty ? Loc.Tr("ui.store.stock_empty") : Loc.Tr("ui.store.stock_count", shop.CurrentStock);
            string cls  = empty ? "store-fact__value--crit" : shop.CurrentStock <= 2 ? "store-fact__value--warn" : "store-fact__value";
            AddFact("store-fact__icon--stock", text, null, cls);
        }
    }

    private void AddFact(string iconClass, string text, string was, string valueClass)
    {
        var rowEl = new VisualElement();
        rowEl.AddToClassList("mm-row");
        rowEl.AddToClassList("store-fact");

        var box = new VisualElement();
        box.AddToClassList("mm-statbox");
        box.AddToClassList("store-fact__box");
        var ic = new VisualElement();
        ic.AddToClassList("mm-icon");
        ic.AddToClassList(iconClass);
        box.Add(ic);
        rowEl.Add(box);

        if (was != null)
        {
            var wasLabel = new Label(was);
            wasLabel.AddToClassList("store-price__was");
            rowEl.Add(wasLabel);
        }

        var value = new Label(text);
        value.AddToClassList(valueClass);
        rowEl.Add(value);

        facts.Add(rowEl);
    }
}
}
