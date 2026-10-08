using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

namespace MoriMonchiSimulator
{

public class BrawlVortexFx : MonoBehaviour
{
    private const int ArmCount = 3;
    private const int ArmPoints = 24;
    private const float SpinDegreesPerSecond = 540f;
    private const float ArmSweep = 3.2f;
    private const float EndRadius = 0.3f;
    private const float GroundLift = 0.3f;
    private const float StartWidth = 0.14f;
    private const float EndWidth = 0.02f;
    private const float FadeStart = 0.7f;
    private const float HaloFrom = 0.4f;
    private const float HaloTo = 1.6f;
    private const float HaloNudge = 0.5f;
    private const int ArmOrder = 20;
    private const int HaloOrder = 21;

    private class Entry
    {
        public GameObject Go;
        public LineRenderer[] Arms = new LineRenderer[ArmCount];
        public SpriteRenderer Halo;
    }

    private class Run
    {
        public Entry Entry;
        public Vector3 Center;
        public float Radius;
        public Color Color;
        public float Start;
        public float Seconds;
    }

    private readonly Stack<Entry> free = new();
    private readonly List<Run> runs = new();
    private readonly Vector3[] points = new Vector3[ArmPoints];

    public void Vortex(Vector3 center, float radius, Color color, float seconds)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.LineMaterial == null) return;

        var entry = free.Count > 0 ? free.Pop() : Create();
        for (int i = 0; i < ArmCount; i++) entry.Arms[i].sharedMaterial = lib.LineMaterial;

        bool halo = lib.GlowSprite != null && lib.ParticleAdditiveMaterial != null;
        entry.Halo.enabled = halo;
        if (halo)
        {
            entry.Halo.sprite = lib.GlowSprite;
            entry.Halo.sharedMaterial = lib.ParticleAdditiveMaterial;
            entry.Halo.transform.localScale = Vector3.zero;
        }

        center.y = GroundY(center) + GroundLift;
        entry.Go.SetActive(true);
        runs.Add(new Run
        {
            Entry = entry,
            Center = center,
            Radius = Mathf.Max(EndRadius, radius),
            Color = color,
            Start = Time.time,
            Seconds = Mathf.Max(0.05f, seconds)
        });
    }

    private void LateUpdate()
    {
        var cam = Camera.main;
        Quaternion face = cam != null ? cam.transform.rotation : Quaternion.identity;
        Vector3 nudge = cam != null ? -cam.transform.forward * HaloNudge : Vector3.zero;
        float now = Time.time;

        for (int i = runs.Count - 1; i >= 0; i--)
        {
            var run = runs[i];
            float t = (now - run.Start) / run.Seconds;
            if (t >= 1f)
            {
                run.Entry.Go.SetActive(false);
                free.Push(run.Entry);
                runs.RemoveAt(i);
                continue;
            }
            Step(run, t, now - run.Start, face, nudge);
        }
    }

    private void Step(Run run, float t, float age, Quaternion face, Vector3 nudge)
    {
        float fade = 1f - Mathf.Clamp01((t - FadeStart) / (1f - FadeStart));
        float outer = Mathf.Lerp(run.Radius, EndRadius, t);
        float spin = age * SpinDegreesPerSecond * Mathf.Deg2Rad;

        Color c = run.Color;
        c.a *= fade;

        for (int arm = 0; arm < ArmCount; arm++)
        {
            float baseAngle = spin + arm * Mathf.PI * 2f / ArmCount;
            for (int p = 0; p < ArmPoints; p++)
            {
                float u = p / (float)(ArmPoints - 1);
                float a = baseAngle - u * ArmSweep;
                float r = outer * u;
                points[p] = run.Center + new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r);
            }

            var line = run.Entry.Arms[arm];
            line.SetPositions(points);
            line.startColor = c;
            line.endColor = c;
        }

        var halo = run.Entry.Halo;
        if (!halo.enabled) return;

        var tr = halo.transform;
        tr.position = run.Center + nudge;
        tr.rotation = face;
        tr.localScale = Vector3.one * Mathf.Lerp(HaloFrom, HaloTo, t);
        Color hc = run.Color;
        hc.a *= 1f - t;
        halo.color = hc;
    }

    private Entry Create()
    {
        var go = new GameObject("Vortex");
        go.transform.SetParent(transform, false);

        var entry = new Entry { Go = go };
        var widthCurve = new AnimationCurve(new Keyframe(0f, 1f), new Keyframe(1f, EndWidth / StartWidth));
        for (int i = 0; i < ArmCount; i++)
        {
            var armGo = new GameObject("Arm");
            armGo.transform.SetParent(go.transform, false);
            var line = armGo.AddComponent<LineRenderer>();
            line.useWorldSpace = true;
            line.numCapVertices = 4;
            line.numCornerVertices = 2;
            line.alignment = LineAlignment.View;
            line.textureMode = LineTextureMode.Stretch;
            line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            line.receiveShadows = false;
            line.sortingOrder = ArmOrder;
            line.widthCurve = widthCurve;
            line.widthMultiplier = StartWidth;
            line.positionCount = ArmPoints;
            entry.Arms[i] = line;
        }

        var haloGo = new GameObject("Halo");
        haloGo.transform.SetParent(go.transform, false);
        entry.Halo = haloGo.AddComponent<SpriteRenderer>();
        entry.Halo.sortingOrder = HaloOrder;
        return entry;
    }

    private static float GroundY(Vector3 p)
    {
        return NavMesh.SamplePosition(p, out var hit, 3f, NavMesh.AllAreas) ? hit.position.y : p.y;
    }
}
}
