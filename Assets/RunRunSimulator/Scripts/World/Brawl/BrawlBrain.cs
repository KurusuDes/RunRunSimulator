using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

namespace MoriMonchiSimulator
{

public class BrawlBrain : MonoBehaviour
{
    [SerializeField, Min(0.05f)] private float thinkInterval = 0.2f;
    [SerializeField, Min(0f)] private float closeRange = 2.6f;
    [SerializeField, Min(0f)] private float switchMargin = 1.5f;
    [SerializeField] private Vector2 hpWeight = new Vector2(6f, 2f);
    [SerializeField, Min(0f)] private float threatWeight = 4f;
    [SerializeField, Min(0f)] private float threatRadius = 3.5f;
    [SerializeField, Min(0f)] private float retreatFoeRange = 6f;
    [SerializeField, Min(0f)] private float retreatRelease = 2f;
    [SerializeField, Min(0f)] private float retreatDistance = 6f;
    [SerializeField, Min(0f)] private float healStandoff = 0.7f;
    [SerializeField, Min(0f)] private float hookExtraRange = 2f;
    [SerializeField, Min(0f)] private float escapeFoeRange = 2.5f;
    [SerializeField, Min(0f)] private float escapeDistance = 5f;
    [SerializeField, Range(0f, 1f)] private float meleeStrafeScale = 0.4f;

    private const float PostureHigh = 0.65f;
    private const float PostureLow = 0.35f;
    private const float HookBoldness = 0.45f;
    private const float CohesionStart = 0.5f;
    private const float CohesionBlend = 0.8f;
    private const float EngageDistanceFactor = 1.3f;
    private const float MinCentroidGap = 2f;
    private const float NavSnapRadius = 2.5f;
    private const float AnyHp = 1.01f;

    private readonly List<BrawlFighter> buffer = new();
    private readonly float[] readySince = { -1f, -1f };

    private BrawlFighter me;
    private BrawlTuningSO tuning;
    private BrawlFighter target;
    private BrawlIntent intent;
    private string postureLabel = "";
    private float boldness = 0.5f;
    private float sociability = 0.5f;
    private float thinkTimer;
    private float strafeSign = 1f;
    private float strafeFlipAt;
    private bool retreating;

    public BrawlFighter Target => target;
    public BrawlIntent Intent => intent;
    public string PostureLabel => postureLabel;
    public float Boldness => boldness;
    public float Sociability => sociability;

    public void Init(BrawlFighter owner, BrawlTuningSO tuningSo)
    {
        me = owner;
        tuning = tuningSo;
        var dna = owner.DNA;
        boldness = dna != null ? Mathf.Clamp01(dna.Boldness) : 0.5f;
        sociability = dna != null ? Mathf.Clamp01(dna.Sociability) : 0.5f;
        string stance = boldness >= PostureHigh ? "Osado" : boldness <= PostureLow ? "Cauto" : "Templado";
        string bond = sociability >= PostureHigh ? "protector" : sociability <= PostureLow ? "solitario" : "de equipo";
        postureLabel = stance + " · " + bond;
        target = null;
        intent = BrawlIntent.Idle;
        retreating = false;
        readySince[0] = -1f;
        readySince[1] = -1f;
        thinkTimer = Random.Range(0f, thinkInterval);
        strafeSign = Random.value < 0.5f ? -1f : 1f;
        strafeFlipAt = Time.time + Random.Range(tuning.StrafeFlipSeconds.x, tuning.StrafeFlipSeconds.y);
    }

    public bool Impatient(int slot)
    {
        if (tuning == null || slot < 0 || slot >= readySince.Length) return false;
        return readySince[slot] >= 0f && Time.time - readySince[slot] > tuning.PatienceSeconds;
    }

    private void Update()
    {
        if (me == null || tuning == null) return;
        if (!me.IsAlive || me.Frozen)
        {
            GoIdle();
            return;
        }
        if (me.Motor.IsForced || me.Caster.IsCasting || me.Wing.IsWindingUp)
        {
            if (me.Caster.IsCasting) intent = BrawlIntent.Cast;
            return;
        }
        thinkTimer -= Time.deltaTime;
        if (thinkTimer > 0f) return;
        thinkTimer = thinkInterval;
        Think();
    }

    private void GoIdle()
    {
        if (intent == BrawlIntent.Idle) return;
        intent = BrawlIntent.Idle;
        me.Motor.Stop();
    }

    private void Think()
    {
        var kit = me.WingKit;
        if (kit == null) return;
        TrackReadiness();
        if (TryCastSkill()) return;
        if (Time.time >= strafeFlipAt)
        {
            strafeSign = -strafeSign;
            strafeFlipAt = Time.time + Random.Range(tuning.StrafeFlipSeconds.x, tuning.StrafeFlipSeconds.y);
        }
        float range = kit.Range;
        if (kit.AllyHeal > 0f && TryHealAlly(kit, range)) return;
        if (!SelectTarget())
        {
            retreating = false;
            GoIdle();
            return;
        }
        bool melee = kit.Attack == BrawlAttackKind.Melee || range < closeRange;
        float dist = BrawlQuery.Planar(me.Position, target.Position);
        retreating = ShouldRetreat();
        if (retreating) Retreat(kit);
        else Reposition(kit, dist, range, melee);
        if (dist > range + target.Radius) return;
        if (!melee && !BrawlQuery.HasLineOfSight(me.Position, target.Position)) return;
        me.Wing.TryAttack(target);
    }

    private void TrackReadiness()
    {
        for (int i = 0; i < readySince.Length; i++)
        {
            if (!me.Caster.IsReady(i)) readySince[i] = -1f;
            else if (readySince[i] < 0f) readySince[i] = Time.time;
        }
    }

    private bool TryCastSkill()
    {
        for (int slot = 0; slot < readySince.Length; slot++)
        {
            if (!me.Caster.IsReady(slot)) continue;
            if (!BrawlSkillJudge.Want(me, this, slot, tuning, out var foe, out var aim)) continue;
            if (!me.Caster.TryCast(slot, foe, aim)) continue;
            readySince[slot] = -1f;
            intent = BrawlIntent.Cast;
            return true;
        }
        return false;
    }

    private bool TryHealAlly(BrawlWingKitSO kit, float range)
    {
        float below = Mathf.Lerp(kit.HealBelow - 0.1f, kit.HealBelow + 0.15f, sociability);
        var ally = BrawlQuery.LowestAlly(me, range + 3f, false, below);
        if (ally == null) return false;
        intent = BrawlIntent.Heal;
        var foe = BrawlQuery.NearestFoeTo(ally.Position, me.Team, float.PositiveInfinity);
        Vector3 side = foe != null ? Flat(ally.Position - foe.Position) : Flat(me.Position - ally.Position);
        MoveToward(ally.Position + side * range * healStandoff);
        me.Motor.LookAt = ally.Position;
        me.Wing.TryAttack(ally);
        return true;
    }

    private bool SelectTarget()
    {
        var taunter = me.Taunter;
        if (taunter != null)
        {
            target = taunter;
            return true;
        }
        Vector3 centroid = BrawlQuery.AlliesCentroid(me, true, out _);
        var weakAlly = BrawlQuery.LowestAlly(me, float.PositiveInfinity, false, AnyHp);
        BrawlFighter best = null;
        float bestScore = float.MaxValue;
        var all = BrawlFighter.All;
        for (int i = 0; i < all.Count; i++)
        {
            var foe = all[i];
            if (!foe.IsAlive || !BrawlQuery.AreFoes(me, foe)) continue;
            float score = Score(foe, centroid, weakAlly);
            if (score >= bestScore) continue;
            best = foe;
            bestScore = score;
        }
        if (best == null)
        {
            target = null;
            return false;
        }
        bool keep = target != null && target.IsAlive && BrawlQuery.AreFoes(me, target)
            && Score(target, centroid, weakAlly) - switchMargin <= bestScore;
        if (!keep) target = best;
        return true;
    }

    private float Score(BrawlFighter foe, Vector3 centroid, BrawlFighter weakAlly)
    {
        float dSelf = BrawlQuery.Planar(me.Position, foe.Position);
        float dTeam = BrawlQuery.Planar(centroid, foe.Position);
        bool threat = weakAlly != null && BrawlQuery.Planar(weakAlly.Position, foe.Position) <= threatRadius;
        return Mathf.Lerp(dSelf, dTeam, sociability)
            + foe.Hp01 * Mathf.Lerp(hpWeight.x, hpWeight.y, sociability)
            - (threat ? threatWeight * sociability : 0f);
    }

    private bool ShouldRetreat()
    {
        float limit = Mathf.Lerp(tuning.RetreatHp.x, tuning.RetreatHp.y, boldness);
        if (me.Hp01 >= limit) return false;
        if (BrawlQuery.AliveCount(me.Team) <= 1) return false;
        float reach = retreating ? retreatFoeRange + retreatRelease : retreatFoeRange;
        return BrawlQuery.NearestFoe(me, reach) != null;
    }

    private void Retreat(BrawlWingKitSO kit)
    {
        intent = BrawlIntent.Retreat;
        Vector3 centroid = BrawlQuery.AlliesCentroid(me, false, out int allies);
        Vector3 destination = allies > 0 && BrawlQuery.Planar(me.Position, centroid) > MinCentroidGap
            ? centroid
            : me.Position + Flat(me.Position - target.Position) * retreatDistance;
        if (IsRetreatMove(kit.Mobility)) me.Wing.TryMobility(destination);
        MoveToward(destination);
        me.Motor.LookAt = null;
    }

    private void Reposition(BrawlWingKitSO kit, float dist, float range, bool melee)
    {
        float pref = melee ? range * 0.75f : range * Mathf.Lerp(tuning.PreferredRange.x, tuning.PreferredRange.y, boldness);
        float angle = tuning.StrafeAngle * strafeSign * (melee ? meleeStrafeScale : 1f);
        Vector3 dir = Quaternion.AngleAxis(angle, Vector3.up) * Flat(me.Position - target.Position);
        Vector3 point = target.Position + dir * pref;
        Vector3 centroid = BrawlQuery.AlliesCentroid(me, false, out int allies);
        if (sociability > CohesionStart && allies > 0)
            point = Vector3.Lerp(point, centroid, (sociability - CohesionStart) * CohesionBlend);
        MoveToward(point);
        me.Motor.LookAt = target.Position;
        intent = ChooseIntent(dist, range, melee);
        TryMobilityMove(kit.Mobility, dist, range);
    }

    private BrawlIntent ChooseIntent(float dist, float range, bool melee)
    {
        if (sociability >= PostureHigh && AllyNear(target.Position)) return BrawlIntent.Protect;
        if (dist > range * EngageDistanceFactor) return sociability < CohesionStart ? BrawlIntent.Hunt : BrawlIntent.Engage;
        return melee ? BrawlIntent.Engage : BrawlIntent.Kite;
    }

    private bool AllyNear(Vector3 point)
    {
        BrawlQuery.AlliesWithin(point, threatRadius, me.Team, buffer);
        for (int i = 0; i < buffer.Count; i++)
            if (buffer[i] != me && buffer[i].IsAlive) return true;
        return false;
    }

    private void TryMobilityMove(BrawlMobilityKind mobility, float dist, float range)
    {
        if (boldness >= HookBoldness)
        {
            if (IsHookMove(mobility) && dist > range + hookExtraRange) me.Wing.TryMobility(target.Position);
            return;
        }
        if (!IsEscapeMove(mobility)) return;
        var near = BrawlQuery.NearestFoe(me, escapeFoeRange);
        if (near == null) return;
        me.Wing.TryMobility(me.Position + Flat(me.Position - near.Position) * escapeDistance);
    }

    private void MoveToward(Vector3 point)
    {
        if (NavMesh.SamplePosition(point, out var hit, NavSnapRadius, NavMesh.AllAreas))
            me.Motor.MoveTo(hit.position);
    }

    private Vector3 Flat(Vector3 v)
    {
        v.y = 0f;
        if (v.sqrMagnitude < 0.0001f)
        {
            v = -me.transform.forward;
            v.y = 0f;
        }
        return v.normalized;
    }

    private static bool IsRetreatMove(BrawlMobilityKind k) =>
        k is BrawlMobilityKind.Roll or BrawlMobilityKind.Hop or BrawlMobilityKind.Blink or BrawlMobilityKind.Glide or BrawlMobilityKind.Sprint;

    private static bool IsHookMove(BrawlMobilityKind k) =>
        k is BrawlMobilityKind.Leap or BrawlMobilityKind.Blink or BrawlMobilityKind.Glide or BrawlMobilityKind.Sprint;

    private static bool IsEscapeMove(BrawlMobilityKind k) =>
        k is BrawlMobilityKind.Roll or BrawlMobilityKind.Hop or BrawlMobilityKind.Blink or BrawlMobilityKind.Glide;
}

}
