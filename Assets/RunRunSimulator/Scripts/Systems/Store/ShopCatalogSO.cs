using System;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "ShopCatalog", menuName = "RunRunSimulator/Store/Shop Catalog")]
public class ShopCatalogSO : SerializedScriptableObject
{
    [Serializable]
    public class ItemListing
    {
        [Required, AssetsOnly, HideLabel, HorizontalGroup(220)]
        public ItemDefinitionSO Item;

        [HideLabel]
        public StoreShopData Shop;

        [AssetsOnly] public ShopUpgradeSO RequiresExpansion;
    }

    [Serializable]
    public class CreatureBoxListing
    {
        [Required, AssetsOnly, HideLabel, HorizontalGroup(220)]
        public CreatureBoxSO Box;

        [HideLabel]
        public StoreShopData Shop;
    }

    [Title("Restock schedule (applies to all listings in this shop)")]
    [Tooltip("Game days between restocks.")]
    [Min(1)] public int RestockEveryDays = 3;

    [Title("Discount schedule (applies to all listings in this shop)")]
    [Tooltip("Game days between discount windows. 0 = never on sale.")]
    [Min(0)] public int DiscountEveryDays = 7;

    [Button("Force Restock All (DEV)", ButtonSizes.Medium), GUIColor(0.9f, 0.75f, 0.2f)]
    private void DevForceRestock()
    {
        int day = GameClock.Instance != null ? GameClock.Instance.Day : 1;
        RestockAll(day);
        Debug.Log("[ShopCatalog] Force restock fired — all listings refilled to MaxStock.");
    }

    [Title("World props for sale")]
    [TableList(AlwaysExpanded = true)]
    [SerializeField] private List<ItemListing> itemListings = new List<ItemListing>();

    [Title("MoriMonchi boxes for sale")]
    [TableList(AlwaysExpanded = true)]
    [SerializeField] private List<CreatureBoxListing> creatureBoxListings = new List<CreatureBoxListing>();

    [Title("Shop upgrades for sale")]
    [SerializeField] private List<ShopUpgradeSO> upgradeListings = new List<ShopUpgradeSO>();

    [Title("Breeding decor for sale (unlimited stock)")]
    [SerializeField] private List<BreedingDecorSO> decorListings = new List<BreedingDecorSO>();

    public IReadOnlyList<BreedingDecorSO>     DecorListings        => decorListings;
    public IReadOnlyList<ShopUpgradeSO>       UpgradeListings      => upgradeListings;
    public IReadOnlyList<ItemListing>         ItemListings         => itemListings;
    public IReadOnlyList<CreatureBoxListing>  CreatureBoxListings  => creatureBoxListings;

    public bool IsDiscountActive(int day) => DiscountEveryDays > 0 && day % DiscountEveryDays == 0;

    public int FinalPrice(StoreShopData shop, int day) =>
        shop?.FinalPrice(IsDiscountActive(day)) ?? 0;

    public bool NeedsRestock(int day) => lastRestockDay <= 0 || day - lastRestockDay >= RestockEveryDays;

    public void RestockAll(int day)
    {
        lastRestockDay = day;

        foreach (var l in itemListings)         l?.Shop?.Restock();
        foreach (var l in creatureBoxListings)  l?.Shop?.Restock();
    }

    public int LastRestockDay => lastRestockDay;

    public Dictionary<string, int> ExportStock()
    {
        var stock = new Dictionary<string, int>();
        foreach (var l in itemListings)        if (l?.Item != null && !string.IsNullOrEmpty(l.Item.Id) && l.Shop != null && !l.Shop.IsUnlimited) stock[l.Item.Id] = l.Shop.CurrentStock;
        foreach (var l in creatureBoxListings) if (l?.Box != null && !string.IsNullOrEmpty(l.Box.Id) && l.Shop != null && !l.Shop.IsUnlimited) stock[l.Box.Id] = l.Shop.CurrentStock;
        return stock;
    }

    public void ImportStock(IReadOnlyDictionary<string, int> stock, int restockDay)
    {
        lastRestockDay = restockDay;
        foreach (var l in itemListings)        if (l?.Item != null) ApplyStock(stock, l.Item.Id, l.Shop);
        foreach (var l in creatureBoxListings) if (l?.Box != null) ApplyStock(stock, l.Box.Id, l.Shop);
    }

    private static void ApplyStock(IReadOnlyDictionary<string, int> stock, string id, StoreShopData shop)
    {
        if (shop == null || string.IsNullOrEmpty(id) || shop.IsUnlimited) return;
        if (stock != null && stock.TryGetValue(id, out var value)) shop.CurrentStock = Mathf.Clamp(value, 0, shop.MaxStock);
        else shop.Restock();
    }

    [NonSerialized] private int lastRestockDay;
}
}
