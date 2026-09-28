import math
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)


def fin(name, base, axis, h, half_len, half_thick, n=19, cap=0.16, rc=0.38):
    back = Vector((0, 1, 0))
    sink = 0.05
    p0 = base - axis * sink
    pts = pc.bezier(p0, base + axis * h * 0.35, base + axis * h * 0.7 + back * h * 0.08,
                    base + axis * h + back * h * 0.22, n)
    radii = []
    for i in range(n):
        t = i / (n - 1)
        k = max(0.0, (t - 0.1) / 0.9)
        if k <= 1 - cap:
            s = k / (1 - cap)
            f = 1 - (1 - rc) * s ** 1.1
        else:
            c = (k - (1 - cap)) / cap
            f = max(0.04, rc * math.sqrt(max(0.0, 1 - c * c)))
        radii.append((half_thick * f, half_len * f))
    return pc.tube(name, pts, radii, sides=14, side_hint=(1, 0, 0))


def build(arm):
    n = 8
    fins = []
    for i in range(n):
        t = i / (n - 1)
        y = -0.32 + t * 1.42
        p, nrm = pc.surface_point((0, y, 3.0), (0, 0, -1))
        if p is None:
            continue
        h = 0.24 * (1 - 0.42 * t ** 1.2) + 0.03 * math.sin(math.pi * min(1, t * 2.5))
        half_len = 0.17 * (1 - 0.38 * t)
        half_thick = 0.092 * (1 - 0.3 * t)
        axis = (nrm * 0.55 + Vector((0, 0.25, 0.8))).normalized()
        fins.append(fin("fin%d" % i, p, axis, h, half_len, half_thick))
    obj = pc.join(fins, "Back_PuasGruesas")
    pc.skin_like(obj, arm, "Back")
    return [obj]
