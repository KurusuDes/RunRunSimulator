using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
namespace MoriMonchiSimulator
{

public static class MonchiPartRegistrar
{
    private const string PartsFolder = "Assets/RunRunSimulator/Resources/Prefabs/MoriMochi/Parts";
    private const string PartsPrefix = "MonchiPart_";
    private const string VisualBankPath = "Assets/RunRunSimulator/ScriptableObjects/Visual/MonchiVisualBank.asset";
    private const string EggFolder = "Assets/RunRunSimulator/Resources/Models/MoriMochi/Parts/Egg";
    private const string EggPrefix = "EggPart_";
    private const string BlobimFolder = "Assets/RunRunSimulator/Resources/Models/MoriMochi/Parts/Blobim";
    private const string BlobimPrefix = "BlobimPart_";
    private const string IconFolder = "Assets/RunRunSimulator/Resources/Sprites/PartIcons";
    private const string IconPrefix = "PartIcon_";

    [MenuItem("RunRunSimulator/Parts/Registrar partes modulares")]
    public static void RegisterAll()
    {
        var bank = AssetDatabase.LoadAssetAtPath<MonchiVisualBankSO>(VisualBankPath);
        var guids = AssetDatabase.FindAssets($"t:Prefab {PartsPrefix}", new[] { PartsFolder });

        int total = 0;
        int added = 0;
        int eggCount = 0;
        int slimeCount = 0;
        int iconCount = 0;
        var summary = new List<string>();

        foreach (var guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) continue;

            string fileName = Path.GetFileNameWithoutExtension(path);
            if (!fileName.StartsWith(PartsPrefix)) continue;
            string partName = fileName.Substring(PartsPrefix.Length);

            string slot = DetectSlot(prefab);
            if (slot == null)
            {
                Debug.LogWarning($"[MonchiPartRegistrar] '{partName}' no tiene un SkinnedMeshRenderer Horn/Back/Wing — se salta.");
                continue;
            }

            var (id, isNew, part) = RegisterPart(slot, partName, prefab);
            bank.SetPartMesh(id, prefab);

            string tags = "";

            string eggPath = $"{EggFolder}/{EggPrefix}{partName}.fbx";
            var eggModel = AssetDatabase.LoadAssetAtPath<GameObject>(eggPath);
            if (eggModel != null)
            {
                bank.SetPartMesh(id, eggModel, MonchiForm.Egg);
                tags += "[huevo]";
                eggCount++;
            }

            string slimePath = $"{BlobimFolder}/{BlobimPrefix}{partName}.fbx";
            var slimeModel = AssetDatabase.LoadAssetAtPath<GameObject>(slimePath);
            if (slimeModel != null)
            {
                bank.SetPartMesh(id, slimeModel, MonchiForm.Slime);
                tags += "[slime]";
                slimeCount++;
            }

            string iconPath = $"{IconFolder}/{IconPrefix}{partName}.png";
            if (AssetDatabase.LoadAssetAtPath<Texture2D>(iconPath) != null)
            {
                EnsurePixelArtIcon(iconPath);
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(iconPath);
                if (sprite != null)
                {
                    part.Icon = sprite;
                    EditorUtility.SetDirty(part);
                    tags += "[icono]";
                    iconCount++;
                }
            }

            total++;
            if (isNew) added++;
            string suffix = tags.Length > 0 ? " " + tags : "";
            summary.Add($"{id}={partName} ({slot}){suffix}");
        }

        AssetDatabase.SaveAssets();
        Debug.Log($"[MonchiPartRegistrar] {total} partes procesadas, {added} nuevas. Huevo: {eggCount} · Slime: {slimeCount} · Icono: {iconCount}\n{string.Join("\n", summary)}");
    }

    private static void EnsurePixelArtIcon(string path)
    {
        var importer = AssetImporter.GetAtPath(path) as TextureImporter;
        if (importer == null) return;

        bool changed = false;
        if (importer.textureType != TextureImporterType.Sprite) { importer.textureType = TextureImporterType.Sprite; changed = true; }
        if (importer.spriteImportMode != SpriteImportMode.Single) { importer.spriteImportMode = SpriteImportMode.Single; changed = true; }
        if (importer.filterMode != FilterMode.Point) { importer.filterMode = FilterMode.Point; changed = true; }
        if (importer.textureCompression != TextureImporterCompression.Uncompressed) { importer.textureCompression = TextureImporterCompression.Uncompressed; changed = true; }
        if (importer.mipmapEnabled) { importer.mipmapEnabled = false; changed = true; }
        if (!importer.alphaIsTransparency) { importer.alphaIsTransparency = true; changed = true; }
        if (importer.spritePixelsPerUnit != 32f) { importer.spritePixelsPerUnit = 32f; changed = true; }

        if (changed)
            importer.SaveAndReimport();
    }

    private static string DetectSlot(GameObject prefab)
    {
        var renderers = prefab.GetComponentsInChildren<SkinnedMeshRenderer>(true);
        string EffectiveName(string name) => name.StartsWith("Deco_", System.StringComparison.OrdinalIgnoreCase) && name.Length > 12 ? name.Substring(12) : name;
        int horn = renderers.Count(r => EffectiveName(r.gameObject.name).StartsWith("Horn", System.StringComparison.OrdinalIgnoreCase));
        int back = renderers.Count(r => EffectiveName(r.gameObject.name).StartsWith("Back", System.StringComparison.OrdinalIgnoreCase));
        int wing = renderers.Count(r => EffectiveName(r.gameObject.name).StartsWith("Wing", System.StringComparison.OrdinalIgnoreCase));

        if (horn == 0 && back == 0 && wing == 0) return null;
        if (horn >= back && horn >= wing) return "Horn";
        if (back >= wing) return "Back";
        return "Wing";
    }

    private static (string id, bool isNew, BodyPart part) RegisterPart(string slot, string partName, GameObject prefab)
    {
        return slot switch
        {
            "Horn" => RegisterPart<HornPart, HornDatabaseSO>(partName, prefab, "Horns", "HornPart", "HornDatabase"),
            "Back" => RegisterPart<BackPart, BackDatabaseSO>(partName, prefab, "Backs", "BackPart", "BackDatabase"),
            _      => RegisterPart<WingPart, WingDatabaseSO>(partName, prefab, "Wings", "WingPart", "WingDatabase"),
        };
    }

    private static (string id, bool isNew, BodyPart part) RegisterPart<TPart, TDatabase>(
        string partName, GameObject prefab, string folder, string typePrefix, string databaseName)
        where TPart : BodyPart
        where TDatabase : PartDatabaseSO<TPart>
    {
        string assetPath = $"Assets/RunRunSimulator/ScriptableObjects/Parts/{folder}/{typePrefix}_{partName}.asset";
        var part = AssetDatabase.LoadAssetAtPath<TPart>(assetPath);
        bool isNew = part == null;

        if (isNew)
        {
            part = ScriptableObject.CreateInstance<TPart>();
            part.Name = ToReadableName(partName);
            AssetDatabase.CreateAsset(part, assetPath);
        }

        string databasePath = $"Assets/RunRunSimulator/ScriptableObjects/Databases/{databaseName}.asset";
        var database = AssetDatabase.LoadAssetAtPath<TDatabase>(databasePath);
        string id = database.RegisterEntry(part);

        return (id, isNew, part);
    }

    private static string ToReadableName(string camelName)
    {
        var matches = Regex.Matches(camelName, "[A-Z][a-z]*");
        var words = new List<string>();
        for (int i = 0; i < matches.Count; i++)
            words.Add(i == 0 ? matches[i].Value : matches[i].Value.ToLowerInvariant());

        return string.Join(" ", words);
    }
}
}
