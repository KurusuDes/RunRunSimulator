using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Random = UnityEngine.Random;

namespace MoriMonchiSimulator
{

public class BrawlWing : MonoBehaviour
{
    private const float MeleeComboGap = 0.12f;
    private const float BurstGap = 0.09f;
    private const float LeapLandRadius = 1.8f;
    private const float LeapLandKnockback = 4f;

    private static readonly WaitForSeconds MeleeWait = new WaitForSeconds(MeleeComboGap);
    private static readonly WaitForSeconds BurstWait = new WaitForSeconds(BurstGap);

    public static event Action<BrawlFighter, BrawlWingKitSO, Vector3, bool> OnAttackFired;
    public static event Action<BrawlFighter, BrawlMobilityKind> OnMobilityUsed;

    private readonly List<BrawlFighter> buffer = new List<BrawlFighter>();

    private BrawlFighter owner;
    private BrawlWingKitSO kit;
    private float attackReadyAt;
    private float mobilityReadyAt;
    private bool windingUp;
    private float windupEndAt;
    private BrawlFighter windupTarget;
    private Coroutine routine;
    private bool comboActive;

    public bool IsWindingUp => windingUp;
    public float Windup01 => windingUp && kit != null && kit.Windup > 0f
        ? Mathf.Clamp01(1f - (windupEndAt - Time.time) / kit.Windup)
        : 0f;
    public Vector3 AimPoint { get; private set; }
    public Vector3 AimDir { get; private set; } = Vector3.forward;
    public bool AimHealing { get; private set; }
    public bool AttackReady => kit != null && Time.time >= attackReadyAt;
    public float Attack01 => kit == null || kit.Reload <= 0f
        ? 1f
        : 1f - Mathf.Clamp01((attackReadyAt - Time.time) / kit.Reload);
    public bool MobilityReady => kit != null && Time.time >= mobilityReadyAt;
    public float Mobility01 => kit == null || kit.MobilityCooldown <= 0f
        ? 1f
        : 1f - Mathf.Clamp01((mobilityReadyAt - Time.time) / kit.MobilityCooldown);

    public void Init(BrawlFighter fighter)
    {
        Cancel();
        owner = fighter;
        kit = fighter.WingKit;
        attackReadyAt = Time.time + Random.Range(0f, kit.Reload);
        mobilityReadyAt = Time.time + kit.MobilityCooldown * 0.5f;
        AimHealing = false;
        AimPoint = fighter.Position;
        AimDir = Forward();
    }

    private void OnDisable() => Cancel();

    private void Update()
    {
        if (!windingUp) return;
        if (!Running())
        {
            Cancel();
            return;
        }

        if (windupTarget != null && windupTarget.IsAlive)
        {
            AimPoint = windupTarget.Position;
            AimDir = Flat(AimPoint - owner.Position, AimDir);
            owner.Motor.LookAt = AimPoint;
        }

        if (Time.time >= windupEndAt) Execute();
    }

    public bool TryAttack(BrawlFighter target)
    {
        if (!CanAct() || windingUp || comboActive || Time.time < attackReadyAt) return false;
        if (target == null || !target.IsAlive) return false;

        bool healing = ExpeditionTeams.AreAllies(owner.Team, target.Team);
        if (healing ? kit.AllyHeal <= 0f || target == owner : !ExpeditionTeams.AreRivals(owner.Team, target.Team)) return false;
        if (BrawlQuery.Planar(owner.Position, target.Position) > kit.Range + target.Radius) return false;

        windupTarget = target;
        AimHealing = healing;
        AimPoint = target.Position;
        AimDir = Flat(AimPoint - owner.Position, Forward());
        owner.Motor.LookAt = target.Position;

        if (kit.Windup <= 0f)
        {
            Execute();
            return true;
        }

        windingUp = true;
        windupEndAt = Time.time + kit.Windup;
        return true;
    }

    public bool TryMobility(Vector3 desiredPoint)
    {
        if (!CanAct() || windingUp || Time.time < mobilityReadyAt) return false;

        Vector3 delta = desiredPoint - owner.Position;
        delta.y = 0f;
        float d = kit.MobilityDistance;
        float s = kit.MobilitySeconds;
        float dist = delta.magnitude;
        bool near = dist < 0.5f;
        Vector3 dir = near ? Flat(-owner.transform.forward, -Vector3.forward) : delta / dist;
        Vector3 start = owner.Position;

        switch (kit.Mobility)
        {
            case BrawlMobilityKind.Leap:
                owner.Motor.Leap(start + dir * (near ? d : Mathf.Min(d, dist)), s, 1.6f, OnLeapLanded);
                break;
            case BrawlMobilityKind.Sprint:
                owner.ApplyHaste(0.6f, s);
                Emit(BrawlFxKind.Pulse, start, start, 1.2f);
                break;
            case BrawlMobilityKind.Roll:
            case BrawlMobilityKind.Blink:
                owner.Motor.Dash(dir, d, s, null, null);
                Emit(BrawlFxKind.Dash, start, start + dir * d);
                break;
            case BrawlMobilityKind.Hop:
                owner.Motor.Leap(start + dir * d, s, 1.2f, null);
                break;
            case BrawlMobilityKind.Glide:
                owner.Motor.Leap(start + dir * d, s, 2.2f, null);
                break;
        }

        mobilityReadyAt = Time.time + kit.MobilityCooldown;
        OnMobilityUsed?.Invoke(owner, kit.Mobility);
        return true;
    }

    public void Cancel()
    {
        windingUp = false;
        windupTarget = null;
        comboActive = false;
        if (routine != null)
        {
            StopCoroutine(routine);
            routine = null;
        }
    }

    private bool Running() => owner != null && owner.IsAlive && !owner.Frozen;

    private bool CanAct() =>
        kit != null && Running() && !owner.IsStunned && !owner.Motor.IsForced && !owner.Caster.IsCasting;

    private void Execute()
    {
        windingUp = false;
        BrawlFighter target = windupTarget;
        windupTarget = null;

        Vector3 aim = AimPoint;
        if (target != null && target.IsAlive) aim = AimAt(target);
        AimPoint = aim;
        AimDir = Flat(aim - owner.Position, Forward());
        attackReadyAt = Time.time + kit.Reload;

        OnAttackFired?.Invoke(owner, kit, aim, AimHealing);

        switch (kit.Attack)
        {
            case BrawlAttackKind.Melee:
                comboActive = true;
                routine = StartCoroutine(MeleeRoutine(target));
                break;
            case BrawlAttackKind.Whip: FireWhip(); break;
            case BrawlAttackKind.Shotgun: FireShotgun(); break;
            case BrawlAttackKind.Sniper: FireSniper(); break;
            case BrawlAttackKind.Burst:
                comboActive = true;
                routine = StartCoroutine(BurstRoutine(target, AimHealing));
                break;
            case BrawlAttackKind.Boomerang: FireBoomerang(); break;
        }
    }

    private Vector3 AimAt(BrawlFighter target)
    {
        Vector3 pos = target.Position;
        bool leads = kit.Attack == BrawlAttackKind.Sniper
            || kit.Attack == BrawlAttackKind.Shotgun
            || kit.Attack == BrawlAttackKind.Burst;
        if (!leads || kit.ProjectileSpeed <= 0.01f) return pos;

        Vector3 velocity = target.Motor.Velocity;
        velocity.y = 0f;
        float dist = BrawlQuery.Planar(owner.Position, pos);
        return pos + velocity * (dist / kit.ProjectileSpeed);
    }

    private IEnumerator MeleeRoutine(BrawlFighter target)
    {
        int count = Mathf.Max(1, kit.Count);
        for (int i = 0; i < count; i++)
        {
            if (!Running()) break;
            Vector3 fwd = i > 0 && target != null && target.IsAlive
                ? Flat(target.Position - owner.Position, AimDir)
                : AimDir;
            MeleeStrike(fwd);
            if (i < count - 1) yield return MeleeWait;
        }
        comboActive = false;
    }

    private void MeleeStrike(Vector3 fwd)
    {
        Vector3 origin = owner.Position;
        BrawlQuery.FoesWithin(origin, kit.Range, owner.Team, buffer);
        for (int i = 0; i < buffer.Count; i++)
        {
            BrawlFighter foe = buffer[i];
            if (!foe.IsAlive || !BrawlQuery.InCone(origin, fwd, kit.Range, kit.Angle * 0.5f, foe)) continue;
            Strike(foe, kit.Damage, Flat(foe.Position - origin, fwd), kit.Knockback, true);
        }
        Emit(BrawlFxKind.Slash, origin, origin + fwd, kit.Range, kit.Angle);
    }

    private void FireWhip()
    {
        Vector3 origin = owner.Position;
        Vector3 dir = AimDir;
        Vector3 tip = origin + dir * kit.Range;

        BrawlQuery.FoesWithin(origin, kit.Range + kit.HitRadius, owner.Team, buffer);
        for (int i = 0; i < buffer.Count; i++)
        {
            BrawlFighter foe = buffer[i];
            if (!foe.IsAlive || !BrawlQuery.OnSegment(origin, tip, kit.HitRadius, foe)) continue;
            Strike(foe, kit.Damage, dir, kit.Knockback, false);
            if (kit.Slow > 0f) foe.ApplySlow(kit.Slow, kit.SlowSeconds);
        }

        Vector3 center = owner.Center;
        Emit(BrawlFxKind.Whip, center, new Vector3(tip.x, center.y, tip.z));
    }

    private void FireShotgun()
    {
        Vector3 origin = owner.Center;
        Vector3 dir = AimDir;
        int count = Mathf.Max(1, kit.Count);
        float half = kit.Spread * 0.5f;
        for (int i = 0; i < count; i++)
        {
            float angle = count > 1 ? Mathf.Lerp(-half, half, i / (float)(count - 1)) : 0f;
            angle += Random.Range(-2f, 2f);
            BrawlProjectile.Fire(NewShot(Rotate(dir, angle)));
        }
        Emit(BrawlFxKind.Muzzle, origin, origin + dir, 0f, kit.Spread);
    }

    private void FireSniper()
    {
        Vector3 origin = owner.Center;
        Vector3 dir = AimDir;
        BrawlProjectile.Fire(NewShot(dir));
        Emit(BrawlFxKind.Muzzle, origin, origin + dir, 0f, 8f);
    }

    private void FireBoomerang()
    {
        BrawlShot shot = NewShot(AimDir);
        shot.Boomerang = true;
        shot.Pierce = true;
        shot.Spin = 900f;
        BrawlProjectile.Fire(shot);
    }

    private IEnumerator BurstRoutine(BrawlFighter target, bool healing)
    {
        int count = Mathf.Max(1, kit.Count);
        float half = kit.Spread * 0.5f;
        for (int i = 0; i < count; i++)
        {
            if (!Running()) break;
            bool alive = target != null && target.IsAlive;
            if (healing && !alive) break;

            Vector3 dir = i > 0 && alive ? Flat(target.Position - owner.Position, AimDir) : AimDir;
            dir = Rotate(dir, Random.Range(-half, half));

            BrawlShot shot = NewShot(dir);
            if (healing)
            {
                shot.Damage = 0f;
                shot.Heal = kit.AllyHeal;
                shot.HealsAllies = true;
                shot.Homing = target;
                shot.HomingTurn = 720f;
            }
            else
            {
                shot.Homing = alive ? target : null;
                shot.HomingTurn = 120f;
            }
            BrawlProjectile.Fire(shot);

            if (i < count - 1) yield return BurstWait;
        }
        comboActive = false;
    }

    private BrawlShot NewShot(Vector3 dir)
    {
        Vector3 center = owner.Center;
        return new BrawlShot
        {
            Owner = owner,
            Team = owner.Team,
            Origin = center,
            Direction = dir,
            Speed = kit.ProjectileSpeed,
            Range = kit.Range,
            Damage = kit.Damage,
            Radius = kit.HitRadius,
            Knockback = kit.Knockback,
            Height = center.y - owner.Position.y,
            SpriteSize = kit.SpriteSize,
            Theme = owner.WingTheme
        };
    }

    private void OnLeapLanded()
    {
        if (owner == null || !owner.IsAlive) return;
        Vector3 pos = owner.Position;

        if (kit.MobilityDamage > 0f)
        {
            BrawlQuery.FoesWithin(pos, LeapLandRadius, owner.Team, buffer);
            for (int i = 0; i < buffer.Count; i++)
            {
                BrawlFighter foe = buffer[i];
                if (foe.IsAlive) Strike(foe, kit.MobilityDamage, Flat(foe.Position - pos, Forward()), LeapLandKnockback, false);
            }
        }

        Emit(BrawlFxKind.Ring, pos, pos, LeapLandRadius);
    }

    private void Strike(BrawlFighter foe, float amount, Vector3 knockDir, float knockback, bool melee)
    {
        foe.TakeDamage(new BrawlHit
        {
            Amount = amount, Source = owner, Point = foe.Center, KnockDir = knockDir,
            Knockback = knockback, Theme = owner.WingTheme, FromSkill = false, Melee = melee
        });
    }

    private void Emit(BrawlFxKind kind, Vector3 from, Vector3 to, float radius = 0f, float angle = 0f)
    {
        BrawlFx.Emit(new BrawlFxEvent
        {
            Kind = kind, From = from, To = to, Radius = radius, Angle = angle,
            Theme = owner.WingTheme, Team = owner.Team, Source = owner
        });
    }

    private Vector3 Forward()
    {
        return Flat(owner.transform.forward, Vector3.forward);
    }

    private static Vector3 Flat(Vector3 v, Vector3 fallback)
    {
        v.y = 0f;
        return v.sqrMagnitude > 0.0001f ? v.normalized : fallback;
    }

    private static Vector3 Rotate(Vector3 dir, float degrees)
    {
        return Quaternion.AngleAxis(degrees, Vector3.up) * dir;
    }
}

}
