using System.Collections.Generic;
using MoreMountains.Feedbacks;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class Bubble : MonoBehaviour
{
    private static readonly List<Bubble> all = new List<Bubble>();
    public static IReadOnlyList<Bubble> All => all;

    [SerializeField] private MMF_Player onPop;
    [SerializeField, Min(0.01f)] private float driftSpeed = 0.6f;
    [SerializeField, Min(0.1f)] private float lifeMin = 6f;
    [SerializeField, Min(0.1f)] private float lifeMax = 9f;
    [SerializeField, Min(0f)] private float heightMin = 0.5f;
    [SerializeField, Min(0f)] private float heightMax = 1.8f;
    [SerializeField, Min(0f)] private float bobAmplitude = 0.2f;
    [SerializeField, Min(0f)] private float bobFrequency = 1.1f;
    [SerializeField, Min(0.01f)] private float riseSpeed = 0.5f;
    [SerializeField, Min(0f)] private float destroyDelay = 0.5f;

    private readonly List<MoriMochiAgent> claimers = new List<MoriMochiAgent>();
    private readonly List<MoriMochiAgent> others = new List<MoriMochiAgent>();
    private Vector3 flatDirection;
    private float floorY;
    private float life;
    private float age;
    private float bobPhase;
    private bool initialized;

    public bool Popped { get; private set; }

    private void OnEnable() => all.Add(this);

    private void OnDisable() => all.Remove(this);

    public void Initialize(Vector3 direction, float floorHeight)
    {
        var flat = new Vector3(direction.x, 0f, direction.z);
        if (flat.sqrMagnitude < 0.01f)
        {
            var circle = Random.insideUnitCircle.normalized;
            flat = new Vector3(circle.x, 0f, circle.y);
        }

        flatDirection = flat.normalized;
        floorY = floorHeight;
        life = Random.Range(lifeMin, Mathf.Max(lifeMin, lifeMax));
        bobPhase = Random.value * Mathf.PI * 2f;

        var position = transform.position;
        position.y = Mathf.Clamp(position.y, floorY + heightMin, floorY + heightMax);
        transform.position = position;
        initialized = true;
    }

    private void Update()
    {
        if (Popped) return;

        if (!initialized) Initialize(Random.onUnitSphere, transform.position.y - heightMin);

        age += Time.deltaTime;
        if (age >= life)
        {
            Pop(null);
            return;
        }

        float mid = floorY + (heightMin + heightMax) * 0.5f;
        float halfBand = (heightMax - heightMin) * 0.5f;
        float amplitude = Mathf.Min(bobAmplitude, halfBand);
        float targetY = mid + Mathf.Sin(age * bobFrequency + bobPhase) * amplitude;

        var position = transform.position + flatDirection * (driftSpeed * Time.deltaTime);
        position.y = Mathf.MoveTowards(position.y, targetY, riseSpeed * Time.deltaTime);
        position.y = Mathf.Clamp(position.y, floorY + heightMin, floorY + heightMax);
        transform.position = position;
    }

    public void Claim(MoriMochiAgent a)
    {
        if (Popped || a == null || claimers.Contains(a)) return;
        claimers.Add(a);
    }

    public IReadOnlyList<MoriMochiAgent> Pop(MoriMochiAgent by)
    {
        others.Clear();
        if (Popped) return others;

        Popped = true;
        foreach (var claimer in claimers)
        {
            if (claimer != null && claimer != by) others.Add(claimer);
        }
        claimers.Clear();

        foreach (var rendererComponent in GetComponentsInChildren<Renderer>()) rendererComponent.enabled = false;
        onPop?.PlayFeedbacks();
        Destroy(gameObject, destroyDelay);
        return others;
    }
}
}
