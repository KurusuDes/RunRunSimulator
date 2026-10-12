using System;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using Sirenix.Serialization;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "PlayerInventory", menuName = "RunRunSimulator/Player/Player Inventory")]
public class PlayerInventorySO : SerializedScriptableObject
{
    public const int HotbarSize = 6;

    [Title("World props stored (I# ids — list, dupes = multiple instances)")]
    [OdinSerialize, ReadOnly]
    private List<string> worldPropsStored = new List<string>();

    [Title("Hotbar (I# ids, 6 slots — persists)")]
    [OdinSerialize, ReadOnly]
    private string[] hotbarSlots = new string[HotbarSize];

    [Title("Dabloons (currency)")]
    [OdinSerialize, ReadOnly]
    private int dabloons;

    [OdinSerialize, ReadOnly, PreviouslySerializedAs("adventureMaterial")]
    private int minerita;

    [Title("Breeding decor owned, not placed (id -> count)")]
    [OdinSerialize, ReadOnly]
    private Dictionary<string, int> decorOwned = new Dictionary<string, int>();

    public IReadOnlyDictionary<string, int> DecorOwned => decorOwned;

    public int DecorCount(string id) =>
        !string.IsNullOrEmpty(id) && decorOwned.TryGetValue(id, out var n) ? n : 0;

    public void AddDecor(string id, int amount = 1)
    {
        if (string.IsNullOrEmpty(id) || amount <= 0) return;
        decorOwned[id] = DecorCount(id) + amount;
        MarkDirty();
    }

    public bool TryTakeDecor(string id)
    {
        int n = DecorCount(id);
        if (n <= 0) return false;
        if (n == 1) decorOwned.Remove(id);
        else decorOwned[id] = n - 1;
        MarkDirty();
        return true;
    }

    public void AddWorldProp(string id)
    {
        if (string.IsNullOrEmpty(id)) return;
        worldPropsStored.Add(id);
        MarkDirty();
    }

    public bool RemoveWorldProp(string id)
    {
        if (!worldPropsStored.Remove(id)) return false;
        MarkDirty();
        return true;
    }

    public IReadOnlyList<string> WorldPropsStored => worldPropsStored;

    public int Balance(Currency c)
    {
        switch (c)
        {
            case Currency.Dabloons: return dabloons;
            case Currency.Minerita: return minerita;
            default: return 0;
        }
    }

    public void Add(Currency c, int amount)
    {
        if (amount <= 0) return;
        switch (c)
        {
            case Currency.Dabloons: dabloons += amount; break;
            case Currency.Minerita: minerita += amount; break;
        }
        MarkDirty();
    }

    public bool TrySpend(Currency c, int amount)
    {
        if (amount <= 0 || Balance(c) < amount) return false;
        switch (c)
        {
            case Currency.Dabloons: dabloons -= amount; break;
            case Currency.Minerita: minerita -= amount; break;
        }
        MarkDirty();
        return true;
    }

    public void ResetCurrency(Currency c)
    {
        switch (c)
        {
            case Currency.Dabloons: dabloons = 0; break;
            case Currency.Minerita: minerita = 0; break;
        }
        MarkDirty();
    }

    public void ClearWorldPropsStored()
    {
        worldPropsStored.Clear();
        MarkDirty();
    }

    public void ClearHotbar()
    {
        for (int i = 0; i < hotbarSlots.Length; i++) hotbarSlots[i] = null;
        MarkDirty();
    }

    public string GetHotbarSlot(int index) =>
        (index >= 0 && index < hotbarSlots.Length) ? hotbarSlots[index] : null;

    public void SetHotbarSlot(int index, string id)
    {
        if (index < 0 || index >= hotbarSlots.Length) return;
        hotbarSlots[index] = id;
        MarkDirty();
    }

    public void ClearHotbarSlot(int index) => SetHotbarSlot(index, null);

    public string[] HotbarSlots => hotbarSlots;

    [Serializable]
    public class InventoryData
    {
        public List<string> WorldPropsStored = new List<string>();
        public string[]      HotbarSlots      = new string[HotbarSize];
        public int           Dabloons         = 0;
        public int           Minerita         = 0;
        public Dictionary<string, int> DecorOwned = new Dictionary<string, int>();
    }

    public InventoryData GetData() => new InventoryData
    {
        WorldPropsStored = new List<string>(worldPropsStored),
        HotbarSlots      = (string[])hotbarSlots.Clone(),
        Dabloons         = dabloons,
        Minerita         = minerita,
        DecorOwned       = new Dictionary<string, int>(decorOwned),
    };

    public void LoadFrom(InventoryData data)
    {
        worldPropsStored = data?.WorldPropsStored ?? new List<string>();
        hotbarSlots      = NormalizeHotbar(data?.HotbarSlots);
        dabloons         = data?.Dabloons ?? 0;
        minerita         = data?.Minerita ?? 0;
        decorOwned       = data?.DecorOwned != null ? new Dictionary<string, int>(data.DecorOwned) : new Dictionary<string, int>();
        MarkDirty();
    }

    private static string[] NormalizeHotbar(string[] saved)
    {
        var slots = new string[HotbarSize];
        if (saved != null)
            for (int i = 0; i < HotbarSize && i < saved.Length; i++)
                slots[i] = saved[i];
        return slots;
    }

    private void MarkDirty()
    {
#if UNITY_EDITOR
        UnityEditor.EditorUtility.SetDirty(this);
#endif
    }
}
}
