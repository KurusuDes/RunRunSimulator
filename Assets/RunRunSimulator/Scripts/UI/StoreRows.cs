using System;
using System.Collections.Generic;
namespace MoriMonchiSimulator
{

public static class StoreRows
{
    public enum Tab { Expansions, WorldProps, Consumables, Creatures, Decor, Toys, Orders, Goals }

    public struct Row
    {
        public string          Name;
        public string          Reward;
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
        Tab.Orders      => Loc.Tr("ui.store.tab.orders"),
        Tab.Goals       => Loc.Tr("ui.store.tab.goals"),
        _              => "",
    };

    public static void Collect(Tab tab, ShopCatalogSO catalog, StoreManager store, List<Row> rows)
    {
        if (tab == Tab.Orders)
        {
            var board = OrderBoardService.Instance;
            if (board == null) return;
            foreach (var order in board.Active)
            {
                if (order == null) continue;
                rows.Add(new Row
                {
                    Name   = order.Describe(),
                    Reward = $"+{order.Reward}",
                });
            }
            return;
        }

        if (tab == Tab.Goals)
        {
            CollectGoals(rows);
            return;
        }

        if (catalog == null) return;

        var goals = GoalService.Instance;

        if (tab == Tab.Expansions)
        {
            foreach (var upgrade in catalog.UpgradeListings)
            {
                if (upgrade == null) continue;
                var locking = goals != null ? goals.LockingGoal(upgrade) : null;
                if (locking != null)
                {
                    rows.Add(new Row { Name = LockedName(NameOf(upgrade.DisplayName, upgrade.Id), locking) });
                    continue;
                }
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
            var lockingGoal = goals != null ? goals.LockingGoal(def) : null;
            if (lockingGoal != null)
            {
                rows.Add(new Row { Name = LockedName(NameOf(def.DisplayName, def.Id), lockingGoal) });
                continue;
            }
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

    private static void CollectGoals(List<Row> rows)
    {
        var service = GoalService.Instance;
        if (service == null) return;
        foreach (var goal in service.Goals)
        {
            if (goal == null) continue;
            string progress = service.IsDone(goal) ? "✓" : $"{service.Progress(goal)}/{goal.Target}";
            string reward   = $"+{goal.RewardDabloons}";
            string opens    = UnlockNames(goal);
            if (opens.Length > 0) reward += $" · {Loc.Tr("ui.store.goal.opens")} {opens}";
            rows.Add(new Row
            {
                Name   = $"{Loc.Tr(goal.TitleKey)}  {progress}",
                Reward = reward,
            });
        }
    }

    private static string UnlockNames(GoalSO goal)
    {
        var names = new List<string>();
        if (goal.UnlocksExpansions != null)
            foreach (var upgrade in goal.UnlocksExpansions)
                if (upgrade != null) names.Add(NameOf(upgrade.DisplayName, upgrade.Id));
        if (goal.UnlocksItems != null)
            foreach (var item in goal.UnlocksItems)
                if (item != null) names.Add(NameOf(item.DisplayName, item.Id));
        return string.Join(", ", names);
    }

    private static string LockedName(string name, GoalSO goal) =>
        $"{name} · {Loc.Tr("ui.store.locked")} {Loc.Tr(goal.TitleKey)}";

    private static bool MatchesItemTab(Tab tab, WorldPropCategory cat) =>
        tab == Tab.WorldProps ? cat == WorldPropCategory.Tool
        : tab == Tab.Toys     ? cat == WorldPropCategory.Toy
        : cat == WorldPropCategory.Food || cat == WorldPropCategory.Medicine;

    private static string NameOf(string display, string id) =>
        string.IsNullOrEmpty(display) ? id : display;
}
}
