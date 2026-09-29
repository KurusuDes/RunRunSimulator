using System.Collections.Generic;
using Sirenix.OdinInspector;
using Sirenix.Serialization;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "MonchiVisualBank", menuName = "RunRunSimulator/Databases/Monchi Visual Bank")]
public class MonchiVisualBankSO : SerializedScriptableObject
{
    [SerializeField] private List<GameObject> bodies = new List<GameObject>();

    [OdinSerialize]
    [DictionaryDrawerSettings(KeyLabel = "Body Shape ID", ValueLabel = "Body Override")]
    private Dictionary<string, GameObject> bodyOverrides = new Dictionary<string, GameObject>();

    [OdinSerialize]
    [DictionaryDrawerSettings(KeyLabel = "Part ID", ValueLabel = "Part Mesh")]
    private Dictionary<string, GameObject> partMeshes = new Dictionary<string, GameObject>();

    [OdinSerialize]
    [DictionaryDrawerSettings(KeyLabel = "Part ID", ValueLabel = "Egg Part Mesh")]
    private Dictionary<string, GameObject> eggPartMeshes = new Dictionary<string, GameObject>();

    [OdinSerialize]
    [DictionaryDrawerSettings(KeyLabel = "Part ID", ValueLabel = "Slime Part Mesh")]
    private Dictionary<string, GameObject> slimePartMeshes = new Dictionary<string, GameObject>();

    [SerializeField] private RuntimeAnimatorController animatorController;
    [SerializeField] private List<Material> gemMaterials = new List<Material>();
    [SerializeField] private MonchiMoodSetSO moodSet;
    [SerializeField] private MonchiMoodSetSO moodSetFemale;
    [SerializeField] private Material faceMaterial;

    [SerializeField] private GameObject slimeModel;
    [SerializeField] private RuntimeAnimatorController slimeAnimatorController;
    [SerializeField] private float slimeScale = 3.4f;

    [SerializeField] private GameObject eggModel;
    [SerializeField] private RuntimeAnimatorController eggAnimatorController;
    [SerializeField] private float eggScale = 3.4f;
    [SerializeField] private float eggHeight = 1.15f;

    public RuntimeAnimatorController AnimatorController => animatorController;
    public MonchiMoodSetSO MoodSet => moodSet;
    public Material FaceMaterial => faceMaterial;
    public MonchiMoodSetSO MoodSetFor(CreatureGender gender) => gender == CreatureGender.Female && moodSetFemale != null ? moodSetFemale : moodSet;
    public GameObject SlimeModel => slimeModel;
    public RuntimeAnimatorController SlimeAnimatorController => slimeAnimatorController;
    public float SlimeScale => slimeScale;
    public GameObject EggModel => eggModel;
    public RuntimeAnimatorController EggAnimatorController => eggAnimatorController;
    public float EggScale => eggScale;
    public float EggHeight => eggHeight;

    public GameObject GetBody(string bodyShapeId)
    {
        if (bodyOverrides != null && bodyOverrides.TryGetValue(bodyShapeId, out var overrideBody) && overrideBody != null)
            return overrideBody;

        if (bodies == null || bodies.Count == 0)
        {
            Debug.LogWarning("[MonchiVisualBankSO] No bodies assigned.");
            return null;
        }

        return bodies[StableHash(bodyShapeId) % bodies.Count];
    }

    public GameObject GetPartMesh(string partId, MonchiForm form = MonchiForm.Adult)
    {
        if (string.IsNullOrEmpty(partId))
            return null;

        var dict = GetPartMeshDictionary(form);
        if (dict.TryGetValue(partId, out var partMesh))
            return partMesh;

        return null;
    }

#if UNITY_EDITOR
    public void SetPartMesh(string partId, GameObject prefab, MonchiForm form = MonchiForm.Adult)
    {
        var dict = GetPartMeshDictionary(form);
        dict[partId] = prefab;
        UnityEditor.EditorUtility.SetDirty(this);
    }
#endif

    private Dictionary<string, GameObject> GetPartMeshDictionary(MonchiForm form)
    {
        switch (form)
        {
            case MonchiForm.Egg:
                if (eggPartMeshes == null) eggPartMeshes = new Dictionary<string, GameObject>();
                return eggPartMeshes;
            case MonchiForm.Slime:
                if (slimePartMeshes == null) slimePartMeshes = new Dictionary<string, GameObject>();
                return slimePartMeshes;
            default:
                if (partMeshes == null) partMeshes = new Dictionary<string, GameObject>();
                return partMeshes;
        }
    }

    public Material GetGem(string uniqueId)
    {
        if (gemMaterials == null || gemMaterials.Count == 0)
            return null;

        return gemMaterials[StableHash(uniqueId) % gemMaterials.Count];
    }

    public static int StableHash(string s)
    {
        unchecked
        {
            uint h = 2166136261u;
            if (!string.IsNullOrEmpty(s))
                foreach (char c in s)
                    h = (h ^ c) * 16777619u;
            return (int)(h & 0x7FFFFFFF);
        }
    }
}
}
