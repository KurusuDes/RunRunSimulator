using System.Collections.Generic;
using System.Globalization;
using System.Text;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BrawlBalanceRecorder : MonoBehaviour
{
    public const string MatchHeader = "batch;seed;mirror;winner;duration;sudden;suddenAt;firstKoTeam;comeback;lastStandTeam;lastStandWon;kos;blueAlive;redAlive;timeout;real\n";
    public const string FighterHeader = "batch;seed;mirror;team;won;name;body;bold;social;posture;wing;wingTitle;horn;hornTitle;hornFamily;hornRole;back;backTitle;backFamily;backRole;maxHp;dmg;dmgWing;dmgHorn;dmgBack;taken;heal;selfHeal;healTaken;shieldTaken;kos;alive;deathAt;attacks;healShots;mobility;hornUses;backUses;lastStand;wingPart;hornPart;backPart\n";

    private class Stat
    {
        public BrawlFighter Fighter;
        public ExpeditionTeam Team;
        public float DmgWing;
        public float DmgHorn;
        public float DmgBack;
        public float Taken;
        public float SelfHeal;
        public float HealTaken;
        public float ShieldTaken;
        public float DeathAt = -1f;
        public int Attacks;
        public int HealShots;
        public int Mobility;
        public int HornUses;
        public int BackUses;
        public int LastStand;
        public float Dmg;
        public float Heal;
        public int Kos;
        public bool Alive;
    }

    private readonly Dictionary<BrawlFighter, Stat> byFighter = new();
    private readonly List<Stat> stats = new();
    private readonly List<string> row = new();

    private string batch = "";
    private int seed;
    private int mirror;
    private bool armed;
    private float fightStart = -1f;
    private float duration;
    private bool sudden;
    private float suddenAt;
    private int totalKos;
    private bool timedOut;
    private ExpeditionTeam winner;
    private ExpeditionTeam firstKoTeam;
    private ExpeditionTeam lastStandTeam;

    public bool Done { get; private set; }
    public float FightSeconds => fightStart < 0f ? 0f : Done ? duration : Time.time - fightStart;

    private void OnEnable()
    {
        BrawlMatch.OnPhaseChanged += HandlePhaseChanged;
        BrawlMatch.OnMatchEnded += HandleMatchEnded;
        BrawlMatch.OnRosterSpawned += HandleRosterSpawned;
        BrawlMatch.OnLastStand += HandleLastStand;
        BrawlFighter.OnDamaged += HandleDamaged;
        BrawlFighter.OnHealed += HandleHealed;
        BrawlFighter.OnShielded += HandleShielded;
        BrawlFighter.OnKnockedOut += HandleKnockedOut;
        BrawlSkillCaster.OnCastFired += HandleCastFired;
        BrawlWing.OnAttackFired += HandleAttackFired;
        BrawlWing.OnMobilityUsed += HandleMobilityUsed;
    }

    private void OnDisable()
    {
        BrawlMatch.OnPhaseChanged -= HandlePhaseChanged;
        BrawlMatch.OnMatchEnded -= HandleMatchEnded;
        BrawlMatch.OnRosterSpawned -= HandleRosterSpawned;
        BrawlMatch.OnLastStand -= HandleLastStand;
        BrawlFighter.OnDamaged -= HandleDamaged;
        BrawlFighter.OnHealed -= HandleHealed;
        BrawlFighter.OnShielded -= HandleShielded;
        BrawlFighter.OnKnockedOut -= HandleKnockedOut;
        BrawlSkillCaster.OnCastFired -= HandleCastFired;
        BrawlWing.OnAttackFired -= HandleAttackFired;
        BrawlWing.OnMobilityUsed -= HandleMobilityUsed;
    }

    public void Arm(string batchLabel, int matchSeed, int mirrorFlag)
    {
        stats.Clear();
        byFighter.Clear();
        batch = Clean(batchLabel);
        seed = matchSeed;
        mirror = mirrorFlag;
        fightStart = -1f;
        duration = 0f;
        sudden = false;
        suddenAt = 0f;
        totalKos = 0;
        timedOut = false;
        winner = ExpeditionTeam.None;
        firstKoTeam = ExpeditionTeam.None;
        lastStandTeam = ExpeditionTeam.None;
        Done = false;
        armed = true;
    }

    public void ForceFinish()
    {
        if (!armed) return;
        Finish(ExpeditionTeam.None, true);
    }

    public string MatchLine(float realSeconds)
    {
        int blue = 0;
        int red = 0;
        foreach (var stat in stats)
        {
            if (!stat.Alive) continue;
            if (stat.Team == ExpeditionTeam.Player) blue++;
            else if (stat.Team == ExpeditionTeam.Rival) red++;
        }

        bool comeback = winner != ExpeditionTeam.None && firstKoTeam != ExpeditionTeam.None && winner == firstKoTeam;
        bool lastStandWon = lastStandTeam != ExpeditionTeam.None && winner == lastStandTeam;

        return string.Join(";", batch, Int(seed), Int(mirror), winner.ToString(), Secs(duration), Flag(sudden),
            sudden ? Secs(suddenAt) : "", firstKoTeam.ToString(), Flag(comeback), lastStandTeam.ToString(),
            Flag(lastStandWon), Int(totalKos), Int(blue), Int(red), Flag(timedOut), Secs(realSeconds)) + "\n";
    }

    public string FighterLines()
    {
        var sb = new StringBuilder();
        foreach (var stat in stats)
        {
            var fighter = stat.Fighter;
            var dna = fighter.DNA;
            row.Clear();
            row.Add(batch);
            row.Add(Int(seed));
            row.Add(Int(mirror));
            row.Add(stat.Team.ToString());
            row.Add(winner == ExpeditionTeam.None ? "0.5" : winner == stat.Team ? "1" : "0");
            row.Add(Clean(fighter.DisplayName));
            row.Add(Clean(fighter.BodyLabel));
            row.Add(Dial(fighter.Brain.Boldness));
            row.Add(Dial(fighter.Brain.Sociability));
            row.Add(Clean(fighter.Brain.PostureLabel));
            row.Add(Clean(dna.WingID));
            row.Add(fighter.WingKit != null ? Clean(fighter.WingKit.Title) : "");
            AddSkill(dna.HornID, fighter.HornSkill);
            AddSkill(dna.BackID, fighter.BackSkill);
            row.Add(Amount(fighter.MaxHp));
            row.Add(Amount(stat.Dmg));
            row.Add(Amount(stat.DmgWing));
            row.Add(Amount(stat.DmgHorn));
            row.Add(Amount(stat.DmgBack));
            row.Add(Amount(stat.Taken));
            row.Add(Amount(stat.Heal));
            row.Add(Amount(stat.SelfHeal));
            row.Add(Amount(stat.HealTaken));
            row.Add(Amount(stat.ShieldTaken));
            row.Add(Int(stat.Kos));
            row.Add(Flag(stat.Alive));
            row.Add(stat.DeathAt < 0f ? "" : Secs(stat.DeathAt));
            row.Add(Int(stat.Attacks));
            row.Add(Int(stat.HealShots));
            row.Add(Int(stat.Mobility));
            row.Add(Int(stat.HornUses));
            row.Add(Int(stat.BackUses));
            row.Add(Int(stat.LastStand));
            row.Add(Clean(fighter.WingTheme.Label));
            row.Add(Clean(fighter.HornTheme.Label));
            row.Add(Clean(fighter.BackTheme.Label));
            sb.Append(string.Join(";", row)).Append('\n');
        }
        return sb.ToString();
    }

    private void AddSkill(string partId, BrawlSkillSO skill)
    {
        row.Add(Clean(partId));
        row.Add(skill != null ? Clean(skill.Title) : "");
        row.Add(skill != null ? skill.Family.ToString() : "");
        row.Add(skill != null ? skill.Role.ToString() : "");
    }

    private void Finish(ExpeditionTeam result, bool timeout)
    {
        duration = FightSeconds;
        winner = result;
        timedOut = timeout;
        foreach (var stat in stats)
        {
            var fighter = stat.Fighter;
            stat.Dmg = fighter.DamageDealt;
            stat.Heal = fighter.HealingDone;
            stat.Kos = fighter.KOs;
            stat.Alive = fighter.IsAlive;
        }
        armed = false;
        Done = true;
    }

    private bool Track(BrawlFighter fighter, out Stat stat)
    {
        stat = null;
        return armed && fighter != null && byFighter.TryGetValue(fighter, out stat);
    }

    private void HandleRosterSpawned(IReadOnlyList<BrawlFighter> fighters)
    {
        if (!armed) return;
        stats.Clear();
        byFighter.Clear();
        foreach (var fighter in fighters)
        {
            if (fighter == null) continue;
            var stat = new Stat { Fighter = fighter, Team = fighter.Team };
            stats.Add(stat);
            byFighter[fighter] = stat;
        }
    }

    private void HandlePhaseChanged(BrawlMatchPhase phase)
    {
        if (!armed) return;
        if (phase == BrawlMatchPhase.Fight)
        {
            fightStart = Time.time;
        }
        else if (phase == BrawlMatchPhase.SuddenDeath)
        {
            sudden = true;
            suddenAt = Time.time - fightStart;
        }
    }

    private void HandleMatchEnded(ExpeditionTeam result)
    {
        if (!armed) return;
        Finish(result, false);
    }

    private void HandleDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (Track(victim, out var target)) target.Taken += hit.Amount;
        if (hit.IsDrain || !Track(hit.Source, out var source)) return;

        if (!hit.FromSkill) source.DmgWing += hit.Amount;
        else if (SameTheme(hit.Theme, hit.Source.HornTheme)) source.DmgHorn += hit.Amount;
        else if (SameTheme(hit.Theme, hit.Source.BackTheme)) source.DmgBack += hit.Amount;
        else if (hit.Source.BackSkill != null) source.DmgBack += hit.Amount;
        else source.DmgHorn += hit.Amount;
    }

    private void HandleHealed(BrawlFighter target, float amount, BrawlFighter source)
    {
        if (Track(source, out var healer) && source == target) healer.SelfHeal += amount;
        if (Track(target, out var patient)) patient.HealTaken += amount;
    }

    private void HandleShielded(BrawlFighter target, float amount)
    {
        if (Track(target, out var stat)) stat.ShieldTaken += amount;
    }

    private void HandleKnockedOut(BrawlFighter victim, BrawlFighter killer)
    {
        if (!Track(victim, out var stat)) return;
        stat.DeathAt = Time.time - fightStart;
        if (firstKoTeam == ExpeditionTeam.None) firstKoTeam = victim.Team;
        totalKos++;
    }

    private void HandleLastStand(BrawlFighter survivor)
    {
        if (!Track(survivor, out var stat)) return;
        stat.LastStand = 1;
        if (lastStandTeam == ExpeditionTeam.None) lastStandTeam = survivor.Team;
    }

    private void HandleCastFired(BrawlFighter caster, BrawlSkillSO skill, Vector3 aim)
    {
        if (!Track(caster, out var stat)) return;
        if (skill == caster.HornSkill) stat.HornUses++;
        else if (skill == caster.BackSkill) stat.BackUses++;
    }

    private void HandleAttackFired(BrawlFighter attacker, BrawlWingKitSO kit, Vector3 aim, bool healing)
    {
        if (!Track(attacker, out var stat)) return;
        stat.Attacks++;
        if (healing) stat.HealShots++;
    }

    private void HandleMobilityUsed(BrawlFighter mover, BrawlMobilityKind kind)
    {
        if (Track(mover, out var stat)) stat.Mobility++;
    }

    private static bool SameTheme(BrawlTheme a, BrawlTheme b) => a.Label == b.Label && a.Icon == b.Icon;

    private static string Clean(string value) =>
        string.IsNullOrEmpty(value) ? "" : value.Replace(';', ' ').Replace('\r', ' ').Replace('\n', ' ');

    private static string Int(int value) => value.ToString(CultureInfo.InvariantCulture);

    private static string Amount(float value) => Mathf.RoundToInt(value).ToString(CultureInfo.InvariantCulture);

    private static string Secs(float value) => value.ToString("0.00", CultureInfo.InvariantCulture);

    private static string Dial(float value) => value.ToString("0.000", CultureInfo.InvariantCulture);

    private static string Flag(bool value) => value ? "1" : "0";
}
}
