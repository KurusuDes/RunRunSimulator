using System;
using System.Collections.Generic;
namespace MoriMonchiSimulator
{

public static class StoreRows
{
    public enum Tab { Expansions, WorldProps, Consumables, Creatures, Decor, Toys }

    public struct Row
    {
        public string          Name;
        public StoreShopData   Shop;
        public Func<BuyResult> Buy;
        public int?            PriceOverride;
        public ShopUpgradeSO   Upgrade;
    }

    public static string TabLabel(Tab tab) => tab switch
    {
        Tab.Expansions  => Loc.Tr("ui.store.tab.expansions"),
        Tab.WorldProps  => Loc.Tr("ui.store.tab.worldprops"),
        Tab.Consumables => Loc.Tr("ui.store.tab.consumables"),
        Tab.Creatures   => Loc.Tr("ui.store.tab.creatures"),
        Tab.Decor       => Loc.Tr("ui.store.tab.decor"),
        Tab.Toys        => Loc.Tr("ui.store.tab.toys"),
        _               => "",
    };

    public static void Collect(Tab tab, ShopCatalogSO catalog, StoreManager store, List<Row> rows)
    {
        if (catalog == null) return;

        if (tab == Tab.Expansions)
        {
            foreach (var upgrade in catalog.UpgradeListings)
            {
                if (upgrade == null) continue;
                var capturedUpgrade = upgrade;
                rows.Add(new Row
                {
                    Name          = NameOf(upgrade.DisplayName, upgrade.Id),
                    Buy           = () => store.BuyUpgrade(capturedUpgrade),
                    PriceOverride = upgrade.PriceFor(upgrade.CurrentLevel),
                    Upgrade       = capturedUpgrade,
                });
            }
            return;
        }

        if (tab == Tab.Decor)
        {
            int bredTotal = GameManager.Instance?.WorldState?.BredTotal ?? 0;
            var inventory = GameManager.CurrentInventory;
            foreach (var decor in catalog.DecorListings)
            {
                if (decor == null) continue;
                var capturedDecor = decor;
                string name = decor.IsDiscovered(bredTotal) ? NameOf(decor.DisplayName, decor.Id) : Loc.Tr("ui.store.decor.unknown");
                int owned = inventory != null ? inventory.DecorCount(decor.Id) : 0;
                if (owned > 0) name = $"{name} ×{owned}";
                rows.Add(new Row
                {
                    Name          = name,
                    Buy           = () => store.BuyDecor(capturedDecor),
                    PriceOverride = decor.Price,
                });
            }
            return;
        }

        if (tab == Tab.Creatures)
        {
            foreach (var listing in catalog.CreatureBoxListings)
            {
                var box = listing?.Box;
                if (box == null) continue;
                var capturedBox  = box;
                var capturedShop = listing.Shop;
                rows.Add(new Row
                {
                    Name          = NameOf(box.DisplayName, box.Id),
                    Shop          = capturedShop,
                    Buy           = () => store.BuyCreatureBox(capturedBox, capturedShop),
                    PriceOverride = store.CreatureBoxPrice(capturedBox, capturedShop),
                });
            }
            return;
        }

        foreach (var listing in catalog.ItemListings)
        {
            var def = listing?.Item;
            if (def == null) continue;
            if (!MatchesItemTab(tab, def.Category)) continue;
            if (listing.RequiresExpansion != null
                && (GameManager.Instance?.WorldState?.UpgradeLevel(listing.RequiresExpansion.Id) ?? 0) < 1) continue;
            var capturedDef  = def;
            var capturedShop = listing.Shop;
            rows.Add(new Row
            {
                Name = NameOf(def.DisplayName, def.Id),
                Shop = capturedShop,
                Buy  = () => store.BuyWorldProp(capturedDef, capturedShop),
            });
        }
    }

    private static bool MatchesItemTab(Tab tab, WorldPropCategory cat) =>
        tab == Tab.WorldProps ? cat == WorldPropCategory.Tool
        : tab == Tab.Toys     ? cat == WorldPropCategory.Toy
        : cat == WorldPropCategory.Food || cat == WorldPropCategory.Medicine;

    private static string NameOf(string display, string id) =>
        string.IsNullOrEmpty(display) ? id : display;
}
}
