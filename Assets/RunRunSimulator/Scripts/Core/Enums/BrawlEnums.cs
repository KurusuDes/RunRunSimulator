namespace MoriMonchiSimulator
{
public enum BrawlAttackKind { Melee, Whip, Shotgun, Sniper, Burst, Boomerang }

public enum BrawlMobilityKind { Leap, Sprint, Roll, Hop, Blink, Glide }

public enum BrawlLocomotion { Ground, Hover }

public enum BrawlSkillFamily { Dash, Chain, Cone, Shot, Nova, Homing, Pull, Zone, Ward, Mend }

public enum BrawlSkillRole { Offense, Control, Support, Tank }

public enum BrawlSkillTarget { Enemy, EnemyCluster, Self, LowestAlly, AlliesAround }

public enum BrawlMatchPhase { Idle, Countdown, Fight, SuddenDeath, Ended }

public enum BrawlIntent { Idle, Engage, Kite, Hunt, Protect, Heal, Retreat, Cast }

public enum BrawlStatusKind { Slow, Stun, Haste, Boost, Thorns, Taunt, Shield }

public enum BrawlFxKind { Slash, Lightning, Beam, Whip, Burst, Ring, Pulse, Ward, Dash, Pull, Throw, Muzzle, Spawn, KnockOut, Land }
public enum BrawlSignature { None, Rainbow, Storm, Cloud, Comet, Lure, Plates }
public enum BrawlRoomKind { Combat, Dummies, Minerals }
public enum BrawlRunState { Planning, Fighting, RoomResult, Over, Transition }

public enum BrawlUpgradeOp { Add = 0, Multiply = 1 }

public enum BrawlUpgradeStat
{
    Damage = 0,
    Heal = 1,
    Shield = 2,
    Duration = 3,
    Cooldown = 4,
    Range = 5,
    Radius = 6,
    Angle = 7,
    Count = 8,
    Knockback = 9,
    Slow = 10,
    SlowSeconds = 11,
    StunSeconds = 12,
    Haste = 13,
    DamageBoost = 14,
    Thorns = 15,
    TauntSeconds = 16,
    Bounces = 17,
    Pierce = 18,
    ExplodeRadius = 19,
    AllyHeal = 20,
    Reload = 21,
    HitRadius = 22,
    MoveSpeed = 23,
    MobilityCooldown = 24,
    MobilityDamage = 25,
    MobilityDistance = 26,
    Hp = 27
}
}
