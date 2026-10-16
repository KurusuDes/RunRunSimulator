using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "ItemDef", menuName = "RunRunSimulator/Items/Item Definition")]
[InlineEditor]
public class ItemDefinitionSO : SerializedScriptableObject
{
    [Title("Identity")]
    [ReadOnly] public string Id;
    public string DisplayName = "";
    public WorldPropCategory Category = WorldPropCategory.Tool;
    [PreviewField(60)] public Sprite Icon;

    [Title("World Prop")]
    [Required, AssetsOnly]
    public GameObject Prefab;
}
}
