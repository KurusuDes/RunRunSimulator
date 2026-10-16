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
        public Material Material;
        public float EdgeFade;
        public float FlowerDensity;
    }

    private const float EdgeStep = 0.25f;

    [Title("Semilla")]
    [SerializeField] private int seed = 11;

    [Title("Material")]
    [SerializeField] private Material bladeMaterial;

    [Title("Parcelas")]
    [SerializeField, Min(2f)] private float chunkSize = 5f;
    [SerializeField] private int maxBlades = 150000;

    [Title("Areas")]
    [SerializeField] private List<Area> areas = new List<Area>();

    [Title("Flores")]
    [SerializeField] private List<Color> flowerColors = new List<Color>
    {
        new Color(0.97f, 0.95f, 0.88f),
        new Color(1f, 0.88f, 0.45f),
        new Color(0.78f, 0.66f, 0.92f),
        new Color(0.62f, 0.8f, 0.95f),
        new Color(0.98f, 0.7f, 0.8f)
    };
    [SerializeField] private float flowerClusterSize = 3.5f;
    [SerializeField, Range(0f, 1f)] private float flowerClusterChance = 0.45f;
    [SerializeField] private Vector2 flowerStemHeight = new Vector2(0.18f, 0.32f);
    [SerializeField] private Vector2 flowerHeadSize = new Vector2(0.05f, 0.08f);

    [Title("Exclusiones")]
    [SerializeField] private float exclusionMargin = 0.4f;
    [SerializeField] private List<Rect> exclusions = new List<Rect>();
    [SerializeField, Min(0f)] private float exclusionInset = 0.5f;
    [SerializeField] private List<Transform> excludeColliderRoots = new List<Transform>();
    [SerializeField] private bool blockByColliders = false;

    [Title("Relieve")]
    [SerializeField] private Transform reliefRoot;

    private GameObject grassField;
    private List<Collider> reliefColliders = new List<Collider>();

    public IReadOnlyList<Rect> Exclusions => exclusions;

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
        var rngEdge = new System.Random(seed + 7);
        var rngFlower = new System.Random(seed + 13);
        var colliders = blockByColliders ? CollectColliders() : new List<Collider>();
        reliefColliders = CollectReliefColliders();
        int totalBlades = 0;

        for (int a = 0; a < areas.Count; a++)
        {
            var area = areas[a];
            if (area.Rect.width <= 0f || area.Rect.height <= 0f || area.Density <= 0f) continue;

            var cover = area.Cover.clumpSpacing > 0f ? area.Cover : ArenaGrassCover.Settings.Default;
            var blocked = BuildBlockedRects(area, colliders);
            var material = area.Material != null ? area.Material : bladeMaterial;
            float fade = Mathf.Max(0f, area.EdgeFade);

            for (float chunkX = area.Rect.xMin; chunkX < area.Rect.xMax; chunkX += chunkSize)
            {
                for (float chunkZ = area.Rect.yMin; chunkZ < area.Rect.yMax; chunkZ += chunkSize)
                {
                    var chunkRect = Rect.MinMaxRect(chunkX, chunkZ, Mathf.Min(chunkX + chunkSize, area.Rect.xMax), Mathf.Min(chunkZ + chunkSize, area.Rect.yMax));
                    var chunkCenter = new Vector3(chunkRect.center.x, area.Height, chunkRect.center.y);

                    var filterRect = Rect.MinMaxRect(chunkRect.xMin - fade, chunkRect.yMin - fade, chunkRect.xMax + fade, chunkRect.yMax + fade);
                    var nearBlocked = new List<Rect>();
                    for (int i = 0; i < blocked.Count; i++)
                        if (filterRect.Overlaps(blocked[i])) nearBlocked.Add(blocked[i]);

                    if (totalBlades < maxBlades)
                        totalBlades += SowGrassChunk(area, material, chunkRect, chunkCenter, nearBlocked, cover, rng, rngEdge, maxBlades - totalBlades);

                    if (area.FlowerDensity > 0f)
                        SowFlowerChunk(area, material, chunkRect, chunkCenter, nearBlocked, rngFlower);
                }
            }
        }
    }

    private int SowGrassChunk(Area area, Material material, Rect chunkRect, Vector3 chunkCenter, List<Rect> nearBlocked, ArenaGrassCover.Settings cover, System.Random rng, System.Random rngEdge, int remaining)
    {
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

            if (area.EdgeFade > 0f)
            {
                float s = EdgeSmooth(point, area, nearBlocked);
                if (rngEdge.NextDouble() > Mathf.Lerp(0.35f, 1f, s)) continue;
                heightScale *= Mathf.Lerp(0.3f, 1f, s);
            }

            roots.Add(new Vector3(x, ReliefY(x, z, area.Height), z));
            heights.Add(heightScale);
        }

        if (roots.Count == 0) return 0;

        if (roots.Count > remaining)
        {
            roots.RemoveRange(remaining, roots.Count - remaining);
            heights.RemoveRange(remaining, heights.Count - remaining);
        }

        var mesh = ArenaGrassBlades.Build(roots, rng, area.HeightRange, area.WidthRange, area.Tilt, chunkCenter, heights, area.Segments);
        if (mesh == null) return 0;

        CreateChunk("GrassChunk", mesh, material, chunkCenter);
        return roots.Count;
    }

    private void SowFlowerChunk(Area area, Material material, Rect chunkRect, Vector3 chunkCenter, List<Rect> nearBlocked, System.Random rngFlower)
    {
        if (flowerColors == null || flowerColors.Count == 0) return;

        float clusterSize = Mathf.Max(0.1f, flowerClusterSize);
        int candidateCount = Mathf.RoundToInt(area.FlowerDensity * chunkRect.width * chunkRect.height);
        var roots = new List<Vector3>(candidateCount);
        var colors = new List<Color>(candidateCount);

        for (int i = 0; i < candidateCount; i++)
        {
            float x = (float)(rngFlower.NextDouble() * chunkRect.width + chunkRect.xMin);
            float z = (float)(rngFlower.NextDouble() * chunkRect.height + chunkRect.yMin);
            var point = new Vector2(x, z);

            if (IsBlocked(point, nearBlocked)) continue;

            int cellX = Mathf.FloorToInt(x / clusterSize);
            int cellZ = Mathf.FloorToInt(z / clusterSize);
            if (CellHash(cellX, cellZ, seed) >= flowerClusterChance) continue;

            var cellCenter = new Vector2((cellX + 0.5f) * clusterSize, (cellZ + 0.5f) * clusterSize);
            float normalized = Mathf.Clamp01(Vector2.Distance(point, cellCenter) / (0.5f * clusterSize));
            if (rngFlower.NextDouble() > 1.0 - normalized) continue;

            if (area.EdgeFade > 0f && EdgeSmooth(point, area, nearBlocked) < 0.6f) continue;

            var baseColor = flowerColors[Mathf.Min((int)(CellHash(cellX, cellZ, seed + 101) * flowerColors.Count), flowerColors.Count - 1)];
            float brightness = Mathf.Lerp(0.92f, 1.05f, (float)rngFlower.NextDouble());

            roots.Add(new Vector3(x, ReliefY(x, z, area.Height), z));
            colors.Add(new Color(baseColor.r * brightness, baseColor.g * brightness, baseColor.b * brightness, 1f));
        }

        var mesh = MeadowFlowers.Build(roots, colors, rngFlower, flowerStemHeight, flowerHeadSize, chunkCenter);
        if (mesh == null) return;

        CreateChunk("FlowerChunk", mesh, material, chunkCenter);
    }

    private void CreateChunk(string chunkName, Mesh mesh, Material material, Vector3 position)
    {
        var chunk = new GameObject(chunkName) { hideFlags = HideFlags.DontSave };
        chunk.transform.SetParent(grassField.transform, false);
        chunk.transform.position = position;

        chunk.AddComponent<MeshFilter>().sharedMesh = mesh;

        var renderer = chunk.AddComponent<MeshRenderer>();
        renderer.sharedMaterial = material;
        renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        renderer.receiveShadows = true;
    }

    private float EdgeSmooth(Vector2 point, Area area, List<Rect> nearBlocked)
    {
        float fade = area.EdgeFade;
        float edge = fade;

        for (int i = 0; i < nearBlocked.Count; i++)
            edge = Mathf.Min(edge, DistanceToRect(point, nearBlocked[i]));

        var directions = new[] { Vector2.right, Vector2.left, Vector2.up, Vector2.down };
        for (int d = 0; d < directions.Length; d++)
        {
            for (float distance = EdgeStep; distance < edge; distance += EdgeStep)
            {
                if (!InsideAnyArea(point + directions[d] * distance, area.Height))
                {
                    edge = distance;
                    break;
                }
            }
        }

        float f = Mathf.Clamp01(edge / fade);
        return f * f * (3f - 2f * f);
    }

    private bool InsideAnyArea(Vector2 point, float height)
    {
        for (int i = 0; i < areas.Count; i++)
        {
            var other = areas[i];
            if (other.Density <= 0f || other.Rect.width <= 0f || other.Rect.height <= 0f) continue;
            if (Mathf.Abs(other.Height - height) >= 0.1f) continue;
            if (other.Rect.Contains(point)) return true;
        }
        return false;
    }

    private static float DistanceToRect(Vector2 point, Rect rect)
    {
        float dx = Mathf.Max(Mathf.Max(rect.xMin - point.x, 0f), point.x - rect.xMax);
        float dz = Mathf.Max(Mathf.Max(rect.yMin - point.y, 0f), point.y - rect.yMax);
        return Mathf.Sqrt(dx * dx + dz * dz);
    }

    private static float CellHash(int x, int z, int salt)
    {
        unchecked
        {
            uint h = (uint)(x * 73856093 ^ z * 19349663 ^ salt * 83492791);
            h ^= h >> 16;
            h *= 0x7feb352dU;
            h ^= h >> 15;
            h *= 0x846ca68bU;
            h ^= h >> 16;
            return (h >> 8) / 16777216f;
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

    private List<Collider> CollectReliefColliders()
    {
        var result = new List<Collider>();
        if (reliefRoot == null) return result;
        var found = reliefRoot.GetComponentsInChildren<Collider>();
        for (int i = 0; i < found.Length; i++)
            if (found[i].enabled && !found[i].isTrigger) result.Add(found[i]);
        return result;
    }

    private float ReliefY(float x, float z, float baseHeight)
    {
        float best = baseHeight;
        if (reliefColliders.Count == 0) return best;

        var ray = new Ray(new Vector3(x, baseHeight + 20f, z), Vector3.down);
        for (int i = 0; i < reliefColliders.Count; i++)
        {
            if (reliefColliders[i] == null) continue;
            if (reliefColliders[i].Raycast(ray, out var hit, 40f) && hit.point.y > best) best = hit.point.y;
        }
        return best;
    }

    private List<Rect> BuildBlockedRects(Area area, List<Collider> colliders)
    {
        var blocked = new List<Rect>(exclusions.Count);
        for (int i = 0; i < exclusions.Count; i++)
        {
            var r = exclusions[i];
            if (r.width > exclusionInset * 2f && r.height > exclusionInset * 2f)
                blocked.Add(new Rect(r.x + exclusionInset, r.y + exclusionInset, r.width - exclusionInset * 2f, r.height - exclusionInset * 2f));
        }
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
