using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public enum ModularSide { South, East, North, West }
public enum ModularOpening { Wall, Window, Door, Open }

[System.Serializable]
public struct ModularEdge
{
    public ModularSide Side;
    [MinValue(0)] public int Index;
    public ModularOpening Opening;
    public int Variant;
}

public class ModularBuilding : MonoBehaviour
{
    public const string GeneratedName = "_Armado";

    [Title("Building")]
    public ModularPieceSetSO PieceSet;
    [MinValue(1)] public Vector2Int SizeCells = new Vector2Int(4, 4);
    public bool BuildFloor = true;
    public bool BuildRoof = true;
    public bool UsePresetRoof = true;
    public bool BuildPlinth = true;

    [Title("Openings")]
    [Tooltip("Edges not listed here are plain walls.")]
    public List<ModularEdge> Edges = new List<ModularEdge>();

    public ModularOpening OpeningAt(ModularSide side, int index, out int variant)
    {
        for (int i = 0; i < Edges.Count; i++)
        {
            var edge = Edges[i];
            if (edge.Side == side && edge.Index == index)
            {
                variant = edge.Variant;
                return edge.Opening;
            }
        }
        variant = 0;
        return ModularOpening.Wall;
    }
}
}
