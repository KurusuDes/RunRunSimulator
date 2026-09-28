import math
import part_common as pc
from p_Carnero import catmull

SLOTS = ("Horn",)

KEYS = ((0.34, -0.10, 1.66), (0.33, -0.22, 1.50), (0.34, -0.50, 1.44), (0.38, -0.80, 1.30),
        (0.42, -0.98, 1.02), (0.42, -0.98, 0.70))
HEEL = 1
STALK = ((0.21, -0.18, 1.16), (0.25, -0.22, 1.30), (0.30, -0.26, 1.42), (0.33, -0.28, 1.49))


def build(arm):
    pts = catmull(KEYS, per=7)
    n = len(pts)
    heel = HEEL * 7
    radii = []
    for i in range(n):
        if i <= heel:
            t = 1 - i / heel
            w = 0.15 * (1 - t) ** 0.6 + 0.01
        else:
            t = (i - heel) / (n - 1 - heel)
            w = 0.17 * (1 - t) ** 0.9 + 0.006
        radii.append((max(0.006, w * 0.22), w))
    blade = pc.tube("Horn_Hoz_R", pts, radii, sides=10, side_hint=(1, 0, 0))
    stalk_pts = pc.bezier(*STALK, 8)
    stalk = pc.tube("Horn_Hoz_Stalk", stalk_pts, [0.06 - 0.025 * i / 7 for i in range(8)], sides=10)
    right = pc.join([blade, stalk], "Horn_Hoz_R")
    left = pc.mirror_x(right, "Horn_Hoz_L")
    for o in (right, left):
        pc.skin_like(o, arm, "Horn")
    return [right, left]
