using System;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{

public struct BrawlHit
{
    public float Amount;
    public BrawlFighter Source;
    public Vector3 Point;
    public Vector3 KnockDir;
    public float Knockback;
    public BrawlTheme Theme;
    public bool FromSkill;
    public bool Melee;
    public bool IsDrain;
}

public class BrawlFighter : MonoBehaviour
{
    [Required, SerializeField] private MonchiVisualizer visualizer;
    [Required, SerializeField] private BrawlMotor motor;
    [Required, SerializeField] private BrawlWing wing;
    [Required, SerializeField] private BrawlSkillCaster caster;
    [Required, SerializeField] private BrawlBrain brain;
    [SerializeField, Min(0.1f)] private float bodyRadius = 0.65f;
    [SerializeField, Min(0f)] private float centerHeight = 0.8f;

    private static readonly List<BrawlFighter> all = new();

    private float shieldPool;
    private float shieldUntil;
    private float slowValue;
    private float slowUntil;
    private float hasteValue;
    private float hasteUntil;
    private float boostValue;
    private float boostUntil;
    private float thornsValue;
    private float thornsUntil;
    private float stunUntil;
    private BrawlFighter taunter;
    private float tauntUntil;
    private bool frozen;

    public static IReadOnlyList<BrawlFighter> All => all;
    public static event Action<BrawlFighter> OnBound;
    public static event Action<BrawlFighter, BrawlHit> OnDamaged;
    public static event Action<BrawlFighter, float, BrawlFighter> OnHealed;
    public static event Action<BrawlFighter, float> OnShielded;
    public static event Action<BrawlFighter, BrawlFighter> OnKnockedOut;
    public static event Action<BrawlFighter, BrawlStatusKind, float> OnStatusApplied;

    public CreatureDNA DNA { get; private set; }
    public ExpeditionTeam Team { get; private set; }
    public string DisplayName => DNA != null && !string.IsNullOrEmpty(DNA.CustomName) ? DNA.CustomName : name;
    public BrawlWingKitSO WingKit { get; private set; }
    public BrawlSkillSO HornSkill { get; private set; }
    public BrawlSkillSO BackSkill { get; private set; }
    public BrawlTheme WingTheme { get; private set; }
    public BrawlTheme HornTheme { get; private set; }
    public BrawlTheme BackTheme { get; private set; }
    public string BodyLabel { get; private set; }
    public MonchiVisualizer Visualizer => visualizer;
    public BrawlMotor Motor => motor;
    public BrawlWing Wing => wing;
    public BrawlSkillCaster Caster => caster;
    public BrawlBrain Brain => brain;
    public float Radius => bodyRadius;
    public Vector3 Position => transform.position;
    public Vector3 Center => transform.position + Vector3.up * (centerHeight + Lift);
    public float MaxHp { get; private set; }
    public float Hp { get; private set; }
    public float Hp01 => MaxHp > 0f ? Hp / MaxHp : 0f;
    public float Shield => Time.time < shieldUntil ? shieldPool : 0f;
    public bool IsAlive => DNA != null && Hp > 0f;
    public bool IsStunned => IsAlive && Time.time < stunUntil;
    public float Lift { get; set; }
    public float BaseSpeed { get; private set; }
    public float HealFactor { get; set; } = 1f;
    public float RoundDamageFactor { get; set; } = 1f;
    public bool Frozen { get => frozen || Dummy; set => frozen = value; }
    public bool Dummy { get; set; }
    public float Power { get; private set; } = 1f;
    public BrawlFighter LastAttacker { get; private set; }
    public float LastHurtAt { get; private set; } = -1000f;
    public float DamageDealt { get; private set; }
    public float HealingDone { get; private set; }
    public int KOs { get; private set; }

    public float SpeedMultiplier
    {
        get
        {
            if (IsStunned)
                return 0f;
            float now = Time.time;
            float slow = now < slowUntil ? slowValue : 0f;
            float haste = now < hasteUntil ? hasteValue : 0f;
            return (1f - slow) * (1f + haste);
        }
    }

    public float DamageMultiplier => (1f + (Time.time < boostUntil ? boostValue : 0f)) * RoundDamageFactor * Power;

    public BrawlFighter Taunter => Time.time < tauntUntil && taunter != null && taunter.IsAlive ? taunter : null;

    private void OnDestroy()
    {
        all.Remove(this);
    }

    public void Bind(CreatureDNA dna, ExpeditionTeam team, BrawlKitDatabaseSO kits, BrawlTuningSO tuning, CreatureDatabaseSO parts, MonchiVisualBankSO bank, FurTypeDatabaseSO fur)
    {
        DNA = dna;
        Team = team;
        Power = 1f;
        Dummy = false;

        visualizer.SetBank(bank);
        visualizer.SetFurDatabase(fur);
        visualizer.Assemble(dna);

        var profile = BrawlKitProfile.Of(dna, kits, parts);
        WingKit = profile.Wing;
        HornSkill = profile.Horn;
        BackSkill = profile.Back;
        WingTheme = profile.WingTheme;
        HornTheme = profile.HornTheme;
        BackTheme = profile.BackTheme;

        var body = tuning.BodyFor(dna.BodyShapeID);
        MaxHp = tuning.BaseHp * body.HpMul;
        BaseSpeed = WingKit.MoveSpeed * body.SpeedMul;
        BodyLabel = body.Label;
        Hp = MaxHp;

        ResetState();

        if (!all.Contains(this))
            all.Add(this);

        motor.Init(this);
        wing.Init(this);
        caster.Init(this);
        brain.Init(this, tuning);

        OnBound?.Invoke(this);
    }

    public void Prime(float power, float health01)
    {
        Power = Mathf.Max(0.05f, power);
        MaxHp *= Power;
        Hp = Mathf.Clamp(MaxHp * Mathf.Clamp01(health01), 1f, MaxHp);
    }

    public void Despawn()
    {
        all.Remove(this);
    }

    public void TakeDamage(BrawlHit hit)
    {
        if (!IsAlive || hit.Amount <= 0f)
            return;

        float amount = hit.Amount * (hit.Source != null ? hit.Source.DamageMultiplier : 1f);

        float absorbed = 0f;
        if (Time.time < shieldUntil && shieldPool > 0f)
        {
            absorbed = Mathf.Min(shieldPool, amount);
            shieldPool -= absorbed;
            amount -= absorbed;
        }

        float applied = Mathf.Min(amount, Hp);
        Hp -= applied;

        if (hit.Source != null && !hit.IsDrain)
        {
            LastAttacker = hit.Source;
            LastHurtAt = Time.time;
            hit.Source.DamageDealt += applied;
        }

        if (Time.time < thornsUntil && hit.Melee && hit.Source != null && hit.Source.IsAlive)
        {
            hit.Source.TakeDamage(new BrawlHit
            {
                Amount = thornsValue,
                Source = this,
                Point = hit.Source.Center,
                Theme = BackTheme,
                FromSkill = true
            });
        }

        if (hit.Knockback > 0f && Hp > 0f)
            motor.Knock(hit.KnockDir, hit.Knockback);

        hit.Amount = applied + absorbed;
        OnDamaged?.Invoke(this, hit);

        if (Hp <= 0f)
        {
            Hp = 0f;
            wing.Cancel();
            caster.Interrupt();
            motor.Halt();
            if (hit.Source != null)
                hit.Source.KOs++;
            OnKnockedOut?.Invoke(this, hit.Source);
        }
    }

    public void Heal(float amount, BrawlFighter source)
    {
        if (!IsAlive)
            return;

        float real = Mathf.Min(amount * HealFactor, MaxHp - Hp);
        if (real <= 0f)
            return;

        Hp += real;
        if (source != null)
            source.HealingDone += real;
        if (real > 0.5f)
            OnHealed?.Invoke(this, real, source);
    }

    public void AddShield(float amount, float seconds)
    {
        if (!IsAlive || amount <= 0f || seconds <= 0f)
            return;

        shieldPool = Mathf.Max(Shield, amount);
        shieldUntil = Time.time + seconds;
        OnShielded?.Invoke(this, amount);
        OnStatusApplied?.Invoke(this, BrawlStatusKind.Shield, seconds);
    }

    public void ApplySlow(float fraction, float seconds)
    {
        fraction = Mathf.Clamp(fraction, 0f, 0.9f);
        if (!CanApply(fraction, seconds))
            return;

        KeepStronger(ref slowValue, ref slowUntil, fraction, seconds);
        OnStatusApplied?.Invoke(this, BrawlStatusKind.Slow, seconds);
    }

    public void ApplyStun(float seconds)
    {
        if (!CanApply(1f, seconds))
            return;

        stunUntil = Mathf.Max(stunUntil, Time.time + seconds);
        wing.Cancel();
        caster.Interrupt();
        OnStatusApplied?.Invoke(this, BrawlStatusKind.Stun, seconds);
    }

    public void ApplyHaste(float fraction, float seconds)
    {
        if (!CanApply(fraction, seconds))
            return;

        KeepStronger(ref hasteValue, ref hasteUntil, fraction, seconds);
        OnStatusApplied?.Invoke(this, BrawlStatusKind.Haste, seconds);
    }

    public void ApplyDamageBoost(float fraction, float seconds)
    {
        if (!CanApply(fraction, seconds))
            return;

        KeepStronger(ref boostValue, ref boostUntil, fraction, seconds);
        OnStatusApplied?.Invoke(this, BrawlStatusKind.Boost, seconds);
    }

    public void ApplyThorns(float damagePerHit, float seconds)
    {
        if (!CanApply(damagePerHit, seconds))
            return;

        KeepStronger(ref thornsValue, ref thornsUntil, damagePerHit, seconds);
        OnStatusApplied?.Invoke(this, BrawlStatusKind.Thorns, seconds);
    }

    public void ApplyTaunt(BrawlFighter by, float seconds)
    {
        if (by == null || !CanApply(1f, seconds))
            return;

        taunter = by;
        tauntUntil = Mathf.Max(tauntUntil, Time.time + seconds);
        OnStatusApplied?.Invoke(this, BrawlStatusKind.Taunt, seconds);
    }

    private bool CanApply(float value, float seconds)
    {
        return IsAlive && value > 0f && seconds > 0f;
    }

    private static void KeepStronger(ref float value, ref float until, float newValue, float seconds)
    {
        float now = Time.time;
        value = now < until ? Mathf.Max(value, newValue) : newValue;
        until = Mathf.Max(until, now + seconds);
    }

    private void ResetState()
    {
        shieldPool = 0f;
        shieldUntil = 0f;
        slowValue = 0f;
        slowUntil = 0f;
        hasteValue = 0f;
        hasteUntil = 0f;
        boostValue = 0f;
        boostUntil = 0f;
        thornsValue = 0f;
        thornsUntil = 0f;
        stunUntil = 0f;
        taunter = null;
        tauntUntil = 0f;
        LastAttacker = null;
        LastHurtAt = -1000f;
        DamageDealt = 0f;
        HealingDone = 0f;
        KOs = 0;
        Lift = 0f;
        HealFactor = 1f;
        RoundDamageFactor = 1f;
        Frozen = false;
    }
}
}
