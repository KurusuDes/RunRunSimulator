using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class MessEmitter : MonoBehaviour
{
    [Required] [SerializeField] private Toy toy;
    [Required, AssetsOnly] [SerializeField] private GameObject stainPrefab;
    [SerializeField] private float spacing = 3f;
    [SerializeField, Range(0f, 1f)] private float chance = 0.35f;
    [SerializeField] private float minGap = 1f;
    [SerializeField] private int maxStains = 12;
    [SerializeField] private float minSpeed = 0.5f;
    [SerializeField] private LayerMask groundMask = ~0;

    private readonly List<GameObject> stains = new List<GameObject>();
    private Vector3 lastPos;
    private float accumulated;
    private bool tracking;

    private void OnDisable() => tracking = false;

    private void Update()
    {
        if (toy.IsHeldByPlayer)
        {
            tracking = false;
            return;
        }

        Vector3 pos = toy.transform.position;
        if (!tracking)
        {
            tracking = true;
            lastPos = pos;
            accumulated = 0f;
            return;
        }

        Vector3 delta = pos - lastPos;
        delta.y = 0f;
        lastPos = pos;

        float dt = Time.deltaTime;
        bool carried = toy.Holder != null;
        if (!carried && (dt <= 0f || delta.magnitude / dt <= minSpeed)) return;

        accumulated += delta.magnitude;
        if (accumulated < spacing) return;
        accumulated = 0f;
        if (Random.value > chance) return;
        TrySpawn(pos);
    }

    private void TrySpawn(Vector3 pos)
    {
        stains.RemoveAll(s => s == null);
        if (stains.Count >= maxStains) return;
        if (!Physics.Raycast(pos + Vector3.up, Vector3.down, out var hit, 3f, groundMask, QueryTriggerInteraction.Ignore)) return;

        var all = Puddle.All;
        for (int i = 0; i < all.Count; i++)
            if ((all[i].transform.position - hit.point).sqrMagnitude < minGap * minGap) return;

        var rot = Quaternion.Euler(0f, Random.Range(0f, 360f), 0f);
        stains.Add(Instantiate(stainPrefab, hit.point, rot));
    }
}
}
