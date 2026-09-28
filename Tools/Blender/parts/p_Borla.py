from mathutils import Vector
import part_common as pc
from p_Unicornio import RAINBOW, blob_stack

SLOTS = ("Back",)

TIP_Y = 1.03
TUFT = ((0, -0.04, 0.0), (0, 0.06, 0.09), (0, 0.15, -0.01), (0, 0.21, 0.11))
TUFT_SHIFT = ((0, 0.008, -0.014), (0, 0.02, -0.024), (0, 0.012, -0.018), (0, -0.004, -0.008))


def tip_root():
    p, _ = pc.surface_point((0, TIP_Y, 3.0), (0, 0, -1))
    q, _ = pc.surface_point((0, TIP_Y, -3.0), (0, 0, 1))
    return Vector((0, TIP_Y, (p.z + q.z) * 0.5))


def build(arm):
    root = tip_root()
    ctrl = [root + Vector(c) for c in TUFT]
    objs = blob_stack("back", RAINBOW[:4], ctrl, 0.06, 0.06, TUFT_SHIFT, grow=0.03, n=14, sides=10)
    for o in objs:
        pc.skin_like(o, arm, "Back")
    return objs
