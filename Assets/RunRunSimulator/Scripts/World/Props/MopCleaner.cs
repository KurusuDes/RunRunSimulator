using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class MopCleaner : MonoBehaviour
{
    [Required] [SerializeField] private Transform player;
    [Required] [SerializeField] private ItemDefinitionSO mopItem;
    [SerializeField] private float radius = 1.6f;
    [SerializeField] private float forwardOffset = 1f;

    private readonly List<Puddle> buffer = new List<Puddle>();

    private void OnEnable() => HotbarController.OnItemUsed += OnItemUsed;
    private void OnDisable() => HotbarController.OnItemUsed -= OnItemUsed;

    private void OnItemUsed(string id)
    {
        if (mopItem == null || id != mopItem.Id) return;

        Vector3 center = player.position + player.forward * forwardOffset;
        buffer.Clear();
        var all = Puddle.All;
        for (int i = 0; i < all.Count; i++)
        {
            Vector3 d = all[i].transform.position - center;
            d.y = 0f;
            if (d.sqrMagnitude <= radius * radius) buffer.Add(all[i]);
        }

        for (int i = 0; i < buffer.Count; i++) buffer[i].Clean();
        Debug.Log($"[MopCleaner] Cleaned {buffer.Count} puddle(s).");
    }
}
}
