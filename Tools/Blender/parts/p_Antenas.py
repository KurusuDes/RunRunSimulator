import math
import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)

ROOT = (0.24, -0.30)
SINK = 0.07
CTRL = ((0.00, 0.00, 0.00),
        (0.03, -0.05, 0.27),
        (0.10, 0.01, 0.51),
        (0.19, 0.22, 0.67),
        (0.29, 0.50, 0.72),
        (0.38, 0.80, 0.71),
        (0.45, 1.06, 0.70),
        (0.50, 1.26, 0.76))
SAMPLES = 52
SIDES = 12
R_BASE = 0.125
SPOON_START = 0.70
SPOON_W = 0.10
SPOON_T = 0.03
R_END = 0.006
FACE = Vector((0.6, 0.0, 0.8)).normalized()


def catmull(ctrl, n):
    c = [ctrl[0] * 2 - ctrl[1]] + list(ctrl) + [ctrl[-1] * 2 - ctrl[-2]]
    segs = len(ctrl) - 1
    out = []
    for i in range(n):
        u = i / (n - 1) * segs
        k = min(int(u), segs - 1)
        t = u - k
        p0, p1, p2, p3 = c[k], c[k + 1], c[k + 2], c[k + 3]
        out.append(0.5 * ((p1 * 2) + (p2 - p0) * t + (p0 * 2 - p1 * 5 + p2 * 4 - p3) * t * t
                          + (p1 * 3 - p0 - p2 * 3 + p3) * t * t * t))
    return out


def stem(t):
    return R_END + (R_BASE - R_END) * (1 - t ** 2) * (1 - 0.25 * min(1.0, t / 0.3))


def section(t):
    r = stem(t)
    if t <= SPOON_START:
        return r, r
    u = (t - SPOON_START) / (1 - SPOON_START)
    close = math.sqrt(max(0.0, 1 - ((u - 0.5) / 0.5) ** 2)) if u > 0.5 else 1.0
    grow = math.sin(min(1.0, u / 0.5) * math.pi / 2)
    w = max(R_END, (r + (SPOON_W - r) * grow) * close)
    th = max(R_END, (r + (SPOON_T - r) * grow) * close)
    return w, th


def params(n):
    out = []
    for i in range(n):
        x = i / (n - 1)
        out.append(1 - (1 - x) ** 1.35)
    return out


def spoon_tube(name, curve):
    ts = params(SAMPLES)
    pts = [curve(t) for t in ts]
    bm = bmesh.new()
    rings = []
    for i, (p, s) in enumerate(zip(pts, ts)):
        a = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        tan = a.normalized()
        wide = tan.cross(FACE)
        wide = (wide - tan * wide.dot(tan)).normalized()
        thin = wide.cross(tan).normalized()
        rw, rt = section(s)
        ring = [bm.verts.new(p + wide * math.cos(2 * math.pi * k / SIDES) * rw
                             + thin * math.sin(2 * math.pi * k / SIDES) * rt) for k in range(SIDES)]
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(SIDES):
            bm.faces.new((a[k], a[(k + 1) % SIDES], b[(k + 1) % SIDES], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return pc.new_object(name, bm)


def build(arm):
    root, _ = pc.head_top(ROOT[0], ROOT[1])
    root = root - Vector((0, 0, SINK))
    ctrl = [root + Vector((x, y, z)) for x, y, z in CTRL]
    dense = catmull(ctrl, 400)

    def curve(t):
        f = t * (len(dense) - 1)
        k = min(int(f), len(dense) - 2)
        return dense[k].lerp(dense[k + 1], f - k)

    right = spoon_tube("Horn_Antenas_R", curve)
    left = pc.mirror_x(right, "Horn_Antenas_L")
    for o in (right, left):
        pc.shade_smooth(o)
        pc.skin_like(o, arm, "Horn")
    return [left, right]
