using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlTrailFx : MonoBehaviour
{
    private const float TrailTime = 0.35f;
    private const float MinFollowSeconds = 0.12f;
    private const float StartAlpha = 0.85f;
    private const float ReleaseMargin = 0.05f;
    private const int SortingOrder = 19;

    private class Running
    {
        public TrailRenderer Trail;
        public BrawlFighter Fighter;
        public float Start;
        public float StopTime;
        public bool Following;
    }

    private readonly Stack<TrailRenderer> free = new();
    private readonly List<Running> running = new();

    public void Follow(BrawlFighter fighter, Color color, float width)
    {
        if (fighter == null) return;
        var lib = BrawlVfxLibrarySO.Current;
        if (lib == null || lib.LineMaterial == null) return;

        Running run = null;
        for (int i = 0; i < running.Count; i++)
        {
            if (running[i].Fighter != fighter) continue;
            run = running[i];
            break;
        }

        if (run == null)
        {
            run = new Running { Trail = free.Count > 0 ? free.Pop() : Create(), Fighter = fighter };
            running.Add(run);
        }

        var trail = run.Trail;
        trail.gameObject.SetActive(false);
        trail.transform.position = fighter.Center;
        trail.sharedMaterial = lib.LineMaterial;
        trail.startWidth = width;
        trail.endWidth = 0f;
        trail.startColor = new Color(color.r, color.g, color.b, StartAlpha);
        trail.endColor = new Color(color.r, color.g, color.b, 0f);
        trail.emitting = true;
        trail.gameObject.SetActive(true);
        trail.Clear();

        run.Start = Time.time;
        run.Following = true;
    }

    private void LateUpdate()
    {
        for (int i = running.Count - 1; i >= 0; i--)
        {
            var run = running[i];
            if (run.Following) Track(run);

            if (run.Following || Time.time - run.StopTime < TrailTime + ReleaseMargin) continue;

            run.Trail.gameObject.SetActive(false);
            free.Push(run.Trail);
            running.RemoveAt(i);
        }
    }

    private static void Track(Running run)
    {
        var fighter = run.Fighter;
        if (fighter == null || !fighter.IsAlive)
        {
            Stop(run);
            return;
        }

        var motor = fighter.Motor;
        bool forced = motor != null && motor.IsForced;
        if (!forced && Time.time - run.Start >= MinFollowSeconds)
        {
            Stop(run);
            return;
        }

        run.Trail.transform.position = fighter.Center;
    }

    private static void Stop(Running run)
    {
        run.Following = false;
        run.StopTime = Time.time;
        run.Trail.emitting = false;
    }

    private TrailRenderer Create()
    {
        var go = new GameObject("Trail");
        go.transform.SetParent(transform, false);

        var trail = go.AddComponent<TrailRenderer>();
        trail.time = TrailTime;
        trail.minVertexDistance = 0.05f;
        trail.numCapVertices = 4;
        trail.alignment = LineAlignment.View;
        trail.textureMode = LineTextureMode.Stretch;
        trail.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        trail.receiveShadows = false;
        trail.autodestruct = false;
        trail.sortingOrder = SortingOrder;
        return trail;
    }
}
}
