import math
import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Wing",)

MAST = (0.30, 0.95, 0.04, 0.80)
BOOM = (0.32, -0.12, 0.94, 0.56)
ROACH = 0.20
CAMBER = 0.07
GRID = (10, 12)


def frame(s):
    out, back, up = Vector((s, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    m = (out * MAST[0] + up * MAST[1] + back * MAST[2]).normalized()
    b = (out * BOOM[0] + up * BOOM[1] + back * BOOM[2]).normalized()
    return m, b


def sail(name, root, m, b, s):
    top = root + m * MAST[3]
    end = root + b * BOOM[3]
    n = m.cross(b).normalized()
    if n.x * s < 0:
        n = -n
    away = ((top + end) / 2 - root).normalized()
    span = (top - end).length
    nu, nv = GRID
    bm = bmesh.new()
    rv = bm.verts.new(root)
    rows = []
    for i in range(nv + 1):
        t = i / nv
        a = top.lerp(end, t) + away * (ROACH * span * 4 * t * (1 - t))
        row = []
        for j in range(1, nu + 1):
            f = j / nu
            bulge = CAMBER * math.sin(math.pi * f) * (4 * t * (1 - t)) ** 0.5
            row.append(bm.verts.new(root.lerp(a, f) + n * bulge))
        rows.append(row)
    for i in range(nv):
        bm.faces.new((rv, rows[i][0], rows[i + 1][0]))
        for j in range(nu - 1):
            bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    for p in obj.data.polygons:
        p.use_smooth = True
    mod = obj.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = 0.018
    mod.offset = 0
    pc.apply_transforms(obj)
    return obj


def spar(name, a, d, L, r0, r1, knob):
    n = 10
    pts = [a + d * (L * k / (n - 1)) for k in range(n)]
    radii = [r0 + (r1 - r0) * k / (n - 1) for k in range(n)]
    obj = pc.tube(name, pts, radii, sides=12)
    tip = a + d * L
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=knob)
    for v in bm.verts:
        v.co += tip
    k = pc.new_object(name + "_knob", bm)
    for p in k.data.polygons:
        p.use_smooth = True
    return [obj, k]


def wing(s):
    root = Vector((0.46 * s, -0.09, 1.06))
    m, b = frame(s)
    parts = [sail("Wing_Vela_mem", root, m, b, s)]
    parts += spar("mast", root - m * 0.05, m, MAST[3] + 0.09, 0.08, 0.056, 0.08)
    parts += spar("boom", root - b * 0.03, b, BOOM[3] + 0.05, 0.056, 0.042, 0.056)
    return pc.join(parts, "Wing_Vela_%s" % ("L" if s > 0 else "R"))


def build(arm):
    objs = [wing(1), wing(-1)]
    for o in objs:
        o.modifiers.clear()
        pc.shade_smooth(o, 60)
        pc.skin_like(o, arm, "Wing")
    return objs
