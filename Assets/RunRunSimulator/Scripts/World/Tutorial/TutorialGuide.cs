using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.AI;

namespace MoriMonchiSimulator
{

public class TutorialGuide : MonoBehaviour
{
    private const int Subdivisions = 8;
    private const float FadeInSeconds = 0.4f;
    private const float FadeOutSeconds = 0.3f;
    private const float StartFadeLength = 1f;
    private const float EndFadeLength = 0.6f;

    [Required, SerializeField] private Transform player;
    [Required, SerializeField] private Material cueMaterial;
    [Required, SerializeField] private Material additiveMaterial;
    [SerializeField] private Color lineColor = new Color(1f, 0.78f, 0.28f, 0.9f);
    [SerializeField] private Color targetColor = new Color(1f, 0.85f, 0.4f, 0.9f);
    [SerializeField] private float lineWidth = 0.12f;
    [SerializeField] private float dashLength = 0.35f;
    [SerializeField] private float dashGap = 0.25f;
    [SerializeField] private float flowSpeed = 1.2f;
    [SerializeField] private float repathInterval = 0.25f;
    [SerializeField] private float floorOffset = 0.05f;

    private NavMeshPath path;
    private readonly List<Vector3> raw = new();
    private readonly List<Vector3> smooth = new();
    private float alpha;
    private float switchFade = 1f;
    private bool visible;
    private float nextRepath;
    private Vector3 targetPos;
    private float targetRadius = 1f;

    private void Awake() => path = new NavMeshPath();

    private void OnEnable()
    {
        TutorialDirector.StepChanged += OnStepChanged;
        TutorialDirector.StepCompleted += OnStepCompleted;
        TutorialDirector.Finished += OnFinished;
    }

    private void OnDisable()
    {
        TutorialDirector.StepChanged -= OnStepChanged;
        TutorialDirector.StepCompleted -= OnStepCompleted;
        TutorialDirector.Finished -= OnFinished;
    }

    private void OnStepChanged(int index, int total, string text)
    {
        var director = TutorialDirector.Instance;
        visible = director != null && director.Active && director.Current.Target != null;
        switchFade = 0f;
        nextRepath = 0f;
        raw.Clear();
    }

    private void OnStepCompleted()
    {
        visible = false;
    }

    private void OnFinished()
    {
        visible = false;
    }

    private void LateUpdate()
    {
        float dt = Time.unscaledDeltaTime;
        var director = TutorialDirector.Instance;
        if (director != null && director.Active && visible)
        {
            var step = director.Current;
            if (step.Target != null)
            {
                targetPos = step.Target.position;
                targetRadius = Mathf.Max(0.5f, step.Radius);
            }
            else visible = false;
        }

        alpha = Mathf.MoveTowards(alpha, visible ? 1f : 0f, dt / (visible ? FadeInSeconds : FadeOutSeconds));
        switchFade = Mathf.MoveTowards(switchFade, 1f, dt / FadeInSeconds);
        if (alpha <= 0.01f || player == null) return;

        float prevScale = CueDrawer.AlphaScale;
        bool prevBehind = CueDrawer.DrawBehind;
        CueDrawer.Configure(cueMaterial, additiveMaterial);
        CueDrawer.AlphaScale = 1f;
        CueDrawer.DrawBehind = false;

        if (Time.unscaledTime >= nextRepath)
        {
            nextRepath = Time.unscaledTime + repathInterval;
            Repath();
        }

        float master = Mathf.SmoothStep(0f, 1f, alpha);
        DrawLine(master);
        DrawTarget(master);

        CueDrawer.AlphaScale = prevScale;
        CueDrawer.DrawBehind = prevBehind;
    }

    private void Repath()
    {
        raw.Clear();
        Vector3 from = player.position;
        Vector3 to = targetPos;
        bool ok = NavMesh.SamplePosition(from, out var hitA, 2f, NavMesh.AllAreas)
                  && NavMesh.SamplePosition(to, out var hitB, 2f, NavMesh.AllAreas)
                  && NavMesh.CalculatePath(hitA.position, hitB.position, NavMesh.AllAreas, path)
                  && path.corners.Length >= 2;
        if (ok)
        {
            raw.AddRange(path.corners);
            return;
        }
        raw.Add(from);
        raw.Add(to);
    }

    private void DrawLine(float master)
    {
        if (raw.Count < 2) return;

        Vector3 lift = Vector3.up * floorOffset;
        Vector3 start = player.position;
        start.y = raw[0].y;
        if (Vector3.Distance(start, targetPos) < targetRadius) return;

        smooth.Clear();
        int n = raw.Count;
        for (int i = 0; i < n - 1; i++)
        {
            Vector3 p1 = i == 0 ? start : raw[i];
            Vector3 p2 = raw[i + 1];
            Vector3 p0 = i == 0 ? p1 - (p2 - p1) : raw[i - 1];
            Vector3 p3 = i == n - 2 ? p2 + (p2 - p1) : raw[i + 2];
            for (int s = 0; s < Subdivisions; s++)
                smooth.Add(CatmullRom(p0, p1, p2, p3, (float)s / Subdivisions) + lift);
        }
        smooth.Add(raw[n - 1] + lift);

        float total = 0f;
        for (int i = 1; i < smooth.Count; i++) total += Vector3.Distance(smooth[i - 1], smooth[i]);

        float baseAlpha = lineColor.a * master * Mathf.SmoothStep(0f, 1f, switchFade);
        float traveled = 0f;
        float time = Time.unscaledTime * flowSpeed;
        for (int i = 1; i < smooth.Count; i++)
        {
            float segLen = Vector3.Distance(smooth[i - 1], smooth[i]);
            float dStart = traveled;
            float dEnd = traveled + segLen;
            traveled = dEnd;
            if (total - dStart < targetRadius) break;

            Color a = lineColor;
            a.a = baseAlpha * EdgeFade(dStart, total);
            Color b = lineColor;
            b.a = baseAlpha * EdgeFade(dEnd, total);
            CueDrawer.DashedSegment(smooth[i - 1], smooth[i], lineWidth, dashLength, dashGap, time - dStart, a, b);
        }
    }

    private float EdgeFade(float distance, float total)
    {
        float head = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(distance / StartFadeLength));
        float tail = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01((total - distance - targetRadius) / EndFadeLength));
        return head * tail;
    }

    private void DrawTarget(float master)
    {
        Vector3 center = targetPos;
        if (NavMesh.SamplePosition(targetPos, out var hit, 2f, NavMesh.AllAreas)) center.y = hit.position.y;
        center += Vector3.up * floorOffset;

        float t = Time.unscaledTime;
        float pulse = 1f + 0.125f * (1f + Mathf.Sin(t * 3f));

        Color dashed = targetColor;
        dashed.a *= master;
        Color ring = targetColor;
        ring.a *= master * Mathf.Lerp(1f, 0.3f, (pulse - 1f) / 0.25f);

        CueDrawer.Disc(center, targetRadius, targetColor, 0.28f * master, 0f, true);
        CueDrawer.DashedRing(center, targetRadius, lineWidth, 24, 0.55f, t * 0.8f, dashed);
        CueDrawer.Ring(center, targetRadius * pulse, lineWidth * 0.6f, ring, true);
    }

    private static Vector3 CatmullRom(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
    {
        float t2 = t * t;
        float t3 = t2 * t;
        return 0.5f * (
            (2f * p1) +
            (-p0 + p2) * t +
            (2f * p0 - 5f * p1 + 4f * p2 - p3) * t2 +
            (-p0 + 3f * p1 - 3f * p2 + p3) * t3
        );
    }
}
}
