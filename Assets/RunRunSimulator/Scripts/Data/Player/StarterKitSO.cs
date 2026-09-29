using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "StarterKit", menuName = "RunRunSimulator/Player/Starter Kit")]
public class StarterKitSO : ScriptableObject
{
    [Title("Currency")]
    public int Dabloons = 0;
    public int Minerita = 30;

    [Title("Furniture")]
    public List<FurnitureDefinitionSO> Furniture = new List<FurnitureDefinitionSO>();
}
}
