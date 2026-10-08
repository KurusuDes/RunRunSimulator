using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlCloudPuffs
{
    private const int PuffCount = 10;
    private const float Spread = 0.7f;
    private const float MinHeight = 0.6f;
    private const float MaxHeight = 1.3f;
    private const float MinSize = 0.9f;
    private const float MaxSize = 1.7f;
    private const float TintAmount = 0.3f;
    private const float Alpha = 0.55f;
    private const float Wobble = 0.12f;
    private const float WobbleSpeed = 1.1f;
    private const float Breathe = 0.06f;
    private const float AppearSeconds = 0.25f;
    private const float FadeSeconds = 0.4f;
    private const float OneShotSeconds = 1.4f;
    private const int SortingOrder = 8;

    private class Puff
    {
        public SpriteRenderer Sprite;
        public Vector3 Offset;
        public float Size;
        public float Phase;
    }

    private class Cloud
    {
        public BrawlZone Zone;
        public Vector3 Center;
        public Color Tint;
        public float Start;
        public float EndStart;
        public float LastAge;
        public int Frame;
        public readonly Puff[] Puffs = new Puff[PuffCount];
    }

    private readonly BrawlSignatureSprites pool;
    private readonly List<Cloud> clouds = new();
    private readonly Dictionary<BrawlZone, Cloud> zoneClouds = new();

    public BrawlCloudPuffs(BrawlSignatureSprites pool)
    {
        this.pool = pool;
    }

    public void Clear()
    {
        for (int i = 0; i < clouds.Count; i++) Release(clouds[i]);
        clouds.Clear();
        zoneClouds.Clear();
    }

    public void Armed(BrawlFxEvent e)
    {
        if (e.Source == null) return;

        var zones = BrawlZone.Active;
        for (int i = 0; i < zones.Count; i++)
        {
            var zone = zones[i];
            if (zone == null) continue;

            var spec = zone.Spec;
            if (spec.Owner != e.Source || spec.Duration > 0f || spec.Theme.Signature != BrawlSignature.Cloud) continue;
            if ((zone.Center - e.To).sqrMagnitude > 0.01f) continue;

            float now = Time.time;
            Create(zone.Center, spec.Radius, spec.Theme, spec.Team, now, now + OneShotSeconds - FadeSeconds);
            return;
        }
    }

    public void Step(float now, Quaternion face)
    {
        Poll(now);
        for (int i = clouds.Count - 1; i >= 0; i--)
        {
            if (StepCloud(clouds[i], now, face)) continue;
            Release(clouds[i]);
            clouds.RemoveAt(i);
        }
    }

    private void Poll(float now)
    {
        int frame = Time.frameCount;
        var zones = BrawlZone.Active;
        for (int i = 0; i < zones.Count; i++)
        {
            var zone = zones[i];
            if (zone == null || !zone.Armed) continue;

            var spec = zone.Spec;
            if (spec.Theme.Signature != BrawlSignature.Cloud || spec.Duration <= 0f) continue;

            zoneClouds.TryGetValue(zone, out var cloud);
            if (cloud != null && zone.Age < cloud.LastAge)
            {
                Detach(cloud, now);
                cloud = null;
            }
            if (cloud == null)
            {
                cloud = Create(zone.Center, spec.Radius, spec.Theme, spec.Team, now, float.MaxValue);
                if (cloud == null) continue;
                cloud.Zone = zone;
                zoneClouds[zone] = cloud;
            }

            cloud.Frame = frame;
            cloud.LastAge = zone.Age;
            cloud.Center = zone.Center;
        }
    }

    private Cloud Create(Vector3 center, float radius, BrawlTheme theme, ExpeditionTeam team, float now, float endStart)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.GlowSprite == null || lib.SpriteMaterial == null) return null;

        var cloud = new Cloud
        {
            Center = center,
            Tint = Color.Lerp(Color.white, BrawlTeamLook.Wash(theme.Color, team), TintAmount),
            Start = now,
            EndStart = endStart
        };
        for (int i = 0; i < PuffCount; i++)
        {
            Vector2 p = Random.insideUnitCircle * (radius * Spread);
            cloud.Puffs[i] = new Puff
            {
                Sprite = pool.AcquireSprite(lib.GlowSprite, lib.SpriteMaterial, SortingOrder),
                Offset = new Vector3(p.x, Random.Range(MinHeight, MaxHeight), p.y),
                Size = Random.Range(MinSize, MaxSize),
                Phase = Random.Range(0f, Mathf.PI * 2f)
            };
        }
        clouds.Add(cloud);
        return cloud;
    }

    private void Detach(Cloud cloud, float now)
    {
        if (cloud.Zone != null) zoneClouds.Remove(cloud.Zone);
        cloud.Zone = null;
        cloud.EndStart = now;
    }

    private bool StepCloud(Cloud cloud, float now, Quaternion face)
    {
        if (cloud.Zone != null && cloud.Frame != Time.frameCount) Detach(cloud, now);

        float fade = Mathf.Clamp01((now - cloud.EndStart) / FadeSeconds);
        if (fade >= 1f) return false;

        float appear = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01((now - cloud.Start) / AppearSeconds));
        Color color = cloud.Tint;
        color.a = Alpha * (1f - fade);

        for (int i = 0; i < PuffCount; i++)
        {
            var puff = cloud.Puffs[i];
            float w = now * WobbleSpeed + puff.Phase;
            Vector3 wobble = new Vector3(Mathf.Sin(w), Mathf.Sin(w * 1.3f) * 0.5f, Mathf.Cos(w * 0.8f)) * Wobble;
            var tr = puff.Sprite.transform;
            tr.position = cloud.Center + puff.Offset + wobble;
            tr.rotation = face;
            tr.localScale = Vector3.one * (puff.Size * appear * (1f + Breathe * Mathf.Sin(now * 1.7f + puff.Phase)));
            puff.Sprite.color = color;
        }
        return true;
    }

    private void Release(Cloud cloud)
    {
        if (cloud.Zone != null) zoneClouds.Remove(cloud.Zone);
        cloud.Zone = null;
        for (int i = 0; i < PuffCount; i++) pool.ReleaseSprite(cloud.Puffs[i].Sprite);
    }
}
}
