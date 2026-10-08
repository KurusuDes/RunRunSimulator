using System.Collections.Generic;
using Sirenix.OdinInspector;
using Unity.Cinemachine;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BrawlCamera : MonoBehaviour
{
    [Required, SerializeField] private CinemachineTargetGroup group;
    [Required, SerializeField] private CinemachineImpulseSource impulse;
    [SerializeField, Min(0f)] private float memberRadius = 1.6f;
    [SerializeField, Min(0f)] private float blendSpeed = 2.5f;
    [SerializeField, Min(0f)] private float actionBoost = 0.6f;
    [SerializeField, Min(0f)] private float actionSeconds = 1.5f;
    [SerializeField, Range(0f, 1f)] private float idleWeight = 0.3f;
    [SerializeField, Min(0f)] private float heavyHitDamage = 1500f;
    [SerializeField, Min(0f)] private float heavyHitForce = 0.25f;
    [SerializeField, Min(0f)] private float knockOutForce = 0.6f;
    [SerializeField, Min(0f)] private float lastStandForce = 0.45f;
    [SerializeField, Min(0f)] private float impulseGap = 0.12f;

    private readonly Dictionary<Transform, BrawlFighter> members = new();
    private readonly Dictionary<BrawlFighter, float> actionUntil = new();
    private bool ended;
    private ExpeditionTeam winner;
    private float lastImpulseAt = -10f;

    private void OnEnable()
    {
        BrawlMatch.OnRosterSpawned += HandleRosterSpawned;
        BrawlMatch.OnMatchEnded += HandleMatchEnded;
        BrawlMatch.OnLastStand += HandleLastStand;
        BrawlFighter.OnDamaged += HandleDamaged;
        BrawlFighter.OnKnockedOut += HandleKnockedOut;
    }

    private void OnDisable()
    {
        BrawlMatch.OnRosterSpawned -= HandleRosterSpawned;
        BrawlMatch.OnMatchEnded -= HandleMatchEnded;
        BrawlMatch.OnLastStand -= HandleLastStand;
        BrawlFighter.OnDamaged -= HandleDamaged;
        BrawlFighter.OnKnockedOut -= HandleKnockedOut;
    }

    private void HandleRosterSpawned(IReadOnlyList<BrawlFighter> fighters)
    {
        group.Targets.Clear();
        members.Clear();
        actionUntil.Clear();
        ended = false;
        winner = ExpeditionTeam.None;

        foreach (var fighter in fighters)
        {
            if (fighter == null) continue;
            group.AddMember(fighter.transform, 1f, memberRadius);
            members[fighter.transform] = fighter;
        }
    }

    private void HandleMatchEnded(ExpeditionTeam matchWinner)
    {
        ended = true;
        winner = matchWinner;
    }

    private void HandleDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (hit.IsDrain) return;
        float until = Time.time + actionSeconds;
        if (victim != null) actionUntil[victim] = until;
        if (hit.Source != null) actionUntil[hit.Source] = until;
        if (hit.Amount >= heavyHitDamage) Shake(heavyHitForce, false);
    }

    private void HandleKnockedOut(BrawlFighter victim, BrawlFighter killer)
    {
        Shake(knockOutForce, true);
    }

    private void HandleLastStand(BrawlFighter survivor)
    {
        Shake(lastStandForce, false);
    }

    private void Shake(float force, bool ignoreGap)
    {
        if (!ignoreGap && Time.time - lastImpulseAt < impulseGap) return;
        lastImpulseAt = Time.time;
        impulse.GenerateImpulseWithForce(force);
    }

    private void LateUpdate()
    {
        var targets = group.Targets;
        if (targets.Count == 0) return;

        float now = Time.time;
        float blend = 1f - Mathf.Exp(-blendSpeed * Time.deltaTime);

        int alive = 0;
        for (int i = 0; i < targets.Count; i++)
        {
            var obj = targets[i].Object;
            if (obj != null && members.TryGetValue(obj, out var member) && member != null && member.IsAlive) alive++;
        }

        for (int i = targets.Count - 1; i >= 0; i--)
        {
            var t = targets[i];
            if (t.Object == null || !members.TryGetValue(t.Object, out var member) || member == null) continue;

            t.Weight = Mathf.Lerp(t.Weight, DesiredWeight(member, alive, now), blend);

            if (alive > 0 && !member.IsAlive && t.Weight < 0.01f)
            {
                members.Remove(t.Object);
                group.RemoveMember(t.Object);
                continue;
            }

            targets[i] = t;
        }
    }

    private float DesiredWeight(BrawlFighter member, int alive, float now)
    {
        if (alive == 0) return 1f;
        if (!member.IsAlive) return 0f;
        if (ended) return member.Team == winner ? 1f : 0f;
        bool inAction = actionUntil.TryGetValue(member, out float until) && until > now;
        if (inAction) return 1f + actionBoost;
        foreach (var pair in actionUntil)
            if (pair.Value > now && pair.Key != null && pair.Key.IsAlive) return idleWeight;
        return 1f;
    }
}
}
