using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public struct ExpeditionResult
{
    public int Seed;
    public ExpeditionTeam Winner;
    public int PlayerSecured;
    public int MaterialLost;
    public int RivalSecured;
    public int Floors;
    public bool Lost;
    public List<string> FallenIds;
    public int Fallen;
    public List<string> TeamIds;
    public int Combats;
}

public struct ExpeditionReturn
{
    public int Seed;
    public ExpeditionTeam Winner;
    public int PlayerSecured;
    public int RivalSecured;
    public int MineritaGained;
    public int MineritaLost;
    public int Fallen;
    public int Floors;
    public bool Lost;
    public List<CreatureDNA> Team;
    public List<string> EvolvedIds;
    public int ExplorationsToEvolve;
}

public static class ExpeditionHandoff
{
    public static bool CameFromStore { get; private set; }
    public static bool HasResult { get; private set; }
    public static ExpeditionResult Result { get; private set; }
    public static int RunSeed { get; private set; }

    private static readonly List<string> selectedIds = new();
    public static IReadOnlyList<string> SelectedIds => selectedIds;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
    private static void ResetState()
    {
        CameFromStore = false;
        HasResult = false;
        Result = default;
        RunSeed = 0;
        selectedIds.Clear();
    }

    public static void GoToArena(IReadOnlyList<string> ids = null)
    {
        selectedIds.Clear();
        if (ids != null) selectedIds.AddRange(ids);
        CameFromStore = true;
        HasResult = false;
        RunSeed = System.Environment.TickCount & 0x7fffffff;
        SceneFlow.GoToArena();
    }

    public static void ReturnToStore(ExpeditionResult? result)
    {
        if (result.HasValue)
        {
            Result = result.Value;
            HasResult = true;
        }
        else
        {
            CameFromStore = false;
        }
        selectedIds.Clear();
        SceneFlow.GoToStore();
    }

    public static bool TryConsumeResult(out ExpeditionResult result)
    {
        result = Result;
        bool had = HasResult;
        HasResult = false;
        CameFromStore = false;
        selectedIds.Clear();
        return had;
    }
}
}
