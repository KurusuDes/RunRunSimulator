using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlRainFx : MonoBehaviour
{
    private const float RainHeight = 7f;
    private const float RainFallSeconds = 0.4f;
    private const float RainFirstFraction = 0.45f;
    private const float ZoneDropHeight = 3f;
    private const float ZoneDropSeconds = 0.3f;
    private const float AmbientInterval = 0.22f;
    private const float MinSize = 0.6f;
    private const float MaxSize = 0.9f;
    private const float MaxSpin = 720f;
    private const float MinFallSeconds = 0.02f;

    private class Drop
    {
        public SpriteRenderer Sprite;
        public BrawlTheme Theme;
        public Vector3 Ground;
        public float Start;
        public float Fall;
        public float Height;
        public float Size;
        public float Spin;
    }

    private class ZoneClock
    {
        public float Accum;
        public int Frame;
    }

    [Required, SerializeField] private BrawlIconParticles icons;

    private readonly Stack<SpriteRenderer> free = new();
    private readonly List<Drop> drops = new();
    private readonly Dictionary<BrawlZone, ZoneClock> clocks = new();
    private readonly List<BrawlZone> stale = new();

    public void Rain(Vector3 center, float radius, BrawlTheme theme, float seconds, int count)
    {
        if (count <= 0) return;

        float now = Time.time;
        seconds = Mathf.Max(0.1f, seconds);
        for (int i = 0; i < count; i++)
        {
            float u = count > 1 ? i / (float)(count - 1) : 1f;
            float land = seconds * Mathf.Lerp(RainFirstFraction, 1f, u);
            float fall = Mathf.Max(MinFallSeconds, Mathf.Min(RainFallSeconds, land));
            Enqueue(theme, RandomInDisc(center, radius), now + land - fall, fall, RainHeight);
        }
    }

    private void LateUpdate()
    {
        float now = Time.time;
        StepZones(Time.deltaTime);

        var cam = Camera.main;
        Quaternion face = cam != null ? cam.transform.rotation : Quaternion.identity;
        for (int i = drops.Count - 1; i >= 0; i--)
        {
            if (StepDrop(drops[i], now, face)) continue;
            drops.RemoveAt(i);
        }
    }

    private void StepZones(float dt)
    {
        int frame = Time.frameCount;
        var zones = BrawlZone.Active;
        for (int i = 0; i < zones.Count; i++)
        {
            var zone = zones[i];
            if (zone == null || !zone.Armed || zone.Spec.Duration <= 0f) continue;

            if (!clocks.TryGetValue(zone, out var clock))
            {
                clock = new ZoneClock();
                clocks[zone] = clock;
            }
            clock.Frame = frame;
            clock.Accum += dt;
            if (clock.Accum < AmbientInterval) continue;

            clock.Accum -= AmbientInterval;
            Ambient(zone);
        }

        stale.Clear();
        foreach (var pair in clocks)
        {
            if (pair.Value.Frame != frame) stale.Add(pair.Key);
        }
        for (int i = 0; i < stale.Count; i++) clocks.Remove(stale[i]);
    }

    private void Ambient(BrawlZone zone)
    {
        var spec = zone.Spec;
        Vector3 point = RandomInDisc(zone.Center, spec.Radius);
        var theme = BrawlTeamLook.Wash(spec.Theme, spec.Team);

        if (spec.HealPerTick > 0f)
        {
            if (icons != null) icons.Burst(point, theme, 2, 1.2f, 0.32f, 0.9f, true);
        }
        else if (spec.DamagePerTick > 0f)
        {
            Enqueue(theme, point, Time.time, ZoneDropSeconds, ZoneDropHeight);
        }
    }

    private bool StepDrop(Drop drop, float now, Quaternion face)
    {
        if (now < drop.Start) return true;

        float t = (now - drop.Start) / drop.Fall;
        if (t >= 1f)
        {
            Land(drop);
            return false;
        }

        if (drop.Sprite == null)
        {
            drop.Sprite = Acquire(drop.Theme);
            if (drop.Sprite == null) return false;
        }

        var tr = drop.Sprite.transform;
        tr.position = drop.Ground + Vector3.up * (drop.Height * (1f - t * t));
        tr.rotation = face * Quaternion.Euler(0f, 0f, t * drop.Spin);
        tr.localScale = Vector3.one * drop.Size;
        return true;
    }

    private void Land(Drop drop)
    {
        if (icons != null) icons.Burst(drop.Ground, drop.Theme, 3, 2.5f, 0.3f, 0.35f);
        Release(drop.Sprite);
        drop.Sprite = null;
    }

    private void Enqueue(BrawlTheme theme, Vector3 ground, float start, float fall, float height)
    {
        drops.Add(new Drop
        {
            Theme = theme,
            Ground = ground,
            Start = start,
            Fall = fall,
            Height = height,
            Size = Random.Range(MinSize, MaxSize),
            Spin = Random.Range(-MaxSpin, MaxSpin)
        });
    }

    private static Vector3 RandomInDisc(Vector3 center, float radius)
    {
        Vector2 p = Random.insideUnitCircle * radius;
        return new Vector3(center.x + p.x, center.y, center.z + p.y);
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
            var go = new GameObject("RainSprite");
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
