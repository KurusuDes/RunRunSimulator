using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class UncleRescueService : MonoBehaviour
{
    private const int FallbackHatchCost = 10;

    [Required, SerializeField] private StoreManager store;
    [Required, SerializeField] private CreatureBoxSO giftBox;
    [Required, SerializeField] private CloudSyncService cloudSync;

    private bool dirty = true;
    private bool giftSent;

    private void OnEnable()
    {
        GameEvents.OnRegistryChanged   += OnRegistryEvent;
        GameEvents.OnRegistryReloaded  += OnRegistryEvent;
        GameEvents.OnInventoryChanged  += OnInventoryEvent;
        GameEvents.OnInventoryReloaded += OnInventoryEvent;
        GameEvents.OnCreatureDeparted  += OnDepartedEvent;
    }

    private void OnDisable()
    {
        GameEvents.OnRegistryChanged   -= OnRegistryEvent;
        GameEvents.OnRegistryReloaded  -= OnRegistryEvent;
        GameEvents.OnInventoryChanged  -= OnInventoryEvent;
        GameEvents.OnInventoryReloaded -= OnInventoryEvent;
        GameEvents.OnCreatureDeparted  -= OnDepartedEvent;
    }

    private void OnRegistryEvent(CreatureRegistrySO registry) => dirty = true;
    private void OnInventoryEvent(PlayerInventorySO inventory) => dirty = true;
    private void OnDepartedEvent(CreatureDNA dna) => dirty = true;

    private void LateUpdate()
    {
        if (!dirty || cloudSync == null || !cloudSync.StartupSyncDone) return;
        dirty = false;

        if (!IsSoftBlocked()) { giftSent = false; return; }
        if (giftSent) return;
        SendGift();
    }

    public bool IsSoftBlocked()
    {
        var registry = GameManager.Instance != null ? GameManager.Instance.Registry : null;
        if (registry == null || registry.Departed.Count == 0) return false;

        bool hasEgg = false;
        foreach (var dna in registry.GetAll().Values)
        {
            if (dna == null || dna.IsDead || dna.IsSold) continue;
            if (dna.Form != MonchiForm.Egg) return false;
            hasEgg = true;
        }

        if (!hasEgg) return true;

        var breeding = BreedingController.Instance;
        int cost = breeding != null && breeding.InheritanceOdds != null ? breeding.InheritanceOdds.HatchCostBase : FallbackHatchCost;
        return Wallet.Balance(Currency.Minerita) < cost;
    }

    [Button]
    public void ForceCall() => SendGift();

    private void SendGift()
    {
        if (store == null || giftBox == null) return;
        if (!store.GiftCreatureBox(giftBox)) { Debug.LogWarning("[UncleRescue] Gift failed."); return; }
        giftSent = true;
        Debug.Log($"[UncleRescue] Uncle called: sent '{giftBox.DisplayName}'.");
        GameEvents.RescueGiftSent(giftBox);
    }
}
}
