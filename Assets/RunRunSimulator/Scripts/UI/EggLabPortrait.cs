using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{
    public class EggLabPortrait : MonoBehaviour
    {
        [Required, SerializeField] private Camera portraitCamera;
        [SerializeField] private int textureSize = 512;
        [SerializeField] private float orbitSpeed = 35f;
        [SerializeField] private float distance = 0.95f;
        [SerializeField] private float height = 0.16f;
        [SerializeField] private float pitch = 8f;

        private RenderTexture rt;
        private Transform target;
        private float yaw;
        private int focusLayer = -1;
        private readonly List<(Transform t, int layer)> originalLayers = new();

        private void Awake()
        {
            focusLayer = LayerMask.NameToLayer("MonchiFocus");

            rt = new RenderTexture(textureSize, textureSize, 16, RenderTextureFormat.ARGB32);
            portraitCamera.targetTexture = rt;
            portraitCamera.enabled = false;
            if (focusLayer >= 0) portraitCamera.cullingMask = 1 << focusLayer;
        }

        public RenderTexture Show(Transform newTarget)
        {
            if (target != null) Hide();

            target = newTarget;

            if (focusLayer >= 0 && target != null)
            {
                foreach (var t in target.GetComponentsInChildren<Transform>(true))
                {
                    originalLayers.Add((t, t.gameObject.layer));
                    t.gameObject.layer = focusLayer;
                }
            }

            portraitCamera.enabled = true;
            UpdateOrbit();

            return rt;
        }

        public void Hide()
        {
            RestoreLayers();
            portraitCamera.enabled = false;
            target = null;
        }

        private void RestoreLayers()
        {
            foreach (var entry in originalLayers)
                if (entry.t != null)
                    entry.t.gameObject.layer = entry.layer;

            originalLayers.Clear();
        }

        private void LateUpdate()
        {
            if (target == null) return;

            yaw += orbitSpeed * Time.deltaTime;
            UpdateOrbit();
        }

        private void UpdateOrbit()
        {
            if (target == null) return;

            Vector3 center = target.position + Vector3.up * height;
            Vector3 dir = Quaternion.Euler(pitch, yaw, 0f) * Vector3.forward;
            Vector3 pos = center - dir * distance;

            portraitCamera.transform.position = pos;
            portraitCamera.transform.rotation = Quaternion.LookRotation(center - pos, Vector3.up);
        }

        private void OnDestroy()
        {
            if (rt != null)
            {
                rt.Release();
                Destroy(rt);
            }
        }
    }
}
