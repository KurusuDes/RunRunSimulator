using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlIconParticles : MonoBehaviour
{
    private static readonly int BaseMapID = Shader.PropertyToID("_BaseMap");
    private static readonly int MainTexID = Shader.PropertyToID("_MainTex");

    private readonly Dictionary<(Texture, bool), ParticleSystem> systems = new();

    public void Burst(Vector3 pos, BrawlTheme theme, int count, float speed, float size, float life, bool rise = false)
    {
        var ps = Get(theme, rise);
        if (ps == null) return;

        var emit = NewEmit(theme, size, life);
        for (int i = 0; i < count; i++)
        {
            Vector3 dir = Random.onUnitSphere;
            if (rise)
            {
                dir.x *= 0.5f;
                dir.z *= 0.5f;
                dir.y = Random.Range(0.6f, 1f);
            }
            else
            {
                dir.y = Mathf.Abs(dir.y);
            }

            emit.position = pos;
            emit.velocity = dir * speed * Random.Range(0.6f, 1.2f);
            emit.rotation = Random.Range(0f, 360f);
            ps.Emit(emit, 1);
        }
        Kick(ps);
    }

    public void Spray(Vector3 origin, Vector3 direction, float angleDeg, BrawlTheme theme, int count, float speed, float size, float life)
    {
        var ps = Get(theme, false);
        if (ps == null || count <= 0) return;

        direction.y = 0f;
        if (direction.sqrMagnitude < 0.0001f) direction = Vector3.forward;
        direction.Normalize();

        float half = angleDeg * 0.5f;
        var emit = NewEmit(theme, size, life);
        for (int i = 0; i < count; i++)
        {
            Vector3 dir = Quaternion.AngleAxis(Random.Range(-half, half), Vector3.up) * direction;
            dir.y = Random.Range(0f, 0.25f);

            emit.position = origin;
            emit.velocity = dir.normalized * speed * Random.Range(0.7f, 1.15f);
            emit.rotation = Random.Range(0f, 360f);
            ps.Emit(emit, 1);
        }
        Kick(ps);
    }

    public void Ring(Vector3 center, BrawlTheme theme, int count, float radius, float speed, float size, float life)
    {
        var ps = Get(theme, true);
        if (ps == null || count <= 0) return;

        var emit = NewEmit(theme, size, life);
        float offset = Random.value * Mathf.PI * 2f;
        for (int i = 0; i < count; i++)
        {
            float a = offset + i * Mathf.PI * 2f / count;
            Vector3 dir = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
            emit.position = center + dir * radius;
            emit.velocity = dir * speed + Vector3.up * 0.5f;
            emit.rotation = Random.Range(0f, 360f);
            ps.Emit(emit, 1);
        }
        Kick(ps);
    }

    public void Converge(Vector3 center, BrawlTheme theme, int count, float radius, float size, float life)
    {
        var ps = Get(theme, true);
        if (ps == null || count <= 0 || life <= 0.01f) return;

        var emit = NewEmit(theme, size, life);
        float offset = Random.value * Mathf.PI * 2f;
        float inward = radius / life;
        for (int i = 0; i < count; i++)
        {
            float a = offset + i * Mathf.PI * 2f / count;
            Vector3 dir = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
            emit.position = center + dir * radius;
            emit.velocity = -dir * inward;
            emit.rotation = Random.Range(0f, 360f);
            ps.Emit(emit, 1);
        }
        Kick(ps);
    }

    private static ParticleSystem.EmitParams NewEmit(BrawlTheme theme, float size, float life)
    {
        return new ParticleSystem.EmitParams
        {
            startColor = theme.Color,
            startSize = size,
            startLifetime = life
        };
    }

    private static void Kick(ParticleSystem ps)
    {
        if (!ps.isPlaying) ps.Play();
    }

    private ParticleSystem Get(BrawlTheme theme, bool rise)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.ParticleMaterial == null) return null;

        Sprite icon = theme.Icon != null ? theme.Icon : lib.SparkSprite;
        if (icon == null) return null;

        Texture tex = icon.texture;
        var key = (tex, rise);
        if (systems.TryGetValue(key, out var existing) && existing != null) return existing;

        var created = Create(lib, tex, rise);
        systems[key] = created;
        return created;
    }

    private ParticleSystem Create(BrawlVfxLibrarySO lib, Texture tex, bool rise)
    {
        var go = new GameObject("Icons_" + tex.name + (rise ? "_Rise" : ""));
        go.transform.SetParent(transform, false);

        var ps = go.AddComponent<ParticleSystem>();
        ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);

        var main = ps.main;
        main.loop = false;
        main.playOnAwake = false;
        main.simulationSpace = ParticleSystemSimulationSpace.World;
        main.maxParticles = 300;
        main.gravityModifier = rise ? -0.15f : 0.9f;

        var emission = ps.emission;
        emission.enabled = false;

        var shape = ps.shape;
        shape.enabled = false;

        var color = ps.colorOverLifetime;
        color.enabled = true;
        var gradient = new Gradient();
        gradient.SetKeys(
            new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
            new[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(1f, 0.6f), new GradientAlphaKey(0f, 1f) });
        color.color = new ParticleSystem.MinMaxGradient(gradient);

        var scale = ps.sizeOverLifetime;
        scale.enabled = true;
        scale.size = new ParticleSystem.MinMaxCurve(1f, new AnimationCurve(new Keyframe(0f, 1f), new Keyframe(1f, 0.7f)));

        var spin = ps.rotationOverLifetime;
        spin.enabled = true;
        spin.separateAxes = false;
        spin.z = new ParticleSystem.MinMaxCurve(-180f * Mathf.Deg2Rad, 180f * Mathf.Deg2Rad);

        var renderer = go.GetComponent<ParticleSystemRenderer>();
        renderer.renderMode = ParticleSystemRenderMode.Billboard;
        var mat = new Material(lib.ParticleMaterial);
        if (mat.HasProperty(BaseMapID)) mat.SetTexture(BaseMapID, tex);
        if (mat.HasProperty(MainTexID)) mat.SetTexture(MainTexID, tex);
        renderer.material = mat;

        return ps;
    }
}
}
