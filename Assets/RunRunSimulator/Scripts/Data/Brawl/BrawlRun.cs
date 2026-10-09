using System.Collections.Generic;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BrawlRun
{
    private readonly List<string> teamIds = new();
    private readonly Dictionary<string, float> health = new();
    private readonly List<BrawlRoom> rooms = new();
    private readonly BrawlRunRulesSO rules;

    public int BaseSeed { get; }
    public IReadOnlyList<string> TeamIds => teamIds;
    public int Depth { get; private set; }
    public IReadOnlyList<BrawlRoom> Rooms => rooms;
    public int RoomIndex { get; private set; }
    public int Material { get; private set; }
    public int MaterialLost { get; private set; }
    public bool Lost { get; private set; }
    public int RoomsCleared { get; private set; }

    public bool TramoDone => RoomIndex >= rooms.Count;
    public float RivalPower => rules.RivalPower(Depth);

    public BrawlRoom CurrentRoom => rooms.Count == 0 ? default : rooms[Mathf.Clamp(RoomIndex, 0, rooms.Count - 1)];

    public BrawlRun(int baseSeed, IReadOnlyList<string> teamIds, BrawlRunRulesSO rules)
    {
        BaseSeed = baseSeed;
        this.rules = rules;
        if (teamIds == null) return;
        for (int i = 0; i < teamIds.Count; i++)
        {
            string id = teamIds[i];
            if (!string.IsNullOrEmpty(id)) this.teamIds.Add(id);
        }
    }

    public float Health01(string id) => health.TryGetValue(id, out float value) ? value : 1f;

    public int RoomSeed() => ArenaRun.FloorSeedOf(BaseSeed, Depth * 16 + RoomIndex);

    public void PlanNextTramo()
    {
        if (Lost) return;
        Depth++;
        RoomIndex = 0;
        rooms.Clear();

        var rng = new System.Random(ArenaRun.FloorSeedOf(BaseSeed, 1000 + Depth));
        int minRooms = Mathf.Max(1, rules.MinRooms);
        int count = rng.Next(minRooms, Mathf.Max(minRooms, rules.MaxRooms) + 1);
        int maxR = Mathf.Clamp(Depth <= 1 ? rules.FirstTramoMaxRivals : 3, 1, 3);
        int minR = Mathf.Min(Depth >= rules.HardFromDepth ? 2 : 1, maxR);

        for (int i = 0; i < count; i++)
        {
            if (i == count - 1)
            {
                rooms.Add(new BrawlRoom { Kind = BrawlRoomKind.Combat, Rivals = maxR });
                continue;
            }

            double r = rng.NextDouble();
            if (r < rules.DummiesChance) rooms.Add(new BrawlRoom { Kind = BrawlRoomKind.Dummies, Rivals = 0 });
            else if (r < rules.DummiesChance + rules.MineralsChance) rooms.Add(new BrawlRoom { Kind = BrawlRoomKind.Minerals, Rivals = 0 });
            else rooms.Add(new BrawlRoom { Kind = BrawlRoomKind.Combat, Rivals = rng.Next(minR, maxR + 1) });
        }
    }

    public void RecordCombat(bool won, IReadOnlyDictionary<string, float> health01, int rivalsDefeated)
    {
        if (Lost) return;

        for (int i = 0; i < teamIds.Count; i++)
        {
            string id = teamIds[i];
            float h = health01 != null && health01.TryGetValue(id, out float value) ? value : Health01(id);
            if (won) h = Mathf.Min(1f, h + rules.HealAfterCombat);
            health[id] = h;
        }

        if (won)
        {
            Material += rivalsDefeated * rules.MaterialPerRival * Depth;
            RoomsCleared++;
            RoomIndex++;
            return;
        }

        Lost = true;
        MaterialLost = Mathf.CeilToInt(Material * rules.LossFraction);
        Material -= MaterialLost;
    }

    public void RecordTrial(IReadOnlyDictionary<string, float> health01, int material)
    {
        if (Lost) return;

        for (int i = 0; i < teamIds.Count; i++)
        {
            string id = teamIds[i];
            health[id] = health01 != null && health01.TryGetValue(id, out float value) ? value : Health01(id);
        }

        Material += Mathf.Max(0, material);
        RoomsCleared++;
        RoomIndex++;
    }

    public ExpeditionResult ToResult()
    {
        return new ExpeditionResult
        {
            Seed = BaseSeed,
            Winner = Lost ? ExpeditionTeam.Rival : ExpeditionTeam.Player,
            PlayerSecured = Material,
            MaterialLost = MaterialLost,
            RivalSecured = 0,
            Floors = RoomsCleared,
            Lost = Lost,
            FallenIds = new List<string>(),
            Fallen = 0,
            TeamIds = new List<string>(teamIds)
        };
    }
}
}
