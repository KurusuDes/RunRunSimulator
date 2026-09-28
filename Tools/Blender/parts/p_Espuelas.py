import math
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)

SPURS = ((0.00, 0.25), (0.17, 0.23), (0.34, 0.20), (0.50, 0.17), (0.65, 0.145), (0.79, 0.12), (0.92, 0.10), (1.03, 0.085))
X = Vector((1, 0, 0))


def spine(y):
    p, n = pc.surface_point((0, y, 3.0), (0, 0, -1))
    q, _ = pc.surface_point((0, y + 0.02, 3.0), (0, 0, -1))
    t = (q - p).normalized()
    n = X.cross(t).normalized()
    if n.z < 0:
        n = -n
    return p, n, t


def profile(n, width, thick, start=0.8, peak=0.25, power=1.6, tip=0.006):
    radii = []
    for i in range(n):
        t = i / (n - 1)
        if t < peak:
            f = start + (1 - start) * math.sin(0.5 * math.pi * t / peak)
        else:
            f = (1 - ((t - peak) / (1 - peak)) ** power) ** 1.1
        radii.append((max(tip, thick * (0.4 + 0.6 * f)), max(tip, width * f)))
    return radii


def spur(i, y, h):
    p, n, t = spine(y)
    b = p - n * 0.05
    main = pc.bezier(b, p + n * h * 0.55 - t * h * 0.08, p + n * h * 1.0 + t * h * 0.12, p + n * h * 0.86 + t * h * 0.62, 14)
    heel = pc.bezier(p - n * 0.03 + t * h * 0.15, p + n * h * 0.22 + t * h * 0.38, p + n * h * 0.34 + t * h * 0.58, p + n * h * 0.36 + t * h * 0.78, 9)
    a = pc.tube("spur%d" % i, main, profile(14, h * 0.42, h * 0.2 + 0.012, start=1.0, peak=0.15, power=1.5), sides=10, side_hint=X)
    c = pc.tube("heel%d" % i, heel, profile(9, h * 0.2, h * 0.14 + 0.01, start=0.7, peak=0.3, power=1.4), sides=8, side_hint=X)
    return [a, c]


def build(arm):
    parts = []
    for i, (y, h) in enumerate(SPURS):
        parts += spur(i, y, h)
    obj = pc.join(parts, "Back_Espuelas")
    obj.modifiers.clear()
    pc.shade_smooth(obj, angle=85)
    pc.skin_like(obj, arm, "Back")
    return [obj]
