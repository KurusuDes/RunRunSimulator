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
    private struct Recipe
    {
        public string Name;
        public int Head;
        public int Nose;
        public int Hair;
        public int Beard;
        public string[] Attachments;
    }

    private const string SynRoot = "Assets/Synty/SidekickCharacters/Resources/Meshes";
    private const string ColorMapPath = "Assets/Synty/SidekickCharacters/Characters/Starter/Starter_01/Textures/T_Starter_01ColorMap.png";
    private const string MeshDir = "Assets/RunRunSimulator/Resources/Models/Humans";
    private const string Knight = "Outfits/Starter/SK_FANT_KNGT_17_";
    private const string Human = "Species/Humans/SK_HUMN_BASE_";
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

    private static readonly Recipe[] Recipes =
    {
        new Recipe { Name = "Knight_01", Head = 1, Nose = 1, Hair = 4, Beard = 10, Attachments = new[] { "29ASHL", "30ASHR", "25AHPF", "33AKNL", "34AKNR" } },
        new Recipe { Name = "Knight_02", Head = 1, Nose = 3, Hair = 0, Beard = 8, Attachments = new[] { "22AHED", "29ASHL", "30ASHR", "26AHPB" } },
        new Recipe { Name = "Knight_03", Head = 2, Nose = 7, Hair = 6, Beard = 0, Attachments = new[] { "25AHPF" } },
        new Recipe { Name = "Knight_04", Head = 1, Nose = 5, Hair = 8, Beard = 1, Attachments = new[] { "24ABAC", "29ASHL", "30ASHR", "31AEBL", "32AEBR" } },
        new Recipe { Name = "Knight_05", Head = 2, Nose = 11, Hair = 0, Beard = 0, Attachments = new[] { "22AHED", "29ASHL", "30ASHR", "27AHPL", "28AHPR", "33AKNL", "34AKNR" } },
    };

    private static readonly string[] KnightBody =
        { "10TORS", "11AUPL", "12AUPR", "13ALWL", "14ALWR", "15HNDL", "16HNDR", "17HIPS", "18LEGL", "19LEGR", "20FOTL", "21FOTR" };

    private const string Civilian = "Outfits/Starter/SK_SCFI_CIVL_09_";

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

        var materials = BuildPresetMaterials();
        var runtime = new SidekickRuntime(Resources.Load<GameObject>("Meshes/SK_BaseModel"), materials[0]);
        var bodies = new List<GameObject>();

        foreach (var recipe in Recipes)
        {
            var body = BuildBodyPrefab(runtime, recipe, materials[0]);
            if (body != null) bodies.Add(body);
        }

        var arms = BuildArmsPrefab(runtime, materials[0]);
        BuildPlayerBodyPrefab(runtime, materials[0]);
        UpdateCatalog(bodies, materials);

        AssetDatabase.SaveAssets();
        AssetDatabase.ImportAsset(MeshDir, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ImportRecursive);
        AssetDatabase.ImportAsset(PrefabDir, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ImportRecursive);
        AssetDatabase.Refresh();
        Debug.Log("[HumanBodyAssembler] Materiales=" + materials.Count + " Cuerpos=" + bodies.Count + " FPArms=" + (arms != null) + " Catalogo=" + CatalogDir + "/HumanBodyCatalog.asset");
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
            result.Add(SaveMaterial(name, template, WriteTexture(TexDir + "/T_Human_" + name + ".png", tex)));
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

    private static Material SaveMaterial(string name, Material template, Texture2D tex)
    {
        var path = MatDir + "/M_Human_" + name + ".mat";
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

    private static GameObject BuildBodyPrefab(SidekickRuntime runtime, Recipe r, Material mat)
    {
        var names = new List<string>
        {
            HumanPart(r.Head, "01HEAD"), HumanPart(1, "03EBRL"), HumanPart(1, "04EBRR"), HumanPart(1, "05EYEL"), HumanPart(1, "06EYER"),
            HumanPart(1, "07EARL"), HumanPart(1, "08EARR"), HumanPart(r.Nose, "35NOSE"), HumanPart(1, "36TETH"), HumanPart(1, "37TONG"),
        };
        if (r.Hair > 0) names.Add(HumanPart(r.Hair, "02HAIR"));
        if (r.Beard > 0) names.Add(HumanPart(r.Beard, "09FCHR"));
        foreach (var t in KnightBody) names.Add(Knight + t + "_HU01");
        foreach (var t in r.Attachments) names.Add(Knight + t + "_HU01");

        var go = Combine(runtime, r.Name, names);
        if (go == null) return null;

        ApplyMaterial(go, mat);
        ConfigureAnimator(go, AnimDir + "/HumanNpc.controller");
        return SavePrefab(go, BodyDir + "/Human_" + r.Name + ".prefab");
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
        var an = ConfigureAnimator(go, AnimDir + "/FPArms.controller");
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
        var an = ConfigureAnimator(go, AnimDir + "/HumanNpc.controller");
        an.cullingMode = AnimatorCullingMode.AlwaysAnimate;
        return SavePrefab(go, PrefabDir + "/PlayerBody.prefab");
    }

    private static string HumanPart(int variant, string type) => Human + variant.ToString("00") + "_" + type + "_HU01";

    private static GameObject Combine(SidekickRuntime runtime, string name, List<string> partNames)
    {
        var temps = new List<GameObject>();
        var parts = new List<SkinnedMeshRenderer>();
        foreach (var n in partNames)
        {
            var fbx = AssetDatabase.LoadAssetAtPath<GameObject>(SynRoot + "/" + n + ".fbx");
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

    private static Animator ConfigureAnimator(GameObject go, string controllerPath)
    {
        var an = go.GetComponent<Animator>();
        if (an == null) an = go.AddComponent<Animator>();
        an.applyRootMotion = false;
        an.runtimeAnimatorController = AssetDatabase.LoadAssetAtPath<RuntimeAnimatorController>(controllerPath);
        return an;
    }

    private static GameObject SavePrefab(GameObject go, string path)
    {
        var prefab = PrefabUtility.SaveAsPrefabAsset(go, path);
        Object.DestroyImmediate(go);
        return prefab;
    }

    private static void UpdateCatalog(List<GameObject> bodies, List<Material> skins)
    {
        var path = CatalogDir + "/HumanBodyCatalog.asset";
        var catalog = AssetDatabase.LoadAssetAtPath<HumanBodyCatalogSO>(path);
        if (catalog == null)
        {
            catalog = ScriptableObject.CreateInstance<HumanBodyCatalogSO>();
            AssetDatabase.CreateAsset(catalog, path);
        }

        catalog.Bodies = new List<HumanBodyCatalogSO.Entry>();
        foreach (var b in bodies)
            catalog.Bodies.Add(new HumanBodyCatalogSO.Entry { Body = b, Skins = new List<Material>(skins) });

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
