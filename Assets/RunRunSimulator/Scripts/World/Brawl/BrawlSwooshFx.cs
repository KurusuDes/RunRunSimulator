using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlSwooshFx : MonoBehaviour
{
    private const int Segments = 28;
    private const int Rows = 3;
    private const float InnerRatio = 0.45f;
    private const float MidRatio = 0.72f;
    private const float TiltDegrees = 12f;
    private const float HeadShare = 0.55f;
    private const float TailDelay = 0.2f;
    private const float FadeStart = 0.5f;
    private const int SortingOrder = 18;

    private class Entry
    {
        public GameObject Go;
        public MeshRenderer Renderer;
        public Mesh Mesh;
        public Vector3[] Vertices = new Vector3[(Segments + 1) * Rows];
        public Color[] Colors = new Color[(Segments + 1) * Rows];
    }

    private class Running
    {
        public Entry Entry;
        public float Start;
        public float Seconds;
        public Vector3 Forward;
        public Quaternion Tilt;
        public float Radius;
        public float Span;
        public Color Color;
    }

    private readonly Stack<Entry> free = new();
    private readonly List<Entry> all = new();
    private readonly List<Running> running = new();

    public void Swoosh(Vector3 origin, Vector3 forward, float radius, float angleDeg, float height, Color color, float seconds = 0.22f)
    {
        var entry = Acquire();
        if (entry == null) return;

        forward.y = 0f;
        forward = forward.sqrMagnitude > 0.0001f ? forward.normalized : Vector3.forward;

        entry.Go.transform.SetPositionAndRotation(origin + Vector3.up * height, Quaternion.identity);
        var run = new Running
        {
            Entry = entry,
            Start = Time.time,
            Seconds = Mathf.Max(0.05f, seconds),
            Forward = forward,
            Tilt = Quaternion.AngleAxis(TiltDegrees, forward),
            Radius = Mathf.Max(0.1f, radius),
            Span = angleDeg >= 360f ? 360f : Mathf.Clamp(angleDeg, 1f, 360f),
            Color = color
        };
        Step(run, 0f);
        running.Add(run);
    }

    private void LateUpdate()
    {
        for (int i = running.Count - 1; i >= 0; i--)
        {
            var run = running[i];
            float t = (Time.time - run.Start) / run.Seconds;
            if (t < 1f)
            {
                Step(run, t);
                continue;
            }

            Release(run.Entry);
            running.RemoveAt(i);
        }
    }

    private void OnDestroy()
    {
        for (int i = 0; i < all.Count; i++)
            if (all[i].Mesh != null) Destroy(all[i].Mesh);
    }

    private static void Step(Running run, float t)
    {
        float headT = Mathf.Clamp01(t / HeadShare);
        float head = 1f - (1f - headT) * (1f - headT);
        float tail = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01((t - TailDelay) / (1f - TailDelay)));
        float fade = (1f - Mathf.Clamp01((t - FadeStart) / (1f - FadeStart))) * Mathf.Clamp01((head - tail) * 6f);

        var entry = run.Entry;
        float half = run.Span * 0.5f;
        float outer = run.Radius;
        float mid = run.Radius * MidRatio;
        float inner = run.Radius * InnerRatio;

        Color white = new Color(1f, 1f, 1f, 1f);
        Color body = run.Color;
        Color edge = new Color(body.r, body.g, body.b, 0f);

        for (int i = 0; i <= Segments; i++)
        {
            float u = i / (float)Segments;
            float angle = Mathf.Lerp(-half, half, Mathf.Lerp(tail, head, u));
            Vector3 dir = run.Tilt * (Quaternion.AngleAxis(angle, Vector3.up) * run.Forward);
            float alpha = u * Mathf.Sqrt(u) * fade;

            int index = i * Rows;
            entry.Vertices[index] = dir * outer;
            entry.Vertices[index + 1] = dir * mid;
            entry.Vertices[index + 2] = dir * inner;

            white.a = alpha;
            body.a = run.Color.a * alpha;
            entry.Colors[index] = white;
            entry.Colors[index + 1] = body;
            entry.Colors[index + 2] = edge;
        }

        entry.Mesh.vertices = entry.Vertices;
        entry.Mesh.colors = entry.Colors;
        entry.Mesh.RecalculateBounds();
    }

    private Entry Acquire()
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.LineMaterial == null) return null;

        Entry entry = free.Count > 0 ? free.Pop() : Create();
        entry.Renderer.sharedMaterial = lib.LineMaterial;
        entry.Go.SetActive(true);
        return entry;
    }

    private Entry Create()
    {
        var entry = new Entry();
        entry.Mesh = new Mesh { name = "Swoosh" };
        entry.Mesh.MarkDynamic();
        entry.Mesh.vertices = entry.Vertices;
        entry.Mesh.colors = entry.Colors;
        entry.Mesh.uv = BuildUv();
        entry.Mesh.triangles = BuildTriangles();

        var go = new GameObject("Swoosh");
        go.transform.SetParent(transform, false);
        go.AddComponent<MeshFilter>().sharedMesh = entry.Mesh;

        var meshRenderer = go.AddComponent<MeshRenderer>();
        meshRenderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        meshRenderer.receiveShadows = false;
        meshRenderer.sortingOrder = SortingOrder;

        entry.Go = go;
        entry.Renderer = meshRenderer;
        all.Add(entry);
        return entry;
    }

    private static int[] BuildTriangles()
    {
        var tris = new int[Segments * (Rows - 1) * 6];
        int n = 0;
        for (int i = 0; i < Segments; i++)
        {
            for (int r = 0; r < Rows - 1; r++)
            {
                int a = i * Rows + r;
                int b = a + 1;
                int c = a + Rows;
                int d = c + 1;
                tris[n++] = a;
                tris[n++] = c;
                tris[n++] = b;
                tris[n++] = b;
                tris[n++] = c;
                tris[n++] = d;
            }
        }
        return tris;
    }

    private static Vector2[] BuildUv()
    {
        var uv = new Vector2[(Segments + 1) * Rows];
        for (int i = 0; i <= Segments; i++)
            for (int r = 0; r < Rows; r++)
                uv[i * Rows + r] = new Vector2(i / (float)Segments, r / (float)(Rows - 1));
        return uv;
    }

    private void Release(Entry entry)
    {
        entry.Go.SetActive(false);
        free.Push(entry);
    }
}
}
