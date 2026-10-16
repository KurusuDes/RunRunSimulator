using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MoriMonchiSimulator
{

[ExecuteAlways]
public class ShopGrassMask : MonoBehaviour
{
    [SerializeField] private Rect area = new Rect(-80f, -30f, 110f, 105f);
    [SerializeField, Min(64)] private int resolution = 1024;
    [SerializeField, Min(0.01f)] private float feather = 0.45f;
    [SerializeField] private float groundHeight = 0f;
    [SerializeField] private float contactTolerance = 0.35f;
    [SerializeField] private List<Transform> roots = new List<Transform>();
    [SerializeField] private List<Transform> ignore = new List<Transform>();
    [SerializeField] private ShopGrassField field;
    [SerializeField, Min(0.01f)] private float rectFeather = 0.45f;
    [SerializeField, Min(0.5f)] private float tallMeshHeight = 3f;
    [SerializeField, Min(0.05f)] private float trunkRadius = 0.45f;

    private static readonly int MaskTexID = Shader.PropertyToID("_ShopGrassMaskTex");
    private static readonly int MaskAreaID = Shader.PropertyToID("_ShopGrassMaskArea");

    private Texture2D tex;
    private float[] cover;
    private byte[] bytes;
    private readonly List<Collider> colliders = new List<Collider>();

    private void OnEnable()
    {
        GameEvents.OnNavMeshRebaked += Bake;
        GameEvents.OnShopZoneOpened += HandleZoneOpened;
        Bake();
    }

    private void OnDisable()
    {
        GameEvents.OnNavMeshRebaked -= Bake;
        GameEvents.OnShopZoneOpened -= HandleZoneOpened;
        Shader.SetGlobalVector(MaskAreaID, new Vector4(area.x, area.y, 0f, 0f));
        if (tex != null)
        {
            if (Application.isPlaying) Destroy(tex);
            else DestroyImmediate(tex);
            tex = null;
        }
    }

    private void HandleZoneOpened(ShopUpgradeSO expansion, int level) => Bake();

    [Button("Hornear")]
    public void Bake()
    {
        if (!isActiveAndEnabled || area.width <= 0f || area.height <= 0f) return;

        int res = Mathf.Max(64, resolution);
        int count = res * res;
        if (cover == null || cover.Length != count)
        {
            cover = new float[count];
            bytes = new byte[count];
        }
        else
        {
            System.Array.Clear(cover, 0, count);
        }

        if (tex == null || tex.width != res)
        {
            if (tex != null)
            {
                if (Application.isPlaying) Destroy(tex);
                else DestroyImmediate(tex);
            }
            tex = new Texture2D(res, res, TextureFormat.R8, false, true)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear,
                hideFlags = HideFlags.DontSave
            };
        }

        CollectColliders();
        float cellX = area.width / res;
        float cellZ = area.height / res;
        for (int i = 0; i < colliders.Count; i++) Rasterize(colliders[i], res, cellX, cellZ);
        if (field != null)
        {
            var rects = field.Exclusions;
            for (int i = 0; i < rects.Count; i++) RasterizeRect(rects[i], res, cellX, cellZ);
        }

        for (int i = 0; i < count; i++) bytes[i] = (byte)Mathf.RoundToInt(Mathf.Clamp01(cover[i]) * 255f);
        tex.SetPixelData(bytes, 0);
        tex.Apply(false);

        Shader.SetGlobalTexture(MaskTexID, tex);
        Shader.SetGlobalVector(MaskAreaID, new Vector4(area.x, area.y, 1f / area.width, 1f / area.height));
    }

    private void CollectColliders()
    {
        colliders.Clear();
        if (roots.Count > 0)
        {
            for (int r = 0; r < roots.Count; r++)
            {
                if (roots[r] == null) continue;
                var found = roots[r].GetComponentsInChildren<Collider>(false);
                for (int i = 0; i < found.Length; i++) TryAdd(found[i]);
            }
            return;
        }

        var scene = SceneManager.GetActiveScene();
        var all = FindObjectsByType<Collider>(FindObjectsSortMode.None);
        for (int i = 0; i < all.Length; i++)
        {
            if (all[i].gameObject.scene != scene) continue;
            TryAdd(all[i]);
        }
    }

    private void TryAdd(Collider c)
    {
        if (c == null || !c.enabled || c.isTrigger || !c.gameObject.activeInHierarchy) return;
        if (c is CharacterController) return;
        if (c.attachedRigidbody != null && !c.attachedRigidbody.isKinematic) return;
        if (c.GetComponentInParent<UnityEngine.AI.NavMeshAgent>() != null) return;
        for (int i = 0; i < ignore.Count; i++)
        {
            if (ignore[i] != null && c.transform.IsChildOf(ignore[i])) return;
        }
        Bounds b = c.bounds;
        if (b.min.y > groundHeight + contactTolerance) return;
        if (b.max.y <= groundHeight + 0.05f) return;
        if (colliders.Contains(c)) return;
        colliders.Add(c);
    }

    private void Rasterize(Collider c, int res, float cellX, float cellZ)
    {
        Bounds b = c.bounds;
        int x0 = Mathf.Max(0, Mathf.FloorToInt((b.min.x - feather - area.x) / cellX));
        int x1 = Mathf.Min(res - 1, Mathf.CeilToInt((b.max.x + feather - area.x) / cellX));
        int z0 = Mathf.Max(0, Mathf.FloorToInt((b.min.z - feather - area.y) / cellZ));
        int z1 = Mathf.Min(res - 1, Mathf.CeilToInt((b.max.z + feather - area.y) / cellZ));
        if (x0 > x1 || z0 > z1) return;

        var box = c as BoxCollider;
        var capsule = c as CapsuleCollider;
        var sphere = c as SphereCollider;

        Vector2 center = default;
        Vector2 half = default;
        float radius = 0f;
        float cos = 1f;
        float sin = 0f;
        int shape = 0;

        if (box != null)
        {
            Transform t = box.transform;
            Vector3 wc = t.TransformPoint(box.center);
            Vector3 s = t.lossyScale;
            center = new Vector2(wc.x, wc.z);
            half = new Vector2(Mathf.Abs(box.size.x * s.x), Mathf.Abs(box.size.z * s.z)) * 0.5f;
            float yaw = t.eulerAngles.y * Mathf.Deg2Rad;
            cos = Mathf.Cos(yaw);
            sin = Mathf.Sin(yaw);
            shape = 1;
        }
        else if (capsule != null)
        {
            Transform t = capsule.transform;
            Vector3 wc = t.TransformPoint(capsule.center);
            Vector3 s = t.lossyScale;
            float sx = Mathf.Abs(s.x);
            float sy = Mathf.Abs(s.y);
            float sz = Mathf.Abs(s.z);
            float scale = capsule.direction == 0 ? Mathf.Max(sy, sz) : capsule.direction == 1 ? Mathf.Max(sx, sz) : Mathf.Max(sx, sy);
            center = new Vector2(wc.x, wc.z);
            radius = capsule.radius * scale;
            shape = 2;
        }
        else if (sphere != null)
        {
            Transform t = sphere.transform;
            Vector3 wc = t.TransformPoint(sphere.center);
            Vector3 s = t.lossyScale;
            center = new Vector2(wc.x, wc.z);
            radius = sphere.radius * Mathf.Max(Mathf.Abs(s.x), Mathf.Abs(s.y), Mathf.Abs(s.z));
            shape = 2;
        }
        else if (b.size.y > tallMeshHeight)
        {
            center = new Vector2(c.transform.position.x, c.transform.position.z);
            radius = trunkRadius * Mathf.Max(Mathf.Abs(c.transform.lossyScale.x), Mathf.Abs(c.transform.lossyScale.z));
            shape = 2;
        }
        else
        {
            center = new Vector2(b.center.x, b.center.z);
            half = new Vector2(b.extents.x, b.extents.z);
            shape = 1;
        }

        for (int z = z0; z <= z1; z++)
        {
            float pz = area.y + (z + 0.5f) * cellZ;
            int row = z * res;
            for (int x = x0; x <= x1; x++)
            {
                float px = area.x + (x + 0.5f) * cellX;
                float dx = px - center.x;
                float dz = pz - center.y;
                float d;
                if (shape == 1)
                {
                    float lx = dx * cos - dz * sin;
                    float lz = dx * sin + dz * cos;
                    float qx = Mathf.Abs(lx) - half.x;
                    float qz = Mathf.Abs(lz) - half.y;
                    float ox = Mathf.Max(qx, 0f);
                    float oz = Mathf.Max(qz, 0f);
                    d = Mathf.Sqrt(ox * ox + oz * oz) + Mathf.Min(Mathf.Max(qx, qz), 0f);
                }
                else
                {
                    d = Mathf.Sqrt(dx * dx + dz * dz) - radius;
                }

                float v = d <= 0f ? 1f : 1f - d / feather;
                if (v > cover[row + x]) cover[row + x] = v;
            }
        }
    }

    private void RasterizeRect(Rect r, int res, float cellX, float cellZ)
    {
        int x0 = Mathf.Max(0, Mathf.FloorToInt((r.xMin - feather - area.x) / cellX));
        int x1 = Mathf.Min(res - 1, Mathf.CeilToInt((r.xMax + feather - area.x) / cellX));
        int z0 = Mathf.Max(0, Mathf.FloorToInt((r.yMin - feather - area.y) / cellZ));
        int z1 = Mathf.Min(res - 1, Mathf.CeilToInt((r.yMax + feather - area.y) / cellZ));
        for (int z = z0; z <= z1; z++)
        {
            float pz = area.y + (z + 0.5f) * cellZ;
            float qz = Mathf.Abs(pz - r.center.y) - r.height * 0.5f;
            int row = z * res;
            for (int x = x0; x <= x1; x++)
            {
                float px = area.x + (x + 0.5f) * cellX;
                float qx = Mathf.Abs(px - r.center.x) - r.width * 0.5f;
                float ox = Mathf.Max(qx, 0f);
                float oz = Mathf.Max(qz, 0f);
                float d = Mathf.Sqrt(ox * ox + oz * oz) + Mathf.Min(Mathf.Max(qx, qz), 0f);
                float v = Mathf.Clamp01(-d / rectFeather);
                if (v > cover[row + x]) cover[row + x] = v;
            }
        }
    }
}
}
