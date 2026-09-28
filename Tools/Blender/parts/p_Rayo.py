import math
import bmesh
from mathutils import Vector, Matrix
import part_common as pc

SLOTS = ("Horn",)

OUTLINE = ((0.00, 0.12), (0.68, 0.34), (0.52, 0.07), (1.45, -0.02), (0.72, -0.07), (0.00, -0.09))
TIP_U = 1.45
FWD = Vector((0.34, -1.0, -0.04))
TILT = 38
THICK = 0.055


def bolt(name, root, fwd, up, T):
    fwd = fwd.normalized()
    up = (up - fwd * up.dot(fwd)).normalized()
    nrm = fwd.cross(up).normalized()
    poly = [Vector(p) for p in OUTLINE]
    bm = bmesh.new()
    front = [bm.verts.new(Vector((p.x, p.y, T / 2))) for p in poly]
    back = [bm.verts.new(Vector((p.x, p.y, -T / 2))) for p in poly]
    n = len(poly)
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    for k in range(n):
        bm.faces.new((front[k], back[k], back[(k + 1) % n], front[(k + 1) % n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    rim = [e for e in bm.edges if all(abs(abs(v.co.z) - T / 2) < 1e-6 for v in e.verts)]
    bmesh.ops.bevel(bm, geom=rim, offset=T * 0.34, segments=2, profile=0.5, affect="EDGES", clamp_overlap=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    for v in bm.verts:
        u, w, z = v.co
        z *= 1 - 0.75 * max(0.0, u / TIP_U) ** 1.3
        v.co = root + fwd * u + up * w + nrm * z
    obj = pc.new_object(name, bm)
    pc.shade_smooth(obj, 35)
    return obj


def build(arm):
    p, nrm = pc.surface_point((1.5, -0.34, 2.4), Vector((-1.0, 0, -0.95)))
    fwd = FWD.normalized()
    root = p - nrm * 0.05 - fwd * 0.10
    up = Matrix.Rotation(-math.radians(TILT), 3, fwd) @ Vector((0, 0, 1.0))
    left = bolt("Horn_Rayo_L", root, fwd, up, THICK)
    pc.apply_transforms(left)
    right = pc.mirror_x(left, "Horn_Rayo_R")
    for o in (left, right):
        pc.skin_like(o, arm, "Horn")
    return [left, right]
