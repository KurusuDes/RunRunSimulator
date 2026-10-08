using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlLureLight
{
    private const float Lift = 1.1f;
    private const float Forward = 0.35f;
    private const float MinSize = 0.6f;
    private const float MaxSize = 1f;
    private const float PulseHz = 6f;
    private const float Alpha = 0.9f;
    private const float AppearSeconds = 0.12f;
    private const float FlashSize = 2.5f;
    private const float FlashSeconds = 0.25f;
    private const float LightRange = 5f;
    private const float WindupIntensity = 3f;
    private const float FlashIntensity = 6f;
    private const int SortingOrder = 12;

    private class Run
    {
        public BrawlFighter Caster;
        public BrawlSkillSO Skill;
        public SpriteRenderer Orb;
        public Light Light;
        public Color Color;
        public Vector3 Anchor;
        public float Start;
        public float Windup;
        public float FlashStart = -1f;
    }

    private readonly BrawlSignatureSprites pool;
    private readonly List<Run> runs = new();

    public BrawlLureLight(BrawlSignatureSprites pool)
    {
        this.pool = pool;
    }

    public void Clear()
    {
        for (int i = 0; i < runs.Count; i++) Release(runs[i]);
        runs.Clear();
    }

    public void Started(BrawlFighter caster, BrawlSkillSO skill, BrawlTheme theme)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.GlowSprite == null || lib.ParticleAdditiveMaterial == null) return;

        End(caster);
        runs.Add(new Run
        {
            Caster = caster,
            Skill = skill,
            Orb = pool.AcquireSprite(lib.GlowSprite, lib.ParticleAdditiveMaterial, SortingOrder),
            Light = pool.AcquireLight(LightRange),
            Color = BrawlTeamLook.Wash(theme.Color, caster.Team),
            Anchor = AnchorOf(caster),
            Start = Time.time,
            Windup = skill.Windup
        });
    }

    public void Fired(BrawlFighter caster, BrawlSkillSO skill)
    {
        for (int i = 0; i < runs.Count; i++)
        {
            var run = runs[i];
            if (run.Caster != caster || run.Skill != skill || run.FlashStart >= 0f) continue;
            run.FlashStart = Time.time;
            return;
        }
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

    private static Vector3 AnchorOf(BrawlFighter caster)
    {
        return caster.Center + Vector3.up * Lift + caster.transform.forward * Forward;
    }

    private bool StepRun(Run run, float now, Quaternion face)
    {
        var caster = run.Caster;
        bool flashing = run.FlashStart >= 0f;
        if (!flashing && (caster == null || !caster.IsAlive || caster.Caster.CastSkill != run.Skill)) return false;
        if (caster != null) run.Anchor = AnchorOf(caster);

        float size;
        float alpha;
        float intensity;
        if (flashing)
        {
            float k = (now - run.FlashStart) / FlashSeconds;
            if (k >= 1f) return false;
            size = FlashSize;
            alpha = Alpha * (1f - k);
            intensity = Mathf.Lerp(FlashIntensity, 0f, k);
        }
        else
        {
            float age = now - run.Start;
            float pulse = 0.5f + 0.5f * Mathf.Sin(age * PulseHz * Mathf.PI * 2f);
            size = Mathf.Lerp(MinSize, MaxSize, pulse) * Mathf.Clamp01(age / AppearSeconds);
            alpha = Alpha;
            intensity = Mathf.Lerp(0f, WindupIntensity, run.Windup > 0.01f ? Mathf.Clamp01(age / run.Windup) : 1f);
        }

        var orb = run.Orb.transform;
        orb.position = run.Anchor;
        orb.rotation = face;
        orb.localScale = Vector3.one * size;
        Color color = run.Color;
        color.a = alpha;
        run.Orb.color = color;

        run.Light.transform.position = run.Anchor;
        run.Light.color = run.Color;
        run.Light.intensity = intensity;
        return true;
    }

    private void End(BrawlFighter caster)
    {
        for (int i = runs.Count - 1; i >= 0; i--)
        {
            if (runs[i].Caster != caster) continue;
            Release(runs[i]);
            runs.RemoveAt(i);
        }
    }

    private void Release(Run run)
    {
        pool.ReleaseSprite(run.Orb);
        pool.ReleaseLight(run.Light);
    }
}
}
