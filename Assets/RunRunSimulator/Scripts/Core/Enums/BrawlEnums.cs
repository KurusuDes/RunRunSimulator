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
}
