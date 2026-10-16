using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
namespace MoriMonchiSimulator
{
    public static class SyntyToonConverter
    {
        const string TemplatePath = "Assets/RunRunSimulator/Resources/Materials/Shop/Forest/PolygonNature_Tree_01_Pal.mat";
        const string OutputFolder = "Assets/RunRunSimulator/Resources/Materials/SyntyToon";
        const string AlphaClipKeyword = "_ALPHACLIP_ON";

        static readonly string[] SourceFolders =
        {
            "Assets/Synty/PolygonNatureBiomes",
            "Assets/Synty/PolygonFantasyVillage",
            "Assets/Synty/PolygonDungeonRealms",
            "Assets/Synty/PolygonDungeon",
            "Assets/Synty/PolygonFantasyKingdom",
            "Assets/Synty/PolygonDog"
        };

        public static Material ToonFor(Material src)
        {
            if (src == null || src.shader == null) return null;
            if (src.name.EndsWith("_Toon")) return null;

            string shaderName = src.shader.name;
            string texProp;
            string colorProp;
            bool foliage;
            switch (shaderName)
            {
                case "Synty/Foliage":
                    texProp = "_Leaf_Texture";
                    colorProp = "_Leaf_Base_Color";
                    foliage = true;
                    break;
                case "Synty/Generic_Basic":
                case "Synty/Generic_Standard":
                    texProp = "_Albedo_Map";
                    colorProp = "_BaseColor";
                    foliage = false;
                    break;
                case "Universal Render Pipeline/Lit":
                    texProp = "_BaseMap";
                    colorProp = "_BaseColor";
                    foliage = src.HasProperty("_AlphaClip") && src.GetFloat("_AlphaClip") > 0.5f;
                    break;
                default:
                    return null;
            }

            string path = OutputFolder + "/" + src.name + "_Toon.mat";
            Material existing = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (existing != null) return existing;

            Material template = AssetDatabase.LoadAssetAtPath<Material>(TemplatePath);
            if (template == null)
            {
                Debug.LogError("SyntyToonConverter: falta el template " + TemplatePath);
                return null;
            }

            EnsureFolder(OutputFolder);

            Material dst = new Material(template);
            dst.name = src.name + "_Toon";
            dst.SetTexture("_BaseMap", src.HasProperty(texProp) ? src.GetTexture(texProp) : null);
            Color tint = src.HasProperty(colorProp) ? src.GetColor(colorProp) : Color.white;
            tint.a = 1f;
            dst.SetColor("_Tint", tint);

            if (foliage)
            {
                dst.SetFloat("_AlphaClip", 1f);
                dst.EnableKeyword(AlphaClipKeyword);
                dst.SetFloat("_Cutoff", 0.5f);
                dst.SetFloat("_Cull", 0f);
                dst.SetFloat("_WindStrength", 0.06f);
                dst.SetFloat("_WindSpeed", 1.2f);
                dst.SetFloat("_WindScale", 0.35f);
            }
            else
            {
                dst.SetFloat("_AlphaClip", 0f);
                dst.DisableKeyword(AlphaClipKeyword);
                dst.SetFloat("_Cull", 2f);
                dst.SetFloat("_WindStrength", 0f);
            }

            AssetDatabase.CreateAsset(dst, path);
            return dst;
        }

        public static int ToonifyHierarchy(GameObject root)
        {
            if (root == null) return 0;
            int changed = 0;
            foreach (Renderer r in root.GetComponentsInChildren<Renderer>(true))
            {
                Material[] mats = r.sharedMaterials;
                bool dirty = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    Material toon = ToonFor(mats[i]);
                    if (toon == null || toon == mats[i]) continue;
                    if (!dirty)
                    {
                        Undo.RecordObject(r, "Toonify Synty");
                        dirty = true;
                    }
                    mats[i] = toon;
                    changed++;
                }
                if (dirty)
                {
                    r.sharedMaterials = mats;
                    EditorUtility.SetDirty(r);
                }
            }
            return changed;
        }

        [MenuItem("RunRunSimulator/Art/Toonify Synty Selection")]
        static void ToonifySelection()
        {
            int total = 0;
            foreach (GameObject go in Selection.gameObjects)
                total += ToonifyHierarchy(go);
            AssetDatabase.SaveAssets();
            Debug.Log("Toonify Synty: " + total + " materiales reemplazados");
        }

        [MenuItem("RunRunSimulator/Art/Build Synty Toon Materials")]
        static void BuildAll()
        {
            List<string> folders = new List<string>();
            foreach (string f in SourceFolders)
                if (AssetDatabase.IsValidFolder(f)) folders.Add(f);
            if (folders.Count == 0)
            {
                Debug.LogWarning("Build Synty Toon Materials: no hay carpetas Synty");
                return;
            }

            int created = 0;
            int skipped = 0;
            int existing = 0;
            AssetDatabase.StartAssetEditing();
            try
            {
                foreach (string guid in AssetDatabase.FindAssets("t:Material", folders.ToArray()))
                {
                    Material src = AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath(guid));
                    if (src == null) continue;
                    bool had = File.Exists(OutputFolder + "/" + src.name + "_Toon.mat");
                    Material toon = ToonFor(src);
                    if (toon == null) skipped++;
                    else if (had) existing++;
                    else created++;
                }
            }
            finally
            {
                AssetDatabase.StopAssetEditing();
            }
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Build Synty Toon Materials: " + created + " creados, " + existing + " ya existian, " + skipped + " no convertibles");
        }

        static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }
    }
}
