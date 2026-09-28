import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)

APEX = (-0.48, 0.80)
RODS = (((0.30, 0.42, 1.0), 0.95, 0.046),
        ((0.32, 1.0, 0.12), 1.0, 0.038),
        ((0.30, 0.85, -0.50), 0.62, 0.034))
MEM_ON_MID = 0.62
SCALLOP = 0.84
EDGE_SAMPLES = 8
RINGS = 5
CLEAR = 0.035


def clear_body(p, s, margin):
    hit, _ = pc.surface_point((2.0 * s, p.y, p.z), (-s, 0, 0))
    if hit is not None and s * p.x < s * hit.x + margin:
        p = Vector((hit.x + s * margin, p.y, p.z))
    return p


def membrane(name, apex, edge, s):
    bm = bmesh.new()
    va = bm.verts.new(apex)
    rings = []
    for k in range(1, RINGS + 1):
        f = k / RINGS
        ring = []
        for q in edge:
            p = apex + (q - apex) * f
            p = clear_body(p, s, min(CLEAR, (p - apex).length * 0.4 - 0.02))
            ring.append(bm.verts.new(p))
        rings.append(ring)
    first = rings[0]
    for j in range(len(first) - 1):
        bm.faces.new((va, first[j], first[j + 1]))
    for a, b in zip(rings, rings[1:]):
        for j in range(len(a) - 1):
            bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    mod = obj.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = 0.018
    mod.offset = 0
    pc.shade_smooth(obj, 50)
    return obj


def scallop_edge(a, b, apex, n):
    pts = []
    for k in range(n + 1):
        t = k / n
        p = a.lerp(b, t)
        dip = 1 - (1 - SCALLOP) * (1 - (2 * t - 1) ** 2)
        pts.append(apex + (p - apex) * dip)
    return pts


def fin(side):
    s = 1 if side == "L" else -1
    hit, nor = pc.surface_point((1.5 * s, APEX[0], APEX[1]), (-s, 0, 0))
    apex = (hit - nor * 0.015) if hit else Vector((0.48 * s, APEX[0], APEX[1]))
    rods = [(Vector((d[0] * s, d[1], d[2])).normalized(), L, r) for d, L, r in RODS]
    up_tip = apex + rods[0][0] * rods[0][1] * 0.97
    mid = apex + rods[1][0] * rods[1][1] * MEM_ON_MID
    low_tip = apex + rods[2][0] * rods[2][1] * 0.97
    edge = scallop_edge(up_tip, mid, apex, EDGE_SAMPLES)
    edge += scallop_edge(mid, low_tip, apex, EDGE_SAMPLES)[1:]
    parts = [membrane("Horn_AletasCara_%s_mem" % side, apex, edge, s)]
    for i, (d, L, r0) in enumerate(rods):
        n = 11
        pts = []
        for k in range(n):
            p = apex + d * (L * k / (n - 1))
            p = clear_body(p, s, min(CLEAR + r0 * 0.6, (p - apex).length * 0.5 - 0.02))
            pts.append(p)
        radii = [max(0.006, r0 * (1 - (k / (n - 1)) ** 1.6)) for k in range(n)]
        parts.append(pc.tube("rod%d" % i, pts, radii, sides=8))
    pc.apply_transforms(parts[0])
    return pc.join(parts, "Horn_AletasCara_%s" % side)


def build(arm):
    objs = [fin("L"), fin("R")]
    for o in objs:
        pc.skin_like(o, arm, "Horn")
    return objs
