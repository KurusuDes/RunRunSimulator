from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)

SURF_Z = 1.10
SINK = 0.10
CTRL = ((0.0, 0.0), (-0.22, 0.17), (-0.46, 0.30), (-0.73, 0.40))
SHAFT = ((0.0, 0.192), (0.15, 0.172), (0.45, 0.150), (0.75, 0.132), (0.90, 0.126), (0.97, 0.122),
         (0.986, 0.112), (0.995, 0.092), (0.999, 0.060), (1.0, 0.006))
HOOPS = ((0.19, 0.072), (0.30, 0.072))
HOOP_OUT = 0.036


def path(root):
    pts = [root + Vector((0, a, b)) for a, b in CTRL]
    dense = pc.bezier(pts[0], pts[1], pts[2], pts[3], 120)
    acc = [0.0]
    for a, b in zip(dense, dense[1:]):
        acc.append(acc[-1] + (b - a).length)
    return dense, acc


def point_at(P, t):
    dense, acc = P
    s = t * acc[-1]
    if s >= acc[-1]:
        d = (dense[-1] - dense[-2]).normalized()
        return dense[-1] + d * (s - acc[-1])
    for i in range(1, len(acc)):
        if acc[i] >= s:
            f = (s - acc[i - 1]) / max(1e-9, acc[i] - acc[i - 1])
            return dense[i - 1].lerp(dense[i], f)
    return dense[-1]


def radius_at(t):
    for (t0, r0), (t1, r1) in zip(SHAFT, SHAFT[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            f = f * f * (3 - 2 * f)
            return r0 + (r1 - r0) * f
    return SHAFT[-1][1]


def shaft(name, P, n=34):
    ts = sorted(set(round(t, 4) for t in [i / (n - 1) for i in range(n)] + [0.97, 0.98, 0.986, 0.991, 0.995, 0.998, 0.999]))
    return pc.tube(name, [point_at(P, t) for t in ts], [radius_at(t) for t in ts], sides=18, side_hint=(1, 0, 0))


def hoop(name, P, t, w):
    L = P[1][-1]
    r = radius_at(t)
    ro = r + HOOP_OUT
    bev = 0.014
    hs = [t - w / 2 / L, t - w / 2 / L, t - (w / 2 - bev) / L, t + (w / 2 - bev) / L, t + w / 2 / L, t + w / 2 / L]
    rs = [r * 0.8, ro - bev, ro, ro, ro - bev, r * 0.8]
    return pc.tube(name, [point_at(P, h) for h in hs], rs, sides=18, side_hint=(1, 0, 0))


def build(arm):
    surf, nrm = pc.surface_point((0, -3.0, SURF_Z), (0, 1, 0))
    root = surf - nrm * SINK
    P = path(root)
    parts = [shaft("Horn_Ariete", P)]
    for i, (t, w) in enumerate(HOOPS):
        parts.append(hoop("hoop%d" % i, P, t, w))
    obj = pc.join(parts, "Horn_Ariete")
    obj.modifiers.clear()
    pc.shade_smooth(obj, 50)
    pc.skin_like(obj, arm, "Horn")
    return [obj]
