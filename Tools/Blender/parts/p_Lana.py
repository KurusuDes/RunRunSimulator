import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)

BALLS = (
    (0.00, -0.54, 0.26),
    (0.00, -0.26, 0.20),
    (0.17, -0.40, 0.14),
    (-0.17, -0.40, 0.14),
    (0.00, -0.02, 0.15),
)
SINK = 0.07
SQUASH = 0.92
SEG_U, SEG_V = 18, 12


def ball(name, x, y, r):
    p, n = pc.head_top(x, y)
    n = (n + Vector((0, 0, 1))).normalized()
    center = p + n * (r * SQUASH - SINK)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=SEG_U, v_segments=SEG_V, radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x, v.co.y, v.co.z * SQUASH)) + center
    obj = pc.new_object(name, bm)
    pc.shade_smooth(obj, 80)
    return obj


def build(arm):
    parts = [ball("lana%d" % i, x, y, r) for i, (x, y, r) in enumerate(BALLS)]
    obj = pc.join(parts, "Horn_Lana")
    pc.skin_like(obj, arm, "Horn")
    return [obj]
