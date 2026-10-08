using System.Collections.Generic;
using System.Text;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.AI;
namespace MoriMonchiSimulator
{

public class BrawlMatch : MonoBehaviour
{
    [Required, SerializeField] private ArenaLayoutBuilder layout;
    [SerializeField] private ArenaPaletteApplier palette;
    [Required, SerializeField] private BrawlFighter fighterPrefab;
    [Required, SerializeField] private CreatureDatabaseSO creatureDatabase;
    [Required, SerializeField] private FurTypeDatabaseSO furDatabase;
    [Required, SerializeField] private MonchiVisualBankSO visualBank;
    [Required, SerializeField] private BrawlKitDatabaseSO kits;
    [Required, SerializeField] private BrawlTuningSO tuning;
    [Required, SerializeField] private BrawlVfxLibrarySO vfx;
    [SerializeField] private int seed = 4242;
    [SerializeField] private bool randomizeEachPlay = true;
    [SerializeField, Min(1)] private int teamSize = 3;
    [SerializeField, Min(0f)] private float spawnSpread = 2.5f;
    [SerializeField] private bool autoRestart = true;

    private const int MaxWingRerolls = 12;

    private readonly List<BrawlFighter> fighters = new();
    private readonly HashSet<BrawlFighter> lastStanders = new();
    private List<CreatureDNA> lastRoster;
    private float phaseStartedAt;
    private float fightElapsed;
    private bool reachedSuddenDeath;

    public static BrawlMatch Current { get; private set; }
    public static event System.Action<BrawlMatchPhase> OnPhaseChanged;
    public static event System.Action<ExpeditionTeam> OnMatchEnded;
    public static event System.Action<IReadOnlyList<BrawlFighter>> OnRosterSpawned;
    public static event System.Action<BrawlFighter> OnLastStand;

    public BrawlMatchPhase Phase { get; private set; }
    public float PhaseTime => Time.time - phaseStartedAt;
    public float TimeLeft { get; private set; }
    public float SuddenDeathElapsed { get; private set; }
    public int Seed { get; private set; }
    public int MatchIndex { get; private set; }
    public ExpeditionTeam Winner { get; private set; }
    public int KnockOuts { get; private set; }
    public float DamageRamp => 1f + tuning.KoDamageRamp * KnockOuts;
    public IReadOnlyList<BrawlFighter> Fighters => fighters;
    public BrawlTuningSO Tuning => tuning;

    private void OnEnable()
    {
        Current = this;
        BrawlVfxLibrarySO.Activate(vfx);
        BrawlFighter.OnKnockedOut += HandleKnockedOut;
    }

    private void OnDisable()
    {
        if (Current == this) Current = null;
        BrawlVfxLibrarySO.Deactivate(vfx);
        BrawlFighter.OnKnockedOut -= HandleKnockedOut;
    }

    private void HandleKnockedOut(BrawlFighter victim, BrawlFighter killer)
    {
        if (Phase != BrawlMatchPhase.Fight && Phase != BrawlMatchPhase.SuddenDeath) return;
        if (!fighters.Contains(victim)) return;
        KnockOuts++;
        float factor = 1f + tuning.KoDamageRamp * KnockOuts;
        foreach (var f in fighters)
            if (f != null) f.RoundDamageFactor = factor;
        var team = victim.Team;
        var other = team == ExpeditionTeam.Player ? ExpeditionTeam.Rival : ExpeditionTeam.Player;
        if (AliveOf(team) != 1 || AliveOf(other) < 2) return;

        foreach (var survivor in fighters)
        {
            if (survivor == null || survivor.Team != team || !survivor.IsAlive || lastStanders.Contains(survivor)) continue;
            lastStanders.Add(survivor);
            survivor.AddShield(survivor.MaxHp * tuning.LastStandShield, tuning.LastStandSeconds);
            survivor.ApplyDamageBoost(tuning.LastStandBoost, tuning.LastStandSeconds);
            survivor.ApplyHaste(tuning.LastStandHaste, tuning.LastStandSeconds);
            survivor.Caster.Refill();
            BrawlFx.Emit(new BrawlFxEvent { Kind = BrawlFxKind.Pulse, To = survivor.Position, Radius = 3f, Theme = survivor.WingTheme, Team = team, Source = survivor });
            OnLastStand?.Invoke(survivor);
        }
    }

    private void Start()
    {
        Application.runInBackground = true;
        StartMatch(randomizeEachPlay ? System.Environment.TickCount : seed);
    }

    private void Update()
    {
        switch (Phase)
        {
            case BrawlMatchPhase.Countdown:
                if (PhaseTime >= tuning.CountdownSeconds) BeginFight();
                break;
            case BrawlMatchPhase.Fight:
                UpdateFight();
                break;
            case BrawlMatchPhase.SuddenDeath:
                UpdateSuddenDeath();
                break;
            case BrawlMatchPhase.Ended:
                if (autoRestart && PhaseTime >= tuning.EndHoldSeconds) NewMatch();
                break;
        }
    }

    [Button] public void NewMatch() => StartMatch(System.Environment.TickCount);

    [Button] public void Rematch()
    {
        if (lastRoster == null) NewMatch();
        else StartMatch(Seed, lastRoster);
    }

    public void StartMatch(int matchSeed, IReadOnlyList<CreatureDNA> roster = null)
    {
        ClearFighters();
        BrawlProjectile.ClearAll();
        BrawlZone.ClearAll();

        Seed = matchSeed;
        MatchIndex++;
        UnityEngine.Random.InitState(Seed);

        var filter = new NavMeshQueryFilter { agentTypeID = fighterPrefab.GetComponent<NavMeshAgent>().agentTypeID, areaMask = NavMesh.AllAreas };
        layout.Build(Seed, filter);
        if (palette != null)
        {
            palette.ApplyIndex(palette.IndexForSeed(Seed));
            palette.SetArenaCenter(layout.Center);
        }

        var dnas = roster != null ? new List<CreatureDNA>(roster) : MintRoster();
        lastRoster = dnas;

        TimeLeft = tuning.RoundSeconds;
        SuddenDeathElapsed = 0f;
        fightElapsed = 0f;
        reachedSuddenDeath = false;
        lastStanders.Clear();
        KnockOuts = 0;
        Winner = ExpeditionTeam.None;

        SpawnTeam(dnas, 0, Mathf.Min(teamSize, dnas.Count), ExpeditionTeam.Player, filter);
        SpawnTeam(dnas, teamSize, Mathf.Clamp(dnas.Count - teamSize, 0, teamSize), ExpeditionTeam.Rival, filter);

        LogStart();
        OnRosterSpawned?.Invoke(fighters);
        SetPhase(BrawlMatchPhase.Countdown);
    }

    private void ClearFighters()
    {
        foreach (var fighter in fighters)
        {
            if (fighter == null) continue;
            fighter.Despawn();
            Destroy(fighter.gameObject);
        }
        fighters.Clear();
    }

    private List<CreatureDNA> MintRoster()
    {
        var result = new List<CreatureDNA>();
        for (int team = 0; team < 2; team++)
        {
            var wings = new HashSet<string>();
            for (int i = 0; i < teamSize; i++)
            {
                var dna = MintRandom();
                for (int retry = 0; retry < MaxWingRerolls && wings.Contains(dna.WingID); retry++)
                    dna = MintRandom();
                wings.Add(dna.WingID);
                result.Add(dna);
            }
        }
        return result;
    }

    private CreatureDNA MintRandom()
    {
        var dna = CreatureGenerator.GenerateRandom(creatureDatabase, furDatabase);
        dna.Gender = UnityEngine.Random.value < 0.5f ? CreatureGender.Male : CreatureGender.Female;
        dna.Element = CreatureGenerator.RandomElement();
        dna.Role = CreatureGenerator.RandomRole();
        dna.Sociability = CreatureGenerator.RandomDial();
        dna.Boldness = CreatureGenerator.RandomDial();
        dna.CustomName = CreatureNameBank.GetRandomName();
        dna.Form = MonchiForm.Adult;
        dna.Generation = 1;
        dna.Stamp();
        return dna;
    }

    private void SpawnTeam(IReadOnlyList<CreatureDNA> dnas, int start, int count, ExpeditionTeam team, NavMeshQueryFilter filter)
    {
        Vector3 around = layout.SpawnPoint(team);
        float offset = UnityEngine.Random.value * 360f;
        float radius = count > 1 ? spawnSpread : 0f;

        for (int i = 0; i < count; i++)
        {
            float angle = (offset + 360f * i / count) * Mathf.Deg2Rad;
            Vector3 point = around + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * radius;
            Vector3 pos = NavMesh.SamplePosition(point, out var hit, 3f, filter) ? hit.position : around;
            SpawnFighter(dnas[start + i], team, pos);
        }
    }

    private void SpawnFighter(CreatureDNA dna, ExpeditionTeam team, Vector3 pos)
    {
        Vector3 look = layout.Center - pos;
        look.y = 0f;
        var rot = look.sqrMagnitude > 0.01f ? Quaternion.LookRotation(look) : Quaternion.identity;

        var fighter = Instantiate(fighterPrefab, pos, rot, transform);
        var agent = fighter.GetComponent<NavMeshAgent>();
        agent.areaMask = NavMesh.AllAreas;
        agent.Warp(pos);
        fighter.Bind(dna, team, kits, tuning, creatureDatabase, visualBank, furDatabase);
        fighter.Frozen = true;
        fighters.Add(fighter);

        BrawlFx.Emit(new BrawlFxEvent { Kind = BrawlFxKind.Spawn, To = pos, Theme = fighter.WingTheme, Team = team });
    }

    private void SetPhase(BrawlMatchPhase phase)
    {
        Phase = phase;
        phaseStartedAt = Time.time;
        OnPhaseChanged?.Invoke(phase);
    }

    private void BeginFight()
    {
        foreach (var fighter in fighters)
            if (fighter != null) fighter.Frozen = false;
        SetPhase(BrawlMatchPhase.Fight);
    }

    private void UpdateFight()
    {
        float dt = Time.deltaTime;
        fightElapsed += dt;
        TimeLeft = Mathf.Max(0f, TimeLeft - dt);
        if (TryEnd()) return;
        if (TimeLeft > 0f) return;

        foreach (var fighter in fighters)
            if (fighter != null) fighter.HealFactor = tuning.SuddenDeathHealFactor;
        reachedSuddenDeath = true;
        SetPhase(BrawlMatchPhase.SuddenDeath);
    }

    private void UpdateSuddenDeath()
    {
        float dt = Time.deltaTime;
        fightElapsed += dt;
        SuddenDeathElapsed += dt;

        float fraction = tuning.SuddenDeathStart + tuning.SuddenDeathRamp * SuddenDeathElapsed;
        foreach (var fighter in fighters)
        {
            if (fighter == null || !fighter.IsAlive) continue;
            fighter.TakeDamage(new BrawlHit { Amount = fighter.MaxHp * fraction * dt, IsDrain = true, Point = fighter.Center });
        }

        TryEnd();
    }

    private bool TryEnd()
    {
        int blue = AliveOf(ExpeditionTeam.Player);
        int red = AliveOf(ExpeditionTeam.Rival);
        if (blue > 0 && red > 0) return false;

        Winner = blue > 0 ? ExpeditionTeam.Player : red > 0 ? ExpeditionTeam.Rival : ExpeditionTeam.None;
        foreach (var fighter in fighters)
            if (fighter != null) fighter.Frozen = true;

        SetPhase(BrawlMatchPhase.Ended);
        LogEnd(blue, red);
        OnMatchEnded?.Invoke(Winner);
        return true;
    }

    private int AliveOf(ExpeditionTeam team)
    {
        int count = 0;
        foreach (var fighter in fighters)
            if (fighter != null && fighter.Team == team && fighter.IsAlive) count++;
        return count;
    }

    private void LogStart()
    {
        string paletteName = palette != null && palette.Current != null ? palette.Current.DisplayName : "";
        var sb = new StringBuilder();
        sb.Append($"[BrawlMatch] partida {MatchIndex} semilla {Seed} {layout.ShapeName}/{paletteName}, roster:");
        ExpeditionTeam previous = ExpeditionTeam.None;
        foreach (var fighter in fighters)
        {
            if (previous != ExpeditionTeam.None && fighter.Team != previous) sb.Append(" |");
            previous = fighter.Team;
            sb.Append($" {fighter.DisplayName}({PartName(fighter.WingTheme, fighter.DNA.WingID)}/{PartName(fighter.HornTheme, fighter.DNA.HornID)}/{PartName(fighter.BackTheme, fighter.DNA.BackID)})");
        }
        Debug.Log(sb.ToString());
    }

    private void LogEnd(int blue, int red)
    {
        var sb = new StringBuilder();
        sb.Append($"[BrawlMatch] fin partida {MatchIndex}: gana {TeamName(Winner)} en {fightElapsed:0.0} s, vivos azul {blue} rojo {red}, muerte súbita {(reachedSuddenDeath ? "sí" : "no")}");
        foreach (var fighter in fighters)
        {
            if (fighter == null) continue;
            sb.Append($"\n  {TeamName(fighter.Team)} {fighter.DisplayName}: ala {PartName(fighter.WingTheme, fighter.DNA.WingID)}, cuerno {PartName(fighter.HornTheme, fighter.DNA.HornID)}, espalda {PartName(fighter.BackTheme, fighter.DNA.BackID)}, daño {Mathf.RoundToInt(fighter.DamageDealt)}, curación {Mathf.RoundToInt(fighter.HealingDone)}, KOs {fighter.KOs}, vivo {(fighter.IsAlive ? "sí" : "no")}");
        }
        Debug.Log(sb.ToString());
    }

    private static string PartName(BrawlTheme theme, string id) => string.IsNullOrEmpty(theme.Label) ? id : theme.Label;

    private static string TeamName(ExpeditionTeam team) =>
        team == ExpeditionTeam.Player ? "azul" : team == ExpeditionTeam.Rival ? "rojo" : "empate";
}
}
