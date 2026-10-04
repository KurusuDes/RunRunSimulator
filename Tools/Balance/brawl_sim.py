import math, random, sys
from dataclasses import dataclass, field

DT = 1 / 30
ARENA_W, ARENA_H = 30.0, 20.0
UNIT_R = 0.55
ROUND_MAX = 90.0
GAS_START, GAS_END = 25.0, 62.0
GAS_R0, GAS_R1 = 19.0, 0.0
GAS_DPS = 700
REGEN_DELAY, REGEN_FRAC = 4.0, 0.05
AMMO_MAX = 3
GADGET_CD = 9.0

BODIES = {
    'A': dict(hp=7000, speed=3.0, label='equilibrado'),
    'B': dict(hp=8600, speed=2.7, label='robusto'),
    'C': dict(hp=6200, speed=3.3, label='ágil'),
    'D': dict(hp=7600, speed=2.9, label='pesado'),
}

ATTACKS = {
    'Astas': dict(name='Cornada en abanico', kind='cone', range=2.7, arc=75, dmg=1150, kb=2.6, windup=0.28, reload=1.4, pref=1.9, hits=3, move=1.18),
    'Mechon': dict(name='Latigazo', kind='line', range=4.6, width=0.7, dmg=640, slow=0.3, slow_t=1.0, windup=0.22, reload=1.3, pref=3.9, hits=5, move=1.06),
    'Hoz': dict(name='Tajo sangrante', kind='cone', range=2.3, arc=120, dmg=760, bleed=520, windup=0.2, reload=1.1, pref=1.7, hits=4, move=1.2),
    'Tapones': dict(name='Tapón rebotín', kind='proj', range=9.5, speed=17, dmg=760, radius=0.45, bounces=1, windup=0.15, reload=1.6, pref=7.0, hits=5, move=0.95),
    'Triceratops': dict(name='Embestida triple', kind='dash', range=4.8, dash_speed=13, dmg=1300, kb=3.2, windup=0.3, reload=1.8, pref=3.8, hits=3, move=1.12),
    'AletasCara': dict(name='Chorro', kind='spray', range=6.5, speed=16, dmg=340, count=3, spread=9, radius=0.35, push=0.7, windup=0.12, reload=1.3, pref=4.6, hits=9, move=1.0),
}

SUPERS = {
    'Malvaviscos': dict(name='Lluvia de malvaviscos', kind='lob', range=8.0, radius=2.6, dmg=1400, slow=0.5, slow_t=2.0, flight=0.8, cost=3200),
    'Espinas': dict(name='Erizo', kind='nova', count=10, speed=13, range=6.5, dmg=520, radius=0.3, cost=3000),
    'PuasDobles': dict(name='Coraza de púas', kind='shield', dur=3.5, reduce=0.55, thorns=320, haste=0.25, cost=2800),
    'Cometitas': dict(name='Cometitas', kind='homing', count=3, speed=9.5, range=14, dmg=720, radius=0.35, cost=3100),
    'Placas': dict(name='Muralla de placas', kind='wall', dur=6.0, heal=1800, cost=2900),
    'LomoLana': dict(name='Nube de lana', kind='zone', radius=3.2, dur=4.0, heal=420, slow=0.35, cost=3000),
}

GADGETS = {
    'Murcielago': dict(name='Aleteo', kind='escape', dist=4.2),
    'Plumitas': dict(name='Planeo', kind='leap', dist=6.5, air=0.55),
    'Cintas': dict(name='Cintas', kind='haste', mult=0.45, dur=2.5),
    'Colibri': dict(name='Colibrí', kind='haste', mult=0.35, dur=3.0),
    'Vela': dict(name='Vela', kind='escape', dist=3.5),
    'Aletas': dict(name='Aletas', kind='haste', mult=0.4, dur=2.5),
}

ROSTER = [
    dict(name='Malvaciervo', horn='Astas', back='Malvaviscos', wing='Murcielago', body='B', fur=(236, 180, 205)),
    dict(name='Erizón', horn='Mechon', back='Espinas', wing='Murcielago', body='A', fur=(170, 215, 160)),
    dict(name='Segadín', horn='Hoz', back='PuasDobles', wing='Plumitas', body='A', fur=(250, 214, 140)),
    dict(name='Tapacometa', horn='Tapones', back='Cometitas', wing='Cintas', body='A', fur=(180, 196, 245)),
    dict(name='Trikoraza', horn='Triceratops', back='Placas', wing='Murcielago', body='C', fur=(205, 170, 140)),
    dict(name='Lanaleta', horn='AletasCara', back='LomoLana', wing='Cintas', body='A', fur=(150, 225, 225)),
]


def v_add(a, b): return (a[0] + b[0], a[1] + b[1])
def v_sub(a, b): return (a[0] - b[0], a[1] - b[1])
def v_mul(a, k): return (a[0] * k, a[1] * k)
def v_len(a): return math.hypot(a[0], a[1])
def v_norm(a):
    l = v_len(a)
    return (a[0] / l, a[1] / l) if l > 1e-6 else (0.0, 0.0)
def v_rot(a, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (a[0] * c - a[1] * s, a[0] * s + a[1] * c)
def v_dot(a, b): return a[0] * b[0] + a[1] * b[1]


def seg_hits_circle(p, q, c, r):
    d = v_sub(q, p)
    f = v_sub(p, c)
    a = v_dot(d, d)
    if a < 1e-9:
        return v_len(f) < r
    t = max(0.0, min(1.0, -v_dot(f, d) / a))
    closest = v_add(p, v_mul(d, t))
    return v_len(v_sub(closest, c)) < r


@dataclass
class Unit:
    uid: int
    name: str
    team: int
    horn: str
    back: str
    wing: str
    body: str
    fur: tuple
    pos: tuple
    maxhp: float
    speed: float
    hp: float = 0
    alive: bool = True
    ammo: float = AMMO_MAX
    charge: float = 0.0
    gadget_cd: float = 3.0
    windup: object = None
    facing: tuple = (1.0, 0.0)
    kb: tuple = (0.0, 0.0)
    dash: object = None
    air_until: float = -1
    air_from: tuple = (0, 0)
    air_to: tuple = (0, 0)
    air_t0: float = 0
    slow_until: float = -1
    slow_amt: float = 0.0
    haste_until: float = -1
    haste_amt: float = 0.0
    shield_until: float = -1
    bleed_left: float = 0.0
    bleed_src: int = -1
    last_hurt: float = -99
    last_act: float = -99
    target: int = -1
    retarget_at: float = 0
    phase: float = 0.0
    fleeing: bool = False
    stats: dict = field(default_factory=lambda: dict(attacks=0, supers=0, gadgets=0, dmg=0.0, kos=0, heal=0.0, landed=0))


class World:
    def __init__(self, roster, teams, seed, log=False):
        self.rng = random.Random(seed)
        self.t = 0.0
        self.log = log
        self.events = []
        self.rocks = []
        self.walls = []
        self.projs = []
        self.lobs = []
        self.zones = []
        self.build_map()
        self.units = []
        spawn = {0: [], 1: []}
        for i, (spec, team) in enumerate(zip(roster, teams)):
            spawn[team].append(i)
        for team, ids in spawn.items():
            for k, i in enumerate(ids):
                spec = roster[i]
                body = BODIES[spec['body']]
                x = 2.5 if team == 0 else ARENA_W - 2.5
                y = ARENA_H / 2 + (k - (len(ids) - 1) / 2) * 3.2
                u = Unit(i, spec['name'], team, spec['horn'], spec['back'], spec['wing'], spec['body'], spec['fur'],
                         (x, y), body['hp'], body['speed'])
                u.hp = u.maxhp
                u.facing = (1.0, 0.0) if team == 0 else (-1.0, 0.0)
                u.phase = self.rng.uniform(0, 6.28)
                self.units.append(u)
        self.units.sort(key=lambda u: u.uid)
        self.hp_trace = []
        self.first_hit = None
        self.hits = 0
        self.ko_times = []
        self.min_alive_both = 3

    def build_map(self):
        half = []
        tries = 0
        while len(half) < 6 and tries < 400:
            tries += 1
            x = self.rng.uniform(5.5, ARENA_W / 2 - 1.2)
            y = self.rng.uniform(1.8, ARENA_H - 1.8)
            r = self.rng.uniform(0.7, 1.4)
            if any(math.hypot(x - a, y - b) < r + c + 2.2 for a, b, c in half):
                continue
            half.append((x, y, r))
        for x, y, r in half:
            self.rocks.append((x, y, r))
            self.rocks.append((ARENA_W - x, ARENA_H - y, r))
        cx, cy = ARENA_W / 2, ARENA_H / 2
        self.rocks.append((cx, cy - 3.6, 0.9))
        self.rocks.append((cx, cy + 3.6, 0.9))

    def blockers(self):
        if not self.walls:
            return self.rocks
        return self.rocks + [(w[0], w[1], w[2]) for w in self.walls]

    def los(self, p, q):
        return not any(seg_hits_circle(p, q, (x, y), r) for x, y, r in self.blockers())

    def gas_r(self):
        if self.t < GAS_START:
            return GAS_R0
        k = min(1.0, (self.t - GAS_START) / (GAS_END - GAS_START))
        return GAS_R0 + (GAS_R1 - GAS_R0) * k

    def emit(self, ev, **kw):
        if self.log:
            kw['t'] = self.t
            kw['ev'] = ev
            self.events.append(kw)

    def enemies(self, u):
        return [e for e in self.units if e.alive and e.team != u.team]

    def allies(self, u):
        return [e for e in self.units if e.alive and e.team == u.team]

    def speed_of(self, u):
        s = u.speed * ATTACKS[u.horn]['move']
        if self.t < u.slow_until:
            s *= 1 - u.slow_amt
        if self.t < u.haste_until:
            s *= 1 + u.haste_amt
        if self.t < u.shield_until and u.back == 'PuasDobles':
            s *= 1 + SUPERS['PuasDobles']['haste']
        return s

    def damage(self, src, dst, amount, tag, melee=False):
        if not dst.alive or self.t < dst.air_until:
            return 0
        if self.t < getattr(dst, 'stand_until', -1):
            amount *= 0.5
        if self.t < dst.shield_until and dst.back == 'PuasDobles':
            amount *= 1 - SUPERS['PuasDobles']['reduce']
            if melee and src is not None and src.alive:
                self.damage(dst, src, SUPERS['PuasDobles']['thorns'], 'thorns')
        amount = round(amount)
        dst.hp -= amount
        dst.last_hurt = self.t
        if src is not None:
            src.stats['dmg'] += amount
            if tag == 'attack':
                src.charge = min(1.0, src.charge + self.underdog(src) / ATTACKS[src.horn]['hits'])
                src.stats['landed'] += 1
        if tag in ('attack', 'super'):
            self.hits += 1
        if self.first_hit is None and src is not None:
            self.first_hit = self.t
        self.emit('hit', src=src.uid if src else -1, dst=dst.uid, dmg=amount, tag=tag, pos=dst.pos)
        if dst.hp <= 0:
            dst.hp = 0
            dst.alive = False
            dst.windup = None
            dst.dash = None
            self.ko_times.append(self.t)
            if src is not None:
                src.stats['kos'] += 1
            self.emit('ko', src=src.uid if src else -1, dst=dst.uid, pos=dst.pos)
            self.last_stand(dst.team)
        return amount

    def last_stand(self, team):
        mine = [a for a in self.units if a.alive and a.team == team]
        theirs = sum(1 for a in self.units if a.alive and a.team != team)
        if len(mine) == 1 and theirs >= 2:
            u = mine[0]
            u.charge = 1.0
            u.stand_until = self.t + 3.0
            self.emit('stand', src=u.uid, pos=u.pos)

    def underdog(self, u):
        mine = sum(1 for a in self.units if a.alive and a.team == u.team)
        theirs = sum(1 for a in self.units if a.alive and a.team != u.team)
        return 1.6 if mine < theirs else 1.0

    def heal(self, u, amount):
        if not u.alive:
            return
        h = min(amount, u.maxhp - u.hp)
        if h > 0:
            u.hp += h
            u.stats['heal'] += h
            self.emit('heal', dst=u.uid, amt=round(h), pos=u.pos)

    def knock(self, u, direction, strength):
        if u.alive and self.t >= u.air_until:
            u.kb = v_add(u.kb, v_mul(v_norm(direction), strength * 6))

    def pick_target(self, u):
        foes = self.enemies(u)
        if not foes:
            return None
        rng = ATTACKS[u.horn]['range']

        def score(e):
            d = v_len(v_sub(e.pos, u.pos))
            s = d
            s -= (1 - e.hp / e.maxhp) * 2
            s += 1.5 * sum(1 for a in self.allies(u) if a is not u and a.target == e.uid)
            if d <= rng * 1.2:
                s -= 2
            if not self.los(u.pos, e.pos):
                s += 3
            return s
        return min(foes, key=score)

    def lead(self, shooter, target, speed):
        tv = getattr(target, 'vel', (0.0, 0.0))
        d = v_len(v_sub(target.pos, shooter.pos))
        tt = d / speed
        return v_add(target.pos, v_mul(tv, tt))

    def start_attack(self, u, tgt):
        a = ATTACKS[u.horn]
        aim = self.lead(u, tgt, a['speed']) if a['kind'] in ('proj', 'spray') else tgt.pos
        d = v_norm(v_sub(aim, u.pos))
        u.facing = d
        u.windup = dict(what='attack', left=a['windup'], total=a['windup'], dir=d, origin=u.pos, tgt=tgt.uid)
        u.ammo -= 1
        u.last_act = self.t
        u.stats['attacks'] += 1
        self.emit('tell', src=u.uid, what='attack', dir=d, dur=a['windup'])

    def exec_attack(self, u, d):
        a = ATTACKS[u.horn]
        k = a['kind']
        if k == 'cone':
            for e in self.enemies(u):
                rel = v_sub(e.pos, u.pos)
                dist = v_len(rel)
                if dist <= a['range'] + UNIT_R and dist > 1e-6:
                    ang = math.degrees(math.acos(max(-1, min(1, v_dot(v_norm(rel), d)))))
                    if ang <= a['arc'] / 2 and self.los(u.pos, e.pos):
                        self.damage(u, e, a['dmg'], 'attack', melee=True)
                        if 'kb' in a:
                            self.knock(e, rel, a['kb'])
                        if 'bleed' in a:
                            e.bleed_left = a['bleed']
                            e.bleed_src = u.uid
            self.emit('swing', src=u.uid, dir=d, range=a['range'], arc=a['arc'])
        elif k == 'line':
            end = v_add(u.pos, v_mul(d, a['range']))
            for e in self.enemies(u):
                if seg_hits_circle(u.pos, end, e.pos, UNIT_R + a['width'] / 2) and self.los(u.pos, e.pos):
                    self.damage(u, e, a['dmg'], 'attack', melee=True)
                    e.slow_until, e.slow_amt = self.t + a['slow_t'], a['slow']
            self.emit('whip', src=u.uid, a=u.pos, b=end)
        elif k == 'proj':
            self.projs.append(dict(owner=u.uid, team=u.team, pos=u.pos, vel=v_mul(d, a['speed']), left=a['range'],
                                   dmg=a['dmg'], r=a['radius'], bounces=a['bounces'], kind='tapon', tag='attack'))
        elif k == 'spray':
            for i in range(a['count']):
                off = (i - (a['count'] - 1) / 2) * a['spread']
                dd = v_rot(d, off)
                self.projs.append(dict(owner=u.uid, team=u.team, pos=u.pos, vel=v_mul(dd, a['speed']), left=a['range'],
                                       dmg=a['dmg'], r=a['radius'], bounces=0, kind='agua', push=a['push'], tag='attack'))
        elif k == 'dash':
            u.dash = dict(dir=d, left=a['range'], speed=a['dash_speed'], hit=set(), dmg=a['dmg'], kb=a['kb'])
            self.emit('dash', src=u.uid)

    def super_ready_use(self, u, tgt):
        s = SUPERS[u.back]
        k = s['kind']
        foes = self.enemies(u)
        dist = v_len(v_sub(tgt.pos, u.pos)) if tgt else 99
        if k == 'lob':
            return tgt is not None and dist <= s['range']
        if k == 'nova':
            return sum(1 for e in foes if v_len(v_sub(e.pos, u.pos)) < 4.5) >= 1
        if k == 'shield':
            return dist < 3.5 or u.hp < u.maxhp * 0.5
        if k == 'homing':
            return any(v_len(v_sub(e.pos, u.pos)) < s['range'] for e in foes)
        if k == 'wall':
            return u.hp < u.maxhp * 0.6 and dist < 9
        if k == 'zone':
            hurt = [a for a in self.allies(u) if a.hp < a.maxhp * 0.6 and v_len(v_sub(a.pos, u.pos)) < 3.5]
            return bool(hurt) or (u.hp < u.maxhp * 0.5)
        return False

    def cast_super(self, u, tgt):
        s = SUPERS[u.back]
        u.charge = 0.0
        u.stats['supers'] += 1
        u.last_act = self.t
        k = s['kind']
        self.emit('super', src=u.uid, name=s['name'], pos=u.pos)
        if k == 'lob':
            aim = self.lead(u, tgt, 8.0)
            self.lobs.append(dict(owner=u.uid, team=u.team, at=self.t + s['flight'], start=u.pos, pos=aim, t0=self.t,
                                  radius=s['radius'], dmg=s['dmg'], slow=s['slow'], slow_t=s['slow_t']))
        elif k == 'nova':
            for i in range(s['count']):
                d = v_rot((1.0, 0.0), i * 360 / s['count'] + self.rng.uniform(0, 10))
                self.projs.append(dict(owner=u.uid, team=u.team, pos=u.pos, vel=v_mul(d, s['speed']), left=s['range'],
                                       dmg=s['dmg'], r=s['radius'], bounces=0, kind='espina', tag='super'))
        elif k == 'shield':
            u.shield_until = self.t + s['dur']
        elif k == 'homing':
            foes = sorted(self.enemies(u), key=lambda e: v_len(v_sub(e.pos, u.pos)))
            for i in range(s['count']):
                e = foes[i % len(foes)]
                d = v_rot(v_norm(v_sub(e.pos, u.pos)), (i - 1) * 35)
                self.projs.append(dict(owner=u.uid, team=u.team, pos=u.pos, vel=v_mul(d, s['speed']), left=s['range'],
                                       dmg=s['dmg'], r=s['radius'], bounces=0, kind='cometa', homing=e.uid, tag='super'))
        elif k == 'wall':
            foe = tgt.pos if tgt else v_add(u.pos, u.facing)
            d = v_norm(v_sub(foe, u.pos))
            c = v_add(u.pos, v_mul(d, 1.6))
            p = (-d[1], d[0])
            for j in (-1, 0, 1):
                w = v_add(c, v_mul(p, j * 0.95))
                self.walls.append((w[0], w[1], 0.55, self.t + s['dur']))
            self.heal(u, s['heal'])
        elif k == 'zone':
            self.zones.append(dict(owner=u.uid, team=u.team, pos=u.pos, radius=s['radius'], until=self.t + s['dur'],
                                   heal=s['heal'], slow=s['slow']))

    def gadget_use(self, u, tgt):
        g = GADGETS[u.wing]
        foes = self.enemies(u)
        near = min((v_len(v_sub(e.pos, u.pos)) for e in foes), default=99)
        if g['kind'] == 'escape':
            if u.hp < u.maxhp * 0.45 and near < 3.0:
                away = v_norm(v_sub(u.pos, min(foes, key=lambda e: v_len(v_sub(e.pos, u.pos))).pos))
                u.dash = dict(dir=away, left=g['dist'], speed=16, hit=None, dmg=0, kb=0)
                return True
        elif g['kind'] == 'leap':
            if tgt and tgt.hp < tgt.maxhp * 0.6 and 3.5 < v_len(v_sub(tgt.pos, u.pos)) < g['dist'] + 1.5:
                dest = v_sub(tgt.pos, v_mul(v_norm(v_sub(tgt.pos, u.pos)), 1.2))
                u.air_from, u.air_to, u.air_t0, u.air_until = u.pos, dest, self.t, self.t + g['air']
                return True
        elif g['kind'] == 'haste':
            if (tgt and tgt.hp < tgt.maxhp * 0.4 and v_len(v_sub(tgt.pos, u.pos)) > ATTACKS[u.horn]['range']) or (u.fleeing and near < 4):
                u.haste_until, u.haste_amt = self.t + g['dur'], g['mult']
                return True
        return False

    def collide(self, pos):
        x, y = pos
        x = min(max(x, UNIT_R), ARENA_W - UNIT_R)
        y = min(max(y, UNIT_R), ARENA_H - UNIT_R)
        for cx, cy, r in self.blockers():
            d = math.hypot(x - cx, y - cy)
            m = r + UNIT_R
            if d < m and d > 1e-6:
                x = cx + (x - cx) / d * m
                y = cy + (y - cy) / d * m
        return (x, y)

    def steer(self, u, desired):
        to = v_sub(desired, u.pos)
        if v_len(to) < 0.15:
            return (0.0, 0.0)
        d = v_norm(to)
        probe = v_add(u.pos, v_mul(d, 1.4))
        for cx, cy, r in self.blockers():
            if seg_hits_circle(u.pos, probe, (cx, cy), r + UNIT_R):
                side = v_sub((cx, cy), u.pos)
                cross = d[0] * side[1] - d[1] * side[0]
                tang = (d[1], -d[0]) if cross > 0 else (-d[1], d[0])
                d = v_norm(v_add(v_mul(d, 0.35), tang))
                break
        return d

    def think(self, u):
        foes = self.enemies(u)
        if not foes:
            return
        if self.t >= u.retarget_at or u.target < 0 or not self.units[u.target].alive:
            t = self.pick_target(u)
            u.target = t.uid if t else -1
            u.retarget_at = self.t + 0.6
        tgt = self.units[u.target] if u.target >= 0 else None
        a = ATTACKS[u.horn]
        if u.hp < u.maxhp * 0.4:
            u.fleeing = True
        elif u.hp > u.maxhp * 0.75:
            u.fleeing = False
        if u.charge >= 1.0 and u.windup is None and self.super_ready_use(u, tgt):
            u.windup = dict(what='super', left=0.3, total=0.3, dir=u.facing, origin=u.pos, tgt=tgt.uid if tgt else -1)
            self.emit('tell', src=u.uid, what='super', dir=u.facing, dur=0.3)
            return
        if u.gadget_cd <= 0 and self.gadget_use(u, tgt):
            u.gadget_cd = GADGET_CD
            u.stats['gadgets'] += 1
            self.emit('gadget', src=u.uid, name=GADGETS[u.wing]['name'], pos=u.pos)
            return
        center = (ARENA_W / 2, ARENA_H / 2)
        gr = self.gas_r()
        if u.fleeing:
            close = min(foes, key=lambda e: v_len(v_sub(e.pos, u.pos)))
            away = v_norm(v_sub(u.pos, close.pos))
            mates = [a for a in self.allies(u) if a is not u]
            if mates:
                hub = min(mates, key=lambda a: v_len(v_sub(a.pos, u.pos))).pos
                away = v_norm(v_add(away, v_mul(v_norm(v_sub(hub, u.pos)), 0.8)))
            desired = v_add(u.pos, v_mul(away, 3))
            if v_len(v_sub(desired, center)) > gr - 1.5:
                desired = v_add(u.pos, v_mul(v_norm(v_sub(center, u.pos)), 2))
        elif tgt:
            rel = v_sub(u.pos, tgt.pos)
            dn = v_norm(rel) if v_len(rel) > 1e-3 else (1.0, 0.0)
            perp = (-dn[1], dn[0])
            strafe = math.sin(self.t * 1.1 + u.phase) * (1.1 if a['pref'] > 3 else 0.5)
            desired = v_add(v_add(tgt.pos, v_mul(dn, a['pref'])), v_mul(perp, strafe))
            if not self.los(u.pos, tgt.pos):
                desired = tgt.pos
        else:
            desired = center
        if v_len(v_sub(u.pos, center)) > gr - 1.0:
            desired = center
        d = self.steer(u, desired)
        u.vel = v_mul(d, self.speed_of(u))
        if tgt and u.windup is None and u.ammo >= 1:
            dist = v_len(v_sub(tgt.pos, u.pos))
            ok_los = a['kind'] == 'dash' or self.los(u.pos, tgt.pos)
            if dist <= a['range'] * 0.95 + UNIT_R and ok_los:
                self.start_attack(u, tgt)

    def step(self):
        t = self.t
        for u in self.units:
            if not u.alive:
                continue
            u.vel = (0.0, 0.0)
            u.ammo = min(AMMO_MAX, u.ammo + DT / ATTACKS[u.horn]['reload'])
            u.gadget_cd -= DT
            if u.bleed_left > 0:
                b = min(u.bleed_left, 120 * DT)
                u.bleed_left -= b
                self.damage(self.units[u.bleed_src], u, b, 'bleed')
                if not u.alive:
                    continue
            if t - u.last_hurt > REGEN_DELAY and t - u.last_act > REGEN_DELAY and u.hp < u.maxhp:
                u.hp = min(u.maxhp, u.hp + u.maxhp * REGEN_FRAC * DT)
            if v_len(v_sub(u.pos, (ARENA_W / 2, ARENA_H / 2))) > self.gas_r():
                self.damage(None, u, GAS_DPS * DT, 'gas')
                if not u.alive:
                    continue
            if t < u.air_until:
                k = (t - u.air_t0) / (u.air_until - u.air_t0)
                u.pos = v_add(u.air_from, v_mul(v_sub(u.air_to, u.air_from), k))
                continue
            elif u.air_until > 0 and t - u.air_until < DT * 1.5:
                u.pos = self.collide(u.air_to)
                self.emit('land', src=u.uid, pos=u.pos)
            if u.dash:
                step = u.dash['speed'] * DT
                nxt = v_add(u.pos, v_mul(u.dash['dir'], step))
                col = self.collide(nxt)
                blocked = v_len(v_sub(col, nxt)) > 0.05
                u.pos = col
                u.dash['left'] -= step
                if u.dash['hit'] is not None:
                    for e in self.enemies(u):
                        if e.uid not in u.dash['hit'] and v_len(v_sub(e.pos, u.pos)) < UNIT_R * 2.2:
                            u.dash['hit'].add(e.uid)
                            dash = u.dash
                            self.damage(u, e, dash['dmg'], 'attack', melee=True)
                            self.knock(e, v_add(dash['dir'], v_sub(e.pos, u.pos)), dash['kb'])
                            if not u.alive:
                                break
                if not u.alive or u.dash is None:
                    continue
                if u.dash['left'] <= 0 or blocked:
                    u.dash = None
                continue
            if u.windup:
                u.windup['left'] -= DT
                if u.windup['left'] <= 0:
                    w = u.windup
                    u.windup = None
                    if w['what'] == 'attack':
                        d = w['dir']
                        tg = self.units[w['tgt']]
                        if tg.alive:
                            a = ATTACKS[u.horn]
                            aim = self.lead(u, tg, a['speed']) if a['kind'] in ('proj', 'spray') else tg.pos
                            nd = v_norm(v_sub(aim, u.pos))
                            if v_dot(nd, d) > math.cos(math.radians(35)):
                                d = nd
                        u.facing = d
                        self.exec_attack(u, d)
                    else:
                        tg = self.units[w['tgt']] if w['tgt'] >= 0 and self.units[w['tgt']].alive else None
                        if tg is None:
                            foes = self.enemies(u)
                            tg = foes[0] if foes else None
                        self.cast_super(u, tg)
            else:
                self.think(u)
            if v_len(u.kb) > 0.05:
                u.pos = self.collide(v_add(u.pos, v_mul(u.kb, DT)))
                u.kb = v_mul(u.kb, 0.82)
            if u.windup is None:
                u.pos = self.collide(v_add(u.pos, v_mul(u.vel, DT)))
                if v_len(u.vel) > 0.1:
                    u.facing = v_norm(u.vel) if u.target < 0 else v_norm(v_sub(self.units[u.target].pos, u.pos)) if self.units[u.target].alive else u.facing
        for i, a in enumerate(self.units):
            for b in self.units[i + 1:]:
                if a.alive and b.alive:
                    d = v_sub(b.pos, a.pos)
                    l = v_len(d)
                    if 1e-6 < l < UNIT_R * 2:
                        push = v_mul(v_norm(d), (UNIT_R * 2 - l) / 2)
                        a.pos = self.collide(v_sub(a.pos, push))
                        b.pos = self.collide(v_add(b.pos, push))
        self.step_projs()
        for lb in self.lobs[:]:
            if t >= lb['at']:
                self.lobs.remove(lb)
                owner = self.units[lb['owner']]
                self.emit('boom', src=lb['owner'], pos=lb['pos'], radius=lb['radius'])
                for e in self.units:
                    if e.alive and e.team != lb['team'] and v_len(v_sub(e.pos, lb['pos'])) < lb['radius'] + UNIT_R:
                        self.damage(owner, e, lb['dmg'], 'super')
                        e.slow_until, e.slow_amt = t + lb['slow_t'], lb['slow']
        for z in self.zones[:]:
            if t >= z['until']:
                self.zones.remove(z)
                continue
            for e in self.units:
                if not e.alive or v_len(v_sub(e.pos, z['pos'])) > z['radius']:
                    continue
                if e.team == z['team']:
                    e.hp = min(e.maxhp, e.hp + z['heal'] * DT)
                    self.units[z['owner']].stats['heal'] += z['heal'] * DT
                else:
                    e.slow_until, e.slow_amt = t + 0.2, z['slow']
        self.walls = [w for w in self.walls if w[3] > t]
        self.t += DT
        if int(self.t / 0.5) != int((self.t - DT) / 0.5):
            hp = [sum(u.hp / u.maxhp for u in self.units if u.team == k and u.alive) for k in (0, 1)]
            self.hp_trace.append((self.t, hp[0], hp[1]))
        alive = [sum(1 for u in self.units if u.alive and u.team == k) for k in (0, 1)]
        self.min_alive_both = min(self.min_alive_both, max(alive))

    def step_projs(self):
        for p in self.projs[:]:
            if 'homing' in p:
                h = self.units[p['homing']]
                if h.alive:
                    want = v_mul(v_norm(v_sub(h.pos, p['pos'])), v_len(p['vel']))
                    p['vel'] = v_norm(v_add(v_mul(p['vel'], 0.86), v_mul(want, 0.14)))
                    p['vel'] = v_mul(p['vel'], 9.5)
            nxt = v_add(p['pos'], v_mul(p['vel'], DT))
            p['left'] -= v_len(p['vel']) * DT
            dead = p['left'] <= 0 or not (0 < nxt[0] < ARENA_W and 0 < nxt[1] < ARENA_H)
            for cx, cy, r in self.blockers():
                if math.hypot(nxt[0] - cx, nxt[1] - cy) < r + p['r']:
                    if p['bounces'] > 0:
                        p['bounces'] -= 1
                        n = v_norm(v_sub(nxt, (cx, cy)))
                        vv = p['vel']
                        p['vel'] = v_sub(vv, v_mul(n, 2 * v_dot(vv, n)))
                        nxt = v_add((cx, cy), v_mul(n, r + p['r'] + 0.02))
                        self.emit('bounce', pos=nxt)
                    else:
                        dead = True
                    break
            p['pos'] = nxt
            if not dead:
                for e in self.units:
                    if e.alive and e.team != p['team'] and v_len(v_sub(e.pos, nxt)) < UNIT_R + p['r'] and self.t >= e.air_until:
                        self.damage(self.units[p['owner']], e, p['dmg'], p['tag'])
                        if p.get('push'):
                            self.knock(e, p['vel'], p['push'])
                        dead = True
                        break
            if dead:
                self.emit('pop', pos=nxt, kind=p['kind'])
                self.projs.remove(p)

    def winner(self):
        alive = [sum(1 for u in self.units if u.alive and u.team == k) for k in (0, 1)]
        if alive[0] == 0 and alive[1] == 0:
            return -1
        if alive[0] == 0:
            return 1
        if alive[1] == 0:
            return 0
        if self.t >= ROUND_MAX:
            hp = [sum(u.hp / u.maxhp for u in self.units if u.team == k and u.alive) for k in (0, 1)]
            return 0 if hp[0] > hp[1] else 1
        return None


def play_round(roster, teams, seed, log=False, frame_cb=None):
    w = World(roster, teams, seed, log)
    while True:
        w.step()
        if frame_cb:
            frame_cb(w)
        win = w.winner()
        if win is not None:
            return w, win


def lead_changes(trace, margin=0.25):
    leader, changes = None, 0
    for _, a, b in trace:
        if abs(a - b) < margin:
            continue
        cur = 0 if a > b else 1
        if leader is not None and cur != leader:
            changes += 1
        leader = cur
    return changes


def comeback(trace, win):
    if not trace:
        return False
    mid = trace[len(trace) // 2]
    behind = 0 if mid[1] < mid[2] else 1
    return abs(mid[1] - mid[2]) > 0.25 and behind == win


def batch(n, seed0=0):
    import statistics as st
    rows = []
    per = {i: dict(wins=0, games=0, attacks=0, supers=0, gadgets=0, dmg=0, kos=0, heal=0, landed=0) for i in range(6)}
    for s in range(n):
        rng = random.Random(seed0 + s)
        ids = list(range(6))
        rng.shuffle(ids)
        teams = [0] * 6
        for i in ids[3:]:
            teams[i] = 1
        w, win = play_round(ROSTER, teams, seed0 + s)
        dur = w.t
        rows.append(dict(dur=dur, first=w.first_hit or dur, hps=w.hits / dur, lc=lead_changes(w.hp_trace),
                         cb=comeback(w.hp_trace, win), one=w.min_alive_both <= 1, gas=dur > GAS_START,
                         timeout=dur >= ROUND_MAX - 0.01, last_gap=(w.ko_times[-1] - w.ko_times[-2]) if len(w.ko_times) > 1 else dur))
        for u in w.units:
            p = per[u.uid]
            p['games'] += 1
            p['wins'] += int(u.team == win)
            for k in ('attacks', 'supers', 'gadgets', 'dmg', 'kos', 'heal', 'landed'):
                p[k] += u.stats[k]
    def m(k): return st.mean(r[k] for r in rows)
    def q(k, f):
        xs = sorted(r[k] for r in rows)
        return xs[int(f * (len(xs) - 1))]
    print(f'{n} rondas 3v3 (equipos al azar entre los 6)')
    print(f'duración        media {m("dur"):.0f} s · p10 {q("dur", .1):.0f} · p90 {q("dur", .9):.0f} · por tiempo {100 * m("timeout"):.0f} %')
    print(f'primer golpe    {m("first"):.1f} s')
    print(f'golpes/s        {m("hps"):.2f} (todos)')
    print(f'cambios de líder {m("lc"):.2f} por ronda · rondas con remontada {100 * m("cb"):.0f} %')
    print(f'terminan 1v1 o menos (en algún momento quedaba 1 de un lado) {100 * m("one"):.0f} %')
    print(f'llegan al gas   {100 * m("gas"):.0f} %')
    print()
    print(f'{"criatura":12s}{"gana %":>8s}{"acierto":>9s}{"ataques":>9s}{"súper":>7s}{"truco":>7s}{"daño":>8s}{"KO":>6s}{"cura":>7s}')
    for i, sp in enumerate(ROSTER):
        p = per[i]
        g = p['games']
        print(f'{sp["name"]:12s}{100 * p["wins"] / g:8.0f}{100 * p["landed"] / max(1, p["attacks"] * (3 if sp["horn"] == "AletasCara" else 1)):8.0f}%{p["attacks"] / g:9.1f}{p["supers"] / g:7.2f}{p["gadgets"] / g:7.2f}{p["dmg"] / g:8.0f}{p["kos"] / g:6.2f}{p["heal"] / g:7.0f}')


if __name__ == '__main__':
    batch(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
