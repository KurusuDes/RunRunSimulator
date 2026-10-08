import math
import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)

BAG_Y = 0.30
BAG_Z = 0.76
SIZE = (0.16, 0.235, 0.225)
EXP = 2.5
FLARE = 0.26
STRAP = (0.07, 0.02)
ICON_BASE = [(-0.2, 0.50), (0.8, 0.50)]


def spow(x, e):
    return math.copysign(abs(x) ** e, x)


def pouch(name, c, size, flare=FLARE, seg=(22, 14), exp=EXP):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=1.0)
    sx, sy, sz = size
    for v in bm.verts:
        x, y, z = v.co
        k = 1 + flare * max(0.0, -z) - 0.08 * max(0.0, z)
        v.co = Vector((spow(x, 2 / exp) * sx * k, spow(y, 2 / exp) * sy * k, spow(z, 2 / exp) * sz)) + c
    obj = pc.new_object(name, bm)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def flap(name, c, size, s, nu=16, nw=14):
    sx, sy, sz = size
    shell = pouch("tmp_flap", c, (sx * 1.10, sy * 1.07, sz * 1.08), flare=FLARE, seg=(36, 20))
    rows = []
    for i in range(nu):
        u = -0.94 + 1.88 * i / (nu - 1)
        lo = math.radians(-14 + 40 * abs(u) ** 2.0)
        hi = math.radians(128)
        row = []
        for j in range(nw):
            a = lo + (hi - lo) * j / (nw - 1)
            d = Vector((s * math.cos(a) * sx, u * sy * 1.25, math.sin(a) * sz)).normalized()
            hit, loc, nrm, _ = shell.ray_cast(c + d * 3.0, -d)
            row.append(loc if hit else c + d * sz)
        rows.append(row)
    bpy_data = shell.data
    import bpy
    bpy.data.objects.remove(shell)
    bpy.data.meshes.remove(bpy_data)
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in row] for row in rows]
    for i in range(nu - 1):
        for j in range(nw - 1):
            bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    for p in obj.data.polygons:
        p.use_smooth = True
    mod = obj.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = 0.032
    mod.offset = 0
    pc.apply_transforms(obj)
    return obj


def rounded_rect(c, a, b, w, h, r, per=4):
    pts = []
    corners = ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270))
    for cx, cy, a0 in corners:
        for k in range(per + 1):
            t = math.radians(a0 + 90 * k / per)
            pts.append(c + a * (cx + r * math.cos(t)) + b * (cy + r * math.sin(t)))
    pts.append(pts[0])
    return pts


def buckle(name, c, a, b, w, h, r=0.016):
    pts = rounded_rect(c, a, b, w, h, min(w, h) * 0.3)
    return pc.tube(name, pts, [r] * len(pts), sides=8, cap=False)


def strap_path(y, s0, s1, n=24):
    pts = []
    center = Vector((0, y, 0.72))
    for i in range(n):
        a = math.radians(s0 + (s1 - s0) * i / (n - 1))
        d = Vector((math.sin(a), 0, math.cos(a)))
        p, nrm = pc.surface_point(center + d * 3.0, -d)
        pts.append(p + nrm * 0.01)
    return pts


def bag(s):
    c = Vector((0, BAG_Y, BAG_Z))
    p, nrm = pc.surface_point((3.0 * s, BAG_Y, BAG_Z), (-s, 0, 0))
    c = Vector((p.x + s * (SIZE[0] * 0.78), BAG_Y, BAG_Z))
    side = "L" if s > 0 else "R"
    parts = [pouch("bag" + side, c, SIZE), flap("flap" + side, c, SIZE, s)]
    out = Vector((s, 0, 0))
    d = Vector((s * math.cos(math.radians(-14)) * SIZE[0], 0, math.sin(math.radians(-14)) * SIZE[2])).normalized()
    probe = pouch("tmp_probe", c, (SIZE[0] * 1.10, SIZE[1] * 1.07, SIZE[2] * 1.08), seg=(36, 20))
    hit, loc, nrm, _ = probe.ray_cast(c + d * 3.0, -d)
    import bpy
    me = probe.data
    bpy.data.objects.remove(probe)
    bpy.data.meshes.remove(me)
    face = loc + nrm * 0.03
    b = Vector((0, 0, 1))
    b = (b - nrm * b.dot(nrm)).normalized()
    parts.append(buckle("bk" + side, face, Vector((0, 1, 0)), b, 0.12, 0.10))
    tab = [face + b * 0.13 - nrm * 0.02, face + b * 0.04 - nrm * 0.008, face - b * 0.03 - nrm * 0.01]
    parts.append(pc.tube("tab" + side, tab, [(0.045, 0.012)] * 3, sides=8, side_hint=(0, 1, 0)))
    return parts


def build(arm):
    bags = bag(1) + bag(-1)
    path = strap_path(BAG_Y, -62, 62)
    strap = [pc.tube("strap", path, [STRAP] * len(path), sides=8, side_hint=(0, 1, 0))]
    top = path[len(path) // 2]
    strap.append(buckle("bk_top", top + Vector((0, 0, 0.016)), Vector((1, 0, 0)), Vector((0, 1, 0)), 0.12, 0.11, 0.012))
    objs = [pc.join(bags, "Back_Alforja"), pc.join(strap, "Back_Alforja_strap")]
    for o in objs:
        o.modifiers.clear()
        pc.shade_smooth(o, 60)
        pc.skin_like(o, arm, "Back")
    return objs
