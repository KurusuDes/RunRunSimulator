using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BrawlTrialRoom : MonoBehaviour
{
    [Required, SerializeField] private BrawlMatch match;

    private BrawlRunRulesSO rules;
    private float graceLeft;

    public bool Active { get; private set; }
    public bool Started { get; private set; }
    public BrawlRoomKind Kind { get; private set; }
    public float TimeLeft { get; private set; }
    public float Damage { get; private set; }
    public int Material => Kind == BrawlRoomKind.Minerals && rules != null && rules.MineralDamagePerMaterial > 0f
        ? rules.MineralBaseLoot + Mathf.FloorToInt(Damage / rules.MineralDamagePerMaterial)
        : 0;

    public event System.Action Began;

    private void OnEnable()
    {
        BrawlFighter.OnDamaged += HandleDamaged;
    }

    private void OnDisable()
    {
        BrawlFighter.OnDamaged -= HandleDamaged;
    }

    private void Update()
    {
        if (!Active || match.Phase != BrawlMatchPhase.Fight) return;

        if (!Started)
        {
            graceLeft -= Time.deltaTime;
            if (graceLeft <= 0f) Started = true;
            return;
        }

        TimeLeft -= Time.deltaTime;
        if (TimeLeft > 0f) return;

        TimeLeft = 0f;
        match.EndNow(ExpeditionTeam.Player);
    }

    public void Begin(BrawlRoomKind kind, BrawlRunRulesSO runRules)
    {
        rules = runRules;
        Kind = kind;
        Damage = 0f;
        TimeLeft = runRules.TrialSeconds;
        graceLeft = runRules.TrialStartGrace;
        Started = false;
        Active = true;
        Began?.Invoke();
    }

    public int End()
    {
        Active = false;
        return Material;
    }

    private void HandleDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (!Active || victim.Team != ExpeditionTeam.Rival) return;
        if (hit.Source == null || hit.Source.Team != ExpeditionTeam.Player || hit.IsDrain) return;

        Started = true;
        Damage += hit.Amount;
        if (Kind != BrawlRoomKind.Dummies) return;

        float heal = hit.Amount * rules.DummyHealFraction;
        foreach (var fighter in match.Fighters)
            if (fighter.Team == ExpeditionTeam.Player && fighter.IsAlive) fighter.Heal(heal, hit.Source);
    }
}
}
