using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "PartSet", menuName = "RunRunSimulator/Parts/Part Set")]
public class PartSetSO : ScriptableObject
{
    public string Name = "";
    public Color Color = Color.white;
}
}
