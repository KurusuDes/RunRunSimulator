using System;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[DefaultExecutionOrder(-50)]
public class BrawlRunDirector : MonoBehaviour
{
    [Required, SerializeField] private BrawlMatch match;
    [Required, SerializeField] private BrawlRunRulesSO rules;
    [Required, SerializeField] private BrawlTrialRoom trial;

    private BrawlRun run;
    private BrawlRoom room;
    private readonly List<CreatureDNA> team = new();

    public bool Active => run != null;
    public BrawlRun Run => run;
    public BrawlRunState State { get; private set; }
    public IReadOnlyList<CreatureDNA> Team => team;
    public string LastRoomSummary { get; private set; }
    public int LastRoomLoot { get; private set; }

    private float stateUntil;

    public event Action Changed;

    private void Awake()
    {
        if (!ExpeditionHandoff.CameFromStore) return;
        BrawlRunRulesSO.Activate(rules);
        run = new BrawlRun(ExpeditionHandoff.RunSeed, ExpeditionHandoff.SelectedIds, rules);
        match.Driven = true;
    }

    private void OnEnable()
    {
        BrawlMatch.OnRosterSpawned += HandleRoster;
        BrawlMatch.OnMatchEnded += HandleEnded;
    }

    private void OnDisable()
    {
        BrawlMatch.OnRosterSpawned -= HandleRoster;
        BrawlMatch.OnMatchEnded -= HandleEnded;
        BrawlRunRulesSO.Deactivate(rules);
    }

    private void Start()
    {
        if (!Active) return;

        var pool = ArenaCastSource.LoadLocal();
        foreach (var id in run.TeamIds)
        {
            var dna = pool.Find(d => d.UniqueID == id);
            if (dna != null) team.Add(dna);
        }

        if (team.Count == 0)
        {
            Debug.LogWarning("[BrawlRunDirector] No se encontro ningun MoriMonchi del equipo en el save, vuelvo a la tienda");
            ExpeditionHandoff.ReturnToStore(null);
            return;
        }

        run.PlanNextTramo();
        State = BrawlRunState.Planning;
        Changed?.Invoke();
    }

    private void Update()
    {
        if (!Active || Time.time < stateUntil) return;

        if (State == BrawlRunState.Transition)
        {
            StartRoom();
        }
        else if (State == BrawlRunState.RoomResult)
        {
            if (run.TramoDone)
            {
                run.PlanNextTramo();
                State = BrawlRunState.Planning;
                Changed?.Invoke();
            }
            else
            {
                EnterTransition();
            }
        }
    }

    public void AcceptTramo()
    {
        if (!Active || State != BrawlRunState.Planning || run.Lost) return;
        EnterTransition();
    }

    public void Leave()
    {
        if (!Active || (State != BrawlRunState.Planning && State != BrawlRunState.Over)) return;
        ExpeditionHandoff.ReturnToStore(run.ToResult());
    }

    private void EnterTransition()
    {
        State = BrawlRunState.Transition;
        stateUntil = Time.time + rules.VeilCoverSeconds;
        Changed?.Invoke();
    }

    private void StartRoom()
    {
        room = run.CurrentRoom;
        State = BrawlRunState.Fighting;
        int rivals = room.Kind == BrawlRoomKind.Combat ? room.Rivals : 3;
        match.StartMatch(run.RoomSeed(), team, rivals);
        if (room.Kind != BrawlRoomKind.Combat) trial.Begin(room.Kind, rules);
        Changed?.Invoke();
    }

    private void HandleRoster(IReadOnlyList<BrawlFighter> fighters)
    {
        if (!Active || State != BrawlRunState.Fighting) return;

        foreach (var fighter in fighters)
        {
            if (fighter.Team == ExpeditionTeam.Player)
            {
                fighter.Prime(1f, run.Health01(fighter.DNA.UniqueID));
            }
            else if (room.Kind == BrawlRoomKind.Combat)
            {
                fighter.Prime(run.RivalPower, 1f);
            }
            else
            {
                fighter.Dummy = true;
                fighter.Prime(rules.DummyPower, 1f);
            }
        }
    }

    private void HandleEnded(ExpeditionTeam winner)
    {
        if (!Active || State != BrawlRunState.Fighting) return;

        var health = new Dictionary<string, float>();
        int defeated = 0;
        foreach (var fighter in match.Fighters)
        {
            if (fighter.Team == ExpeditionTeam.Player) health[fighter.DNA.UniqueID] = fighter.Hp01;
            else if (!fighter.IsAlive) defeated++;
        }

        int before = run.Material;
        int rate = rules.MineritaPerLoot;
        string result;
        if (room.Kind == BrawlRoomKind.Combat)
        {
            bool won = winner == ExpeditionTeam.Player || winner == ExpeditionTeam.None;
            run.RecordCombat(won, health, defeated);
            if (run.Lost) result = $"Perdiste: se pierden {run.MaterialLost * rate} Minerita";
            else if (winner == ExpeditionTeam.None) result = $"Empate: cuenta como victoria · +{(run.Material - before) * rate} Minerita";
            else result = $"Ganaste: +{(run.Material - before) * rate} Minerita";
        }
        else
        {
            run.RecordTrial(health, trial.End());
            result = room.Kind == BrawlRoomKind.Dummies
                ? "Muñecos: el equipo se curó"
                : $"Minerales: +{(run.Material - before) * rate} Minerita";
        }

        LastRoomSummary = result;
        LastRoomLoot = run.Lost || room.Kind == BrawlRoomKind.Dummies ? 0 : Mathf.Max(0, run.Material - before);
        if (run.Lost)
        {
            State = BrawlRunState.Over;
        }
        else
        {
            State = BrawlRunState.RoomResult;
            stateUntil = Time.time + rules.LootBeatSeconds;
        }
        Debug.Log($"[BrawlRunDirector] tramo {run.Depth} sala {room.Kind} ({run.RoomsCleared} superadas): {result} · llevas {run.Material}");
        Changed?.Invoke();
    }
}
}
