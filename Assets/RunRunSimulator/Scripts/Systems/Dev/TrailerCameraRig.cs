using UnityEngine;

namespace MoriMonchiSimulator
{
    public class TrailerCameraRig : MonoBehaviour
    {
        public enum Move { Orbit, Dolly, Static }

        public Transform Target;
        public Vector3 FixedPoint;
        public Vector3 LookOffset = new Vector3(0f, 0.4f, 0f);
        public Move Mode = Move.Orbit;

        public float Radius = 3f;
        public float Height = 1.2f;
        public float StartAngle = 0f;
        public float AngularSpeed = 20f;
        public float RadiusEnd = -1f;

        public Vector3 From;
        public Vector3 To;

        public float Duration = 3f;
        public float FovStart = 40f;
        public float FovEnd = 40f;
        public float Smoothing = 8f;
        public bool AvoidObstacles = true;
        public float ObstaclePadding = 0.3f;
        public UnityEngine.Rendering.Universal.DepthOfField Dof;

        Camera cam;
        float elapsed;
        Vector3 smoothedLook;
        bool lookInitialized;

        public void Restart()
        {
            elapsed = 0f;
            lookInitialized = false;
        }

        void Awake()
        {
            cam = GetComponent<Camera>();
        }

        void LateUpdate()
        {
            elapsed += Time.deltaTime;
            float k = Duration > 0f ? Mathf.Clamp01(elapsed / Duration) : 1f;

            Vector3 anchor = Target != null ? Target.position : FixedPoint;
            Vector3 look = anchor + LookOffset;

            switch (Mode)
            {
                case Move.Orbit:
                    float radius = RadiusEnd >= 0f ? Mathf.Lerp(Radius, RadiusEnd, k) : Radius;
                    float angle = (StartAngle + AngularSpeed * elapsed) * Mathf.Deg2Rad;
                    Vector3 desired = anchor + new Vector3(Mathf.Sin(angle) * radius, Height, Mathf.Cos(angle) * radius);
                    transform.position = AvoidObstacles ? Unblocked(look, desired) : desired;
                    break;
                case Move.Dolly:
                    transform.position = Vector3.Lerp(From, To, Mathf.SmoothStep(0f, 1f, k));
                    break;
            }

            if (!lookInitialized)
            {
                smoothedLook = look;
                lookInitialized = true;
            }
            else
            {
                smoothedLook = Vector3.Lerp(smoothedLook, look, 1f - Mathf.Exp(-Smoothing * Time.deltaTime));
            }

            Vector3 dir = smoothedLook - transform.position;
            if (dir.sqrMagnitude > 0.0001f)
                transform.rotation = Quaternion.LookRotation(dir, Vector3.up);

            if (Dof != null)
                Dof.focusDistance.value = Vector3.Distance(transform.position, look);

            if (cam == null)
                cam = GetComponent<Camera>();
            if (cam != null)
                cam.fieldOfView = Mathf.Lerp(FovStart, FovEnd, k);
        }

        Vector3 Unblocked(Vector3 from, Vector3 to)
        {
            Vector3 dir = to - from;
            float dist = dir.magnitude;
            if (dist < 0.001f) return to;
            if (Physics.SphereCast(from, 0.2f, dir / dist, out var hit, dist, ~0, QueryTriggerInteraction.Ignore)
                && (Target == null || !hit.transform.IsChildOf(Target)))
                return from + dir / dist * Mathf.Max(0.4f, hit.distance - ObstaclePadding);
            return to;
        }
    }
}
