using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "BreedingDecorDatabase", menuName = "RunRunSimulator/Breeding/Breeding Decor Database")]
public class BreedingDecorDatabaseSO : ScriptableObject
{
    [SerializeField] private List<BreedingDecorSO> decors = new List<BreedingDecorSO>();

    public IReadOnlyList<BreedingDecorSO> All => decors;

    public BreedingDecorSO Get(string id)
    {
        if (string.IsNullOrEmpty(id)) return null;
        for (int i = 0; i < decors.Count; i++)
            if (decors[i] != null && decors[i].Id == id) return decors[i];
        return null;
    }
}
}
