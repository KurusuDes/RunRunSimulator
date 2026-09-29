import math
import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)

ROOT2 = Vector((-0.02, 0.0))
WRIST = Vector((0.08, 0.2))
TIPS = (Vector((0.46, 0.29)), Vector((0.44, 0.1)), Vector((0.3, -0.03)))
TAIL = Vector((0.08, -0.05))
DEPTH = 0.42
ICON_BASE = [(-0.2, 0.7), (0.4, 0.7)]


def quad(a, b, c, n):
    return [a * (1 - t) ** 2 + c * 2 * t * (1 - t) + b * t * t for t in (i / (n - 1) for i in range(n))]


def outline2d(tips, wrist, tail, root2, depth):
    pts = []
    pts += quad(root2, wrist, (root2 + wrist) / 2 + Vector((-0.035, 0.0)), 5)[:-1]
    pts += quad(wrist, tips[0], (wrist + tips[0]) / 2 + Vector((-0.02, 0.04)), 6)[:-1]
    ends = list(tips) + [tail]
    for a, b in zip(ends, ends[1:]):
        mid = (a + b) / 2
        pts += quad(a, b, mid + (wrist - mid) * depth, 7)[:-1]
    pts += quad(tail, root2, (tail + root2) / 2, 3)[:-1]
    return pts


def rod(name, pts, r0, r1, sides=8, taper=0.8):
    n = len(pts)
    radii = [r1 + (r0 - r1) * (1 - i / (n - 1)) ** taper for i in range(n)]
    radii[-1] = 0.006
    return pc.tube(name, pts, radii, sides=sides)


def knuckle(name, center, r, axis):
    pts, radii = [], []
    for i in range(7):
        a = math.pi * i / 6
        pts.append(center + axis * (-math.cos(a) * r))
        radii.append(max(math.sin(a) * r, 0.004))
    return pc.tube(name, pts, radii, sides=8)


def kite(name, root, arm_dir, fin_dir, size, tips=TIPS, wrist=WRIST, tail=TAIL, root2=ROOT2,
         depth=DEPTH, bend=-0.35, thick=1.0, stalk=None, bones=True, mem_thick=0.018):
    A = Vector(arm_dir).normalized()
    F = Vector(fin_dir)
    F = (F - A * F.dot(A)).normalized()
    N = F.cross(A).normalized()

    def to3(p, lift=0.0):
        b = bend * (max(p.x, 0.0) ** 2 + 0.7 * max(p.y - wrist.y * 0.5, 0.0) ** 2)
        return Vector(root) + (F * p.x + A * p.y + N * b) * size + N * lift

    ol = outline2d(tips, wrist, tail, root2, depth)
    c2 = sum(ol, Vector((0, 0))) / len(ol)
    bm = bmesh.new()
    cv = bm.verts.new(to3(c2))
    rings = 3
    grid = [[bm.verts.new(to3(c2 + (p - c2) * (k / rings))) for p in ol] for k in range(1, rings + 1)]
    n = len(ol)
    for i in range(n):
        bm.faces.new((cv, grid[0][i], grid[0][(i + 1) % n]))
    for a, b in zip(grid, grid[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], b[i], b[j], a[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mem = pc.new_object(name + "_mem", bm)
    for p in mem.data.polygons:
        p.use_smooth = True
    mod = mem.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = mem_thick * size * thick
    mod.offset = 0
    pc.apply_transforms(mem)
    parts = [mem]
    if not bones:
        return pc.join(parts, name)
    k = size * thick
    arm_pts = [to3(p) for p in quad(root2 + Vector((0.0, -0.08)), wrist, (root2 + wrist) / 2 + Vector((-0.035, 0.0)), 6)]
    if stalk is not None:
        arm_pts = [Vector(stalk)] + arm_pts
    parts.append(pc.tube(name + "_arm", arm_pts, [0.055 * k] + [0.052 * k - 0.01 * k * i / (len(arm_pts) - 2) for i in range(len(arm_pts) - 1)], sides=8))
    parts.append(rod(name + "_f0", [to3(p) for p in quad(wrist, tips[0], (wrist + tips[0]) / 2 + Vector((-0.02, 0.04)), 8)], 0.04 * k, 0.013 * k))
    for i, t in enumerate(tips[1:]):
        parts.append(rod(name + "_f%d" % (i + 1), [to3(p) for p in quad(wrist, t, (wrist + t) / 2 + Vector((0.0, 0.025)), 8)], 0.035 * k, 0.012 * k))
    parts.append(knuckle(name + "_kn", to3(wrist), 0.055 * k, A))
    return pc.join(parts, name)


def build(arm):
    side = []
    for s in (1, -1):
        p, nrm = pc.surface_point((3.0 * s, 0.02, 0.76), (-s, 0, 0))
        root = p - nrm * 0.03
        o = kite("Back_Cometitas_%s" % ("L" if s > 0 else "R"), root, (0.4 * s, 0.55, 0.8),
                 (0.2 * s, 1.0, -0.15), 1.3, bend=-0.3 * s)
        side.append(o)
    obj = pc.join(side, "Back_Cometitas")
    pc.shade_smooth(obj, 70)
    pc.skin_like(obj, arm, "Back")
    return [obj]
