import math
from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)


def crystal(name, base, axis, L, r, roll=0.0, sides=6):
    axis = axis.normalized()
    pts = [base, base + axis * L * 0.22, base + axis * L * 0.48, base + axis * L]
    radii = [r * 0.55, r, r * 0.96, 0.006]
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    side = axis.cross(ref).normalized()
    up = side.cross(axis)
    hint = side * math.cos(roll) + up * math.sin(roll)
    obj = pc.tube(name, pts, radii, sides=sides, side_hint=tuple(hint))
    for m in list(obj.modifiers):
        obj.modifiers.remove(m)
    for p in obj.data.polygons:
        p.use_smooth = False
    return obj


def build(arm):
    root, nrm = pc.head_top(0.0, -0.60)
    center = root - nrm * 0.10
    specs = [
        ((0.00, -0.32, 0.95), 0.72, 0.190, 0.1),
        ((0.06, -0.94, 0.34), 0.60, 0.170, 0.5),
        ((0.84, -0.45, 0.30), 0.56, 0.160, 0.3),
        ((-0.80, -0.52, 0.30), 0.52, 0.158, 0.7),
        ((0.45, 0.02, 0.89), 0.42, 0.140, 0.9),
        ((-0.38, 0.30, 0.87), 0.34, 0.125, 0.2),
    ]
    parts = []
    for i, (d, L, r, roll) in enumerate(specs):
        parts.append(crystal("c%d" % i, center, Vector(d), L + 0.10, r, roll))
    obj = pc.join(parts, "Horn_Cristal")
    pc.skin_like(obj, arm, "Horn")
    return [obj]
