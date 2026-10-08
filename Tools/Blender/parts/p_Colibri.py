import math
from mathutils import Vector
import part_common as pc

SLOTS = ("Wing",)

AXIS = (0.42, 0.22, 0.80)
SWEEP = 0.22
PRIMARIES = ((0.0, 0.98, 0.105), (6.5, 0.87, 0.104), (13.0, 0.76, 0.102), (19.5, 0.65, 0.10),
             (26.0, 0.55, 0.098))
COVERTS = ((4.0, 0.40, 0.105), (13.0, 0.35, 0.105), (22.0, 0.30, 0.10))


def feather(name, root, d, n, L, W, thick=0.026, tip=0.006):
    back = n.cross(d).normalized()
    if back.y < 0:
        back = -back
    pts = pc.bezier(root - d * 0.04, root + d * (L * 0.35), root + d * (L * 0.72) + back * (L * SWEEP * 0.4),
                    root + d * L + back * (L * SWEEP), 13)
    radii = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        w = W * (0.6 + 0.4 * math.sin(math.pi * min(1.0, t / 0.4) * 0.5)) * (1 - max(0.0, (t - 0.62) / 0.38) ** 1.8) ** 0.7
        radii.append((thick * (1 - 0.5 * t) + 0.004, max(tip, w)))
    return pc.tube(name, pts, radii, sides=8, side_hint=n)


def wing(side):
    s = 1 if side == "L" else -1
    root = Vector((0.47 * s, -0.09, 1.07))
    out, back, up = Vector((s, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    a = (out * AXIS[0] + back * AXIS[1] + up * AXIS[2]).normalized()
    plane_b = (back - a * back.dot(a)).normalized()
    n = a.cross(plane_b).normalized()
    if n.x * s < 0:
        n = -n
    parts = []
    for i, (ang, L, W) in enumerate(PRIMARIES):
        r = math.radians(ang)
        d = (a * math.cos(r) + plane_b * math.sin(r)).normalized()
        base = root + plane_b * (0.022 * i) + n * (0.014 * i)
        parts.append(feather("p%d" % i, base, d, n, L, W))
    for i, (ang, L, W) in enumerate(COVERTS):
        r = math.radians(ang)
        d = (a * math.cos(r) + plane_b * math.sin(r)).normalized()
        base = root + n * (0.03 + 0.006 * i) + plane_b * (0.02 * i)
        parts.append(feather("c%d" % i, base, d, n, L, W, thick=0.03))
    return pc.join(parts, "Wing_Colibri_%s" % side)


def build(arm):
    objs = [wing("L"), wing("R")]
    for o in objs:
        o.modifiers.clear()
        pc.shade_smooth(o, 70)
        pc.skin_like(o, arm, "Wing")
    return objs
