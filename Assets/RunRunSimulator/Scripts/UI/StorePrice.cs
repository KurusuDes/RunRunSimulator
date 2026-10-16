namespace MoriMonchiSimulator
{

public static class StorePrice
{
    public struct Info
    {
        public int  Final;
        public int  Was;
        public bool Minerita;
        public bool Discounted => Was >= 0;
    }

    public static Info Resolve(StoreRows.Row row, bool discountActive)
    {
        var shop = row.Shop;
        bool discounted = !row.PriceOverride.HasValue && discountActive && shop?.DiscountBase > 0f;
        return new Info
        {
            Final    = row.PriceOverride ?? (shop != null ? shop.FinalPrice(discounted) : 0),
            Was      = discounted ? shop.BasePrice : -1,
            Minerita = shop != null && shop.Currency == Currency.Minerita,
        };
    }

    public static string Text(int amount, bool minerita) =>
        minerita ? $"{amount} Minerita" : Loc.Tr("ui.store.price", amount);

    public static bool IsMaxed(StoreRows.Row row) =>
        row.Upgrade != null && row.Upgrade.IsMaxed(row.Upgrade.CurrentLevel);

    public static bool CanBuy(StoreRows.Row row)
    {
        if (row.Buy == null) return false;
        if (row.Upgrade != null) return !IsMaxed(row);
        return row.Shop == null || row.Shop.InStock;
    }
}
}
