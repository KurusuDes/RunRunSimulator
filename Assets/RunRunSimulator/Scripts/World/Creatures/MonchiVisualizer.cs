using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{
public class MonchiVisualizer : MonoBehaviour
{
    [Required, SerializeField] private Transform modelRoot;

    private static readonly int RimColorId = Shader.PropertyToID("_RimLightColor");
    private static readonly int RimPowerId = Shader.PropertyToID("_RimLight_Power");
    private static readonly int RimInsideMaskId = Shader.PropertyToID("_RimLight_InsideMask");
    private static readonly int RimLightColorSwitchId = Shader.PropertyToID("_Is_LightColor_RimLight");

    private MonchiVisualBankSO bank;
    private FurTypeDatabaseSO furDatabase;
    private GameObject bodyInstance;
    private Animator animator;
    private SkinnedMeshRenderer faceRenderer;
    private readonly List<Renderer> tintRenderers = new();
    private CreatureDNA currentDna;
    private MonchiForm assembledForm;
    private MonchiMood currentMood = MonchiMood.Neutral;
    private bool rimOverride;
    private Color rimOverrideColor;
    private float rimOverridePower;
    private float rimOverrideInsideMask;

    public Animator Animator => animator;
    public Transform ModelRoot => Root;

    private Transform Root => modelRoot != null ? modelRoot : transform;

    public void SetBank(MonchiVisualBankSO visualBank)
    {
        bank = visualBank;
    }

    public void SetFurDatabase(FurTypeDatabaseSO furDb)
    {
        furDatabase = furDb;
    }

    public void Assemble(CreatureDNA dna)
    {
        for (int i = Root.childCount - 1; i >= 0; i--)
        {
            var child = Root.GetChild(i).gameObject;
            child.SetActive(false);
            Object.Destroy(child);
        }

        bodyInstance = null;
        animator = null;
        faceRenderer = null;
        tintRenderers.Clear();
        assembledForm = dna.Form;

        if (bank == null)
        {
            Debug.LogWarning("[MonchiVisualizer] No MonchiVisualBankSO — model will be empty.");
            return;
        }

        var controller = InstantiateBody(dna);
        if (bodyInstance == null)
            return;

        foreach (var childTransform in bodyInstance.GetComponentsInChildren<Transform>(true))
            childTransform.gameObject.layer = Root.gameObject.layer;

        animator = bodyInstance.GetComponent<Animator>();
        if (animator == null)
            animator = bodyInstance.AddComponent<Animator>();
        if (controller != null)
            animator.runtimeAnimatorController = controller;

        if (dna.Form != MonchiForm.Adult)
        {
            foreach (var renderer in bodyInstance.GetComponentsInChildren<Renderer>(false))
            {
                if (renderer.gameObject.name == "Face" && renderer is SkinnedMeshRenderer skinned)
                    faceRenderer = skinned;
                else
                    tintRenderers.Add(renderer);
            }
        }
        else
        {
            GraftPart(dna.HornID, "Horn");
            GraftPart(dna.BackID, "Back");
            GraftPart(dna.WingID, "Wing");

            foreach (var renderer in bodyInstance.GetComponentsInChildren<SkinnedMeshRenderer>(false))
            {
                if (renderer.gameObject.name == "Face")
                    faceRenderer = renderer;
                else
                    tintRenderers.Add(renderer);
            }
        }

        currentDna = dna;
        ApplyLook();
        SetMood(currentMood);
    }

    private RuntimeAnimatorController InstantiateBody(CreatureDNA dna)
    {
        if (dna.Form == MonchiForm.Slime)
        {
            bodyInstance = MonchiSlimeBody.Build(dna, bank, Root);
            if (bodyInstance == null)
            {
                Debug.LogWarning($"[MonchiVisualizer] No slime body for BodyShapeID '{dna.BodyShapeID}'.");
                return null;
            }

            return bank.SlimeAnimatorController;
        }

        if (dna.Form == MonchiForm.Egg)
        {
            bodyInstance = MonchiEggBody.Build(dna, bank, Root);
            if (bodyInstance == null)
            {
                Debug.LogWarning($"[MonchiVisualizer] No egg body for BodyShapeID '{dna.BodyShapeID}'.");
                return null;
            }

            return bank.EggAnimatorController;
        }

        var prefab = bank.GetBody(dna.BodyShapeID);
        if (prefab == null)
        {
            Debug.LogWarning($"[MonchiVisualizer] No body prefab for BodyShapeID '{dna.BodyShapeID}'.");
            return null;
        }

        bodyInstance = Object.Instantiate(prefab, Root);
        bodyInstance.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
        return bank.AnimatorController;
    }

    private void GraftPart(string partId, string prefix)
    {
        var partPrefab = bank.GetPartMesh(partId);
        if (partPrefab == null)
            return;

        foreach (var renderer in bodyInstance.GetComponentsInChildren<SkinnedMeshRenderer>(true))
        {
            if (renderer.gameObject.name.StartsWith(prefix))
                renderer.gameObject.SetActive(false);
        }

        var grafted = new List<SkinnedMeshRenderer>();
        MonchiPartGrafter.Graft(partPrefab, bodyInstance, grafted);
    }

    public void RefreshLook(CreatureDNA dna)
    {
        currentDna = dna;
        if (bodyInstance == null || dna.Form != assembledForm)
        {
            Assemble(dna);
            return;
        }

        ApplyLook();
        SetMood(currentMood);
    }

    public void SetRimOverride(Color color, float power, float insideMask)
    {
        rimOverride = true;
        rimOverrideColor = color;
        rimOverridePower = power;
        rimOverrideInsideMask = insideMask;
        ApplyLook();
    }

    public void ClearRimOverride()
    {
        if (!rimOverride) return;
        rimOverride = false;
        ApplyLook();
    }

    public void SetMood(MonchiMood mood)
    {
        currentMood = mood;
        if (faceRenderer == null || bank?.MoodSet == null) return;

        var face = bank.MoodSet.GetFace(mood);
        if (face != null)
            faceRenderer.sharedMaterial = face;
    }

    private void ApplyLook()
    {
        if (currentDna == null || tintRenderers.Count == 0) return;

        if (currentDna.IsShiny)
        {
            var gem = bank != null ? bank.GetGem(currentDna.UniqueID) : null;
            if (gem != null)
            {
                foreach (var renderer in tintRenderers)
                {
                    renderer.sharedMaterial = gem;
                    renderer.SetPropertyBlock(new MaterialPropertyBlock());
                }
                return;
            }
        }

        var furMat = furDatabase != null ? furDatabase.GetMaterial(currentDna.FurType) : null;
        ColorGenetics.BuildHarmony(currentDna.BaseColor, out var wing, out var accent);

        foreach (var renderer in tintRenderers)
        {
            var partName = renderer.gameObject.name;
            if (partName.StartsWith("Egg_"))
                partName = partName.Substring(4);
            if (furMat != null)
                renderer.sharedMaterial = furMat;

            var color = MonchiTint.ColorFor(partName, currentDna, wing, accent);
            Tint(renderer, color);
        }
    }

    private void Tint(Renderer renderer, Color color)
    {
        var mpb = new MaterialPropertyBlock();
        MonchiTint.Fill(mpb, color);
        if (rimOverride)
        {
            mpb.SetColor(RimColorId, rimOverrideColor);
            mpb.SetFloat(RimPowerId, rimOverridePower);
            mpb.SetFloat(RimInsideMaskId, rimOverrideInsideMask);
            mpb.SetFloat(RimLightColorSwitchId, 0f);
        }
        renderer.SetPropertyBlock(mpb);
    }
}
}
