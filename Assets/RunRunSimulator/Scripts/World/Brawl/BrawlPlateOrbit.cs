using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlPlateOrbit
{
    private const int PlateCount = 6;
    private const float PlateSize = 0.75f;
    private const float OrbitRadius = 1.25f;
    private const float OrbitDegrees = 90f;
    private const float AppearSeconds = 0.2f;
    private const float Stagger = 0.05f;
    private const float ShrinkSeconds = 0.2f;
    private const float GraceSeconds = 0.3f;
    private const int SortingOrder = 10;

    private class Run
    {
        public BrawlFighter Target;
        public float Start;
        public float Seconds;
        public float Phase;
        public float EndStart = -1f;
        public readonly SpriteRenderer[] Sprites = new SpriteRenderer[PlateCount];
    }

    private static readonly Quaternion Tilt = Quaternion.Euler(18f, 0f, 10f);

    private readonly BrawlSignatureSprites pool;
    private readonly List<Run> runs = new();

    public BrawlPlateOrbit(BrawlSignatureSprites pool)
    {
        this.pool = pool;
    }

    public void Clear()
    {
        for (int i = 0; i < runs.Count; i++) Release(runs[i]);
        runs.Clear();
    }

    public void Ward(BrawlFxEvent e)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (e.Target == null || lib == null || lib.SpriteMaterial == null) return;

        Sprite icon = e.Theme.Icon != null ? e.Theme.Icon : lib.SparkSprite;
        if (icon == null) return;

        End(e.Target);
        var run = new Run
        {
            Target = e.Target,
            Start = Time.time,
            Seconds = Mathf.Max(0.1f, e.Duration),
            Phase = Random.Range(0f, 360f)
        };
        Color color = BrawlTeamLook.Wash(e.Theme.Color, e.Team);
        for (int i = 0; i < PlateCount; i++)
        {
            var sprite = pool.AcquireSprite(icon, lib.SpriteMaterial, SortingOrder);
            sprite.color = color;
            run.Sprites[i] = sprite;
        }
        runs.Add(run);
    }

    public void Step(float now, Quaternion face)
    {
        for (int i = runs.Count - 1; i >= 0; i--)
        {
            if (StepRun(runs[i], now, face)) continue;
            Release(runs[i]);
            runs.RemoveAt(i);
        }
    }

    private bool StepRun(Run run, float now, Quaternion face)
    {
        var target = run.Target;
        float age = now - run.Start;

        if (run.EndStart < 0f)
        {
            bool expired = age >= run.Seconds;
            bool dead = target == null || !target.IsAlive;
            bool broken = age > GraceSeconds && target != null && target.Shield <= 0f;
            if (expired || dead || broken) run.EndStart = now;
        }

        float shrink = 1f;
        if (run.EndStart >= 0f)
        {
            float k = (now - run.EndStart) / ShrinkSeconds;
            if (k >= 1f) return false;
            shrink = 1f - k;
        }

        if (target == null) return false;

        Vector3 center = target.Center;
        float spin = run.Phase + now * OrbitDegrees;
        for (int i = 0; i < PlateCount; i++)
        {
            float a = (spin + i * 360f / PlateCount) * Mathf.Deg2Rad;
            Vector3 local = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * OrbitRadius;
            float pop = Pop((age - i * Stagger) / AppearSeconds);
            var tr = run.Sprites[i].transform;
            tr.position = center + Tilt * local;
            tr.rotation = face;
            tr.localScale = Vector3.one * (PlateSize * pop * shrink);
        }
        return true;
    }

    private void End(BrawlFighter target)
    {
        for (int i = runs.Count - 1; i >= 0; i--)
        {
            if (runs[i].Target != target) continue;
            Release(runs[i]);
            runs.RemoveAt(i);
        }
    }

    private void Release(Run run)
    {
        for (int i = 0; i < PlateCount; i++) pool.ReleaseSprite(run.Sprites[i]);
    }

    private static float Pop(float u)
    {
        if (u <= 0f) return 0f;
        if (u >= 1f) return 1f;
        float k = u - 1f;
        return 1f + 2.70158f * k * k * k + 1.70158f * k * k;
    }
}
}
