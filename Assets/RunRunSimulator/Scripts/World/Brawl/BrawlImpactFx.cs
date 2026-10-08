using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlImpactFx : MonoBehaviour
{
    private const int RingTextureSize = 64;
    private const float RingRadius = 0.8f;
    private const float RingHalfWidth = 0.14f;
    private const float StarSeconds = 0.16f;
    private const float StarPeak = 1.3f;
    private const float StarRiseFraction = 0.3f;
    private const float RingSeconds = 0.22f;
    private const float RingFrom = 0.3f;
    private const float RingTo = 1.7f;
    private const float CameraNudge = 0.5f;
    private const int StarOrder = 41;
    private const int RingOrder = 40;

    private class Pair
    {
        public SpriteRenderer Star;
        public SpriteRenderer Ring;
    }

    private class Run
    {
        public Pair Pair;
        public Vector3 Point;
        public Color Color;
        public float Scale;
        public float Angle;
        public float Start;
    }

    private readonly Stack<Pair> free = new();
    private readonly List<Run> runs = new();

    private Texture2D ringTexture;
    private Sprite ringSprite;

    public void Hit(Vector3 point, Color color, float scale)
    {
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.SpriteMaterial == null) return;

        var pair = free.Count > 0 ? free.Pop() : Create();

        pair.Star.sprite = lib.SparkSprite;
        pair.Star.color = Color.white;
        pair.Star.sharedMaterial = lib.SpriteMaterial;
        pair.Star.transform.localScale = Vector3.zero;
        pair.Star.gameObject.SetActive(true);

        pair.Ring.sprite = GetRingSprite();
        pair.Ring.color = color;
        pair.Ring.sharedMaterial = lib.SpriteMaterial;
        pair.Ring.transform.localScale = Vector3.zero;
        pair.Ring.gameObject.SetActive(true);

        runs.Add(new Run
        {
            Pair = pair,
            Point = point,
            Color = color,
            Scale = scale,
            Angle = Random.Range(0f, 360f),
            Start = Time.time
        });
    }

    private void LateUpdate()
    {
        var cam = Camera.main;
        Quaternion face = cam != null ? cam.transform.rotation : Quaternion.identity;
        Vector3 nudge = cam != null ? -cam.transform.forward * CameraNudge : Vector3.zero;
        float now = Time.time;

        for (int i = runs.Count - 1; i >= 0; i--)
        {
            var run = runs[i];
            float age = now - run.Start;
            if (age >= RingSeconds)
            {
                Release(run.Pair);
                runs.RemoveAt(i);
                continue;
            }
            Step(run, age, face, nudge);
        }
    }

    private static void Step(Run run, float age, Quaternion face, Vector3 nudge)
    {
        Vector3 pos = run.Point + nudge;

        float starT = age / StarSeconds;
        float starK = 0f;
        if (starT < 1f)
            starK = starT < StarRiseFraction ? starT / StarRiseFraction : 1f - (starT - StarRiseFraction) / (1f - StarRiseFraction);

        var star = run.Pair.Star.transform;
        star.position = pos;
        star.rotation = face * Quaternion.Euler(0f, 0f, run.Angle);
        star.localScale = Vector3.one * (run.Scale * StarPeak * starK);

        float ringT = age / RingSeconds;
        float eased = 1f - (1f - ringT) * (1f - ringT);
        var ring = run.Pair.Ring;
        ring.transform.position = pos;
        ring.transform.rotation = face;
        ring.transform.localScale = Vector3.one * (run.Scale * Mathf.Lerp(RingFrom, RingTo, eased));

        Color c = run.Color;
        c.a *= 1f - ringT;
        ring.color = c;
    }

    private Pair Create()
    {
        return new Pair
        {
            Star = NewSprite("ImpactStar", StarOrder),
            Ring = NewSprite("ImpactRing", RingOrder)
        };
    }

    private SpriteRenderer NewSprite(string label, int order)
    {
        var go = new GameObject(label);
        go.transform.SetParent(transform, false);
        var sr = go.AddComponent<SpriteRenderer>();
        sr.sortingOrder = order;
        return sr;
    }

    private void Release(Pair pair)
    {
        pair.Star.gameObject.SetActive(false);
        pair.Ring.gameObject.SetActive(false);
        free.Push(pair);
    }

    private Sprite GetRingSprite()
    {
        if (ringSprite != null) return ringSprite;

        ringTexture = new Texture2D(RingTextureSize, RingTextureSize, TextureFormat.RGBA32, false)
        {
            name = "BrawlImpactRing",
            wrapMode = TextureWrapMode.Clamp,
            filterMode = FilterMode.Bilinear
        };

        var pixels = new Color[RingTextureSize * RingTextureSize];
        float half = RingTextureSize * 0.5f;
        for (int y = 0; y < RingTextureSize; y++)
        {
            for (int x = 0; x < RingTextureSize; x++)
            {
                float dx = x + 0.5f - half;
                float dy = y + 0.5f - half;
                float r = Mathf.Sqrt(dx * dx + dy * dy) / half;
                float a = Mathf.Clamp01(1f - Mathf.Abs(r - RingRadius) / RingHalfWidth);
                a = a * a * (3f - 2f * a);
                pixels[y * RingTextureSize + x] = new Color(1f, 1f, 1f, a);
            }
        }
        ringTexture.SetPixels(pixels);
        ringTexture.Apply();

        ringSprite = Sprite.Create(
            ringTexture,
            new Rect(0f, 0f, RingTextureSize, RingTextureSize),
            new Vector2(0.5f, 0.5f),
            RingTextureSize);
        return ringSprite;
    }

    private void OnDestroy()
    {
        if (ringSprite != null) Destroy(ringSprite);
        if (ringTexture != null) Destroy(ringTexture);
    }
}
}
