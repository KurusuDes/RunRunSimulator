import math
import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)

CENTER = Vector((0, 0.25, 0.45))
TH0, TH_R, PHI_R = 0.22, 0.80, 0.92
DOME = 0.21
BURY = 0.03
LIFT = 0.04
SHRINK = 0.86
HEX_R = 0.33
RIM = (0.045, 0.06)
ICON_BASE = [(-0.45, 1.00), (0.95, 0.19)]


def ray(u, v):
    th = TH0 + u * TH_R
    ph = v * PHI_R
    d = Vector((math.sin(ph), math.cos(ph) * math.sin(th), math.cos(ph) * math.cos(th)))
    p, n = pc.surface_point(CENTER + d * 3.0, -d)
    return p, n


def dome_h(u, v):
    r2 = u * u + v * v
    return DOME * math.sqrt(max(0.0, 1 - r2)) - BURY


def shell_point(u, v, extra=0.0):
    p, n = ray(u, v)
    return p + n * (dome_h(u, v) + extra), n


def shell(name, rings=12, seg=44):
    bm = bmesh.new()
    c = bm.verts.new(shell_point(0, 0)[0])
    loops = []
    for i in range(1, rings + 1):
        r = (i / rings) ** 0.8
        loop = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            loop.append(bm.verts.new(shell_point(r * math.cos(a), r * math.sin(a))[0]))
        loops.append(loop)
    for k in range(seg):
        bm.faces.new((c, loops[0][k], loops[0][(k + 1) % seg]))
    for a, b in zip(loops, loops[1:]):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a[k], b[k], b[j], a[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    mod = obj.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = 0.03
    mod.offset = -1
    for p in obj.data.polygons:
        p.use_smooth = True
    pc.apply_transforms(obj)
    return obj


def hex_outline(cu, cv, R, per=3):
    corners = []
    for k in range(6):
        a = math.radians(30 + 60 * k)
        corners.append(Vector((cu + R * math.cos(a), cv + R * math.sin(a))))
    pts = []
    for k in range(6):
        p, a, b = corners[k], corners[k - 1], corners[(k + 1) % 6]
        pa, pb = p.lerp(a, 0.22), p.lerp(b, 0.22)
        for s in range(per):
            t = s / per
            pts.append(pa * (1 - t) ** 2 + p * 2 * (1 - t) * t + pb * t * t)
    return pts


def scute(name, cu, cv, R):
    ol = hex_outline(cu, cv, R * SHRINK)
    c = Vector((cu, cv))
    bm = bmesh.new()
    fs = (0.0, 0.55, 0.82, 0.94, 1.0)
    rings = []
    for f in fs:
        lift = LIFT * (1 - f ** 6) ** 0.5 if f < 1 else -0.015
        if f == 0:
            rings.append([bm.verts.new(shell_point(cu, cv, LIFT)[0])])
            continue
        ring = []
        for q in ol:
            w = c + (q - c) * f
            ring.append(bm.verts.new(shell_point(w.x, w.y, lift)[0]))
        rings.append(ring)
    m = len(ol)
    for k in range(m):
        bm.faces.new((rings[0][0], rings[1][k], rings[1][(k + 1) % m]))
    for a, b in zip(rings[1:], rings[2:]):
        for k in range(m):
            j = (k + 1) % m
            bm.faces.new((a[k], b[k], b[j], a[j]))
    bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def rim(name, seg=56):
    pts = []
    for k in range(seg + 1):
        a = 2 * math.pi * k / seg
        u, v = 0.97 * math.cos(a), 0.97 * math.sin(a)
        pts.append(shell_point(u, v, 0.0)[0])
    p, n = ray(0, 0)
    return pc.tube(name, pts, [RIM] * len(pts), sides=8, cap=False)


def build(arm):
    parts = [shell("Back_Coraza")]
    k = 0
    for j in (-1, 0, 1):
        for i in range(-2, 3):
            u = i * 0.6 + (0.3 if j % 2 else 0.0)
            v = j * 0.52
            if u * u + v * v < 0.75:
                parts.append(scute("sc%d" % k, u, v, HEX_R))
                k += 1
    parts.append(rim("rim"))
    obj = pc.join(parts, "Back_Coraza")
    obj.modifiers.clear()
    pc.shade_smooth(obj, 50)
    pc.skin_like(obj, arm, "Back")
    return [obj]
