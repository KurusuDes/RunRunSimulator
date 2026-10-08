using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlLineFx : MonoBehaviour
{
    private const int LightningSubdivisions = 6;
    private const int BeamPoints = 12;
    private const int WhipPoints = 14;
    private const float JitterInterval = 0.04f;
    private const float JitterAmount = 0.25f;
    private const float LightningWidth = 0.24f;
    private const float LightningCoreWidth = 0.06f;
    private const float LightningGlowWidth = 0.6f;
    private const float LightningGlowAlpha = 0.28f;
    private const float BeamWidth = 0.26f;
    private const float BeamGlowWidth = 0.7f;
    private const float BeamGlowAlpha = 0.25f;
    private const float WhipWidth = 0.22f;
    private const float WhipTipWidth = 0.04f;
    private const float WhipGlowWidth = 0.5f;
    private const float WhipGlowAlpha = 0.25f;
    private const int GlowOrder = 19;
    private const int OuterOrder = 20;
    private const int CoreOrder = 21;
    private const float StormWidthScale = 1.3f;
    private const int RainbowKeys = 6;
    private const float RainbowSpeed = 0.8f;
    private const float RainbowSaturation = 0.7f;

    private enum Kind { Lightning, Beam, Whip }

    private class Entry
    {
        public GameObject Go;
        public LineRenderer Glow;
        public LineRenderer Outer;
        public LineRenderer Core;
        public BrawlLightningBranches Branches;
    }

    private class Running
    {
        public Entry Entry;
        public Kind Kind;
        public float Start;
        public float Seconds;
        public Color Color;
        public Vector3[] Path;
        public Vector3[] Points;
        public float NextJitter;
        public Vector3 From;
        public Vector3 To;
        public BrawlFighter FromFighter;
        public BrawlFighter ToFighter;
        public BrawlSignature Signature;
        public float WidthScale = 1f;
        public BrawlLightningBranches Branches;
    }

    private static readonly GradientAlphaKey[] OpaqueAlpha = { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(1f, 1f) };

    private readonly Stack<Entry> free = new();
    private readonly List<Running> running = new();
    private readonly Gradient rainbow = new();
    private readonly GradientColorKey[] rainbowKeys = new GradientColorKey[RainbowKeys];

    private BrawlGlowFlashFx flashes;

    public void Lightning(Vector3[] path, Color color, float seconds = 0.3f, BrawlSignature signature = BrawlSignature.None)
    {
        if (path == null || path.Length < 2) return;
        var entry = Acquire();
        if (entry == null) return;

        var run = new Running
        {
            Entry = entry,
            Kind = Kind.Lightning,
            Start = Time.time,
            Seconds = Mathf.Max(0.05f, seconds),
            Color = color,
            Path = path,
            Points = new Vector3[(path.Length - 1) * LightningSubdivisions + 1],
            NextJitter = 0f
        };

        Prepare(entry, true, AnimationCurve.Constant(0f, 1f, 1f));
        SetColors(entry.Outer, color, color);
        SetColors(entry.Core, Color.white, Color.white);
        SetGlowColor(entry, color, LightningGlowAlpha);
        if (signature == BrawlSignature.Storm)
        {
            entry.Branches ??= new BrawlLightningBranches(entry.Go.transform, OuterOrder);
            entry.Branches.Arm(BrawlVfxLibrarySO.Current.LineMaterial, color);
            run.Branches = entry.Branches;
            run.WidthScale = StormWidthScale;
        }
        if (flashes == null) flashes = gameObject.AddComponent<BrawlGlowFlashFx>();
        flashes.Pop(path, color);
        running.Add(run);
    }

    public void Beam(BrawlFighter from, BrawlFighter to, Color color, float seconds, BrawlSignature signature = BrawlSignature.None)
    {
        if (from == null || to == null) return;
        var entry = Acquire();
        if (entry == null) return;

        var run = new Running
        {
            Entry = entry,
            Kind = Kind.Beam,
            Start = Time.time,
            Seconds = Mathf.Max(0.05f, seconds),
            Color = color,
            Points = new Vector3[BeamPoints],
            FromFighter = from,
            ToFighter = to,
            Signature = signature
        };

        Prepare(entry, false, AnimationCurve.Constant(0f, 1f, 1f));
        if (signature == BrawlSignature.Rainbow)
        {
            ApplyRainbow(run);
            running.Add(run);
            return;
        }

        var gradient = new Gradient();
        gradient.SetKeys(
            new[] { new GradientColorKey(color, 0f), new GradientColorKey(Color.white, 0.5f), new GradientColorKey(color, 1f) },
            new[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(1f, 1f) });
        entry.Outer.colorGradient = gradient;
        SetGlowColor(entry, color, BeamGlowAlpha);
        running.Add(run);
    }

    public void Whip(Vector3 from, Vector3 to, Color color, float seconds = 0.2f)
    {
        var entry = Acquire();
        if (entry == null) return;

        var run = new Running
        {
            Entry = entry,
            Kind = Kind.Whip,
            Start = Time.time,
            Seconds = Mathf.Max(0.05f, seconds),
            Color = color,
            Points = new Vector3[WhipPoints],
            From = from,
            To = to
        };

        Prepare(entry, false, new AnimationCurve(new Keyframe(0f, 1f), new Keyframe(1f, WhipTipWidth / WhipWidth)));
        SetColors(entry.Outer, color, color);
        SetGlowColor(entry, color, WhipGlowAlpha);
        running.Add(run);
    }

    private void LateUpdate()
    {
        for (int i = running.Count - 1; i >= 0; i--)
        {
            var run = running[i];
            float t = (Time.time - run.Start) / run.Seconds;
            bool alive = t < 1f && Step(run, t);
            if (alive) continue;

            Release(run.Entry);
            running.RemoveAt(i);
        }
    }

    private bool Step(Running run, float t)
    {
        switch (run.Kind)
        {
            case Kind.Lightning: StepLightning(run, t); return true;
            case Kind.Beam: return StepBeam(run, t);
            default: StepWhip(run, t); return true;
        }
    }

    private void StepLightning(Running run, float t)
    {
        if (Time.time >= run.NextJitter)
        {
            run.NextJitter = Time.time + JitterInterval;
            BuildLightning(run);
            SetPoints(run.Entry.Glow, run.Points);
            SetPoints(run.Entry.Outer, run.Points);
            SetPoints(run.Entry.Core, run.Points);
            run.Branches?.Rebuild(run.Points);
        }

        float fade = 1f - Mathf.Clamp01((t - 0.5f) * 2f);
        float scaled = fade * run.WidthScale;
        run.Entry.Glow.widthMultiplier = LightningGlowWidth * scaled;
        run.Entry.Outer.widthMultiplier = LightningWidth * scaled;
        run.Entry.Core.widthMultiplier = LightningCoreWidth * scaled;
        run.Branches?.Fade(fade);
    }

    private static void BuildLightning(Running run)
    {
        var path = run.Path;
        int index = 0;
        for (int s = 0; s < path.Length - 1; s++)
        {
            Vector3 a = path[s];
            Vector3 b = path[s + 1];
            Vector3 side = Vector3.Cross((b - a).normalized, Vector3.up);
            if (side.sqrMagnitude < 0.0001f) side = Vector3.right;
            side.Normalize();

            for (int k = 0; k < LightningSubdivisions; k++)
            {
                Vector3 p = Vector3.Lerp(a, b, k / (float)LightningSubdivisions);
                if (k > 0)
                    p += side * Random.Range(-JitterAmount, JitterAmount) + Vector3.up * Random.Range(-JitterAmount, JitterAmount) * 0.6f;
                run.Points[index++] = p;
            }
        }
        run.Points[index] = path[path.Length - 1];
    }

    private bool StepBeam(Running run, float t)
    {
        var from = run.FromFighter;
        var to = run.ToFighter;
        if (from == null || to == null || !from.IsAlive || !to.IsAlive) return false;
        if (run.Signature == BrawlSignature.Rainbow) ApplyRainbow(run);

        Vector3 a = from.Center;
        Vector3 b = to.Center;
        Vector3 side = Vector3.Cross((b - a).normalized, Vector3.up);
        if (side.sqrMagnitude < 0.0001f) side = Vector3.right;
        side.Normalize();

        float phase = Time.time * 18f;
        for (int i = 0; i < BeamPoints; i++)
        {
            float u = i / (float)(BeamPoints - 1);
            float envelope = Mathf.Sin(u * Mathf.PI);
            run.Points[i] = Vector3.Lerp(a, b, u) + side * Mathf.Sin(u * 14f - phase) * 0.12f * envelope;
        }

        SetPoints(run.Entry.Glow, run.Points);
        SetPoints(run.Entry.Outer, run.Points);

        float fade = 1f - Mathf.Clamp01((t - 0.85f) / 0.15f);
        run.Entry.Glow.widthMultiplier = BeamGlowWidth * fade;
        run.Entry.Outer.widthMultiplier = BeamWidth * (0.85f + 0.15f * Mathf.Sin(Time.time * 30f)) * fade;
        return true;
    }

    private void ApplyRainbow(Running run)
    {
        ExpeditionTeam team = run.FromFighter.Team;
        for (int k = 0; k < RainbowKeys; k++)
        {
            Color c = Color.HSVToRGB(((k / (float)RainbowKeys) + Time.time * RainbowSpeed) % 1f, RainbowSaturation, 1f);
            rainbowKeys[k] = new GradientColorKey(BrawlTeamLook.Wash(c, team), k / (float)(RainbowKeys - 1));
        }
        rainbow.SetKeys(rainbowKeys, OpaqueAlpha);
        run.Entry.Outer.colorGradient = rainbow;
        SetGlowColor(run.Entry, rainbow.Evaluate(0.5f), BeamGlowAlpha);
    }

    private void StepWhip(Running run, float t)
    {
        Vector3 a = run.From;
        Vector3 b = run.To;
        Vector3 dir = b - a;
        float dist = dir.magnitude;
        Vector3 side = dist > 0.001f ? Vector3.Cross(dir / dist, Vector3.up) : Vector3.right;

        float sweep = Mathf.Lerp(-1f, 1f, Mathf.SmoothStep(0f, 1f, t));
        Vector3 control = (a + b) * 0.5f + side * sweep * dist * 0.35f;

        for (int i = 0; i < WhipPoints; i++)
        {
            float u = i / (float)(WhipPoints - 1);
            float v = 1f - u;
            run.Points[i] = v * v * a + 2f * v * u * control + u * u * b;
        }

        SetPoints(run.Entry.Glow, run.Points);
        SetPoints(run.Entry.Outer, run.Points);
        float shrink = 1f - t * 0.5f;
        run.Entry.Glow.widthMultiplier = WhipGlowWidth * shrink;
        run.Entry.Outer.widthMultiplier = WhipWidth * shrink;

        Color faded = run.Color;
        faded.a = 1f - t * t;
        SetColors(run.Entry.Outer, faded, faded);
        SetGlowColor(run.Entry, run.Color, WhipGlowAlpha * faded.a);
    }

    private Entry Acquire()
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.LineMaterial == null) return null;

        Entry entry = free.Count > 0 ? free.Pop() : Create();
        entry.Glow.sharedMaterial = lib.LineMaterial;
        entry.Outer.sharedMaterial = lib.LineMaterial;
        entry.Core.sharedMaterial = lib.LineMaterial;
        entry.Go.SetActive(true);
        return entry;
    }

    private static void Prepare(Entry entry, bool core, AnimationCurve curve)
    {
        entry.Glow.widthCurve = curve;
        entry.Outer.widthCurve = curve;
        entry.Core.widthCurve = AnimationCurve.Constant(0f, 1f, 1f);
        entry.Glow.positionCount = 0;
        entry.Outer.positionCount = 0;
        entry.Core.positionCount = 0;
        entry.Core.enabled = core;
        entry.Branches?.Disable();
    }

    private static void SetPoints(LineRenderer line, Vector3[] points)
    {
        line.positionCount = points.Length;
        line.SetPositions(points);
    }

    private static void SetColors(LineRenderer line, Color start, Color end)
    {
        line.startColor = start;
        line.endColor = end;
    }

    private static void SetGlowColor(Entry entry, Color color, float alpha)
    {
        color.a = alpha;
        SetColors(entry.Glow, color, color);
    }

    private Entry Create()
    {
        var go = new GameObject("Line");
        go.transform.SetParent(transform, false);

        var glowGo = new GameObject("Glow");
        glowGo.transform.SetParent(go.transform, false);

        var coreGo = new GameObject("Core");
        coreGo.transform.SetParent(go.transform, false);

        var entry = new Entry
        {
            Go = go,
            Glow = Setup(glowGo.AddComponent<LineRenderer>(), GlowOrder),
            Outer = Setup(go.AddComponent<LineRenderer>(), OuterOrder),
            Core = Setup(coreGo.AddComponent<LineRenderer>(), CoreOrder)
        };
        return entry;
    }

    public static LineRenderer Setup(LineRenderer line, int order)
    {
        line.useWorldSpace = true;
        line.numCapVertices = 4;
        line.numCornerVertices = 2;
        line.alignment = LineAlignment.View;
        line.textureMode = LineTextureMode.Stretch;
        line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        line.receiveShadows = false;
        line.sortingOrder = order;
        return line;
    }

    private void Release(Entry entry)
    {
        entry.Go.SetActive(false);
        free.Push(entry);
    }
}
}
