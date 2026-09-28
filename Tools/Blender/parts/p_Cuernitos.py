from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)


def cone(name, pts, r0, power=0.85, tip=0.006):
    n = len(pts)
    radii = []
    for i in range(n):
        t = i / (n - 1)
        flare = 1 + 0.35 * max(0.0, 1 - t / 0.18) ** 2
        radii.append(max(tip, r0 * flare * (1 - t) ** power))
    return pc.tube(name, pts, radii, sides=16)


def horn(name, x, y, length, r0, direction, curl):
    root, nrm = pc.head_top(x, y)
    d = Vector(direction).normalized()
    root = root - nrm * 0.06
    back = Vector((0, 1, 0))
    pts = pc.bezier(root,
                    root + d * length * 0.4,
                    root + d * length * 0.75 + back * curl * 0.3,
                    root + d * length + back * curl, 16)
    return cone(name, pts, r0)


def build(arm):
    right = horn("Horn_Cuernitos_R", 0.2, -0.47, 0.29, 0.11, (0.55, -0.55, 1.0), 0.07)
    left = pc.mirror_x(right, "Horn_Cuernitos_L")
    for o in (right, left):
        pc.shade_smooth(o)
        pc.skin_like(o, arm, "Horn")
    return [right, left]
