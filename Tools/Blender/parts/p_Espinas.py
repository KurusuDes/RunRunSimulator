import math
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)

COUNT = 9
Y0, Y1 = -0.40, 1.02


def spine_samples(y0, y1, count, weights=None):
    ys = [y0 + (y1 - y0) * i / 60 for i in range(61)]
    pts = [pc.head_top(0.0, y) for y in ys]
    acc = [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + (b[0] - a[0]).length)
    out = []
    w = weights or [1.0] * count
    gaps = [(w[i] + w[i + 1]) / 2 for i in range(count - 1)]
    marks = [0.0]
    for g in gaps:
        marks.append(marks[-1] + g)
    for k in range(count):
        target = acc[-1] * marks[k] / marks[-1]
        j = min(range(len(acc)), key=lambda i: abs(acc[i] - target))
        out.append(pts[j])
    return out


def thorn(name, base, nrm, H, R):
    back = Vector((0, 1, 0))
    up = Vector((0, nrm.y, nrm.z)).normalized()
    pts = pc.bezier(base - up * 0.05, base + up * H * 0.45, base + up * H * 0.85 + back * H * 0.12,
                    base + up * H * 1.0 + back * H * 0.42, 10)
    radii = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        r = R * (1 - t) ** 0.85
        radii.append((max(0.006, r * 0.72), max(0.006, r)))
    return pc.tube(name, pts, radii, sides=10, side_hint=(1, 0, 0))


def build(arm):
    parts = []
    for i, (p, nrm) in enumerate(spine_samples(Y0, Y1, COUNT)):
        t = i / (COUNT - 1)
        k = 1.0 if t < 0.3 else 1.0 - 0.55 * (t - 0.3) / 0.7
        parts.append(thorn("t%d" % i, p, nrm, 0.27 * k, 0.125 * k))
    obj = pc.join(parts, "Back_Espinas")
    pc.shade_smooth(obj)
    pc.skin_like(obj, arm, "Back")
    return [obj]
