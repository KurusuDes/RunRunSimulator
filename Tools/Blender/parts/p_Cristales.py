import math
from mathutils import Vector
import part_common as pc
from p_Espinas import spine_samples

SLOTS = ("Back",)

COUNT = 7
Y0, Y1 = -0.18, 0.98


def crystal(name, base, axis, L, r, roll=0.0, sides=4):
    axis = axis.normalized()
    pts = [base, base + axis * L * 0.2, base + axis * L * 0.45, base + axis * L]
    radii = [r * 0.8, r, r * 0.96, 0.006]
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
    parts = []
    ks = [1.0 - 0.58 * i / (COUNT - 1) for i in range(COUNT)]
    for i, (p, nrm) in enumerate(spine_samples(Y0, Y1, COUNT, ks)):
        k = ks[i]
        nrm = Vector((0, nrm.y, nrm.z)).normalized()
        axis = (nrm * 0.8 + Vector((0, 0.35, 0.3))).normalized()
        L = 0.33 * k
        r = 0.125 * k
        parts.append(crystal("c%d" % i, p - axis * 0.06, axis, L + 0.06, r, math.pi / 4))
    obj = pc.join(parts, "Back_Cristales")
    pc.skin_like(obj, arm, "Back")
    return [obj]
