import part_common as pc
from p_Cometa import patch_gem

SLOTS = ("Horn",)

ELEV = 24
TOP, BOTTOM, SIDE = 0.44, 0.26, 0.34
RIM = 0.024
APEX = 0.13
SINK = 0.06


def build(arm):
    obj = patch_gem("Horn_Mechon", ELEV, TOP, BOTTOM, SIDE, RIM, APEX, SINK)
    pc.skin_like(obj, arm, "Horn")
    return [obj]
