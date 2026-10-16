using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{

[ExecuteAlways]
public class ShopTrampleMap : MonoBehaviour
{
    private struct StampRequest
    {
        public Vector3 World;
        public float Radius;
        public float Strength;
        public float TrailGain;
    }

    [Title("Shader")]
    [SerializeField] private Shader trampleShader;

    [Title("Area")]
    [SerializeField] private Rect area = new Rect(-80f, -30f, 110f, 105f);

    [Title("Resolucion")]
    [SerializeField, Min(64)] private int resolution = 1024;

    [Title("Decaimiento")]
    [SerializeField] private float freshHalfLife = 0.35f;
    [SerializeField] private float trailHalfLife = 6f;

    [Title("Rastro")]
    [SerializeField] private float trailGain = 0.6f;
    [SerializeField] private float stampRate = 8f;

    private static readonly int AreaID = Shader.PropertyToID("_ArenaTrampleArea");
    private static readonly int TrampleTexID = Shader.PropertyToID("_ArenaTrampleTex");
    private static readonly int FreshDecayID = Shader.PropertyToID("_FreshDecay");
    private static readonly int TrailDecayID = Shader.PropertyToID("_TrailDecay");

    private RenderTexture current;
    private RenderTexture scratch;
    private Material decayMaterial;
    private Material stampMaterial;

    private float areaOriginX;
    private float areaOriginZ;
    private float areaInvSize;

    private readonly List<StampRequest> queuedStamps = new List<StampRequest>();

    private void OnEnable()
    {
        if (trampleShader == null) return;

        current = CreateRenderTexture();
        scratch = CreateRenderTexture();
        ClearBlack(current);
        ClearBlack(scratch);

        decayMaterial = new Material(trampleShader) { hideFlags = HideFlags.DontSave };
        stampMaterial = new Material(trampleShader) { hideFlags = HideFlags.DontSave };

        RecalculateArea();
    }

    private void OnDisable()
    {
        queuedStamps.Clear();

        ReleaseRT(ref current);
        ReleaseRT(ref scratch);

        if (decayMaterial != null) { DestroyImmediate(decayMaterial); decayMaterial = null; }
        if (stampMaterial != null) { DestroyImmediate(stampMaterial); stampMaterial = null; }

        Shader.SetGlobalTexture(TrampleTexID, Texture2D.blackTexture);
    }

    private void LateUpdate()
    {
        if (current == null) return;

        if (!Application.isPlaying)
        {
            Shader.SetGlobalTexture(TrampleTexID, Texture2D.blackTexture);
            return;
        }

        ApplyDecay(Time.deltaTime);
        CollectStamps();
        DrawStamps();

        Shader.SetGlobalTexture(TrampleTexID, current);
    }

    private void RecalculateArea()
    {
        float sizeX = area.width;
        float sizeZ = area.height;
        float size = Mathf.Max(sizeX, sizeZ);

        areaInvSize = size > 0f ? 1f / size : 0f;
        areaOriginX = area.xMin - (size - sizeX) * 0.5f;
        areaOriginZ = area.yMin - (size - sizeZ) * 0.5f;

        Shader.SetGlobalVector(AreaID, new Vector4(areaOriginX, areaOriginZ, areaInvSize, areaInvSize));
        Shader.SetGlobalTexture(TrampleTexID, current);
    }

    private void ApplyDecay(float dt)
    {
        decayMaterial.SetFloat(FreshDecayID, Mathf.Exp(-dt * Mathf.Log(2f) / freshHalfLife));
        decayMaterial.SetFloat(TrailDecayID, Mathf.Exp(-dt * Mathf.Log(2f) / trailHalfLife));

        Graphics.Blit(current, scratch, decayMaterial, 0);

        var swap = current;
        current = scratch;
        scratch = swap;
    }

    private void CollectStamps()
    {
        float pressure = Mathf.Min(1f, stampRate * Time.deltaTime);
        var trampers = GrassTrampler.All;

        for (int i = 0; i < trampers.Count; i++)
        {
            var trampler = trampers[i];
            queuedStamps.Add(new StampRequest
            {
                World = trampler.Position,
                Radius = trampler.Radius,
                Strength = pressure,
                TrailGain = trailGain * pressure * trampler.Trail
            });
        }
    }

    private void DrawStamps()
    {
        if (queuedStamps.Count == 0) return;

        Graphics.SetRenderTarget(current);
        stampMaterial.SetPass(1);

        GL.PushMatrix();
        GL.LoadOrtho();
        GL.Begin(GL.QUADS);

        for (int i = 0; i < queuedStamps.Count; i++)
        {
            var stamp = queuedStamps[i];

            float u = (stamp.World.x - areaOriginX) * areaInvSize;
            float v = (stamp.World.z - areaOriginZ) * areaInvSize;
            float ru = stamp.Radius * areaInvSize;

            GL.Color(new Color(stamp.Strength, stamp.TrailGain, 0f, 0f));

            GL.TexCoord2(0f, 0f);
            GL.Vertex3(u - ru, v - ru, 0f);
            GL.TexCoord2(1f, 0f);
            GL.Vertex3(u + ru, v - ru, 0f);
            GL.TexCoord2(1f, 1f);
            GL.Vertex3(u + ru, v + ru, 0f);
            GL.TexCoord2(0f, 1f);
            GL.Vertex3(u - ru, v + ru, 0f);
        }

        GL.End();
        GL.PopMatrix();
        Graphics.SetRenderTarget(null);

        queuedStamps.Clear();
    }

    private RenderTexture CreateRenderTexture()
    {
        var rt = new RenderTexture(resolution, resolution, 0, RenderTextureFormat.ARGBHalf)
        {
            filterMode = FilterMode.Bilinear,
            wrapMode = TextureWrapMode.Clamp,
            useMipMap = false,
            autoGenerateMips = false,
            hideFlags = HideFlags.DontSave
        };
        rt.Create();
        return rt;
    }

    private static void ClearBlack(RenderTexture rt)
    {
        var active = RenderTexture.active;
        RenderTexture.active = rt;
        GL.Clear(true, true, Color.clear);
        RenderTexture.active = active;
    }

    private static void ReleaseRT(ref RenderTexture rt)
    {
        if (rt == null) return;
        rt.Release();
        DestroyImmediate(rt);
        rt = null;
    }
}
}
