using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class HoseSpray : MonoBehaviour
{
    [Required] [SerializeField] private Toy toy;
    [Required, AssetsOnly] [SerializeField] private GameObject puddlePrefab;
    [SerializeField] private float spacing = 1.2f;
    [SerializeField] private float minGap = 0.8f;
    [SerializeField] private int maxPuddles = 25;
    [SerializeField] private LayerMask groundMask = ~0;

    [SerializeField] private float refillRadius = 1.5f;
    [SerializeField] private float refillPerSecond = 25f;

    private Vector3 lastPos;
    private float accumulated;
    private bool tracking;

    private void Update()
    {
        if (toy.Holder == null)
        {
            tracking = false;
            return;
        }

        Vector3 pos = toy.transform.position;
        RefillNearbyWater(pos);
        if (!tracking)
        {
            tracking = true;
            lastPos = pos;
            accumulated = 0f;
            return;
        }

        Vector3 delta = pos - lastPos;
        delta.y = 0f;
        accumulated += delta.magnitude;
        lastPos = pos;

        if (accumulated < spacing) return;
        accumulated = 0f;
        TrySpawn(pos);
    }

    private void RefillNearbyWater(Vector3 pos)
    {
        var supplies = StationSupply.All;
        for (int i = 0; i < supplies.Count; i++)
        {
            var s = supplies[i];
            if (s.Kind != SupplyKind.Water) continue;
            if ((s.transform.position - pos).sqrMagnitude > refillRadius * refillRadius) continue;
            s.Refill(refillPerSecond * Time.deltaTime);
        }
    }

    private void TrySpawn(Vector3 pos)
    {
        if (Puddle.All.Count >= maxPuddles) return;
        if (!Physics.Raycast(pos + Vector3.up, Vector3.down, out var hit, 3f, groundMask, QueryTriggerInteraction.Ignore)) return;

        var all = Puddle.All;
        for (int i = 0; i < all.Count; i++)
            if ((all[i].transform.position - hit.point).sqrMagnitude < minGap * minGap) return;

        Instantiate(puddlePrefab, hit.point, Quaternion.identity);
    }
}
}
