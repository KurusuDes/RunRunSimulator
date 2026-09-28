import math
import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Horn",)

ORIGIN = Vector((0, -0.1, 0.72))
ELEV = 22
TOP, BOTTOM, SIDE = 0.36, 0.28, 0.25
RIM = 0.022
APEX = 0.11
SINK = 0.06
STEPS = 6


def ray_dir(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))


def surf(elev, x, y):
    d = ray_dir(0, elev)
    up = Vector((0, 0, 1))
    v = (up - d * up.dot(d)).normalized()
    return pc.surface_point(ORIGIN + Vector((x, 0, 0)) + v * y + d * 3.0, -d)


def patch_gem(name, elev, top, bottom, side, rim, apex, sink):
    corners = [(0, top), (-side, 0), (0, -bottom), (side, 0)]
    bm = bmesh.new()

    def vert(a, b, w_apex, w_a, w_b, lift):
        p, n = surf(elev, a[0] * w_a + b[0] * w_b, a[1] * w_a + b[1] * w_b)
        return bm.verts.new(p + n * lift)

    for k in range(4):
        a, b = corners[k], corners[(k + 1) % 4]
        rows = []
        for i in range(STEPS + 1):
            row = []
            for j in range(i + 1):
                w_apex = 1 - i / STEPS
                w_a = (i - j) / STEPS
                w_b = j / STEPS
                row.append(vert(a, b, w_apex, w_a, w_b, rim + (apex - rim) * w_apex))
            rows.append(row)
        for i in range(STEPS):
            for j in range(i + 1):
                bm.faces.new((rows[i][j], rows[i + 1][j], rows[i + 1][j + 1]))
                if j < i:
                    bm.faces.new((rows[i][j], rows[i + 1][j + 1], rows[i][j + 1]))
        edge = rows[-1]
        low = [vert(a, b, 0, 1 - j / STEPS, j / STEPS, -sink) for j in range(STEPS + 1)]
        up = [vert(a, b, 0, 1 - j / STEPS, j / STEPS, rim) for j in range(STEPS + 1)]
        for j in range(STEPS):
            bm.faces.new((up[j], low[j], low[j + 1], up[j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    pc.shade_smooth(obj, 25)
    return obj


def build(arm):
    obj = patch_gem("Horn_Cometa", ELEV, TOP, BOTTOM, SIDE, RIM, APEX, SINK)
    pc.skin_like(obj, arm, "Horn")
    return [obj]
