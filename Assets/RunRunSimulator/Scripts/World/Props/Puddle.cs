using System.Collections.Generic;
using MoreMountains.Feedbacks;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class Puddle : MonoBehaviour
{
    private static readonly List<Puddle> all = new List<Puddle>();
    public static IReadOnlyList<Puddle> All => all;

    [SerializeField] private MMF_Player onClean;

    private bool cleaned;

    private void OnEnable() => all.Add(this);
    private void OnDisable() => all.Remove(this);

    public void Clean()
    {
        if (cleaned) return;
        cleaned = true;
        onClean?.PlayFeedbacks();
        foreach (var col in GetComponentsInChildren<Collider>()) col.enabled = false;
        all.Remove(this);
        Destroy(gameObject, 0.4f);
    }
}
}
