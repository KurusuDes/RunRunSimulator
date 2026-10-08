using System;
using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlCometSparks
{
    private const float TrailInterval = 0.04f;
    private const float TrailSpeed = 1.5f;
    private const float TrailSize = 0.22f;
    private const float TrailLife = 0.35f;
    private const int BurstSparks = 16;
    private const float BurstSpeed = 5f;
    private const float BurstSize = 0.26f;
    private const float BurstLife = 0.5f;
    private const float MinRadius = 0.5f;
    private const float RingGrowth = 1.2f;
    private const float RingFrom = 0.3f;
    private const float RingSeconds = 0.35f;
    private const float RingDelay = 0.05f;

    private class Clock
    {
        public float Accum;
        public bool Alt;
        public int Frame;
    }

    private static readonly Color Yellow = new Color(1f, 0.9f, 0.4f);
    private static readonly Color Orange = new Color(1f, 0.5f, 0.12f);
    private static readonly Color Red = new Color(1f, 0.2f, 0.08f);

    private readonly BrawlIconParticles icons;
    private readonly Action<Vector3, Color, float, float, float, float> addRing;
    private readonly Dictionary<BrawlProjectile, Clock> clocks = new();
    private readonly List<BrawlProjectile> stale = new();

    public BrawlCometSparks(BrawlIconParticles icons, Action<Vector3, Color, float, float, float, float> addRing)
    {
        this.icons = icons;
        this.addRing = addRing;
    }

    public void Clear()
    {
        clocks.Clear();
    }

    public void Burst(BrawlFxEvent e)
    {
        int half = BurstSparks / 2;
        icons.Burst(e.To, SparkTheme(false, e.Team), half, BurstSpeed, BurstSize, BurstLife);
        icons.Burst(e.To, SparkTheme(true, e.Team), half, BurstSpeed, BurstSize, BurstLife);

        float radius = Mathf.Max(e.Radius, MinRadius) * RingGrowth;
        addRing(e.To, BrawlTeamLook.Wash(Orange, e.Team), 0f, RingSeconds, RingFrom, radius);
        addRing(e.To, BrawlTeamLook.Wash(Red, e.Team), RingDelay, RingSeconds, RingFrom, radius);
    }

    public void Step(float dt)
    {
        if (BrawlVfxLibrarySO.Current == null)
        {
            clocks.Clear();
            return;
        }

        int frame = Time.frameCount;
        var list = BrawlProjectile.Active;
        for (int i = 0; i < list.Count; i++)
        {
            var projectile = list[i];
            if (projectile == null) continue;

            var shot = projectile.Shot;
            if (shot.Theme.Signature != BrawlSignature.Comet) continue;

            if (!clocks.TryGetValue(projectile, out var clock))
            {
                clock = new Clock();
                clocks[projectile] = clock;
            }
            clock.Frame = frame;
            clock.Accum += dt;
            if (clock.Accum < TrailInterval) continue;

            clock.Accum %= TrailInterval;
            clock.Alt = !clock.Alt;
            icons.Burst(projectile.transform.position, SparkTheme(clock.Alt, shot.Team), 2, TrailSpeed, TrailSize, TrailLife);
        }

        stale.Clear();
        foreach (var pair in clocks)
        {
            if (pair.Value.Frame != frame) stale.Add(pair.Key);
        }
        for (int i = 0; i < stale.Count; i++) clocks.Remove(stale[i]);
    }

    private static BrawlTheme SparkTheme(bool alt, ExpeditionTeam team)
    {
        return new BrawlTheme
        {
            Icon = BrawlVfxLibrarySO.Current.SparkSprite,
            Color = BrawlTeamLook.Wash(alt ? Orange : Yellow, team)
        };
    }
}
}
