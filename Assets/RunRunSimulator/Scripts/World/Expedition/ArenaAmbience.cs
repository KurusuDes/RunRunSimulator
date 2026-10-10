using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class ArenaAmbience : MonoBehaviour
{
    [Required, SerializeField] private ArenaPaletteApplier palette;
    [SerializeField] private ParticleSystem fireflies;
    [SerializeField] private ParticleSystem fairyDust;
    [SerializeField] private List<ArenaShapeShafts> shafts = new List<ArenaShapeShafts>();
    [SerializeField] private Transform focus;
    [Min(0f), SerializeField] private float followSharpness = 1.5f;

    private void OnEnable()
    {
        if (palette == null) return;
        palette.Applied += Apply;
        if (palette.Current != null) Apply(palette.Current);
    }

    private void OnDisable()
    {
        if (palette != null) palette.Applied -= Apply;
    }

    private void Apply(ArenaPaletteSO p)
    {
        SetSystem(fireflies, p.Fireflies);
        SetSystem(fairyDust, p.FairyDust);

        if (fairyDust != null)
        {
            foreach (ParticleSystem ps in fairyDust.GetComponentsInChildren<ParticleSystem>(true))
            {
                ParticleSystem.MainModule main = ps.main;
                float alpha = main.startColor.color.a;
                main.startColor = new Color(p.DustColor.r, p.DustColor.g, p.DustColor.b, alpha);
            }
        }

        foreach (ArenaShapeShafts shaft in shafts)
        {
            if (shaft != null) shaft.enabled = p.LightShafts;
        }
    }

    private static void SetSystem(ParticleSystem ps, bool on)
    {
        if (ps == null) return;
        if (on)
        {
            if (!ps.isPlaying) ps.Play(true);
        }
        else
        {
            ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
        }
    }

    private void LateUpdate()
    {
        if (focus == null) return;
        float t = 1f - Mathf.Exp(-followSharpness * Time.deltaTime);
        Follow(fireflies, t);
        Follow(fairyDust, t);
    }

    private void Follow(ParticleSystem ps, float t)
    {
        if (ps == null) return;
        Transform tr = ps.transform;
        Vector3 current = tr.position;
        Vector3 target = new Vector3(focus.position.x, current.y, focus.position.z);
        tr.position = Vector3.Lerp(current, target, t);
    }
}
}
