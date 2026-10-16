using System.Collections.Generic;
using System.IO;
using UnityEditor;
using Synty.SidekickCharacters.API;
using Synty.SidekickCharacters.Database;
using Synty.SidekickCharacters.Database.DTO;
using UnityEngine;

namespace MoriMonchiSimulator
{
public static class HumanBodyAssembler
{
    private const string ColorMapPath = "Assets/Synty/SidekickCharacters/Characters/Starter/Starter_01/Textures/T_Starter_01ColorMap.png";
    private const string MeshDir = "Assets/RunRunSimulator/Resources/Models/Humans";
    private const string Human = "SK_HUMN_BASE_";
    private const string ControllerNpc = AnimDir + "/HumanNpcSK.controller";
    private const string ControllerNpcFemn = AnimDir + "/HumanNpcSK_Femn.overrideController";
    private const string TemplatePath = "Assets/RunRunSimulator/Resources/Materials/Brawl/Scarecrow/SC_Burlap.mat";
    private const string TexDir = "Assets/RunRunSimulator/Resources/Textures/Humans";
    private const string MatDir = "Assets/RunRunSimulator/Resources/Materials/Humans";
    private const string BodyDir = "Assets/RunRunSimulator/Resources/Prefabs/Humans/Bodies";
    private const string PrefabDir = "Assets/RunRunSimulator/Resources/Prefabs/Humans";
    private const string CatalogDir = "Assets/RunRunSimulator/Resources/Data/Humans";
    private const string AnimDir = "Assets/RunRunSimulator/Resources/Animations/Humans";
    private const float OutlineWidth = 0f;

    private static readonly string[] SkinPresets =
        { "Human - Light Tan", "Human - Tan", "Human - Dark Tan", "Human - Light Brown", "Human - Medium Brown", "Human - Dark Brown" };

    private static readonly string[] RoleHumanSkins =
        { "Human - Light Tan", "Human - Tan", "Human - Light Brown", "Human - Dark Brown" };

    private const string Civilian = "SK_SCFI_CIVL_09_";

    private static Dictionary<string, string> partIndex;
    private static bool controllerErrorLogged;

    private static readonly string[] PlayerLegs = { "17HIPS", "18LEGL", "19LEGR", "20FOTL", "21FOTR" };

    private static readonly string[] BareArms = { "11AUPL", "12AUPR", "13ALWL", "14ALWR", "15HNDL", "16HNDR" };

    [MenuItem("RunRunSimulator/Humans/Build Bodies")]
    public static void BuildBodies()
    {
        EnsureFolder(TexDir);
        EnsureFolder(MatDir);
        EnsureFolder(BodyDir);
        EnsureFolder(CatalogDir);
        EnsureFolder(MeshDir);

        partIndex = HumanRoleRecipes.BuildPartIndex();
        controllerErrorLogged = false;

        var materials = BuildPresetMaterials();
        var runtime = new SidekickRuntime(Resources.Load<GameObject>("Meshes/SK_BaseModel"), materials[0]);

        SetShape(runtime, 0f, 0f, 0f);
        var arms = BuildArmsPrefab(runtime, materials[0]);
        BuildPlayerBodyPrefab(runtime, materials[0]);

        var roles = HumanRoleRecipes.Load();
        var db = new DatabaseManager();
        db.GetDbConnection(true);
        var template = AssetDatabase.LoadAssetAtPath<Material>(TemplatePath);
        var entries = new List<HumanBodyCatalogSO.Entry>();
        int built = 0, neighbors = 0, missing = 0;

        foreach (var role in roles)
        {
            var variants = BuildRoleMaterials(db, template, role);
            if (variants == null) { missing++; continue; }
            var body = BuildRoleBody(runtime, role, variants[0]);
            if (body == null) { missing++; continue; }
            built++;
            if (string.IsNullOrEmpty(role.Archetype)) { neighbors++; continue; }
            var archetype = FindArchetype(role.Archetype);
            if (archetype == null)
            {
                Debug.LogError("[HumanBodyAssembler] Arquetipo no encontrado: " + role.Archetype + " (rol " + role.Name + ")");
                missing++;
                continue;
            }
            entries.Add(new HumanBodyCatalogSO.Entry { Archetype = archetype, Body = body, Skins = variants });
        }

        UpdateCatalog(entries);

        AssetDatabase.SaveAssets();
        AssetDatabase.ImportAsset(MeshDir, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ImportRecursive);
        AssetDatabase.ImportAsset(PrefabDir, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ImportRecursive);
        AssetDatabase.Refresh();
        Debug.Log("[HumanBodyAssembler] Roles=" + built + " Vecinos=" + neighbors + " Catalogo=" + entries.Count + " Faltantes=" + missing + " FPArms=" + (arms != null));
    }

    private static void SetShape(SidekickRuntime runtime, float bodyType, float bodySize, float muscle)
    {
        runtime.BodyTypeBlendValue = bodyType;
        runtime.MusclesBlendValue = muscle;
        runtime.BodySizeHeavyBlendValue = bodySize > 0f ? bodySize : 0f;
        runtime.BodySizeSkinnyBlendValue = bodySize < 0f ? -bodySize : 0f;
    }

    private static List<Material> BuildRoleMaterials(DatabaseManager db, Material template, HumanRoleRecipe role)
    {
        var colorMap = AssetDatabase.LoadAssetAtPath<Texture2D>(HumanRoleRecipes.ColorMapTexturePath(role.ColorMap));
        if (colorMap == null)
        {
            Debug.LogError("[HumanBodyAssembler] ColorMap no encontrado para rol " + role.Name + ": " + role.ColorMap);
            return null;
        }

        var source = ReadPixels(colorMap);
        var skins = role.Species == "Elf" ? new string[] { null } : RoleHumanSkins;
        var result = new List<Material>();
        for (int i = 0; i < skins.Length; i++)
        {
            var tex = new Texture2D(colorMap.width, colorMap.height, TextureFormat.RGBA32, false, false);
            tex.SetPixels(source);
            if (skins[i] != null) ApplyPreset(db, tex, skins[i]);
            tex.Apply();
            var suffix = "Role_" + role.Name + "_" + i;
            var saved = WriteTexture(TexDir + "/T_" + suffix + ".png", tex);
            result.Add(SaveMaterial(MatDir + "/M_" + suffix + ".mat", template, saved));
            Object.DestroyImmediate(tex);
        }
        return result;
    }

    private static CustomerArchetypeSO FindArchetype(string displayName)
    {
        foreach (var guid in AssetDatabase.FindAssets("t:CustomerArchetypeSO"))
        {
            var so = AssetDatabase.LoadAssetAtPath<CustomerArchetypeSO>(AssetDatabase.GUIDToAssetPath(guid));
            if (so != null && so.DisplayName == displayName) return so;
        }
        return null;
    }

    private static GameObject BuildRoleBody(SidekickRuntime runtime, HumanRoleRecipe role, Material mat)
    {
        SetShape(runtime, role.BodyType, role.BodySize, role.Muscle);
        var go = Combine(runtime, role.Name, role.Parts);
        if (go == null) return null;

        ApplyMaterial(go, mat);
        var controllerPath = role.BodyType > 0f ? ControllerNpcFemn : ControllerNpc;
        ConfigureAnimator(go, LoadController(controllerPath));
        return SavePrefab(go, BodyDir + "/Human_" + role.Name + ".prefab");
    }

    private static RuntimeAnimatorController LoadController(string path)
    {
        var controller = AssetDatabase.LoadAssetAtPath<RuntimeAnimatorController>(path);
        if (controller == null && !controllerErrorLogged)
        {
            controllerErrorLogged = true;
            Debug.LogError("[HumanBodyAssembler] Controller no encontrado: " + path);
        }
        return controller;
    }

    private static List<Material> BuildPresetMaterials()
    {
        var template = AssetDatabase.LoadAssetAtPath<Material>(TemplatePath);
        var colorMap = AssetDatabase.LoadAssetAtPath<Texture2D>(ColorMapPath);
        var source = ReadPixels(colorMap);
        var db = new DatabaseManager();
        db.GetDbConnection(true);
        var result = new List<Material>();

        for (int i = 0; i < SkinPresets.Length; i++)
        {
            var name = "Sk" + (i + 1).ToString("00");
            var tex = new Texture2D(colorMap.width, colorMap.height, TextureFormat.RGBA32, false, false);
            tex.SetPixels(source);
            var knight = "Fantasy Knights " + (i + 1).ToString("00");
            ApplyPreset(db, tex, SkinPresets[i]);
            foreach (var group in new[] { ColorGroupOutfits, ColorGroupAttachments, ColorGroupMaterials })
                ApplyPreset(db, tex, knight, group);
            tex.Apply();
            result.Add(SaveMaterial(MatDir + "/M_Human_" + name + ".mat", template,WriteTexture(TexDir + "/T_Human_" + name + ".png", tex)));
            Object.DestroyImmediate(tex);
        }
        return result;
    }

    private const string ColorGroupOutfits = "Outfits";
    private const string ColorGroupAttachments = "Attachments";
    private const string ColorGroupMaterials = "Materials";

    private static void ApplyPreset(DatabaseManager db, Texture2D tex, string presetName, string group = null)
    {
        foreach (var preset in SidekickColorPreset.GetAll(db))
        {
            if (preset.Name != presetName || preset.PtrSpecies != 1) continue;
            if (group != null && preset.ColorGroup.ToString() != group) continue;
            foreach (var row in SidekickColorPresetRow.GetAllByPreset(db, preset))
            {
                var prop = SidekickColorProperty.GetByID(db, row.PtrColorProperty);
                if (prop == null) continue;
                int u = prop.U * 2, v = prop.V * 2;
                if (u + 1 >= tex.width || v + 1 >= tex.height) continue;
                var c = row.NiceColor;
                tex.SetPixel(u, v, c); tex.SetPixel(u + 1, v, c); tex.SetPixel(u, v + 1, c); tex.SetPixel(u + 1, v + 1, c);
            }
        }
    }

    private static Texture2D WriteTexture(string path, Texture2D tex)
    {
        File.WriteAllBytes(path, tex.EncodeToPNG());
        AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
        var importer = (TextureImporter)AssetImporter.GetAtPath(path);
        importer.sRGBTexture = true;
        importer.mipmapEnabled = false;
        importer.filterMode = FilterMode.Point;
        importer.textureCompression = TextureImporterCompression.Uncompressed;
        importer.wrapMode = TextureWrapMode.Clamp;
        importer.SaveAndReimport();
        return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
    }

    private static Color[] ReadPixels(Texture2D src)
    {
        var rt = RenderTexture.GetTemporary(src.width, src.height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
        var prev = RenderTexture.active;
        Graphics.Blit(src, rt);
        RenderTexture.active = rt;
        var tmp = new Texture2D(src.width, src.height, TextureFormat.RGBA32, false, false);
        tmp.ReadPixels(new Rect(0, 0, src.width, src.height), 0, 0);
        tmp.Apply();
        RenderTexture.active = prev;
        RenderTexture.ReleaseTemporary(rt);
        var px = tmp.GetPixels();
        Object.DestroyImmediate(tmp);
        return px;
    }

    private static Material SaveMaterial(string path, Material template, Texture2D tex)
    {
        var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (mat == null)
        {
            mat = new Material(template);
            AssetDatabase.CreateAsset(mat, path);
        }
        else
        {
            mat.shader = template.shader;
            mat.CopyPropertiesFromMaterial(template);
        }

        mat.SetTexture("_MainTex", tex);
        mat.SetTexture("_1st_ShadeMap", tex);
        mat.SetTexture("_2nd_ShadeMap", tex);
        mat.SetColor("_BaseColor", Color.white);
        mat.SetColor("_1st_ShadeColor", new Color(0.8f, 0.74f, 0.82f, 1f));
        mat.SetColor("_2nd_ShadeColor", new Color(0.66f, 0.58f, 0.7f, 1f));
        mat.SetColor("_Outline_Color", new Color(0.18f, 0.13f, 0.16f, 1f));
        mat.SetFloat("_Outline_Width", OutlineWidth);
        mat.SetFloat("_RimLight", 0f);
        mat.SetFloat("_Set_SystemShadowsToBase", 0f);
        EditorUtility.SetDirty(mat);
        return mat;
    }

    private static GameObject BuildArmsPrefab(SidekickRuntime runtime, Material mat)
    {
        var names = new List<string>();
        foreach (var t in BareArms) names.Add(HumanPart(1, t));

        var go = Combine(runtime, "FPArms", names);
        if (go == null) return null;

        ApplyMaterial(go, mat);
        foreach (var smr in go.GetComponentsInChildren<SkinnedMeshRenderer>(true))
        {
            smr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            smr.receiveShadows = false;
            smr.updateWhenOffscreen = true;
        }
        var an = ConfigureAnimator(go, LoadController(AnimDir + "/FPArms.controller"));
        an.cullingMode = AnimatorCullingMode.AlwaysAnimate;
        go.AddComponent<PlayerAnimator>();
        EnsureFolder(PrefabDir);
        return SavePrefab(go, PrefabDir + "/FPArms.prefab");
    }

    private static GameObject BuildPlayerBodyPrefab(SidekickRuntime runtime, Material mat)
    {
        var names = new List<string>
        {
            HumanPart(1, "01HEAD"), HumanPart(1, "07EARL"), HumanPart(1, "08EARR"), HumanPart(1, "35NOSE"), HumanPart(2, "02HAIR"),
            HumanPart(1, "10TORS"),
        };
        foreach (var t in BareArms) names.Add(HumanPart(1, t));
        foreach (var t in PlayerLegs) names.Add(Civilian + t + "_HU01");

        var go = Combine(runtime, "PlayerBody", names);
        if (go == null) return null;

        ApplyMaterial(go, mat);
        foreach (var smr in go.GetComponentsInChildren<SkinnedMeshRenderer>(true))
            smr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.ShadowsOnly;

        var viewNames = new List<string> { HumanPart(1, "10TORS") };
        foreach (var t in BareArms) viewNames.Add(HumanPart(1, t));
        foreach (var t in PlayerLegs) viewNames.Add(Civilian + t + "_HU01");
        var view = Combine(runtime, "PlayerBodyView", viewNames);
        if (view != null)
        {
            ApplyMaterial(view, mat);
            AttachSkin(go, view.GetComponentInChildren<SkinnedMeshRenderer>(true));
            Object.DestroyImmediate(view);
        }

        var an = ConfigureAnimator(go, LoadController(AnimDir + "/PlayerBody.controller"));
        an.cullingMode = AnimatorCullingMode.AlwaysAnimate;
        return SavePrefab(go, PrefabDir + "/PlayerBody.prefab");
    }

    private static void AttachSkin(GameObject owner, SkinnedMeshRenderer skin)
    {
        var map = new Dictionary<string, Transform>();
        foreach (var t in owner.GetComponentsInChildren<Transform>(true))
            if (!map.ContainsKey(t.name)) map[t.name] = t;

        var bones = skin.bones;
        for (int i = 0; i < bones.Length; i++)
        {
            if (bones[i] == null) continue;
            if (map.TryGetValue(bones[i].name, out var match)) bones[i] = match;
            else Debug.LogError("[HumanBodyAssembler] Hueso no encontrado en PlayerBody: " + bones[i].name);
        }

        var root = skin.rootBone;
        if (root != null)
        {
            if (map.TryGetValue(root.name, out var rootMatch)) root = rootMatch;
            else Debug.LogError("[HumanBodyAssembler] Root bone no encontrado en PlayerBody: " + root.name);
        }

        skin.transform.SetParent(owner.transform, false);
        skin.name = "BodyView";
        skin.bones = bones;
        skin.rootBone = root;
        skin.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        skin.receiveShadows = true;
        skin.updateWhenOffscreen = true;
    }

    private static string HumanPart(int variant, string type) => Human + variant.ToString("00") + "_" + type + "_HU01";

    private static GameObject Combine(SidekickRuntime runtime, string name, List<string> partNames)
    {
        var temps = new List<GameObject>();
        var parts = new List<SkinnedMeshRenderer>();
        foreach (var n in partNames)
        {
            GameObject fbx = null;
            if (partIndex.TryGetValue(n, out var fbxPath)) fbx = AssetDatabase.LoadAssetAtPath<GameObject>(fbxPath);
            if (fbx == null)
            {
                Debug.LogError("[HumanBodyAssembler] Parte no encontrada: " + n);
                foreach (var t in temps) Object.DestroyImmediate(t);
                return null;
            }
            var inst = Object.Instantiate(fbx);
            inst.name = fbx.name;
            temps.Add(inst);
            var smr = inst.GetComponentInChildren<SkinnedMeshRenderer>();
            smr.name = fbx.name;
            parts.Add(smr);
        }

        var go = runtime.CreateCharacter(name, parts, true, true, null, false, false);
        foreach (var t in temps) Object.DestroyImmediate(t);

        foreach (var smr in go.GetComponentsInChildren<SkinnedMeshRenderer>(true))
        {
            var meshPath = MeshDir + "/Mesh_" + name + ".asset";
            var built = smr.sharedMesh;
            built.name = "Mesh_" + name;
            var existing = AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);
            if (existing == null)
            {
                AssetDatabase.CreateAsset(built, meshPath);
                continue;
            }
            EditorUtility.CopySerialized(built, existing);
            EditorUtility.SetDirty(existing);
            smr.sharedMesh = existing;
        }
        return go;
    }

    private static void ApplyMaterial(GameObject go, Material mat)
    {
        foreach (var smr in go.GetComponentsInChildren<SkinnedMeshRenderer>(true))
        {
            var slots = new Material[Mathf.Max(1, smr.sharedMesh.subMeshCount)];
            for (int i = 0; i < slots.Length; i++) slots[i] = mat;
            smr.sharedMaterials = slots;
            smr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.On;
            smr.receiveShadows = true;
        }
    }

    private static Animator ConfigureAnimator(GameObject go, RuntimeAnimatorController controller)
    {
        var an = go.GetComponent<Animator>();
        if (an == null) an = go.AddComponent<Animator>();
        an.applyRootMotion = false;
        an.runtimeAnimatorController = controller;
        return an;
    }

    private static GameObject SavePrefab(GameObject go, string path)
    {
        var prefab = PrefabUtility.SaveAsPrefabAsset(go, path);
        Object.DestroyImmediate(go);
        return prefab;
    }

    private static void UpdateCatalog(List<HumanBodyCatalogSO.Entry> entries)
    {
        var path = CatalogDir + "/HumanBodyCatalog.asset";
        var catalog = AssetDatabase.LoadAssetAtPath<HumanBodyCatalogSO>(path);
        if (catalog == null)
        {
            catalog = ScriptableObject.CreateInstance<HumanBodyCatalogSO>();
            AssetDatabase.CreateAsset(catalog, path);
        }

        catalog.Bodies = entries;

        EditorUtility.SetDirty(catalog);
    }

    private static void EnsureFolder(string path)
    {
        if (AssetDatabase.IsValidFolder(path)) return;
        var parent = Path.GetDirectoryName(path).Replace('\\', '/');
        EnsureFolder(parent);
        AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
    }
}
}
