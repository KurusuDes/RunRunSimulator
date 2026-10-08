using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlTelegraphs : MonoBehaviour
{
    [Required, SerializeField] private Material cueMaterial;
    [Required, SerializeField] private Material additiveMaterial;
    [Required, SerializeField] private BrawlTuningSO tuning;

    [SerializeField] private float baseRadius = 0.85f;
    [SerializeField] private float baseInnerAlpha = 0.35f;
    [SerializeField] private float baseRingThickness = 0.05f;
    [SerializeField] private float baseRingAlpha = 0.75f;
    [SerializeField] private float trackAlpha = 0.12f;
    [SerializeField] private float fillAlpha = 0.38f;
    [SerializeField] private float edgeAlpha = 0.9f;
    [SerializeField] private float edgeThickness = 0.06f;
    [SerializeField] private float laserThickness = 0.04f;
    [SerializeField] private float zoneFillAlpha = 0.16f;
    [SerializeField] private float zoneEdgeAlpha = 0.75f;
    [SerializeField] private int zoneDashCount = 28;
    [SerializeField] private float zoneSpinSpeed = 40f;
    [SerializeField] private float groundOffset = 0.03f;
    [SerializeField] private float targetLineThickness = 0.035f;
    [SerializeField] private float targetLineAlpha = 0.55f;
    [SerializeField] private float targetRingThickness = 0.03f;

    private const float TargetDashLength = 0.35f;
    private const float TargetDashGap = 0.25f;
    private const float TargetDashSpeed = 1.5f;
    private const float TargetRingRadius = 0.95f;

    private static readonly Color HealLineColor = new Color(0.45f, 1f, 0.55f);

    private void OnEnable()
    {
        CueDrawer.Configure(cueMaterial, additiveMaterial);
    }

    private void LateUpdate()
    {
        var all = BrawlFighter.All;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (f == null || !f.IsAlive) continue;

            Vector3 pos = f.Position + Vector3.up * groundOffset;
            Color team = tuning.TeamColor(f.Team);

            DrawBase(pos, team);
            if (f.Wing != null && f.Wing.IsWindingUp)
            {
                if (f.Wing.AimHealing) DrawTargetLine(pos, OnGround(f.Wing.AimPoint, pos.y), HealLineColor);
                else DrawWing(f, pos, team);
            }
            if (f.Caster != null && f.Caster.IsCasting)
            {
                DrawCast(f, pos, team);
                var castTarget = f.Caster.CastTarget;
                if (castTarget != null && castTarget != f && castTarget.IsAlive)
                {
                    DrawTargetLine(pos, OnGround(castTarget.Position, pos.y), team);
                }
            }
        }

        var zones = BrawlZone.Active;
        for (int i = 0; i < zones.Count; i++)
        {
            if (zones[i] != null) DrawZone(zones[i]);
        }
    }

    private void DrawBase(Vector3 pos, Color team)
    {
        CueDrawer.Disc(pos, baseRadius, team, baseInnerAlpha, 0f);
        Color ring = team;
        ring.a = baseRingAlpha;
        CueDrawer.Ring(pos, baseRadius, baseRingThickness, ring);
    }

    private void DrawTargetLine(Vector3 from, Vector3 to, Color color)
    {
        color.a = targetLineAlpha;
        CueDrawer.DashedSegment(from, to, targetLineThickness, TargetDashLength, TargetDashGap, Time.time * TargetDashSpeed, color, color);
        CueDrawer.Ring(to, TargetRingRadius, targetRingThickness, color);
    }

    private void DrawWing(BrawlFighter f, Vector3 pos, Color team)
    {
        var kit = f.WingKit;
        if (kit == null) return;

        float t = f.Wing.Windup01;
        Color edge = BrawlTeamLook.Wash(f.WingTheme.Color, f.Team);
        Vector3 dir = Flat(f.Wing.AimDir, f.transform.forward);

        switch (kit.Attack)
        {
            case BrawlAttackKind.Melee:
                DrawCone(pos, dir, kit.Range, kit.Angle, t, team, edge);
                break;
            case BrawlAttackKind.Whip:
                DrawCapsule(pos, pos + dir * kit.Range, kit.HitRadius, t, team, edge);
                break;
            case BrawlAttackKind.Sniper:
                DrawLaser(pos, OnGround(f.Wing.AimPoint, pos.y), t, team, edge);
                break;
            case BrawlAttackKind.Shotgun:
                DrawCone(pos, dir, kit.Range, Mathf.Max(kit.Spread, 8f), 0f, team, edge);
                break;
        }
    }

    private void DrawCast(BrawlFighter f, Vector3 pos, Color team)
    {
        var caster = f.Caster;
        var s = caster.CastSkill;
        if (s == null) return;

        float t = caster.Cast01;
        Color edge = BrawlTeamLook.Wash(caster.Theme(caster.CastSlot).Color, f.Team);
        Vector3 dir = Flat(caster.AimDir, f.transform.forward);
        Vector3 aim = OnGround(caster.AimPoint, pos.y);
        var target = caster.CastTarget;
        float spin = Time.time * zoneSpinSpeed * Mathf.Deg2Rad;

        switch (s.Family)
        {
            case BrawlSkillFamily.Dash:
            case BrawlSkillFamily.Shot:
                DrawCapsule(pos, pos + dir * s.Range, s.Radius, t, team, edge);
                break;
            case BrawlSkillFamily.Chain:
            {
                Vector3 c = target != null ? OnGround(target.Position, pos.y) : aim;
                DrawArea(c, 1.1f, t, team, edge, false, 0f);
                Color link = edge;
                link.a = edgeAlpha;
                CueDrawer.DashedSegment(pos, c, edgeThickness, 0.3f, 0.2f, Time.time * 3f, link, link, true);
                break;
            }
            case BrawlSkillFamily.Cone:
                DrawCone(pos, dir, s.Range, s.Angle, t, team, edge);
                break;
            case BrawlSkillFamily.Nova:
                DrawArea(pos, s.Range * 0.5f, t, team, edge, true, spin);
                break;
            case BrawlSkillFamily.Homing:
                DrawArea(pos, 1.6f, t, team, edge, true, spin);
                break;
            case BrawlSkillFamily.Pull:
                DrawPull(pos, s.Radius, t, team, edge, spin);
                break;
            case BrawlSkillFamily.Zone:
            {
                Vector3 c = s.Target == BrawlSkillTarget.Self ? pos
                          : s.Target == BrawlSkillTarget.LowestAlly || s.Target == BrawlSkillTarget.AlliesAround
                              ? (target != null ? OnGround(target.Position, pos.y) : pos)
                              : aim;
                DrawArea(c, s.Radius, t, team, edge, false, 0f);
                break;
            }
            case BrawlSkillFamily.Ward:
            case BrawlSkillFamily.Mend:
            {
                Vector3 c = target != null ? OnGround(target.Position, pos.y) : pos;
                DrawArea(c, 1.2f, t, edge, edge, false, 0f);
                break;
            }
        }
    }

    private void DrawZone(BrawlZone zone)
    {
        var spec = zone.Spec;
        Color theme = BrawlTeamLook.Wash(spec.Theme.Color, spec.Team);
        Vector3 c = zone.Center + Vector3.up * groundOffset;
        float r = spec.Radius;

        if (!zone.Armed)
        {
            float d = zone.Delay01;
            CueDrawer.Disc(c, r, theme, zoneFillAlpha * d, zoneFillAlpha * d);
            Color edge = theme;
            edge.a = zoneEdgeAlpha;
            CueDrawer.Ring(c, r, edgeThickness, edge, true);
            CueDrawer.Ring(c, Mathf.Max(0.05f, r * (1f - d)), edgeThickness * 0.8f, edge, true);
            return;
        }

        float fill = zoneFillAlpha * (1f - zone.Life01 * 0.6f);
        CueDrawer.Disc(c, r, theme, fill, fill);
        Color dashed = theme;
        dashed.a = zoneEdgeAlpha;
        CueDrawer.DashedRing(c, r, edgeThickness, zoneDashCount, 0.55f, Time.time * zoneSpinSpeed * Mathf.Deg2Rad, dashed, true);
    }

    private void DrawCone(Vector3 pos, Vector3 dir, float range, float angleDeg, float t, Color team, Color edge)
    {
        if (angleDeg >= 359f)
        {
            DrawArea(pos, range, t, team, edge, false, 0f);
            return;
        }

        float sweep = Mathf.Max(angleDeg, 1f) * Mathf.Deg2Rad;
        float start = Mathf.Atan2(dir.z, dir.x) - sweep * 0.5f;

        CueDrawer.Sector(pos, range, start, sweep, team, trackAlpha, trackAlpha);
        if (t > 0.01f) CueDrawer.Sector(pos, range * t, start, sweep, team, fillAlpha, fillAlpha);

        edge.a = edgeAlpha;
        CueDrawer.Arc(pos, range, edgeThickness, start, sweep, edge, edge, true);
        Vector3 a = pos + new Vector3(Mathf.Cos(start), 0f, Mathf.Sin(start)) * range;
        Vector3 b = pos + new Vector3(Mathf.Cos(start + sweep), 0f, Mathf.Sin(start + sweep)) * range;
        CueDrawer.Segment(pos, a, edgeThickness, edge, true);
        CueDrawer.Segment(pos, b, edgeThickness, edge, true);
    }

    private void DrawCapsule(Vector3 a, Vector3 b, float radius, float t, Color team, Color edge)
    {
        CueDrawer.Capsule(a, b, radius, team, trackAlpha, trackAlpha);
        if (t > 0.01f) CueDrawer.Capsule(a, Vector3.Lerp(a, b, t), radius, team, fillAlpha, fillAlpha);
        edge.a = edgeAlpha;
        CueDrawer.CapsuleOutline(a, b, radius, edgeThickness, edge, edge, true);
    }

    private void DrawLaser(Vector3 a, Vector3 b, float t, Color team, Color edge)
    {
        float wide = laserThickness * 3f;
        Color track = team;
        track.a = trackAlpha;
        CueDrawer.Segment(a, b, wide, track);
        if (t > 0.01f)
        {
            Color fill = team;
            fill.a = fillAlpha;
            CueDrawer.Segment(a, Vector3.Lerp(a, b, t), wide, fill);
        }
        edge.a = edgeAlpha * (0.6f + 0.4f * Mathf.Sin(Time.time * 30f));
        CueDrawer.Segment(a, b, laserThickness, edge, true);
    }

    private void DrawArea(Vector3 center, float radius, float t, Color team, Color edge, bool dashed, float spin)
    {
        CueDrawer.Disc(center, radius, team, trackAlpha, trackAlpha);
        if (t > 0.01f) CueDrawer.Disc(center, radius * t, team, fillAlpha, fillAlpha);
        edge.a = edgeAlpha;
        if (dashed) CueDrawer.DashedRing(center, radius, edgeThickness, zoneDashCount, 0.55f, spin, edge, true);
        else CueDrawer.Ring(center, radius, edgeThickness, edge, true);
    }

    private void DrawPull(Vector3 center, float radius, float t, Color team, Color edge, float spin)
    {
        CueDrawer.Disc(center, radius, team, trackAlpha, trackAlpha);
        if (t > 0.01f) CueDrawer.Disc(center, radius * t, team, fillAlpha, fillAlpha);
        edge.a = edgeAlpha;
        float closing = Mathf.Lerp(radius, radius * 0.3f, t);
        CueDrawer.DashedRing(center, closing, edgeThickness, zoneDashCount, 0.55f, -spin, edge, true);
    }

    private static Vector3 Flat(Vector3 dir, Vector3 fallback)
    {
        dir.y = 0f;
        if (dir.sqrMagnitude < 0.0001f)
        {
            dir = fallback;
            dir.y = 0f;
            if (dir.sqrMagnitude < 0.0001f) dir = Vector3.forward;
        }
        return dir.normalized;
    }

    private static Vector3 OnGround(Vector3 p, float y)
    {
        return new Vector3(p.x, y, p.z);
    }
}
}
