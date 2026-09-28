import math
from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)


def plug(name, base, axis, R, H, sink=0.08, bevel=0.32, sides=24, side_hint=None):
    axis = Vector(axis).normalized()
    b = R * bevel
    prof = [(-sink, R * 0.94), (0.0, R), (H - b, R)]
    for a in (22, 45, 68):
        t = math.radians(a)
        prof.append((H - b + b * math.sin(t), R - b + b * math.cos(t)))
    prof.append((H, (R - b) * 0.85))
    prof.append((H + 0.004, (R - b) * 0.45))
    pts = [Vector(base) + axis * h for h, _ in prof]
    return pc.tube(name, pts, [r for _, r in prof], sides=sides, side_hint=side_hint)


def build(arm):
    p, nrm = pc.surface_point((1.5, -0.36, 1.0), (-1, 0, 0))
    axis = (nrm + Vector((1.2, -0.15, 0.1))).normalized()
    left = plug("plugL", p, axis, 0.14, 0.15, side_hint=(0, 0, 1))
    obj = pc.join([left, pc.mirror_x(left, "plugR")], "Horn_Tapones")
    pc.skin_like(obj, arm, "Horn")
    return [obj]
