import math
import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)

RIM = [(-0.66, 1.00), (-0.70, 1.20), (-0.74, 1.40), (-0.78, 1.60), (-0.73, 1.76), (-0.58, 1.85), (-0.36, 1.89),
       (-0.10, 1.86), (0.24, 1.76), (0.49, 1.61), (0.71, 1.40), (0.87, 1.16), (0.98, 0.91), (1.04, 0.67), (1.03, 0.50)]
INNER = [RIM[0], RIM[-1]]
PIVOT = Vector((0, -0.05, 0.75))
N = 101
T = (0.0, 0.07, 0.18, 0.34, 0.54, 0.76, 1.0)
K = 6
PLEATS = 18
PLEAT_AMP = 0.005
SINK = 0.06
MIN_H = 0.012
CREST_H = 0.42
EDGE = 0.07


def catmull(pts, n):
    pts = [Vector((0, y, z)) for y, z in pts]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    dense = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(20):
            t = k / 20
            dense.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    dense.append(pts[-1])
    acc = [0.0]
    for a, b in zip(dense, dense[1:]):
        acc.append(acc[-1] + (b - a).length)
    out, j = [], 0
    for i in range(n):
        s = acc[-1] * i / (n - 1)
        while j < len(acc) - 2 and acc[j + 1] < s:
            j += 1
        f = (s - acc[j]) / max(acc[j + 1] - acc[j], 1e-9)
        out.append(dense[j].lerp(dense[j + 1], f))
    return out


def rib(tip):
    d = (tip - PIVOT).normalized()
    hit, _ = pc.surface_point(PIVOT + d * 3.0, -d)
    if hit is None:
        hit = PIVOT + d * 0.5
    hit = Vector((0, hit.y, hit.z))
    if (tip - PIVOT).length < (hit - PIVOT).length + MIN_H:
        tip = hit + d * MIN_H
    return hit - d * SINK, hit, tip, d


def build(arm):
    rim = catmull(RIM, N)
    X = Vector((1, 0, 0))
    bm = bmesh.new()
    loops = []
    for i in range(N):
        u = i / (N - 1)
        base, surf, tip, d = rib(rim[i])
        wave = math.sin(2 * math.pi * PLEATS * u)
        end = min(u, 1 - u)
        edge = min(1.0, end / EDGE)
        tip = surf + d * CREST_H * math.sqrt(max(0.0, 1 - (1 - edge) ** 2))
        tip = surf + d * max((tip - surf).length, MIN_H)
        fade = min(1.0, end / 0.05)
        taper = 0.45 + 0.55 * min(1.0, end / 0.08) ** 0.6

        def point(q):
            p = surf.lerp(tip, q) if q >= 0 else surf.lerp(base, -q)
            return p + X * (PLEAT_AMP * max(0.0, q) ** 1.2 * wave * fade)

        def half(q):
            q = max(0.0, q)
            return taper * (0.016 + 0.020 * (1 - q) ** 1.5 + 0.026 * max(0.0, 1 - q / 0.14) ** 2)

        qs = [-1.0] + list(T)
        plus = [point(q) + X * half(q) for q in qs]
        hr = half(1.0)
        top = point(1.0)
        cap = [top + d * hr * math.sin(math.pi * k / K) + X * hr * math.cos(math.pi * k / K) for k in range(1, K)]
        minus = [point(q) - X * half(q) for q in reversed(qs)]
        loops.append([bm.verts.new(p) for p in plus + cap + minus])
    M = len(loops[0])
    for la, lb in zip(loops, loops[1:]):
        for k in range(M):
            bm.faces.new((la[k], la[(k + 1) % M], lb[(k + 1) % M], lb[k]))
    bm.faces.new(list(reversed(loops[0])))
    bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object("Back_Abanico", bm)
    pc.shade_smooth(obj, 50)
    pc.skin_like(obj, arm, "Back")
    return [obj]
