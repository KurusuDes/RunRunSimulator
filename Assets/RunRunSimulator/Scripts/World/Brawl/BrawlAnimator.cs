using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BrawlAnimator : MonoBehaviour
{
    private const string IdleState = "Idle";
    private const string WalkState = "Walk";
    private const string RunState = "Run";
    private const string FlyState = "Fly";
    private const string SickState = "Sick";
    private const string DamageState = "Damage";
    private const string DieState = "Die";
    private const string JumpState = "Jump";
    private const string RoarState = "Roar";
    private const float FireLockSeconds = 0.3f;
    private const float CastFireLockSeconds = 0.35f;
    private const float DamageLockSeconds = 0.25f;
    private const float VictoryInterval = 1.2f;
    private const float HealMoodSeconds = 1f;
    private const float ScaredHp01 = 0.3f;

    [Required, SerializeField] private BrawlFighter fighter;
    [Required, SerializeField] private MonchiVisualizer visualizer;
    [Required, SerializeField] private BrawlMotor motor;
    [SerializeField] private float walkThreshold = 0.2f;
    [SerializeField] private float runThreshold = 2.6f;
    [SerializeField] private float crossFade = 0.15f;
    [SerializeField] private float actionCrossFade = 0.06f;
    [SerializeField] private float hitStopMinDamage = 600f;
    [SerializeField] private float hitStopSeconds = 0.05f;
    [SerializeField] private float heavyHitStopDamage = 1500f;
    [SerializeField] private float heavyHitStopSeconds = 0.1f;

    private readonly Dictionary<string, bool> hasStateCache = new();
    private Animator lastAnimator;
    private Animator frozenAnimator;
    private float freezeUntil;
    private string currentState = "";
    private float actionUntil;
    private bool dead;
    private bool victory;
    private bool victoryJump;
    private float nextVictoryAt;
    private float lastHealAt = -999f;
    private bool moodShown;
    private MonchiMood shownMood;

    private void OnEnable()
    {
        BrawlFighter.OnBound += HandleBound;
        BrawlFighter.OnDamaged += HandleDamaged;
        BrawlFighter.OnHealed += HandleHealed;
        BrawlFighter.OnKnockedOut += HandleKnockedOut;
        BrawlWing.OnAttackFired += HandleAttackFired;
        BrawlSkillCaster.OnCastStarted += HandleCastStarted;
        BrawlSkillCaster.OnCastFired += HandleCastFired;
        BrawlMatch.OnMatchEnded += HandleMatchEnded;
    }

    private void OnDisable()
    {
        BrawlFighter.OnBound -= HandleBound;
        BrawlFighter.OnDamaged -= HandleDamaged;
        BrawlFighter.OnHealed -= HandleHealed;
        BrawlFighter.OnKnockedOut -= HandleKnockedOut;
        BrawlWing.OnAttackFired -= HandleAttackFired;
        BrawlSkillCaster.OnCastStarted -= HandleCastStarted;
        BrawlSkillCaster.OnCastFired -= HandleCastFired;
        BrawlMatch.OnMatchEnded -= HandleMatchEnded;

        freezeUntil = 0f;
        ReleaseFreeze();
    }

    private void Update()
    {
        if (fighter.DNA == null) return;

        UpdateMood();

        var anim = CurrentAnimator();
        UpdateFreeze(anim);
        if (anim == null || !anim.isActiveAndEnabled) return;
        if (dead || !fighter.IsAlive) return;
        if (Time.time < actionUntil) return;

        if (victory && Time.time >= nextVictoryAt)
        {
            nextVictoryAt = Time.time + VictoryInterval;
            bool jump = victoryJump;
            victoryJump = !victoryJump;
            if (Play(jump ? JumpState : RoarState, VictoryInterval)) return;
        }

        string target = LocomotionState(anim);
        if (target == currentState || !HasState(anim, target)) return;
        anim.CrossFadeInFixedTime(target, crossFade);
        currentState = target;
    }

    private string LocomotionState(Animator anim)
    {
        if (fighter.IsStunned) return HasState(anim, SickState) ? SickState : IdleState;
        if (motor.IsLeaping) return FlyState;

        var kit = fighter.WingKit;
        if (kit != null && kit.Locomotion == BrawlLocomotion.Hover) return FlyState;

        float speed = motor.Velocity.magnitude;
        if (speed >= runThreshold) return RunState;
        return speed >= walkThreshold ? WalkState : IdleState;
    }

    private void UpdateMood()
    {
        MonchiMood mood;
        if (dead || !fighter.IsAlive) mood = MonchiMood.KO;
        else if (fighter.IsStunned) mood = MonchiMood.Mareado;
        else if (fighter.Caster != null && fighter.Caster.IsCasting) mood = MonchiMood.Enojado;
        else if (victory) mood = MonchiMood.Emocionado;
        else if (fighter.Hp01 < ScaredHp01) mood = MonchiMood.Asustado;
        else if (Time.time - lastHealAt <= HealMoodSeconds) mood = MonchiMood.Feliz;
        else mood = MonchiMood.Neutral;

        if (moodShown && mood == shownMood) return;
        moodShown = true;
        shownMood = mood;
        visualizer.SetMood(mood);
    }

    private bool Play(string state, float lockSeconds)
    {
        if (string.IsNullOrEmpty(state)) return false;
        var anim = CurrentAnimator();
        if (anim == null || !anim.isActiveAndEnabled || !HasState(anim, state)) return false;
        anim.CrossFadeInFixedTime(state, actionCrossFade);
        currentState = state;
        actionUntil = Time.time + lockSeconds;
        return true;
    }

    private Animator CurrentAnimator()
    {
        var anim = visualizer != null ? visualizer.Animator : null;
        if (anim != lastAnimator)
        {
            ReleaseFreeze();
            lastAnimator = anim;
            hasStateCache.Clear();
            currentState = "";
        }
        return anim;
    }

    private void UpdateFreeze(Animator anim)
    {
        bool freeze = anim != null && Time.time < freezeUntil && !dead && fighter.IsAlive;
        if (!freeze)
        {
            ReleaseFreeze();
            return;
        }
        if (frozenAnimator != null) return;
        frozenAnimator = anim;
        anim.speed = 0f;
    }

    private void ReleaseFreeze()
    {
        if (frozenAnimator == null) return;
        frozenAnimator.speed = 1f;
        frozenAnimator = null;
    }

    private void TryHitStop(BrawlFighter victim, BrawlHit hit)
    {
        if (victim != fighter && hit.Source != fighter) return;
        if (hit.Amount < hitStopMinDamage) return;
        float seconds = hit.Amount >= heavyHitStopDamage ? heavyHitStopSeconds : hitStopSeconds;
        freezeUntil = Mathf.Max(freezeUntil, Time.time + seconds);
        UpdateFreeze(CurrentAnimator());
    }

    private bool HasState(Animator anim, string state)
    {
        if (hasStateCache.TryGetValue(state, out bool cached)) return cached;
        bool has = anim.HasState(0, Animator.StringToHash(state));
        hasStateCache[state] = has;
        return has;
    }

    private void HandleBound(BrawlFighter bound)
    {
        if (bound != fighter) return;
        dead = false;
        victory = false;
        victoryJump = false;
        actionUntil = 0f;
        nextVictoryAt = 0f;
        lastHealAt = -999f;
        currentState = "";
        moodShown = false;
        freezeUntil = 0f;
        ReleaseFreeze();
    }

    private void HandleDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (hit.IsDrain) return;
        TryHitStop(victim, hit);
        if (victim != fighter || dead || !fighter.IsAlive) return;
        if (Time.time < actionUntil) return;
        Play(DamageState, DamageLockSeconds);
    }

    private void HandleHealed(BrawlFighter target, float amount, BrawlFighter source)
    {
        if (source == fighter && target != fighter) lastHealAt = Time.time;
    }

    private void HandleKnockedOut(BrawlFighter victim, BrawlFighter killer)
    {
        if (victim != fighter) return;
        dead = true;
        victory = false;
        freezeUntil = 0f;
        ReleaseFreeze();
        Play(DieState, float.MaxValue);
    }

    private void HandleAttackFired(BrawlFighter source, BrawlWingKitSO kit, Vector3 aim, bool healing)
    {
        if (source != fighter || dead || kit == null) return;
        Play(kit.AttackAnim, FireLockSeconds);
    }

    private void HandleCastStarted(BrawlFighter caster, BrawlSkillSO skill, Vector3 aim)
    {
        if (caster != fighter || dead || skill == null) return;
        Play(skill.CastAnim, skill.Windup);
    }

    private void HandleCastFired(BrawlFighter caster, BrawlSkillSO skill, Vector3 aim)
    {
        if (caster != fighter || dead || skill == null) return;
        Play(skill.FireAnim, CastFireLockSeconds);
    }

    private void HandleMatchEnded(ExpeditionTeam winner)
    {
        if (dead || !fighter.IsAlive || fighter.Team != winner) return;
        victory = true;
        victoryJump = true;
        nextVictoryAt = Time.time;
    }
}
}
