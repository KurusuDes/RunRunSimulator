using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlStormCrackle
{
    private const int BoltCount = 3;
    private const int BoltPoints = 5;
    private const float MinLength = 0.5f;
    private const float MaxLength = 0.8f;
    private const float AroundRadius = 0.5f;
    private const float Jitter = 0.12f;
    private const float Width = 0.07f;
    private const float RegenSeconds = 0.05f;
    private const int SortingOrder = 22;

    private class Run
    {
        public BrawlFighter Target;
        public Color Color;
        public float Start;
        public float Seconds;
        public float NextRegen;
        public readonly LineRenderer[] Bolts = new LineRenderer[BoltCount];
    }

    private readonly Transform root;
    private readonly List<Run> runs = new();
    private readonly Stack<LineRenderer> free = new();
    private readonly Vector3[] points = new Vector3[BoltPoints];

    public BrawlStormCrackle(Transform root)
    {
        this.root = root;
    }

    public void Clear()
    {
        for (int i = 0; i < runs.Count; i++) Release(runs[i]);
        runs.Clear();
    }

    public void Crackle(BrawlFighter target, Color color, float seconds)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (target == null || seconds <= 0.01f || lib == null || lib.LineMaterial == null) return;

        float now = Time.time;
        Run run = null;
        for (int i = 0; i < runs.Count; i++)
        {
            if (runs[i].Target == target)
            {
                run = runs[i];
                break;
            }
        }

        if (run == null)
        {
            run = new Run { Target = target };
            for (int i = 0; i < BoltCount; i++) run.Bolts[i] = Acquire(lib.LineMaterial);
            runs.Add(run);
        }
        else
        {
            seconds = Mathf.Max(seconds, run.Start + run.Seconds - now);
        }

        run.Color = color;
        run.Start = now;
        run.Seconds = seconds;
        run.NextRegen = 0f;
    }

    public void Step(float now)
    {
        for (int i = runs.Count - 1; i >= 0; i--)
        {
            var run = runs[i];
            if (run.Target == null || now - run.Start >= run.Seconds)
            {
                Release(run);
                runs.RemoveAt(i);
                continue;
            }
            if (now < run.NextRegen) continue;

            run.NextRegen = now + RegenSeconds;
            Vector3 center = run.Target.Center;
            for (int k = 0; k < BoltCount; k++) Build(run.Bolts[k], center, run.Color);
        }
    }

    private void Build(LineRenderer line, Vector3 center, Color color)
    {
        Vector3 start = center + Random.onUnitSphere * AroundRadius;
        Vector3 dir = Random.onUnitSphere;
        float length = Random.Range(MinLength, MaxLength);
        for (int p = 0; p < BoltPoints; p++)
        {
            float u = p / (float)(BoltPoints - 1);
            Vector3 point = start + dir * (length * u);
            if (p > 0 && p < BoltPoints - 1)
                point += Vector3.Cross(dir, Random.onUnitSphere).normalized * Random.Range(-Jitter, Jitter);
            points[p] = point;
        }
        line.SetPositions(points);
        line.startColor = color;
        line.endColor = color;
    }

    private LineRenderer Acquire(Material material)
    {
        LineRenderer line;
        if (free.Count > 0)
        {
            line = free.Pop();
        }
        else
        {
            var go = new GameObject("StormBolt");
            go.transform.SetParent(root, false);
            line = go.AddComponent<LineRenderer>();
            line.useWorldSpace = true;
            line.numCapVertices = 2;
            line.numCornerVertices = 1;
            line.alignment = LineAlignment.View;
            line.textureMode = LineTextureMode.Stretch;
            line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            line.receiveShadows = false;
            line.sortingOrder = SortingOrder;
            line.widthMultiplier = Width;
            line.positionCount = BoltPoints;
        }
        line.sharedMaterial = material;
        line.gameObject.SetActive(true);
        return line;
    }

    private void Release(Run run)
    {
        for (int i = 0; i < BoltCount; i++)
        {
            var line = run.Bolts[i];
            if (line == null) continue;
            line.gameObject.SetActive(false);
            free.Push(line);
        }
    }
}
}
