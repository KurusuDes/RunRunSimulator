using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlBubbleFx : MonoBehaviour
{
    private const float Radius = 1.05f;
    private const float AlphaMin = 0.08f;
    private const float AlphaMax = 0.14f;
    private const float PulseHz = 3f;
    private const float WobbleAmount = 0.03f;
    private const float WobbleSpeed = 7f;
    private const float AppearSeconds = 0.18f;
    private const float AppearPeak = 1.15f;
    private const float AppearPeakFraction = 0.6f;
    private const float PopSeconds = 0.12f;
    private const float PopScale = 1.3f;
    private const float ShieldGraceSeconds = 0.3f;
    private const int SortingOrder = 18;

    private static readonly int TintColorId = Shader.PropertyToID("_TintColor");
    private static readonly int ColorId = Shader.PropertyToID("_Color");

    private class Entry
    {
        public GameObject Go;
        public Transform Tf;
        public Material Material;
    }

    private class Run
    {
        public Entry Entry;
        public BrawlFighter Target;
        public Color Color;
        public float Start;
        public float Seconds;
        public float EndStart = -1f;
        public float Phase;
    }

    private readonly Stack<Entry> free = new();
    private readonly List<Run> runs = new();

    private Mesh sphereMesh;

    public void Bubble(BrawlFighter target, Color color, float seconds)
    {
        if (target == null) return;

        Run run = Find(target);
        if (run == null)
        {
            var entry = Acquire();
            if (entry == null) return;
            run = new Run { Entry = entry, Target = target };
            runs.Add(run);
        }

        run.Color = color;
        run.Start = Time.time;
        run.Seconds = Mathf.Max(0.1f, seconds);
        run.EndStart = -1f;
        run.Phase = Random.Range(0f, Mathf.PI * 2f);
        run.Entry.Tf.position = target.Center;
        run.Entry.Tf.localScale = Vector3.zero;
    }

    private Run Find(BrawlFighter target)
    {
        for (int i = 0; i < runs.Count; i++)
        {
            if (runs[i].Target == target) return runs[i];
        }
        return null;
    }

    private void LateUpdate()
    {
        for (int i = runs.Count - 1; i >= 0; i--)
        {
            if (Step(runs[i])) continue;
            Release(runs[i].Entry);
            runs.RemoveAt(i);
        }
    }

    private static bool Step(Run run)
    {
        var target = run.Target;
        if (target == null) return false;

        float now = Time.time;
        float age = now - run.Start;

        if (run.EndStart < 0f)
        {
            bool expired = age >= run.Seconds;
            bool dead = !target.IsAlive;
            bool broken = age > ShieldGraceSeconds && target.Shield <= 0f;
            if (expired || dead || broken) run.EndStart = now;
        }

        float scale;
        float alpha;
        if (run.EndStart >= 0f)
        {
            float k = (now - run.EndStart) / PopSeconds;
            if (k >= 1f) return false;
            scale = Mathf.Lerp(1f, PopScale, k);
            alpha = (AlphaMin + AlphaMax) * 0.5f * (1f - k);
        }
        else
        {
            float wobble = 1f + WobbleAmount * Mathf.Sin(now * WobbleSpeed + run.Phase);
            scale = AppearScale(age) * wobble;
            float pulse = 0.5f + 0.5f * Mathf.Sin(now * PulseHz * Mathf.PI * 2f + run.Phase);
            alpha = Mathf.Lerp(AlphaMin, AlphaMax, pulse) * Mathf.Clamp01(age / AppearSeconds);
        }

        var entry = run.Entry;
        entry.Tf.position = target.Center;
        entry.Tf.localScale = Vector3.one * (Radius * 2f * scale);

        Color c = run.Color;
        c.a = alpha;
        entry.Material.SetColor(TintColorId, c);
        entry.Material.SetColor(ColorId, c);
        return true;
    }

    private static float AppearScale(float age)
    {
        float u = age / AppearSeconds;
        if (u >= 1f) return 1f;
        return u < AppearPeakFraction
            ? Mathf.Lerp(0f, AppearPeak, u / AppearPeakFraction)
            : Mathf.Lerp(AppearPeak, 1f, (u - AppearPeakFraction) / (1f - AppearPeakFraction));
    }

    private Entry Acquire()
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.ParticleAdditiveMaterial == null) return null;

        Entry entry = free.Count > 0 ? free.Pop() : Create(lib.ParticleAdditiveMaterial);
        entry.Tf.localScale = Vector3.zero;
        entry.Go.SetActive(true);
        return entry;
    }

    private Entry Create(Material source)
    {
        var go = new GameObject("Bubble");
        go.transform.SetParent(transform, false);
        go.AddComponent<MeshFilter>().sharedMesh = GetSphereMesh();

        var material = new Material(source);
        var renderer = go.AddComponent<MeshRenderer>();
        renderer.sharedMaterial = material;
        renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        renderer.receiveShadows = false;
        renderer.lightProbeUsage = UnityEngine.Rendering.LightProbeUsage.Off;
        renderer.reflectionProbeUsage = UnityEngine.Rendering.ReflectionProbeUsage.Off;
        renderer.sortingOrder = SortingOrder;

        return new Entry { Go = go, Tf = go.transform, Material = material };
    }

    private Mesh GetSphereMesh()
    {
        if (sphereMesh != null) return sphereMesh;

        var primitive = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        sphereMesh = primitive.GetComponent<MeshFilter>().sharedMesh;
        Destroy(primitive);
        return sphereMesh;
    }

    private void Release(Entry entry)
    {
        entry.Go.SetActive(false);
        free.Push(entry);
    }

    private void OnDestroy()
    {
        foreach (var entry in free) DestroyMaterial(entry);
        for (int i = 0; i < runs.Count; i++) DestroyMaterial(runs[i].Entry);
    }

    private static void DestroyMaterial(Entry entry)
    {
        if (entry != null && entry.Material != null) Destroy(entry.Material);
    }
}
}
