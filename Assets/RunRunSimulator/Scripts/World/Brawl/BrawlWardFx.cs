using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlWardFx : MonoBehaviour
{
    private const int OrbitCount = 5;
    private const float OrbitRadius = 1f;
    private const float OrbitScale = 0.45f;
    private const float OrbitSpeed = 2.2f;
    private const float AppearSeconds = 0.15f;
    private const float ShrinkSeconds = 0.15f;
    private const float ShieldGraceSeconds = 0.3f;

    private class WardRun
    {
        public BrawlFighter Target;
        public float Start;
        public float Seconds;
        public float EndStart = -1f;
        public SpriteRenderer[] Sprites = new SpriteRenderer[OrbitCount];
    }

    private class TossRun
    {
        public SpriteRenderer Sprite;
        public Vector3 From;
        public Vector3 To;
        public float Start;
        public float Seconds;
        public float Size;
        public float Height;
    }

    private readonly Stack<SpriteRenderer> free = new();
    private readonly List<WardRun> wards = new();
    private readonly List<TossRun> tosses = new();

    public void Ward(BrawlFighter target, BrawlTheme theme, float seconds)
    {
        if (target == null) return;

        var run = new WardRun { Target = target, Start = Time.time, Seconds = Mathf.Max(0.1f, seconds) };
        for (int i = 0; i < OrbitCount; i++)
        {
            var sr = Acquire(theme);
            if (sr == null)
            {
                for (int k = 0; k < i; k++) Release(run.Sprites[k]);
                return;
            }
            run.Sprites[i] = sr;
        }
        wards.Add(run);
    }

    public void Toss(Vector3 from, Vector3 to, BrawlTheme theme, float seconds, float size)
    {
        var sr = Acquire(theme);
        if (sr == null) return;

        Vector3 flat = to - from;
        flat.y = 0f;
        tosses.Add(new TossRun
        {
            Sprite = sr,
            From = from,
            To = to,
            Start = Time.time,
            Seconds = Mathf.Max(0.05f, seconds),
            Size = size,
            Height = Mathf.Max(2f, flat.magnitude * 0.35f)
        });
    }

    private void LateUpdate()
    {
        var cam = Camera.main;
        Quaternion face = cam != null ? cam.transform.rotation : Quaternion.identity;

        for (int i = wards.Count - 1; i >= 0; i--)
        {
            if (StepWard(wards[i], face)) continue;
            for (int k = 0; k < OrbitCount; k++) Release(wards[i].Sprites[k]);
            wards.RemoveAt(i);
        }

        for (int i = tosses.Count - 1; i >= 0; i--)
        {
            if (StepToss(tosses[i], face)) continue;
            Release(tosses[i].Sprite);
            tosses.RemoveAt(i);
        }
    }

    private bool StepWard(WardRun run, Quaternion face)
    {
        var target = run.Target;
        float now = Time.time;
        float age = now - run.Start;

        if (run.EndStart < 0f)
        {
            bool expired = age >= run.Seconds;
            bool dead = target == null || !target.IsAlive;
            bool broken = age > ShieldGraceSeconds && target != null && target.Shield <= 0f;
            if (expired || dead || broken) run.EndStart = now;
        }

        float scale = OrbitScale * Mathf.Clamp01(age / AppearSeconds);
        if (run.EndStart >= 0f)
        {
            float k = (now - run.EndStart) / ShrinkSeconds;
            if (k >= 1f) return false;
            scale *= 1f - k;
        }

        if (target == null) return false;

        Vector3 center = target.Center;
        for (int i = 0; i < OrbitCount; i++)
        {
            float a = now * OrbitSpeed + i * Mathf.PI * 2f / OrbitCount;
            float bob = Mathf.Sin(now * 3f + i * 1.3f) * 0.15f;
            var t = run.Sprites[i].transform;
            t.position = center + new Vector3(Mathf.Cos(a) * OrbitRadius, bob, Mathf.Sin(a) * OrbitRadius);
            t.rotation = face;
            t.localScale = Vector3.one * scale;
        }
        return true;
    }

    private bool StepToss(TossRun run, Quaternion face)
    {
        float t = (Time.time - run.Start) / run.Seconds;
        if (t >= 1f) return false;

        Vector3 pos = Vector3.Lerp(run.From, run.To, t) + Vector3.up * (4f * run.Height * t * (1f - t));
        var tr = run.Sprite.transform;
        tr.position = pos;
        tr.rotation = face * Quaternion.Euler(0f, 0f, -t * run.Seconds * 540f);
        tr.localScale = Vector3.one * run.Size;
        return true;
    }

    private SpriteRenderer Acquire(BrawlTheme theme)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.SpriteMaterial == null) return null;

        Sprite icon = theme.Icon != null ? theme.Icon : lib.SparkSprite;
        if (icon == null) return null;

        SpriteRenderer sr;
        if (free.Count > 0)
        {
            sr = free.Pop();
        }
        else
        {
            var go = new GameObject("WardSprite");
            go.transform.SetParent(transform, false);
            sr = go.AddComponent<SpriteRenderer>();
            sr.sortingOrder = 10;
        }

        sr.sprite = icon;
        sr.color = theme.Color;
        sr.sharedMaterial = lib.SpriteMaterial;
        sr.transform.localScale = Vector3.zero;
        sr.gameObject.SetActive(true);
        return sr;
    }

    private void Release(SpriteRenderer sr)
    {
        if (sr == null) return;
        sr.gameObject.SetActive(false);
        free.Push(sr);
    }
}
}
