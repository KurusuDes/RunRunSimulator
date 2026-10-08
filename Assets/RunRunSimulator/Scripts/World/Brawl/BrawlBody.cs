using System.Collections;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BrawlBody : MonoBehaviour
{
    private const float MaxPulse = 0.6f;
    private const float SpringStep = 1f / 120f;
    private const float MaxSpringDt = 0.034f;

    [Required, SerializeField] private BrawlFighter fighter;
    [Required, SerializeField] private MonchiVisualizer visualizer;
    [Required, SerializeField] private Transform pivot;
    [Required, SerializeField] private BrawlTuningSO tuning;
    [SerializeField] private float stiffness = 260f;
    [SerializeField] private float damping = 12f;
    [SerializeField] private float hitPulse = 0.3f;
    [SerializeField] private float castPulse = -0.18f;
    [SerializeField] private float firePulse = 0.25f;
    [SerializeField] private float landPulse = -0.35f;
    [SerializeField] private float healPulse = 0.12f;
    [SerializeField, Range(0f, 1f)] private float rimPower = 0.55f;
    [SerializeField, Range(0f, 1f)] private float rimInsideMask = 0.55f;
    [SerializeField] private float heavyHitDamage = 1000f;
    [SerializeField] private Color allyHitFlash = new Color(1f, 0.12f, 0.08f);
    [SerializeField] private Color foeHitFlash = Color.white;
    [SerializeField, Range(0f, 1f)] private float heavyFlashAlpha = 0.85f;
    [SerializeField, Range(0f, 1f)] private float lightFlashAlpha = 0.6f;
    [SerializeField, Min(0.01f)] private float hitFlashSeconds = 0.2f;
    [SerializeField] private Color healFlash = new Color(0.45f, 1f, 0.55f);
    [SerializeField, Range(0f, 1f)] private float healFlashAlpha = 0.35f;
    [SerializeField, Min(0.01f)] private float healFlashSeconds = 0.25f;
    [SerializeField] private float koShrinkDelay = 1.4f;
    [SerializeField] private float koShrinkSeconds = 0.5f;

    private float pulse;
    private float pulseVelocity;
    private float koScale = 1f;
    private bool knockedOut;
    private bool flashing;
    private Color flashColor;
    private float flashPeak;
    private float flashStartedAt;
    private float flashSeconds;
    private Coroutine koRoutine;

    private void OnEnable()
    {
        BrawlFighter.OnBound += HandleBound;
        BrawlFighter.OnDamaged += HandleDamaged;
        BrawlFighter.OnHealed += HandleHealed;
        BrawlFighter.OnKnockedOut += HandleKnockedOut;
        BrawlSkillCaster.OnCastStarted += HandleCastStarted;
        BrawlSkillCaster.OnCastFired += HandleCastFired;
        BrawlWing.OnAttackFired += HandleAttackFired;
        BrawlFx.Emitted += HandleFx;
    }

    private void OnDisable()
    {
        BrawlFighter.OnBound -= HandleBound;
        BrawlFighter.OnDamaged -= HandleDamaged;
        BrawlFighter.OnHealed -= HandleHealed;
        BrawlFighter.OnKnockedOut -= HandleKnockedOut;
        BrawlSkillCaster.OnCastStarted -= HandleCastStarted;
        BrawlSkillCaster.OnCastFired -= HandleCastFired;
        BrawlWing.OnAttackFired -= HandleAttackFired;
        BrawlFx.Emitted -= HandleFx;

        koRoutine = null;
        pulse = 0f;
        pulseVelocity = 0f;
        StopFlash();
        if (pivot != null)
        {
            pivot.localScale = Vector3.one;
            pivot.localPosition = Vector3.zero;
        }
    }

    private void LateUpdate()
    {
        if (pivot == null || !pivot.gameObject.activeInHierarchy) return;

        if (flashing) StepFlash();

        float dt = Time.deltaTime;
        if (dt > 0f) StepSpring(dt);

        float s = Mathf.Clamp(pulse, -MaxPulse, MaxPulse);
        pivot.localScale = new Vector3(1f - s * 0.5f, 1f + s, 1f - s * 0.5f) * koScale;
        pivot.localPosition = new Vector3(0f, fighter.Lift, 0f);
    }

    private void StepSpring(float dt)
    {
        float remaining = Mathf.Min(dt, MaxSpringDt);
        while (remaining > 0f)
        {
            float h = Mathf.Min(remaining, SpringStep);
            pulseVelocity += (-stiffness * pulse - damping * pulseVelocity) * h;
            pulse += pulseVelocity * h;
            remaining -= h;
        }
    }

    private void Kick(float amount)
    {
        if (knockedOut) return;
        pulse = amount;
        pulseVelocity = 0f;
    }

    private void ApplyTeamRim()
    {
        visualizer.SetRimOverride(tuning.TeamColor(fighter.Team), rimPower, rimInsideMask);
    }

    private void StartFlash(Color color, float alpha, float seconds)
    {
        if (knockedOut) return;
        flashColor = color;
        flashPeak = alpha;
        flashStartedAt = Time.time;
        flashSeconds = seconds;
        flashing = true;
        visualizer.SetFlash(flashColor, flashPeak);
    }

    private void StepFlash()
    {
        float t = (Time.time - flashStartedAt) / flashSeconds;
        if (t >= 1f)
        {
            StopFlash();
            return;
        }
        float fade = 1f - t;
        visualizer.SetFlash(flashColor, flashPeak * fade * fade);
    }

    private void StopFlash()
    {
        flashing = false;
        if (visualizer != null) visualizer.SetFlash(flashColor, 0f);
    }

    private void HandleBound(BrawlFighter bound)
    {
        if (bound != fighter) return;
        if (koRoutine != null) StopCoroutine(koRoutine);
        koRoutine = null;
        knockedOut = false;
        koScale = 1f;
        pulse = 0f;
        pulseVelocity = 0f;
        StopFlash();
        pivot.gameObject.SetActive(true);
        pivot.localScale = Vector3.one;
        ApplyTeamRim();
    }

    private void HandleDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (victim != fighter || hit.IsDrain) return;
        Kick(hitPulse);
        bool heavy = hit.FromSkill || hit.Amount >= heavyHitDamage;
        var color = fighter.Team == ExpeditionTeam.Player ? allyHitFlash : foeHitFlash;
        StartFlash(color, heavy ? heavyFlashAlpha : lightFlashAlpha, hitFlashSeconds);
    }

    private void HandleHealed(BrawlFighter target, float amount, BrawlFighter source)
    {
        if (target != fighter) return;
        Kick(healPulse);
        StartFlash(healFlash, healFlashAlpha, healFlashSeconds);
    }

    private void HandleCastStarted(BrawlFighter caster, BrawlSkillSO skill, Vector3 aim)
    {
        if (caster == fighter) Kick(castPulse);
    }

    private void HandleCastFired(BrawlFighter caster, BrawlSkillSO skill, Vector3 aim)
    {
        if (caster == fighter) Kick(firePulse);
    }

    private void HandleAttackFired(BrawlFighter source, BrawlWingKitSO kit, Vector3 aim, bool healing)
    {
        if (source == fighter) Kick(firePulse * 0.5f);
    }

    private void HandleFx(BrawlFxEvent e)
    {
        if (e.Kind == BrawlFxKind.Land && e.Source == fighter) Kick(landPulse);
    }

    private void HandleKnockedOut(BrawlFighter victim, BrawlFighter killer)
    {
        if (victim != fighter || knockedOut) return;
        knockedOut = true;
        StopFlash();
        if (koRoutine != null) StopCoroutine(koRoutine);
        koRoutine = StartCoroutine(KnockOutRoutine());
    }

    private IEnumerator KnockOutRoutine()
    {
        yield return new WaitForSeconds(koShrinkDelay);

        float elapsed = 0f;
        while (elapsed < koShrinkSeconds)
        {
            elapsed += Time.deltaTime;
            koScale = 1f - Mathf.Clamp01(elapsed / koShrinkSeconds);
            yield return null;
        }

        koScale = 0f;
        koRoutine = null;
        pivot.gameObject.SetActive(false);
    }
}
}
