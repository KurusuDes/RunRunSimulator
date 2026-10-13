using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class ToyPlayArea : MonoBehaviour
{
    private static readonly List<ToyPlayArea> all = new List<ToyPlayArea>();
    public static IReadOnlyList<ToyPlayArea> All => all;

    [SerializeField, Min(0.5f)] private float radius = 6f;

    public Vector3 Center => transform.position;

    private void OnEnable() => all.Add(this);

    private void OnDisable() => all.Remove(this);

    public bool Contains(Vector3 p)
    {
        Vector3 d = p - transform.position; d.y = 0f;
        return d.sqrMagnitude <= radius * radius;
    }

    public Vector3 RandomPoint(float margin)
    {
        float r = Mathf.Max(radius - margin, 0.25f);
        Vector2 o = Random.insideUnitCircle * r;
        Vector3 c = transform.position;
        return new Vector3(c.x + o.x, c.y, c.z + o.y);
    }

    public static ToyPlayArea Nearest(Vector3 p)
    {
        ToyPlayArea best = null;
        float bestSqr = float.MaxValue;
        for (int i = 0; i < all.Count; i++)
        {
            var area = all[i];
            if (area == null) continue;
            Vector3 d = area.transform.position - p; d.y = 0f;
            float sqr = d.sqrMagnitude;
            if (sqr >= bestSqr) continue;
            bestSqr = sqr;
            best = area;
        }
        return best;
    }

    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.cyan;
        Gizmos.DrawWireSphere(transform.position, radius);
    }
}
}
