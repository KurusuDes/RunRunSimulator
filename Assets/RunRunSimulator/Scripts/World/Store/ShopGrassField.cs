using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{

[ExecuteAlways]
public class ShopGrassField : MonoBehaviour
{
    [System.Serializable]
    public struct Area
    {
        public string Name;
        public Rect Rect;
        public float Height;
        public float Density;
        public Vector2 HeightRange;
        public Vector2 WidthRange;
        public float Tilt;
        public int Segments;
        public ArenaGrassCover.Settings Cover;
    }

    [Title("Semilla")]
    [SerializeField] private int seed = 11;

    [Title("Material")]
    [SerializeField] private Material bladeMaterial;

    [Title("Parcelas")]
    [SerializeField, Min(2f)] private float chunkSize = 5f;
    [SerializeField] private int maxBlades = 150000;

    [Title("Areas")]
    [SerializeField] private List<Area> areas = new List<Area>();

    [Title("Exclusiones")]
    [SerializeField] private float exclusionMargin = 0.4f;
    [SerializeField] private List<Rect> exclusions = new List<Rect>();
    [SerializeField] private List<Transform> excludeColliderRoots = new List<Transform>();

    private GameObject grassField;

    private void OnEnable()
    {
        Sow();
    }

    private void OnDisable()
    {
        DestroyGrassField();
    }

    private void OnValidate()
    {
#if UNITY_EDITOR
        if (!Application.isPlaying)
        {
            UnityEditor.EditorApplication.delayCall -= SowIfAlive;
            UnityEditor.EditorApplication.delayCall += SowIfAlive;
        }
#endif
    }

#if UNITY_EDITOR
    private void SowIfAlive()
    {
        if (this != null && isActiveAndEnabled) Sow();
    }
#endif

    [Button("Sembrar")]
    public void Sow()
    {
        DestroyGrassField();

        if (bladeMaterial == null || areas.Count == 0) return;

        grassField = new GameObject("GrassField") { hideFlags = HideFlags.DontSave };
        grassField.transform.SetParent(transform, false);

        var rng = new System.Random(seed);
        var colliders = CollectColliders();
        int totalBlades = 0;

        for (int a = 0; a < areas.Count; a++)
        {
            var area = areas[a];
            if (area.Rect.width <= 0f || area.Rect.height <= 0f || area.Density <= 0f) continue;

            var cover = area.Cover.clumpSpacing > 0f ? area.Cover : ArenaGrassCover.Settings.Default;
            var blocked = BuildBlockedRects(area, colliders);

            for (float chunkX = area.Rect.xMin; chunkX < area.Rect.xMax; chunkX += chunkSize)
            {
                for (float chunkZ = area.Rect.yMin; chunkZ < area.Rect.yMax; chunkZ += chunkSize)
                {
                    var chunkRect = Rect.MinMaxRect(chunkX, chunkZ, Mathf.Min(chunkX + chunkSize, area.Rect.xMax), Mathf.Min(chunkZ + chunkSize, area.Rect.yMax));
                    var chunkCenter = new Vector3(chunkRect.center.x, area.Height, chunkRect.center.y);

                    var nearBlocked = new List<Rect>();
                    for (int i = 0; i < blocked.Count; i++)
                        if (chunkRect.Overlaps(blocked[i])) nearBlocked.Add(blocked[i]);

                    int candidateCount = Mathf.RoundToInt(area.Density * chunkRect.width * chunkRect.height);
                    var roots = new List<Vector3>(candidateCount);
                    var heights = new List<float>(candidateCount);

                    for (int i = 0; i < candidateCount; i++)
                    {
                        float x = (float)(rng.NextDouble() * chunkRect.width + chunkRect.xMin);
                        float z = (float)(rng.NextDouble() * chunkRect.height + chunkRect.yMin);
                        var point = new Vector2(x, z);

                        if (IsBlocked(point, nearBlocked)) continue;

                        float density = ArenaGrassCover.Sample(point, seed, in cover, out float heightScale);
                        if (rng.NextDouble() >= density) continue;
                        roots.Add(new Vector3(x, area.Height, z));
                        heights.Add(heightScale);
                    }

                    if (roots.Count == 0) continue;

                    if (totalBlades + roots.Count > maxBlades)
                    {
                        int remaining = maxBlades - totalBlades;
                        if (remaining <= 0) return;
                        roots.RemoveRange(remaining, roots.Count - remaining);
                        heights.RemoveRange(remaining, heights.Count - remaining);
                    }

                    totalBlades += roots.Count;

                    var mesh = ArenaGrassBlades.Build(roots, rng, area.HeightRange, area.WidthRange, area.Tilt, chunkCenter, heights, area.Segments);
                    if (mesh == null) continue;

                    var chunk = new GameObject("GrassChunk") { hideFlags = HideFlags.DontSave };
                    chunk.transform.SetParent(grassField.transform, false);
                    chunk.transform.position = chunkCenter;

                    chunk.AddComponent<MeshFilter>().sharedMesh = mesh;

                    var renderer = chunk.AddComponent<MeshRenderer>();
                    renderer.sharedMaterial = bladeMaterial;
                    renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                    renderer.receiveShadows = true;

                    if (totalBlades >= maxBlades) return;
                }
            }
        }
    }

    private List<Collider> CollectColliders()
    {
        var result = new List<Collider>();
        for (int i = 0; i < excludeColliderRoots.Count; i++)
        {
            if (excludeColliderRoots[i] == null) continue;
            var found = excludeColliderRoots[i].GetComponentsInChildren<Collider>();
            for (int c = 0; c < found.Length; c++)
                if (found[c].enabled) result.Add(found[c]);
        }
        return result;
    }

    private List<Rect> BuildBlockedRects(Area area, List<Collider> colliders)
    {
        var blocked = new List<Rect>(exclusions);
        for (int i = 0; i < colliders.Count; i++)
        {
            var bounds = colliders[i].bounds;
            if (bounds.max.y <= area.Height + 0.05f) continue;
            blocked.Add(Rect.MinMaxRect(
                bounds.min.x - exclusionMargin,
                bounds.min.z - exclusionMargin,
                bounds.max.x + exclusionMargin,
                bounds.max.z + exclusionMargin));
        }
        return blocked;
    }

    private static bool IsBlocked(Vector2 point, List<Rect> blocked)
    {
        for (int i = 0; i < blocked.Count; i++)
            if (blocked[i].Contains(point)) return true;
        return false;
    }

    private void DestroyGrassField()
    {
        if (grassField != null)
        {
            DestroyChunks(grassField.transform);
            DestroyImmediate(grassField);
            grassField = null;
        }

        for (int i = transform.childCount - 1; i >= 0; i--)
        {
            var child = transform.GetChild(i);
            if (child.name == "GrassField")
            {
                DestroyChunks(child);
                DestroyImmediate(child.gameObject);
            }
        }
    }

    private static void DestroyChunks(Transform field)
    {
        for (int i = 0; i < field.childCount; i++)
        {
            var filter = field.GetChild(i).GetComponent<MeshFilter>();
            if (filter != null && filter.sharedMesh != null) DestroyImmediate(filter.sharedMesh);
        }
    }
}
}
