using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "BreedingDecor", menuName = "RunRunSimulator/Breeding/Breeding Decor")]
public class BreedingDecorSO : SerializedScriptableObject
{
    public string Id;
    public string DisplayName;
    [TextArea] public string Effect;
    public int    Price;
    public Sprite Icon;
    public GameObject Prefab;
    public Color  Tint = Color.white;
    [Min(0)] public int DiscoverAtBreeds;
    public List<BreedingModifier> Modifiers = new List<BreedingModifier>();

    public bool IsDiscovered(int bredTotal) => bredTotal >= DiscoverAtBreeds;
}
}
