using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public struct BrawlZoneSpec
{
    public BrawlFighter Owner;
    public ExpeditionTeam Team;
    public Vector3 Center;
    public float Radius;
    public float Delay;
    public float Duration;
    public float TickSeconds;
    public float DamagePerTick;
    public float HealPerTick;
    public float Slow;
    public float SlowSeconds;
    public float StunSeconds;
    public float Knockback;
    public float Pull;
    public bool FollowOwner;
    public bool HitOnArm;
    public BrawlTheme Theme;
}

public class BrawlZone : MonoBehaviour
{
    private const float DefaultTickSeconds = 0.5f;
    private const float PullMinDistance = 0.1f;

    private static readonly List<BrawlZone> active = new();
    private static readonly List<BrawlZone> pool = new();
    private static Transform root;

    public static IReadOnlyList<BrawlZone> Active => active;

    private readonly List<BrawlFighter> scratch = new();

    private BrawlZoneSpec spec;
    private Vector3 center;
    private float age;
    private float tickClock;
    private bool armed;
    private bool live;

    public BrawlZoneSpec Spec => spec;
    public Vector3 Center => center;
    public float Age => age;
    public bool Armed => age >= spec.Delay;
    public float Delay01 => spec.Delay > 0f ? Mathf.Clamp01(age / spec.Delay) : 1f;
    public float Life01 => Armed && spec.Duration > 0f ? Mathf.Clamp01((age - spec.Delay) / spec.Duration) : 0f;

    public static BrawlZone Spawn(BrawlZoneSpec spec)
    {
        var zone = Acquire();
        zone.Begin(spec);
        return zone;
    }

    public static void ClearAll()
    {
        for (int i = active.Count - 1; i >= 0; i--)
        {
            var zone = active[i];
            if (zone != null) zone.Release();
            else active.RemoveAt(i);
        }
    }

    private static BrawlZone Acquire()
    {
        while (pool.Count > 0)
        {
            var pooled = pool[pool.Count - 1];
            pool.RemoveAt(pool.Count - 1);
            if (pooled != null) return pooled;
        }
        if (root == null) root = new GameObject("BrawlZones").transform;
        var go = new GameObject("BrawlZone");
        go.transform.SetParent(root, false);
        return go.AddComponent<BrawlZone>();
    }

    private void OnDestroy()
    {
        active.Remove(this);
        pool.Remove(this);
    }

    private void Begin(BrawlZoneSpec s)
    {
        if (s.TickSeconds <= 0f) s.TickSeconds = DefaultTickSeconds;
        spec = s;
        center = FollowsOwner() ? s.Owner.Position : s.Center;
        age = 0f;
        tickClock = 0f;
        armed = false;
        live = true;
        active.Add(this);
        transform.position = center;
        gameObject.SetActive(true);
    }

    private void Release()
    {
        if (!live) return;
        live = false;
        active.Remove(this);
        gameObject.SetActive(false);
        pool.Add(this);
    }

    private bool FollowsOwner()
    {
        return spec.FollowOwner && spec.Owner != null && spec.Owner.IsAlive;
    }

    private void Update()
    {
        if (!live) return;
        float dt = Time.deltaTime;
        age += dt;
        if (FollowsOwner())
        {
            center = spec.Owner.Position;
            transform.position = center;
        }

        if (!armed)
        {
            if (age < spec.Delay) return;
            armed = true;
            Arm();
            if (spec.Duration <= 0f)
            {
                Release();
                return;
            }
        }

        if (age >= spec.Delay + spec.Duration)
        {
            Release();
            return;
        }

        if (spec.Pull > 0f) PullFoes(dt);

        tickClock -= dt;
        if (tickClock > 0f) return;
        tickClock += spec.TickSeconds;
        Tick();
    }

    private Vector3 Away(BrawlFighter f)
    {
        Vector3 away = f.Position - center;
        away.y = 0f;
        return away.sqrMagnitude > 0.0001f ? away.normalized : Vector3.forward;
    }

    private BrawlHit Hit(BrawlFighter f, float knockback)
    {
        return new BrawlHit
        {
            Amount = spec.DamagePerTick, Source = spec.Owner, Point = f.Center, KnockDir = Away(f),
            Knockback = knockback, Theme = spec.Theme, FromSkill = true
        };
    }

    private void Arm()
    {
        BrawlFx.Emit(new BrawlFxEvent
        {
            Kind = BrawlFxKind.Ring, From = center, To = center, Radius = spec.Radius,
            Theme = spec.Theme, Team = spec.Team, Source = spec.Owner
        });

        bool damages = spec.HitOnArm && spec.DamagePerTick > 0f;
        BrawlQuery.FoesWithin(center, spec.Radius, spec.Team, scratch);
        for (int i = 0; i < scratch.Count; i++)
        {
            var f = scratch[i];
            if (damages) f.TakeDamage(Hit(f, spec.Knockback));
            else if (spec.Knockback > 0f) f.Motor.Knock(Away(f), spec.Knockback);
            if (spec.StunSeconds > 0f) f.ApplyStun(spec.StunSeconds);
        }
    }

    private void Tick()
    {
        bool damages = !spec.HitOnArm && spec.DamagePerTick > 0f;
        float slowSeconds = spec.SlowSeconds > 0f ? spec.SlowSeconds : spec.TickSeconds + 0.1f;
        BrawlQuery.FoesWithin(center, spec.Radius, spec.Team, scratch);
        for (int i = 0; i < scratch.Count; i++)
        {
            var f = scratch[i];
            if (damages) f.TakeDamage(Hit(f, 0f));
            if (spec.Slow > 0f) f.ApplySlow(spec.Slow, slowSeconds);
        }

        if (spec.HealPerTick <= 0f) return;
        BrawlQuery.AlliesWithin(center, spec.Radius, spec.Team, scratch);
        for (int i = 0; i < scratch.Count; i++) scratch[i].Heal(spec.HealPerTick, spec.Owner);
    }

    private void PullFoes(float dt)
    {
        BrawlQuery.FoesWithin(center, spec.Radius, spec.Team, scratch);
        for (int i = 0; i < scratch.Count; i++)
        {
            var f = scratch[i];
            if (!f.IsAlive || BrawlQuery.Planar(f.Position, center) < PullMinDistance) continue;
            f.Motor.Knock(-Away(f), spec.Pull * dt * 4f);
        }
    }
}
}
