import math
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)


def spike(name, base, axis, h, r0, n=12, tip=0.006):
    back = Vector((0, 1, 0))
    p0 = base - axis * 0.05
    pts = pc.bezier(p0, base + axis * h * 0.35, base + axis * h * 0.7 + back * h * 0.06,
                    base + axis * h + back * h * 0.18, n)
    radii = []
    for i in range(n):
        t = i / (n - 1)
        flare = 1 + 0.35 * max(0.0, 1 - t / 0.2) ** 2
        radii.append(max(tip, r0 * flare * (1 - t) ** 0.85))
    return pc.tube(name, pts, radii, sides=12)


def build(arm):
    n = 5
    spikes = []
    for side in (1, -1):
        for i in range(n):
            t = (i + (0.0 if side > 0 else 0.5)) / (n - 0.5)
            y = -0.16 + t * 1.12
            x = side * (0.11 - 0.03 * t)
            p, nrm = pc.surface_point((x, y, 3.0), (0, 0, -1))
            if p is None:
                continue
            h = 0.24 * (1 - 0.6 * t ** 1.1)
            r0 = 0.1 * (1 - 0.5 * t)
            axis = (nrm * 0.6 + Vector((side * 0.38, 0.35, 0.7))).normalized()
            spikes.append(spike("s%d_%d" % (side, i), p, axis, h, r0))
    obj = pc.join(spikes, "Back_PuasDobles")
    pc.skin_like(obj, arm, "Back")
    return [obj]
