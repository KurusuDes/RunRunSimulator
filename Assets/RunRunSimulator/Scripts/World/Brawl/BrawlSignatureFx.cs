using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlSignatureFx : MonoBehaviour
{
    private const float RainbowSaturation = 0.75f;
    private const float BeamInterval = 0.05f;
    private const int BeamSparks = 2;
    private const float BeamHueSpeed = 1.5f;
    private const float BeamHueStep = 0.13f;
    private const float BeamSparkSpeed = 1.2f;
    private const float BeamSparkSize = 0.28f;
    private const float BeamSparkLife = 0.6f;
    private const int PulseRings = 3;
    private const float PulseRingDelay = 0.1f;
    private const float PulseRingSeconds = 0.6f;
    private const float PulseRingFrom = 0.3f;
    private const int PulseSparks = 12;
    private const float PulseSparkSpeed = 2f;
    private const float PulseSparkSize = 0.3f;
    private const float PulseSparkLife = 0.8f;
    private const float PulseSparkLift = 0.3f;
    private const float PulseSparkRadius = 0.5f;
    private const float RingThickness = 0.12f;
    private const float RingLift = 0.06f;
    private const float StormHitSeconds = 0.4f;

    private class BeamRun
    {
        public BrawlFighter Source;
        public BrawlFighter Target;
        public BrawlTheme Theme;
        public ExpeditionTeam Team;
        public float Start;
        public float Seconds;
        public float Accum;
    }

    private struct GroundRing
    {
        public Vector3 Center;
        public Color Color;
        public float Start;
        public float Seconds;
        public float From;
        public float To;
    }

    [Required, SerializeField] private BrawlIconParticles icons;

    private readonly List<BeamRun> beams = new();
    private readonly List<GroundRing> rings = new();

    private BrawlCometSparks comet;
    private BrawlStormCrackle storm;
    private BrawlCloudPuffs clouds;
    private BrawlLureLight lure;
    private BrawlPlateOrbit plates;

    private void Awake()
    {
        var pool = new BrawlSignatureSprites(transform);
        comet = new BrawlCometSparks(icons, AddRing);
        storm = new BrawlStormCrackle(transform);
        clouds = new BrawlCloudPuffs(pool);
        lure = new BrawlLureLight(pool);
        plates = new BrawlPlateOrbit(pool);
    }

    private void OnEnable()
    {
        BrawlFx.Emitted += OnFx;
        BrawlSkillCaster.OnCastStarted += OnCastStarted;
        BrawlSkillCaster.OnCastFired += OnCastFired;
        BrawlFighter.OnDamaged += OnDamaged;
    }

    private void OnDisable()
    {
        BrawlFx.Emitted -= OnFx;
        BrawlSkillCaster.OnCastStarted -= OnCastStarted;
        BrawlSkillCaster.OnCastFired -= OnCastFired;
        BrawlFighter.OnDamaged -= OnDamaged;

        beams.Clear();
        rings.Clear();
        comet.Clear();
        storm.Clear();
        clouds.Clear();
        lure.Clear();
        plates.Clear();
    }

    private void OnFx(BrawlFxEvent e)
    {
        if (BrawlVfxLibrarySO.Current == null) return;

        switch (e.Theme.Signature)
        {
            case BrawlSignature.Rainbow:
                if (e.Kind == BrawlFxKind.Beam) RainbowBeam(e);
                else if (e.Kind == BrawlFxKind.Pulse) RainbowPulse(e);
                break;
            case BrawlSignature.Comet:
                if (e.Kind == BrawlFxKind.Burst) comet.Burst(e);
                break;
            case BrawlSignature.Cloud:
                if (e.Kind == BrawlFxKind.Ring) clouds.Armed(e);
                break;
            case BrawlSignature.Plates:
                if (e.Kind == BrawlFxKind.Ward) plates.Ward(e);
                break;
        }
    }

    private void OnDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (hit.Theme.Signature != BrawlSignature.Storm || victim == null) return;

        var team = hit.Source != null ? hit.Source.Team : ExpeditionTeam.None;
        storm.Crackle(victim, BrawlTeamLook.Wash(hit.Theme.Color, team), StormHitSeconds);
    }

    private void OnCastStarted(BrawlFighter caster, BrawlSkillSO skill, Vector3 aim)
    {
        if (caster == null || skill == null || caster.Caster == null) return;
        if (skill.Signature != BrawlSignature.Storm && skill.Signature != BrawlSignature.Lure) return;

        var theme = caster.Caster.Theme(caster.Caster.CastSlot);
        if (skill.Signature == BrawlSignature.Storm) storm.Crackle(caster, BrawlTeamLook.Wash(theme.Color, caster.Team), skill.Windup);
        else lure.Started(caster, skill, theme);
    }

    private void OnCastFired(BrawlFighter caster, BrawlSkillSO skill, Vector3 aim)
    {
        if (caster == null || skill == null) return;
        lure.Fired(caster, skill);
    }

    private void RainbowBeam(BrawlFxEvent e)
    {
        if (e.Source == null || e.Target == null) return;

        beams.Add(new BeamRun
        {
            Source = e.Source,
            Target = e.Target,
            Theme = e.Theme,
            Team = e.Team,
            Start = Time.time,
            Seconds = Mathf.Max(0.05f, e.Duration)
        });
    }

    private void RainbowPulse(BrawlFxEvent e)
    {
        float radius = Mathf.Max(e.Radius, PulseRingFrom + 0.1f);
        float baseHue = Random.value;
        for (int k = 0; k < PulseRings; k++)
        {
            Color color = BrawlTeamLook.Wash(Hue(baseHue + k / (float)PulseRings), e.Team);
            AddRing(e.To, color, k * PulseRingDelay, PulseRingSeconds, PulseRingFrom, radius);
        }

        for (int i = 0; i < PulseSparks; i++)
        {
            float a = i * Mathf.PI * 2f / PulseSparks;
            Vector3 point = e.To + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * (radius * PulseSparkRadius) + Vector3.up * PulseSparkLift;
            var theme = Tinted(e.Theme, Hue(i / (float)PulseSparks), e.Team);
            icons.Burst(point, theme, 1, PulseSparkSpeed, PulseSparkSize, PulseSparkLife, true);
        }
    }

    private void AddRing(Vector3 center, Color color, float delay, float seconds, float from, float to)
    {
        center.y += RingLift;
        rings.Add(new GroundRing
        {
            Center = center,
            Color = color,
            Start = Time.time + delay,
            Seconds = seconds,
            From = from,
            To = to
        });
    }

    private void LateUpdate()
    {
        float now = Time.time;
        StepBeams(Time.deltaTime, now);
        StepRings(now);
        comet.Step(Time.deltaTime);
        storm.Step(now);

        if (BrawlVfxLibrarySO.Current == null) return;

        var cam = Camera.main;
        Quaternion face = cam != null ? cam.transform.rotation : Quaternion.identity;
        clouds.Step(now, face);
        lure.Step(now, face);
        plates.Step(now, face);
    }

    private void StepBeams(float dt, float now)
    {
        for (int i = beams.Count - 1; i >= 0; i--)
        {
            var run = beams[i];
            float age = now - run.Start;
            bool over = age >= run.Seconds || run.Source == null || run.Target == null || !run.Source.IsAlive || !run.Target.IsAlive;
            if (over)
            {
                beams.RemoveAt(i);
                continue;
            }

            run.Accum += dt;
            if (run.Accum < BeamInterval) continue;
            run.Accum -= BeamInterval;

            Vector3 a = run.Source.Center;
            Vector3 b = run.Target.Center;
            for (int k = 0; k < BeamSparks; k++)
            {
                Vector3 point = Vector3.Lerp(a, b, Random.value);
                var theme = Tinted(run.Theme, Hue(age * BeamHueSpeed + k * BeamHueStep), run.Team);
                icons.Burst(point, theme, 1, BeamSparkSpeed, BeamSparkSize, BeamSparkLife, true);
            }
        }
    }

    private void StepRings(float now)
    {
        for (int i = rings.Count - 1; i >= 0; i--)
        {
            var ring = rings[i];
            float t = (now - ring.Start) / ring.Seconds;
            if (t >= 1f)
            {
                rings.RemoveAt(i);
                continue;
            }
            if (t < 0f) continue;

            float eased = 1f - (1f - t) * (1f - t);
            Color color = ring.Color;
            color.a *= 1f - t;
            CueDrawer.Ring(ring.Center, Mathf.Lerp(ring.From, ring.To, eased), RingThickness, color, true);
        }
    }

    private static Color Hue(float hue)
    {
        return Color.HSVToRGB(Mathf.Repeat(hue, 1f), RainbowSaturation, 1f);
    }

    private static BrawlTheme Tinted(BrawlTheme theme, Color color, ExpeditionTeam team)
    {
        theme.Color = BrawlTeamLook.Wash(color, team);
        return theme;
    }
}
}
