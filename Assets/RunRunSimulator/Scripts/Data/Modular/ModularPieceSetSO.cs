using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[System.Serializable]
public struct ModularRoofPreset
{
    public Vector2Int Size;
    public GameObject Prefab;
}

[CreateAssetMenu(fileName = "ModularPieceSet", menuName = "RunRunSimulator/Modular/Piece Set")]
public class ModularPieceSetSO : SerializedScriptableObject
{
    public const float Cell = 2.5f;
    public const float Storey = 3f;
    public const float RoofRise = 3f;

    [Title("Floor")]
    public GameObject Floor;
    [Tooltip("If not empty, applied to the floor pieces.")]
    public Material[] FloorMaterials;

    [Title("Walls")]
    public GameObject Wall;
    public GameObject GableAngle;
    public Material WallExterior;
    public Material WallInterior;
    [Tooltip("Exterior of gable walls above the ground floor. Falls back to WallExterior if empty.")]
    public Material GableExterior;

    [Title("Openings")]
    public GameObject[] Windows;
    public GameObject[] Doors;

    [Title("Structure")]
    public GameObject Pillar;
    public GameObject Beam;

    [Title("Plinth")]
    public GameObject Plinth;
    public Material PlinthMaterial;
    public GameObject PillarHalf;
    public const float PlinthHeight = 1.51f;
    public const float PillarHalfHeight = 1.55f;

    [Title("Roof")]
    public GameObject RoofRow;
    public GameObject RoofEnd;
    public GameObject RoofRowHalf;
    public GameObject RoofEndHalf;
    public GameObject GableAngleHalf;
    public const float RoofRiseHalf = 1.5f;

    [Title("Roof Presets")]
    public List<ModularRoofPreset> RoofPresets = new List<ModularRoofPreset>();

    public GameObject RoofPresetFor(Vector2Int size)
    {
        for (int i = 0; i < RoofPresets.Count; i++)
            if (RoofPresets[i].Size == size && RoofPresets[i].Prefab != null) return RoofPresets[i].Prefab;
        return null;
    }

    public GameObject PickWindow(int variant) =>
        Windows == null || Windows.Length == 0 ? null : Windows[Mathf.Abs(variant) % Windows.Length];

    public GameObject PickDoor(int variant) =>
        Doors == null || Doors.Length == 0 ? null : Doors[Mathf.Abs(variant) % Doors.Length];
}
}
