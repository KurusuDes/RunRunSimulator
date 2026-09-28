import math, bmesh
from mathutils import Vector
import part_common as pc
from p_Carnero import catmull

SLOTS = ("Horn",)

RAINBOW = ("F26B6B", "F5A15A", "F5D65A", "8FD16A", "6AB8E8", "A98BE0")


def spiral_band(name, base, axis, length, r0, t0, t1, rings=10, sides=16):
    axis = axis.normalized()
    side = axis.cross(Vector((1, 0, 0))).normalized()
    up = side.cross(axis).normalized()
    bm = bmesh.new()
    loops = []
    for i in range(rings + 1):
        t = t0 + (t1 - t0) * i / rings
        r = r0 * (1 - 0.55 * t) if t < 0.999 else 0.0
        c = base + axis * length * t
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            rr = r * (1 + 0.05 * math.sin(2 * a - t * 26)) * (0.93 + 0.07 * math.sin(math.pi * ((t - t0) / (t1 - t0))))
            ring.append(bm.verts.new(c + side * math.cos(a) * rr + up * math.sin(a) * rr))
        loops.append(ring)
    for a, b in zip(loops, loops[1:]):
        for k in range(sides):
            bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]))
    if t0 == 0:
        bm.faces.new(list(reversed(loops[0])))
    if t1 >= 0.999:
        tip = bm.verts.new(base + axis * (length + r0 * 0.25))
        for k in range(sides):
            bm.faces.new((loops[-1][k], loops[-1][(k + 1) % sides], tip))
    else:
        bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    pc.shade_smooth(obj)
    return obj


def curve(ctrl, t):
    p0, p1, p2, p3 = [Vector(c) for c in ctrl]
    u = 1 - t
    return p0 * u ** 3 + p1 * 3 * u * u * t + p2 * 3 * u * t * t + p3 * t ** 3


def stroke(name, ctrl, width, thick, n=18, sides=12, cap=0.24, tip=0.006, flat=1.6):
    pts, radii = [], []
    for i in range(n):
        t = (1 - math.cos(math.pi * i / (n - 1))) / 2
        pts.append(curve(ctrl, t))
        if t < cap:
            f = math.sqrt(max(0.0, 1 - (1 - t / cap) ** 2))
        else:
            s = (t - cap) / (1 - cap)
            f = (1 - s ** flat) ** 1.3
        f = max(f, 0.08 if i == 0 else 0.0)
        radii.append((width * f + tip, thick * f + tip))
    return pc.tube(name, pts, radii, sides=sides, side_hint=(1, 0, 0))


def blob_stack(prefix, colors, ctrl, width, thick, shifts, grow=0.05, n=18, sides=12):
    objs = []
    for k, hexc in enumerate(colors):
        c = [Vector(p) + Vector(s) * k for p, s in zip(ctrl, shifts)]
        objs.append(stroke("Deco_%s_%s%d" % (hexc, prefix, k), c, width * (1 + grow * k), thick, n=n, sides=sides))
    return objs


MANE_TOP = ((-0.56, 1.20), (-0.53, 1.40), (-0.43, 1.57), (-0.27, 1.64), (-0.10, 1.60), (0.03, 1.58), (0.13, 1.66), (0.20, 1.78))
MANE_LOW = ((-0.54, 1.10), (-0.44, 1.18), (-0.30, 1.25), (-0.16, 1.28), (-0.03, 1.30), (0.07, 1.35), (0.13, 1.47), (0.17, 1.60))
MANE_W = (0.14, 0.17, 0.19, 0.20, 0.20)


def mane_strand(name, keys, half_w, rad, tip):
    pts = catmull([(0, y, z) for y, z in keys], per=3)
    n = len(pts)
    radii = []
    for i in range(n):
        t = i / (n - 1)
        if t < 0.12:
            f = 0.55 + 0.45 * math.sin(0.5 * math.pi * t / 0.12)
        elif t < 0.55:
            f = 1.0
        else:
            s = (t - 0.55) / 0.45
            f = (1 - s ** 1.6) ** 1.2
        radii.append((half_w * f + tip, rad * f + tip))
    return pc.tube(name, pts, radii, sides=10, side_hint=(1, 0, 0))


def mane(colors):
    objs = []
    m = len(colors)
    for k, hexc in enumerate(colors):
        f = k / (m - 0.4)
        keys = [(a[0] * (1 - f) + b[0] * f, a[1] * (1 - f) + b[1] * f) for a, b in zip(MANE_TOP, MANE_LOW)]
        objs.append(mane_strand("Deco_%s_mane%d" % (hexc, k), keys, MANE_W[k], 0.07, 0.006))
    return objs


def build(arm):
    objs = []
    base, nrm = pc.head_top(0, -0.58)
    axis = Vector((0, -0.67, 0.74)).normalized()
    base = base - axis * 0.03
    n = len(RAINBOW)
    for i, hexc in enumerate(RAINBOW):
        objs.append(spiral_band("Deco_%s_horn%d" % (hexc, i), base, axis, 0.72, 0.1, i / n, (i + 1) / n))
    objs += mane(RAINBOW[:5])
    horn = [o for o in objs if "horn" in o.name]
    hair = [o for o in objs if "mane" in o.name]
    for o in horn:
        pc.skin_like(o, arm, "Horn")
    for o in hair:
        pc.skin_like(o, arm, "Back")
    return objs
