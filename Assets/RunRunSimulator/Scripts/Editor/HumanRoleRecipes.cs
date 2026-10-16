using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using UnityEditor;
using UnityEngine;

namespace MoriMonchiSimulator
{
public class HumanRoleRecipe
{
    [JsonProperty("name")] public string Name;
    [JsonProperty("colorMap")] public string ColorMap;
    [JsonProperty("archetype")] public string Archetype;
    [JsonProperty("species")] public string Species;
    [JsonProperty("bodyType")] public float BodyType;
    [JsonProperty("bodySize")] public float BodySize;
    [JsonProperty("muscle")] public float Muscle;
    [JsonProperty("parts")] public List<string> Parts = new();
}

public static class HumanRoleRecipes
{
    public const string JsonPath = "Assets/RunRunSimulator/ScriptableObjects/NPC/HumanRoles.json";
    public const string SynRoot = "Assets/Synty/SidekickCharacters/Resources/Meshes";
    public const string CharactersRoot = "Assets/Synty/SidekickCharacters/Characters";

    public static List<HumanRoleRecipe> Load()
    {
        if (!File.Exists(JsonPath))
        {
            Debug.LogError("[HumanRoleRecipes] No existe " + JsonPath);
            return new List<HumanRoleRecipe>();
        }
        return JsonConvert.DeserializeObject<List<HumanRoleRecipe>>(File.ReadAllText(JsonPath)) ?? new List<HumanRoleRecipe>();
    }

    public static Dictionary<string, string> BuildPartIndex()
    {
        var index = new Dictionary<string, string>();
        foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { SynRoot }))
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var name = Path.GetFileNameWithoutExtension(path);
            if (!index.ContainsKey(name)) index[name] = path;
        }
        return index;
    }

    public static string ColorMapTexturePath(string colorMap)
    {
        var last = colorMap.Substring(colorMap.LastIndexOf('/') + 1);
        return CharactersRoot + "/" + colorMap + "/Textures/T_" + last + "ColorMap.png";
    }
}
}
