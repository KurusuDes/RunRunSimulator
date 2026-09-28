import math
import bmesh
from mathutils import Vector
import part_common as pc
from p_Carnero import catmull

SLOTS = ("Horn",)

ROOT_RAY = ((0.0, -0.40, 0.95), (1.0, 0.0, 0.35))
SINK = 0.03
KEYS = ((-0.08, 0.10, 0.0), (0.0, 0.0, 0.0), (0.05, -0.22, -0.06), (0.06, -0.43, -0.17),
        (0.04, -0.62, -0.31), (0.0, -0.79, -0.48), (-0.05, -0.92, -0.68))
HEEL = ((0.0, -0.10, -0.05), (0.0, -0.02, 0.10), (-0.01, 0.07, 0.25), (-0.02, 0.14, 0.38))
W_OUT = 0.25
W_IN = 0.11
THICK = 0.04
PEAK = 0.12
HOLD = 0.42
UP = Vector((0.0, 0.0, 1.0))
BACK = Vector((0.0, 1.0, 0.0))


def blade(name, pts, prof, ref):
    bm = bmesh.new()
    rings = []
    n = len(pts)
    for i, (p, (wo, wi, th)) in enumerate(zip(pts, prof)):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        wdir = (ref - t * ref.dot(t)).normalized()
        nrm = t.cross(wdir).normalized()
        rings.append([bm.verts.new(p + wdir * wo), bm.verts.new(p + nrm * th),
                      bm.verts.new(p - wdir * wi), bm.verts.new(p - nrm * th)])
    for a, b in zip(rings, rings[1:]):
        for k in range(4):
            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    pc.shade_smooth(obj, 25)
    return obj


def profile(pts, w_out, w_in, thick, peak, start):
    arc = [0.0]
    for a, b in zip(pts, pts[1:]):
        arc.append(arc[-1] + (b - a).length)
    out = []
    for L in arc:
        s = L / arc[-1]
        if s <= peak:
            f = start + (1 - start) * math.sin(0.5 * math.pi * s / peak)
        elif s <= HOLD:
            f = 1.0
        else:
            f = ((1 - s) / (1 - HOLD)) ** 0.85
        out.append((max(0.006, w_out * f), max(0.006, w_in * f), max(0.006, thick * f ** 0.5)))
    return out


def build(arm):
    d = Vector(ROOT_RAY[1]).normalized()
    hit, _ = pc.surface_point(Vector(ROOT_RAY[0]) + d * 3.0, -d)
    root = hit - d * SINK
    pts = catmull([root + Vector(k) for k in KEYS], per=6)
    edge = blade("Horn_Hoz_R", pts, profile(pts, W_OUT, W_IN, THICK, PEAK, 0.6), UP)
    heel_pts = catmull([root + Vector(k) for k in HEEL], per=4)
    heel = blade("heel", heel_pts, profile(heel_pts, 0.12, 0.06, THICK * 0.9, 0.05, 1.0), BACK)
    right = pc.join([edge, heel], "Horn_Hoz_R")
    left = pc.mirror_x(right, "Horn_Hoz_L")
    for o in (right, left):
        pc.skin_like(o, arm, "Horn")
    return [right, left]
