using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class GrassTrampler : MonoBehaviour
{
    private static readonly List<GrassTrampler> all = new List<GrassTrampler>();

    [SerializeField] private float radius = 0.5f;
    [SerializeField] private float trail = 1f;

    public static IReadOnlyList<GrassTrampler> All => all;

    public Vector3 Position => transform.position;
    public float Radius => radius;
    public float Trail => trail;

    private void OnEnable()
    {
        all.Add(this);
    }

    private void OnDisable()
    {
        all.Remove(this);
    }
}
}
