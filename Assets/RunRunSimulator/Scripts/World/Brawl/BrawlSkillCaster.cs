using System;
using UnityEngine;
namespace MoriMonchiSimulator
{

public struct BrawlCast
{
    public BrawlFighter Caster;
    public BrawlSkillSO Skill;
    public BrawlTheme Theme;
    public BrawlFighter Target;
    public Vector3 AimPoint;
    public Vector3 AimDir;
}

public class BrawlSkillCaster : MonoBehaviour
{
    public static event Action<BrawlFighter, BrawlSkillSO, Vector3> OnCastStarted;
    public static event Action<BrawlFighter, BrawlSkillSO, Vector3> OnCastFired;

    private const float TrackCutoffSeconds = 0.15f;
    private const float InterruptCooldownFactor = 0.5f;

    private readonly float[] readyAt = new float[2];

    private BrawlFighter owner;
    private bool casting;
    private int castSlot = -1;
    private BrawlSkillSO castSkill;
    private float castStart;
    private float castEnd;

    public int Count => 2;
    public bool IsCasting => casting;
    public int CastSlot => casting ? castSlot : -1;
    public BrawlSkillSO CastSkill => casting ? castSkill : null;
    public Vector3 AimPoint { get; private set; }
    public Vector3 AimDir { get; private set; }
    public BrawlFighter CastTarget { get; private set; }

    public float Cast01
    {
        get
        {
            if (!casting) return 0f;
            var span = castEnd - castStart;
            return span > 0f ? Mathf.Clamp01((Time.time - castStart) / span) : 1f;
        }
    }

    public void Init(BrawlFighter owner)
    {
        this.owner = owner;
        casting = false;
        castSlot = -1;
        castSkill = null;
        CastTarget = null;
        for (var i = 0; i < readyAt.Length; i++)
        {
            var skill = Skill(i);
            readyAt[i] = skill != null ? Time.time + skill.Cooldown * skill.FirstDelay : 0f;
        }
    }

    public BrawlSkillSO Skill(int slot)
    {
        if (owner == null) return null;
        return slot switch
        {
            0 => owner.HornSkill,
            1 => owner.BackSkill,
            _ => null,
        };
    }

    public BrawlTheme Theme(int slot)
    {
        if (owner == null) return default;
        return slot == 0 ? owner.HornTheme : owner.BackTheme;
    }

    public bool IsReady(int slot)
    {
        if (slot < 0 || slot >= Count || Skill(slot) == null) return false;
        if (casting && castSlot == slot) return false;
        return Time.time >= readyAt[slot];
    }

    public float Charge01(int slot)
    {
        var skill = Skill(slot);
        if (skill == null) return 0f;
        if (casting && castSlot == slot) return 0f;
        if (IsReady(slot)) return 1f;
        if (skill.Cooldown <= 0f) return 1f;
        return Mathf.Clamp01(1f - (readyAt[slot] - Time.time) / skill.Cooldown);
    }

    public bool TryCast(int slot, BrawlFighter target, Vector3 aimPoint)
    {
        if (owner == null || !IsReady(slot)) return false;
        if (!owner.IsAlive || owner.IsStunned || owner.Frozen) return false;
        if (owner.Motor.IsForced || casting || owner.Wing.IsWindingUp) return false;

        var skill = Skill(slot);
        casting = true;
        castSlot = slot;
        castSkill = skill;
        CastTarget = target;
        AimPoint = aimPoint;
        AimDir = PlanarAim(aimPoint);
        castStart = Time.time;
        castEnd = castStart + Mathf.Max(0f, skill.Windup);

        owner.Motor.Rooted = skill.RootWhileCasting;
        owner.Motor.LookAt = aimPoint;
        OnCastStarted?.Invoke(owner, skill, aimPoint);

        if (skill.Windup <= 0f) Fire();
        return true;
    }

    public void Refill()
    {
        for (var i = 0; i < readyAt.Length; i++)
            readyAt[i] = Time.time;
    }

    public void Interrupt()
    {
        if (!casting) return;
        var slot = castSlot;
        var skill = castSkill;
        casting = false;
        castSlot = -1;
        castSkill = null;
        owner.Motor.Rooted = false;
        readyAt[slot] = Time.time + skill.Cooldown * InterruptCooldownFactor;
    }

    private void Update()
    {
        if (!casting) return;
        if (owner == null || !owner.IsAlive)
        {
            Interrupt();
            return;
        }

        var remaining = castEnd - Time.time;
        if (castSkill.TracksTarget && remaining > TrackCutoffSeconds && castSkill.Target != BrawlSkillTarget.EnemyCluster
            && CastTarget != null && CastTarget.IsAlive)
        {
            AimPoint = CastTarget.Position;
            AimDir = PlanarAim(AimPoint);
            owner.Motor.LookAt = AimPoint;
        }

        if (remaining <= 0f) Fire();
    }

    private void Fire()
    {
        var slot = castSlot;
        var skill = castSkill;
        var cast = new BrawlCast
        {
            Caster = owner,
            Skill = skill,
            Theme = Theme(slot),
            Target = CastTarget,
            AimPoint = AimPoint,
            AimDir = AimDir,
        };

        casting = false;
        castSlot = -1;
        castSkill = null;
        owner.Motor.Rooted = false;
        readyAt[slot] = Time.time + skill.Cooldown;

        BrawlSkillEffects.Execute(cast);
        OnCastFired?.Invoke(owner, skill, cast.AimPoint);
    }

    private Vector3 PlanarAim(Vector3 point)
    {
        var dir = point - owner.Position;
        dir.y = 0f;
        if (dir.sqrMagnitude < 0.0001f)
        {
            dir = owner.transform.forward;
            dir.y = 0f;
        }
        return dir.sqrMagnitude > 0.0001f ? dir.normalized : Vector3.forward;
    }
}

}
