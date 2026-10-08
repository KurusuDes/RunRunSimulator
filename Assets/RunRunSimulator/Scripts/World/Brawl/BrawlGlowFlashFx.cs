using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlGlowFlashFx : MonoBehaviour
{
    private const float Seconds = 0.18f;
    private const float ScaleFrom = 0.2f;
    private const float ScalePeak = 1.2f;
    private const float PeakFraction = 0.4f;
    private const float CameraNudge = 0.5f;
    private const int SortingOrder = 22;

    private class Run
    {
        public SpriteRenderer[] Sprites;
        public Vector3[] Points;
        public float Start;
    }

    private readonly Stack<SpriteRenderer> free = new();
    private readonly List<Run> runs = new();

    public void Pop(Vector3[] points, Color color)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (points == null || points.Length == 0) return;
        if (lib == null || lib.GlowSprite == null || lib.ParticleAdditiveMaterial == null) return;

        var run = new Run
        {
            Sprites = new SpriteRenderer[points.Length],
            Points = (Vector3[])points.Clone(),
            Start = Time.time
        };

        for (int i = 0; i < points.Length; i++)
        {
            var sr = free.Count > 0 ? free.Pop() : Create();
            sr.sprite = lib.GlowSprite;
            sr.sharedMaterial = lib.ParticleAdditiveMaterial;
            sr.color = color;
            sr.transform.localScale = Vector3.zero;
            sr.gameObject.SetActive(true);
            run.Sprites[i] = sr;
        }
        runs.Add(run);
    }

    private void LateUpdate()
    {
        var cam = Camera.main;
        Quaternion face = cam != null ? cam.transform.rotation : Quaternion.identity;
        Vector3 nudge = cam != null ? -cam.transform.forward * CameraNudge : Vector3.zero;

        for (int i = runs.Count - 1; i >= 0; i--)
        {
            var run = runs[i];
            float u = (Time.time - run.Start) / Seconds;
            if (u >= 1f)
            {
                for (int k = 0; k < run.Sprites.Length; k++)
                {
                    run.Sprites[k].gameObject.SetActive(false);
                    free.Push(run.Sprites[k]);
                }
                runs.RemoveAt(i);
                continue;
            }

            float scale = u < PeakFraction
                ? Mathf.Lerp(ScaleFrom, ScalePeak, u / PeakFraction)
                : Mathf.Lerp(ScalePeak, 0f, (u - PeakFraction) / (1f - PeakFraction));

            for (int k = 0; k < run.Sprites.Length; k++)
            {
                var tr = run.Sprites[k].transform;
                tr.position = run.Points[k] + nudge;
                tr.rotation = face;
                tr.localScale = Vector3.one * scale;
            }
        }
    }

    private SpriteRenderer Create()
    {
        var go = new GameObject("Flash");
        go.transform.SetParent(transform, false);
        var sr = go.AddComponent<SpriteRenderer>();
        sr.sortingOrder = SortingOrder;
        return sr;
    }
}
}
