using System.Collections.Generic;
using MoreMountains.Feedbacks;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BubbleMachine : MonoBehaviour
{
    [SerializeField] private Bubble bubblePrefab;
    [SerializeField] private Transform nozzle;
    [SerializeField] private MMF_Player onEmit;
    [SerializeField, Min(0.1f)] private float interval = 1.2f;
    [SerializeField, Min(1)] private int maxAlive = 8;
    [SerializeField, Range(0f, 90f)] private float coneAngle = 35f;

    private readonly List<Bubble> alive = new List<Bubble>();
    private WorldPropInstance prop;
    private float timer;

    private void Awake() => prop = GetComponent<WorldPropInstance>();

    private void Update()
    {
        if (prop != null && prop.IsHeld) return;

        timer += Time.deltaTime;
        if (timer < interval) return;
        timer = 0f;

        alive.RemoveAll(b => b == null || b.Popped);
        if (alive.Count >= maxAlive || bubblePrefab == null) return;

        Emit();
    }

    private void Emit()
    {
        var origin = nozzle != null ? nozzle : transform;
        var spin = Quaternion.AngleAxis(Random.Range(0f, 360f), origin.forward);
        var tilt = Quaternion.AngleAxis(Random.Range(0f, coneAngle), origin.right);
        var direction = spin * tilt * origin.forward;

        var bubble = Instantiate(bubblePrefab, origin.position, Quaternion.identity);
        bubble.Initialize(direction, transform.position.y);
        alive.Add(bubble);
        onEmit?.PlayFeedbacks();
    }
}
}
