import math
import bmesh
from mathutils import Vector, Matrix
import part_common as pc

SLOTS = ("Back",)

CTRL = ((0, 0.86, 0.42), (0, 1.10, 0.31), (0, 1.28, 0.34), (0, 1.36, 0.50))
TAIL_R = ((0.0, 0.08), (0.25, 0.140), (0.6, 0.120), (1.0, 0.105))
BALL_R = 0.20
SPIKE_LEN = 0.66
SPIKE_HALF = math.radians(21)
SPIN = math.radians(18)
ICON_BASE = [(1.10, 0.60), (1.50, 0.20)]


def lerp_prof(prof, t):
    for (t0, r0), (t1, r1) in zip(prof, prof[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            return r0 + (r1 - r0) * f * f * (3 - 2 * f)
    return prof[-1][1]


def tail(name, n=20):
    pts = pc.bezier(*[Vector(c) for c in CTRL], n)
    radii = [lerp_prof(TAIL_R, i / (n - 1)) for i in range(n)]
    return pc.tube(name, pts, radii, sides=16, side_hint=(1, 0, 0)), pts


def ico_dirs():
    out = [Vector((0, 0, 1)), Vector((0, 0, -1))]
    z = 1 / math.sqrt(5)
    r = 2 / math.sqrt(5)
    for k in range(5):
        a = math.radians(72 * k)
        b = math.radians(72 * k + 36)
        out.append(Vector((r * math.cos(a), r * math.sin(a), z)))
        out.append(Vector((r * math.cos(b), r * math.sin(b), -z)))
    return out


def mace(name, c, back):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    dirs = ico_dirs()
    pole = max(dirs, key=lambda d: d.z)
    best = max((v.co.normalized() for v in bm.verts), key=lambda q: q.dot(pole))
    rot = best.rotation_difference(Vector((0, 0, -1))).to_matrix()
    dirs = [d for d in (min((v.co.normalized() for v in bm.verts), key=lambda q: (q - d).length) for d in dirs)]
    for v in bm.verts:
        n = v.co.normalized()
        s = 0.0
        for d in dirs:
            if (rot @ d).z > 0.9:
                continue
            s = max(s, 1 - math.acos(max(-1.0, min(1.0, n.dot(d)))) / SPIKE_HALF)
        v.co = n * BALL_R * (1 + SPIKE_LEN * max(0.0, s) ** 1.5)
    align = Vector((0, 0, -1)).rotation_difference(-back).to_matrix() @ Matrix.Rotation(SPIN, 3, "Z") @ rot
    for v in bm.verts:
        v.co = align @ v.co + c
    obj = pc.new_object(name, bm)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def build(arm):
    t, pts = tail("Back_Cola")
    tan = (pts[-1] - pts[-2]).normalized()
    c = pts[-1] + tan * (BALL_R * 0.55)
    obj = pc.join([t, mace("ball", c, tan)], "Back_Cola")
    obj.modifiers.clear()
    pc.shade_smooth(obj, 60)
    pc.skin_like(obj, arm, "Back")
    return [obj]
