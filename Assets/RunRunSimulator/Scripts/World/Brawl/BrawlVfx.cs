using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.AI;

namespace MoriMonchiSimulator
{

public class BrawlVfx : MonoBehaviour
{
    [Required, SerializeField] private BrawlIconParticles icons;
    [Required, SerializeField] private BrawlLineFx lines;
    [Required, SerializeField] private BrawlWardFx wards;
    [Required, SerializeField] private BrawlSwooshFx swoosh;
    [Required, SerializeField] private BrawlTrailFx trails;
    [Required, SerializeField] private BrawlImpactFx impacts;
    [Required, SerializeField] private BrawlRainFx rain;
    [Required, SerializeField] private BrawlBubbleFx bubbles;
    [Required, SerializeField] private BrawlVortexFx vortex;
    [Required, SerializeField] private Material cueMaterial;
    [Required, SerializeField] private Material additiveMaterial;

    [SerializeField] private float groundOffset = 0.04f;
    [SerializeField] private float slashSeconds = 0.2f;
    [SerializeField] private float slashAlpha = 0.85f;
    [SerializeField, Range(0f, 1f)] private float slashGroundScale = 0.5f;
    [SerializeField] private float ringSeconds = 0.35f;
    [SerializeField] private float ringStartRadius = 0.3f;
    [SerializeField] private float ringThicknessFrom = 0.14f;
    [SerializeField] private float ringThicknessTo = 0.02f;
    [SerializeField] private float pulseSeconds = 0.5f;
    [SerializeField] private float pullSeconds = 0.4f;
    [SerializeField] private float pullEndRadius = 0.3f;
    [SerializeField] private float muzzleSeconds = 0.12f;
    [SerializeField] private float muzzleRadius = 1.2f;
    [SerializeField, Min(1)] private int maxInstancesPerPrefab = 12;

    private const float AllyIconCountBoost = 1.5f;

    private struct Flash
    {
        public BrawlFxKind Kind;
        public Vector3 Center;
        public float Start;
        public float Sweep;
        public float Radius;
        public Color Color;
        public float Begin;
    }

    private class Instance
    {
        public GameObject Go;
        public ParticleSystem[] Systems;
    }

    private class PrefabPool
    {
        public readonly List<Instance> Items = new();
        public int Cursor;
    }

    private static GameObject HitFx => BrawlVfxLibrarySO.Current != null ? BrawlVfxLibrarySO.Current.HitFx : null;
    private static GameObject DustFx => BrawlVfxLibrarySO.Current != null ? BrawlVfxLibrarySO.Current.DustFx : null;
    private static GameObject KnockOutFx => BrawlVfxLibrarySO.Current != null ? BrawlVfxLibrarySO.Current.KnockOutFx : null;

    private readonly List<Flash> flashes = new();
    private readonly Dictionary<GameObject, PrefabPool> pools = new();
    private BrawlFighter lastKnockOut;
    private float lastKnockOutAt = -10f;

    private void OnEnable()
    {
        CueDrawer.Configure(cueMaterial, additiveMaterial);
        BrawlFx.Emitted += OnFx;
        BrawlFighter.OnDamaged += OnDamaged;
        BrawlFighter.OnHealed += OnHealed;
        BrawlFighter.OnKnockedOut += OnKnockedOut;
        BrawlSkillCaster.OnCastStarted += OnCastStarted;
        BrawlWing.OnMobilityUsed += OnMobilityUsed;
    }

    private void OnDisable()
    {
        BrawlFx.Emitted -= OnFx;
        BrawlFighter.OnDamaged -= OnDamaged;
        BrawlFighter.OnHealed -= OnHealed;
        BrawlFighter.OnKnockedOut -= OnKnockedOut;
        BrawlSkillCaster.OnCastStarted -= OnCastStarted;
        BrawlWing.OnMobilityUsed -= OnMobilityUsed;
        flashes.Clear();
    }

    private void OnFx(BrawlFxEvent e)
    {
        var theme = BrawlTeamLook.Wash(Safe(e.Theme), e.Team);
        float k = BrawlTeamLook.Size(e.Team);
        Vector3 up = Vector3.up;

        switch (e.Kind)
        {
            case BrawlFxKind.Slash:
            {
                Vector3 dir = Planar(e.To - e.From);
                float sweep = Mathf.Max(e.Angle, 1f) * Mathf.Deg2Rad;
                bool all = e.Angle >= 359f;
                float begin = all ? 0f : Mathf.Atan2(dir.z, dir.x) - sweep * 0.5f;
                AddFlash(BrawlFxKind.Slash, e.From, theme.Color, e.Radius, sweep, begin);
                bool around = e.Angle >= 300f;
                swoosh.Swoosh(e.From, dir, e.Radius, e.Angle, 0.75f, theme.Color, around ? 0.32f : 0.22f);
                Vector3 chest = e.From + up * 0.75f;
                if (around) icons.Ring(chest, theme, Count(8, e.Team), e.Radius * 0.6f, 4f, 0.32f * k, 0.4f);
                else icons.Spray(chest, dir, Mathf.Min(e.Angle, 120f), theme, Count(5, e.Team), 5f, 0.32f * k, 0.35f);
                break;
            }
            case BrawlFxKind.Lightning:
                if (e.Path == null || e.Path.Length < 2) break;
                lines.Lightning(e.Path, theme.Color, signature: theme.Signature);
                for (int i = 0; i < e.Path.Length; i++) icons.Burst(e.Path[i], theme, 3, 2.5f, 0.3f * k, 0.4f);
                break;
            case BrawlFxKind.Beam:
                if (e.Source == null || e.Target == null) break;
                lines.Beam(e.Source, e.Target, theme.Color, e.Duration, theme.Signature);
                icons.Burst(e.Target.Center, theme, 4, 1.5f, 0.4f * k, 0.8f, true);
                break;
            case BrawlFxKind.Whip:
                lines.Whip(e.From, e.To, theme.Color);
                icons.Burst(e.To, theme, 4, 3f, 0.35f * k, 0.45f);
                break;
            case BrawlFxKind.Burst:
                icons.Burst(e.To, theme, 6 + Mathf.RoundToInt(e.Radius * 4f), 3f + e.Radius * 2f, 0.45f * k, 0.7f);
                Spawn(HitFx, e.To, 1f);
                AddFlash(BrawlFxKind.Ring, e.To, theme.Color, Mathf.Max(e.Radius, 0.5f), 0f, 0f);
                impacts.Hit(e.To, theme.Color, (0.8f + e.Radius * 0.25f) * k);
                break;
            case BrawlFxKind.Ring:
                AddFlash(BrawlFxKind.Ring, e.To, theme.Color, e.Radius, 0f, 0f);
                icons.Ring(e.To + up * 0.3f, theme, 10, e.Radius * 0.5f, 4f, 0.4f * k, 0.5f);
                break;
            case BrawlFxKind.Pulse:
                AddFlash(BrawlFxKind.Pulse, e.To, theme.Color, e.Radius, 0f, 0f);
                icons.Burst(e.To + up * 0.3f, theme, 8, 2f, 0.4f * k, 0.8f, true);
                break;
            case BrawlFxKind.Ward:
                wards.Ward(e.Target, theme, e.Duration);
                if (e.Target != null) bubbles.Bubble(e.Target, theme.Color, e.Duration);
                break;
            case BrawlFxKind.Dash:
                for (int i = 0; i < 6; i++)
                    icons.Burst(Vector3.Lerp(e.From, e.To, i / 5f) + up * 0.4f, theme, 2, 1.5f, 0.3f * k, 0.4f);
                Spawn(DustFx, e.From, 1f);
                if (e.Source != null) trails.Follow(e.Source, theme.Color, 0.95f);
                break;
            case BrawlFxKind.Pull:
                AddFlash(BrawlFxKind.Pull, e.To, theme.Color, e.Radius, 0f, 0f);
                icons.Converge(e.To + up * 0.3f, theme, 10, e.Radius, 0.4f * k, 0.4f);
                vortex.Vortex(e.To, e.Radius, theme.Color, 0.45f);
                break;
            case BrawlFxKind.Throw:
                rain.Rain(e.To, e.Radius > 0f ? e.Radius : 2.2f, theme, e.Duration, 9);
                break;
            case BrawlFxKind.Muzzle:
            {
                Vector3 dir = Planar(e.To - e.From);
                float sweep = Mathf.Max(e.Angle, 24f) * Mathf.Deg2Rad;
                float begin = Mathf.Atan2(dir.z, dir.x) - sweep * 0.5f;
                AddFlash(BrawlFxKind.Muzzle, e.From, theme.Color, muzzleRadius, sweep, begin);
                icons.Spray(e.From, dir, Mathf.Max(e.Angle, 18f), theme, Count(4, e.Team), 6f, 0.28f * k, 0.3f);
                break;
            }
            case BrawlFxKind.Spawn:
                icons.Ring(e.To + up * 0.3f, theme, 8, 0.6f, 3f, 0.4f * k, 0.6f);
                Spawn(DustFx, e.To, 1f);
                break;
            case BrawlFxKind.KnockOut:
                KnockOutAt(e.Source, e.Source != null ? e.Source.Center : e.To + up * 0.8f);
                break;
            case BrawlFxKind.Land:
                Spawn(DustFx, e.To, 1f);
                AddFlash(BrawlFxKind.Ring, e.To, theme.Color, 1.2f, 0f, 0f);
                break;
        }
    }

    private void OnDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (hit.IsDrain) return;

        var team = hit.Source != null ? hit.Source.Team : ExpeditionTeam.None;
        var theme = BrawlTeamLook.Wash(Safe(hit.Theme), team);
        float k = BrawlTeamLook.Size(team);
        int count = Mathf.RoundToInt(Mathf.Clamp(hit.Amount / 150f, 2f, 10f));
        icons.Burst(hit.Point, theme, count, 4f, 0.35f * k, 0.45f);
        if (hit.Amount >= 1200f) Spawn(HitFx, hit.Point, 0.5f);
        impacts.Hit(hit.Point, theme.Color, Mathf.Clamp(0.55f + hit.Amount / 1800f, 0.55f, 1.6f) * k);
    }

    private void OnMobilityUsed(BrawlFighter fighter, BrawlMobilityKind kind)
    {
        if (fighter == null || kind == BrawlMobilityKind.Sprint) return;
        trails.Follow(fighter, BrawlTeamLook.Wash(Safe(fighter.WingTheme), fighter.Team).Color, 0.6f);
    }

    private void OnHealed(BrawlFighter target, float amount, BrawlFighter source)
    {
        if (target == null) return;

        var theme = new BrawlTheme { Icon = null, Color = new Color(0.5f, 1f, 0.6f, 1f) };
        int count = Mathf.Min(8, 3 + Mathf.FloorToInt(amount / 200f));
        icons.Burst(target.Center, theme, count, 2f, 0.35f, 0.8f, true);
    }

    private void OnKnockedOut(BrawlFighter victim, BrawlFighter killer)
    {
        if (victim == null) return;
        KnockOutAt(victim, victim.Center);
    }

    private void OnCastStarted(BrawlFighter caster, BrawlSkillSO skill, Vector3 aim)
    {
        if (caster == null || skill == null || caster.Caster == null || skill.Windup <= 0.01f) return;
        var theme = BrawlTeamLook.Wash(Safe(caster.Caster.Theme(caster.Caster.CastSlot)), caster.Team);
        icons.Converge(caster.Center, theme, 8, 1.6f, 0.4f * BrawlTeamLook.Size(caster.Team), skill.Windup);
    }

    private void KnockOutAt(BrawlFighter victim, Vector3 pos)
    {
        if (victim != null && victim == lastKnockOut && Time.time - lastKnockOutAt < 0.5f) return;
        lastKnockOut = victim;
        lastKnockOutAt = Time.time;

        Spawn(KnockOutFx, pos, 1f);
        var team = victim != null ? victim.Team : ExpeditionTeam.None;
        float k = BrawlTeamLook.Size(team);
        impacts.Hit(pos, Color.white, 2.2f * k);
        if (victim == null) return;
        icons.Burst(pos, BrawlTeamLook.Wash(Safe(victim.WingTheme), team), 8, 5f, 0.5f * k, 0.9f);
        icons.Burst(pos, BrawlTeamLook.Wash(Safe(victim.HornTheme), team), 8, 5f, 0.5f * k, 0.9f);
        icons.Burst(pos, BrawlTeamLook.Wash(Safe(victim.BackTheme), team), 8, 5f, 0.5f * k, 0.9f);
    }

    private void AddFlash(BrawlFxKind kind, Vector3 center, Color color, float radius, float sweep, float begin)
    {
        center.y = GroundY(center) + groundOffset;
        flashes.Add(new Flash
        {
            Kind = kind,
            Center = center,
            Start = Time.time,
            Sweep = sweep,
            Radius = radius,
            Color = color,
            Begin = begin
        });
    }

    private void LateUpdate()
    {
        for (int i = flashes.Count - 1; i >= 0; i--)
        {
            var f = flashes[i];
            float t = (Time.time - f.Start) / SecondsOf(f.Kind);
            if (t >= 1f)
            {
                flashes.RemoveAt(i);
                continue;
            }
            DrawFlash(f, t);
        }
    }

    private float SecondsOf(BrawlFxKind kind)
    {
        switch (kind)
        {
            case BrawlFxKind.Slash: return Mathf.Max(0.01f, slashSeconds);
            case BrawlFxKind.Ring: return Mathf.Max(0.01f, ringSeconds);
            case BrawlFxKind.Pulse: return Mathf.Max(0.01f, pulseSeconds);
            case BrawlFxKind.Pull: return Mathf.Max(0.01f, pullSeconds);
            default: return Mathf.Max(0.01f, muzzleSeconds);
        }
    }

    private void DrawFlash(Flash f, float t)
    {
        Color c = f.Color;
        switch (f.Kind)
        {
            case BrawlFxKind.Slash:
                c.a = slashAlpha * slashGroundScale * (1f - t);
                CueDrawer.Sector(f.Center, f.Radius, f.Begin, f.Sweep, c, 0.15f, 1f, true);
                break;
            case BrawlFxKind.Ring:
            {
                float ease = 1f - (1f - t) * (1f - t);
                c.a = 1f - t;
                CueDrawer.Ring(f.Center, Mathf.Lerp(ringStartRadius, f.Radius, ease), Mathf.Lerp(ringThicknessFrom, ringThicknessTo, t), c, true);
                break;
            }
            case BrawlFxKind.Pulse:
            {
                float ease = 1f - (1f - t) * (1f - t);
                c.a = 1f - t;
                CueDrawer.Disc(f.Center, f.Radius * ease, c, 0.5f, 0f, true);
                CueDrawer.Ring(f.Center, f.Radius * ease, 0.08f, c, true);
                break;
            }
            case BrawlFxKind.Pull:
            {
                c.a = 1f - t * t;
                float radius = Mathf.Lerp(f.Radius, pullEndRadius, t);
                CueDrawer.DashedRing(f.Center, radius, 0.08f, 20, 0.55f, Time.time * 2f, c, true);
                break;
            }
            case BrawlFxKind.Muzzle:
                c.a = 1f - t;
                CueDrawer.Sector(f.Center, f.Radius, f.Begin, f.Sweep, c, 0.3f, 1f, true);
                break;
        }
    }

    private void Spawn(GameObject prefab, Vector3 pos, float scale)
    {
        if (prefab == null) return;

        if (!pools.TryGetValue(prefab, out var pool))
        {
            pool = new PrefabPool();
            pools[prefab] = pool;
        }

        Instance instance = null;
        for (int i = 0; i < pool.Items.Count; i++)
        {
            var candidate = pool.Items[i];
            if (candidate.Go != null && !candidate.Go.activeSelf)
            {
                instance = candidate;
                break;
            }
        }

        if (instance == null)
        {
            if (pool.Items.Count < maxInstancesPerPrefab)
            {
                var go = Instantiate(prefab, transform);
                instance = new Instance { Go = go, Systems = go.GetComponentsInChildren<ParticleSystem>(true) };
                pool.Items.Add(instance);
            }
            else
            {
                instance = pool.Items[pool.Cursor % pool.Items.Count];
                pool.Cursor++;
                if (instance.Go == null) return;
            }
        }

        var tr = instance.Go.transform;
        tr.position = pos;
        tr.localScale = prefab.transform.localScale * scale;
        instance.Go.SetActive(true);
        for (int i = 0; i < instance.Systems.Length; i++)
        {
            var ps = instance.Systems[i];
            if (ps == null) continue;
            ps.Clear(false);
            ps.Play(false);
        }
    }

    private static int Count(int baseCount, ExpeditionTeam team)
    {
        return BrawlTeamLook.IsAlly(team) ? Mathf.RoundToInt(baseCount * AllyIconCountBoost) : baseCount;
    }

    private static BrawlTheme Safe(BrawlTheme theme)
    {
        if (theme.Color.a < 0.01f) theme.Color = Color.white;
        return theme;
    }

    private static Vector3 Planar(Vector3 v)
    {
        v.y = 0f;
        return v.sqrMagnitude < 0.0001f ? Vector3.forward : v.normalized;
    }

    private static float GroundY(Vector3 p)
    {
        return NavMesh.SamplePosition(p, out var hit, 3f, NavMesh.AllAreas) ? hit.position.y : p.y;
    }
}
}
