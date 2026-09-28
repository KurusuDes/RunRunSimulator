from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)

KEYS = ((0.16, -0.42, 1.10), (0.22, -0.34, 1.36), (0.34, -0.16, 1.48), (0.47, 0.04, 1.40),
        (0.57, 0.14, 1.18), (0.63, 0.08, 0.96), (0.66, -0.06, 0.82), (0.68, -0.20, 0.80),
        (0.68, -0.30, 0.87), (0.67, -0.31, 0.97), (0.65, -0.24, 1.02))
CURL = 3
R0, R1 = 0.19, 0.065


def catmull(keys, per=6):
    k = [Vector(p) for p in keys]
    k = [k[0] * 2 - k[1]] + k + [k[-1] * 2 - k[-2]]
    out = []
    for i in range(1, len(k) - 2):
        p0, p1, p2, p3 = k[i - 1], k[i], k[i + 1], k[i + 2]
        for s in range(per):
            t = s / per
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    out.append(k[-2])
    return out


def build(arm):
    pts = catmull(KEYS)
    n = len(pts)
    body = n - 1 - CURL * 6
    radii = []
    for i in range(n):
        if i <= body:
            t = i / body
            r = R0 + (R1 - R0) * t ** 1.3
        else:
            s = (i - body) / (n - 1 - body)
            r = R1 * (1 - s ** 1.8) ** 0.9 + 0.006 * s
        radii.append((r * 0.9, r * 1.25))
    right = pc.tube("Horn_Carnero_R", pts, radii, sides=14, side_hint=(1, 0, 0))
    left = pc.mirror_x(right, "Horn_Carnero_L")
    for o in (right, left):
        pc.skin_like(o, arm, "Horn")
    return [right, left]
