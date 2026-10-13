using System.Collections;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.AI;

namespace MoriMonchiSimulator
{
    public class TitleWanderer : MonoBehaviour
    {
        [Required, SerializeField] private NavMeshAgent agent;
        [Required, SerializeField] private MonchiLocomotionAnimator locomotion;
        [SerializeField] private Vector2 idleSeconds = new Vector2(2f, 6f);
        [Range(0f, 1f), SerializeField] private float gestureChance = 0.35f;
        [Range(0f, 1f), SerializeField] private float approachChance = 0.25f;
        [SerializeField] private float approachDistance = 1.6f;
        [SerializeField] private float turnSpeed = 180f;
        [SerializeField] private string[] gestures = { "Yes", "No", "Eat", "Roar" };

        private Transform center;
        private float radius;
        private readonly List<Transform> others = new();

        public void Init(Transform centerPoint, float wanderRadius)
        {
            center = centerPoint;
            radius = wanderRadius;
            agent.speed = Random.Range(0.8f, 1.4f);
            StopAllCoroutines();
            StartCoroutine(Loop());
        }

        private IEnumerator Loop()
        {
            yield return null;
            foreach (var other in FindObjectsByType<TitleWanderer>(FindObjectsSortMode.None))
                if (other != this) others.Add(other.transform);

            while (true)
            {
                Transform lookTarget = others.Count > 0 && Random.value < approachChance ? NearestOther() : null;
                bool found = lookTarget != null ? TryApproachPoint(lookTarget.position, out var destination) : TryRandomPoint(out destination);

                if (found && agent.isOnNavMesh)
                {
                    agent.SetDestination(destination);
                    yield return WaitArrival();
                }
                yield return null;
                if (lookTarget == null && gestures.Length > 0 && Random.value < gestureChance)
                    locomotion.PlayGesture(gestures[Random.Range(0, gestures.Length)]);
                float until = Time.time + Random.Range(idleSeconds.x, idleSeconds.y);
                while (Time.time < until)
                {
                    if (lookTarget != null) FaceTowards(lookTarget.position);
                    yield return null;
                }
            }
        }

        private IEnumerator WaitArrival()
        {
            float timeout = Time.time + 30f;
            yield return null;
            while (Time.time < timeout && agent.isOnNavMesh && (agent.pathPending || agent.remainingDistance > agent.stoppingDistance + 0.1f))
                yield return null;
        }

        private Transform NearestOther()
        {
            Transform best = null;
            float bestSqr = float.MaxValue;
            foreach (var other in others)
            {
                if (other == null) continue;
                float sqr = (other.position - transform.position).sqrMagnitude;
                if (sqr < bestSqr) { bestSqr = sqr; best = other; }
            }
            return best;
        }

        private bool TryRandomPoint(out Vector3 point)
        {
            Vector3 origin = center != null ? center.position : transform.position;
            for (int i = 0; i < 8; i++)
            {
                Vector2 offset = Random.insideUnitCircle * radius;
                if (TrySample(origin + new Vector3(offset.x, 0f, offset.y), out point)) return true;
            }
            point = transform.position;
            return false;
        }

        private bool TryApproachPoint(Vector3 target, out Vector3 point)
        {
            Vector3 away = Vector3.ProjectOnPlane(transform.position - target, Vector3.up);
            Vector3 direction = away.sqrMagnitude > 0.001f ? away.normalized : Vector3.forward;
            return TrySample(target + direction * approachDistance, out point);
        }

        private bool TrySample(Vector3 candidate, out Vector3 point)
        {
            bool ok = NavMesh.SamplePosition(candidate, out var hit, 2f, NavMesh.AllAreas);
            point = ok ? hit.position : transform.position;
            return ok;
        }


        private void FaceTowards(Vector3 target)
        {
            Vector3 direction = Vector3.ProjectOnPlane(target - transform.position, Vector3.up);
            if (direction.sqrMagnitude < 0.001f) return;
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(direction), turnSpeed * Time.deltaTime);
        }
    }
}
