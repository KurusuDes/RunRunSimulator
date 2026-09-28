import math
from mathutils import Vector
import part_common as pc
from p_Carnero import catmull

SLOTS = ("Horn",)

SPREAD = math.radians(45)
LEAN = math.radians(12)
U = Vector((math.cos(SPREAD), -math.sin(SPREAD), 0))
V = Vector((math.sin(LEAN), 0, math.cos(LEAN)))
W = Vector((math.sin(SPREAD), math.cos(SPREAD), 0))

TRUNK = ((0.0, -0.08, 0.0), (0.03, 0.21, 0.06), (0.07, 0.46, 0.08), (0.04, 0.70, 0.05), (-0.04, 0.90, -0.03))
TINE = ((0.02, 0.20, 0.06), (0.13, 0.36, 0.05), (0.25, 0.49, 0.035), (0.31, 0.67, 0.015))
NUB = ((0.05, 0.58, 0.065), (0.10, 0.65, 0.06), (0.13, 0.74, 0.05))


def profile(n, width, thick, start=1.0, peak=0.25, tip=0.006, power=1.4):
    radii = []
    for i in range(n):
        t = i / (n - 1)
        if t < peak:
            f = start + (1 - start) * math.sin(0.5 * math.pi * t / peak)
        else:
            f = (1 - ((t - peak) / (1 - peak)) ** power) ** 0.9
        radii.append((max(tip, thick * (0.45 + 0.55 * f)), max(tip, width * f)))
    return radii


def local(root, keys):
    return [root + U * u + V * v + W * w for u, v, w in keys]


def build(arm):
    root, _ = pc.head_top(0.21, -0.36)
    trunk_pts = catmull(local(root, TRUNK), per=5)
    tine_pts = catmull(local(root, TINE), per=5)
    nub_pts = catmull(local(root, NUB), per=4)
    parts = [pc.tube("trunk", trunk_pts, profile(len(trunk_pts), 0.14, 0.068, start=1.15, peak=0.12, power=2.2), sides=12, side_hint=W),
             pc.tube("tine", tine_pts, profile(len(tine_pts), 0.10, 0.055, start=0.5, peak=0.3, power=1.8), sides=10, side_hint=W),
             pc.tube("nub", nub_pts, profile(len(nub_pts), 0.055, 0.04, start=0.5, peak=0.3, power=1.6), sides=10, side_hint=W)]
    brow_pts = []
    for i in range(10):
        t = i / 9
        ang = math.radians(24 + 14 * t)
        y = root.y + 0.02 - 0.30 * t
        c = Vector((0, y, 0.72))
        d = Vector((math.sin(ang), 0, math.cos(ang)))
        p, nrm = pc.surface_point(c + d * 3.0, -d)
        brow_pts.append(p + nrm * (0.0 - 0.03 * (1 - t) ** 4))
        brow_nrm = nrm
    radii = []
    for i in range(10):
        t = i / 9
        w = 0.055 * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.6 + 0.006
        radii.append((0.016, w))
    parts.append(pc.tube("brow", brow_pts, radii, sides=10, side_hint=brow_nrm))
    right = pc.join(parts, "Horn_Astas_R")
    right.modifiers.clear()
    pc.shade_smooth(right, angle=85)
    left = pc.mirror_x(right, "Horn_Astas_L")
    for o in (right, left):
        pc.skin_like(o, arm, "Horn")
    return [right, left]
