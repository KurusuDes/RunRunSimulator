using System;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class StoreManager : MonoBehaviour
{
    [Title("Catalog")]
    [Required, AssetsOnly] [SerializeField] private ShopCatalogSO catalog;

    [Title("World-prop delivery")]
    [Required, AssetsOnly] [SerializeField] private DeliveryBox deliveryBoxPrefab;
    [Required]             [SerializeField] private Transform   deliverySpawnPoint;

    public ShopCatalogSO Catalog => catalog;

    private static int Today => GameClock.Instance != null ? GameClock.Instance.Day : 1;

    private void OnEnable()
    {
        GameEvents.OnDayStarted += OnDayStarted;
        GameEvents.OnWorldStateReloaded += OnWorldStateReloaded;
    }

    private void OnDisable()
    {
        GameEvents.OnDayStarted -= OnDayStarted;
        GameEvents.OnWorldStateReloaded -= OnWorldStateReloaded;
    }

    private void OnDayStarted(int day) => RestockIfNeeded();

    private void OnWorldStateReloaded(WorldStateSO world)
    {
        if (catalog == null || world == null) return;
        catalog.ImportStock(world.ShopStock, world.LastRestockDay);
        if (catalog.NeedsRestock(Today)) catalog.RestockAll(Today);
    }

    private void PersistStock()
    {
        var world = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
        if (catalog == null || world == null) return;
        world.SetShopStock(catalog.ExportStock());
        world.LastRestockDay = catalog.LastRestockDay;
        GameEvents.WorldStateChanged(world);
    }

    public BuyResult BuyWorldProp(ItemDefinitionSO def, StoreShopData shop)
    {
        if (def == null || shop == null) { Debug.LogWarning("[StoreManager] BuyWorldProp: null arg."); return BuyResult.OutOfStock; }

        if (GoalService.Instance?.LockingGoal(def) != null) return BuyResult.Locked;

        if (!shop.InStock) return BuyResult.OutOfStock;

        if (deliveryBoxPrefab == null || deliverySpawnPoint == null)
        {
            Debug.LogError("[StoreManager] Assign deliveryBoxPrefab + deliverySpawnPoint first.");
            return BuyResult.OutOfStock;
        }
        if (!Application.isPlaying)
        {
            Debug.LogWarning("[StoreManager] Enter Play mode to buy (spawns a DeliveryBox).");
            return BuyResult.OutOfStock;
        }

        var inventory = GameManager.CurrentInventory;
        if (inventory == null) { Debug.LogError("[StoreManager] No PlayerInventory available."); return BuyResult.OutOfStock; }

        int price = catalog.FinalPrice(shop, Today);
        if (price > 0 && !Wallet.TrySpend(shop.Currency, price, "store")) return BuyResult.InsufficientFunds;

        if (shop.TryConsume()) PersistStock();

        var box = SpawnDeliveryBox(price, shop);
        if (box == null) return BuyResult.OutOfStock;

        box.Configure(def);
        if (price <= 0) GameEvents.InventoryChanged(inventory);
        Debug.Log($"[StoreManager] Ordered '{def.DisplayName}' ({def.Id}) for {price} {shop.Currency}.");
        return BuyResult.Success;
    }

    public BuyResult BuyCreatureBox(CreatureBoxSO box, StoreShopData shop)
    {
        if (box == null || shop == null) { Debug.LogWarning("[StoreManager] BuyCreatureBox: null arg."); return BuyResult.OutOfStock; }

        if (!shop.InStock) return BuyResult.OutOfStock;

        if (deliveryBoxPrefab == null || deliverySpawnPoint == null)
        {
            Debug.LogError("[StoreManager] Assign deliveryBoxPrefab + deliverySpawnPoint first.");
            return BuyResult.OutOfStock;
        }
        if (!Application.isPlaying)
        {
            Debug.LogWarning("[StoreManager] Enter Play mode to buy (spawns a DeliveryBox).");
            return BuyResult.OutOfStock;
        }

        var inventory = GameManager.CurrentInventory;
        if (inventory == null) { Debug.LogError("[StoreManager] No PlayerInventory available."); return BuyResult.OutOfStock; }

        int price = CreatureBoxPrice(box, shop);
        if (price > 0 && !Wallet.TrySpend(shop.Currency, price, "store")) return BuyResult.InsufficientFunds;

        if (shop.TryConsume()) PersistStock();

        var deliveryBox = SpawnDeliveryBox(price, shop);
        if (deliveryBox == null) return BuyResult.OutOfStock;

        deliveryBox.Configure(box);
        GameEvents.CreatureBoxOrdered(box);
        if (price <= 0) GameEvents.InventoryChanged(inventory);
        Debug.Log($"[StoreManager] Ordered creature box '{box.DisplayName}' ({box.Id}) for {price} {shop.Currency}.");
        return BuyResult.Success;
    }

    public bool GiftCreatureBox(CreatureBoxSO box)
    {
        if (box == null) { Debug.LogWarning("[StoreManager] GiftCreatureBox: null box."); return false; }

        if (deliveryBoxPrefab == null || deliverySpawnPoint == null)
        {
            Debug.LogError("[StoreManager] Assign deliveryBoxPrefab + deliverySpawnPoint first.");
            return false;
        }
        if (!Application.isPlaying)
        {
            Debug.LogWarning("[StoreManager] Enter Play mode to gift (spawns a DeliveryBox).");
            return false;
        }

        var deliveryBox = SpawnDeliveryBox(0, null);
        if (deliveryBox == null) return false;

        deliveryBox.Configure(box);
        Debug.Log($"[StoreManager] Gifted creature box '{box.DisplayName}' ({box.Id}).");
        return true;
    }

    public BuyResult BuyUpgrade(ShopUpgradeSO upgrade)
    {
        var world = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
        if (upgrade == null || world == null) { Debug.LogWarning("[StoreManager] BuyUpgrade: null arg."); return BuyResult.OutOfStock; }

        if (GoalService.Instance?.LockingGoal(upgrade) != null) return BuyResult.Locked;

        int level = world.UpgradeLevel(upgrade.Id);
        if (upgrade.IsMaxed(level)) return BuyResult.AlreadyOwned;

        int price = upgrade.PriceFor(level);
        if (price > 0 && !Wallet.TrySpend(Currency.Dabloons, price, "upgrade")) return BuyResult.InsufficientFunds;

        world.SetUpgradeLevel(upgrade.Id, level + 1);
        GameEvents.WorldStateChanged(world);
        Debug.Log($"[StoreManager] Bought upgrade '{upgrade.DisplayName}' ({upgrade.Id}) level {level + 1}/{upgrade.MaxLevel} for {price} Dabloons.");
        return BuyResult.Success;
    }

    public BuyResult BuyDecor(BreedingDecorSO decor)
    {
        if (decor == null || string.IsNullOrEmpty(decor.Id)) { Debug.LogWarning("[StoreManager] BuyDecor: null arg."); return BuyResult.OutOfStock; }

        var inventory = GameManager.CurrentInventory;
        if (inventory == null) { Debug.LogError("[StoreManager] No PlayerInventory available."); return BuyResult.OutOfStock; }

        int price = decor.Price;
        if (price > 0 && !Wallet.TrySpend(Currency.Dabloons, price, "decor")) return BuyResult.InsufficientFunds;

        inventory.AddDecor(decor.Id);
        GameEvents.InventoryChanged(inventory);
        Debug.Log($"[StoreManager] Bought decor '{decor.DisplayName}' ({decor.Id}) for {price} Dabloons.");
        return BuyResult.Success;
    }

    public int CreatureBoxPrice(CreatureBoxSO box, StoreShopData shop)
    {
        if (box != null && box.FreeWhileNoCreatures)
        {
            var registry = GameManager.Instance?.Registry;
            if (registry == null) return catalog.FinalPrice(shop, Today);

            bool hasLivingCreature = false;
            foreach (var dna in registry.GetAll().Values)
            {
                if (dna.IsDead || dna.IsSold) continue;
                hasLivingCreature = true;
                break;
            }
            if (!hasLivingCreature) return 0;
        }
        return catalog.FinalPrice(shop, Today);
    }

    private DeliveryBox SpawnDeliveryBox(int price, StoreShopData shop)
    {
        var go  = Instantiate(deliveryBoxPrefab, deliverySpawnPoint.position, deliverySpawnPoint.rotation);
        var box = go.GetComponent<DeliveryBox>();
        if (box == null)
        {
            Debug.LogError("[StoreManager] deliveryBoxPrefab has no DeliveryBox component.");
            Destroy(go);
            if (price > 0) { Wallet.Add(shop.Currency, price, "store-refund"); shop.CurrentStock++; }
            return null;
        }
        return box;
    }

    public void RestockIfNeeded()
    {
        if (catalog == null) return;
        int day = Today;
        if (!catalog.NeedsRestock(day)) return;
        catalog.RestockAll(day);
        PersistStock();
    }
}
}
