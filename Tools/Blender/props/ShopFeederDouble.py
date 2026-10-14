import sys, random
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


G = [Matrix.Identity(4)]


def front_matrix(x, y, z, rz=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ M


def fin(name, bm, mat, angle=50.0):
    xf(bm, G[0])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def offset2d(pts, d):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        t = (p2 - p0).normalized()
        nin = Vector((-t.y, t.x)) * s
        out.append((p1.x + nin.x * d, p1.y + nin.y * d))
    return out


def badge_bm(outline, t, bev, steps=2, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = [(0.0, 0.0), (0.0, t - bev)]
    for j in range(1, steps + 1):
        a = math.pi / 2 * j / steps
        rings.append((bev * (1 - math.cos(a)), t - bev + bev * math.sin(a)))
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    vr = []
    for d, z in rings:
        vr.append([bm.verts.new((x, y, z)) for x, y in offset2d(outline, d)])
    n = len(outline)
    for A, B in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    c0 = bm.verts.new((cx, cy, 0.0))
    c1 = bm.verts.new((cx, cy, t))
    for k in range(n):
        bm.faces.new((vr[0][(k + 1) % n], vr[0][k], c0))
        bm.faces.new((vr[-1][k], vr[-1][(k + 1) % n], c1))
    if matrix is not None:
        xf(bm, matrix, [v for r in vr for v in r] + [c0, c1])
    return bm


def loop_tube_bm(path, radius, sides=6, bm=None, matrix=None):
    bm = bm or bmesh.new()
    P = [Vector(p) for p in path]
    n = len(P)
    rings = []
    for i in range(n):
        t = (P[(i + 1) % n] - P[i - 1]).normalized()
        side = (UP - t * UP.dot(t))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = t.cross(side).normalized()
        rings.append([bm.verts.new(P[i] + side * math.cos(2 * math.pi * k / sides) * radius +
                                   up * math.sin(2 * math.pi * k / sides) * radius) for k in range(sides)])
    for i in range(n):
        A, B = rings[i], rings[(i + 1) % n]
        for k in range(sides):
            bm.faces.new((A[k], A[(k + 1) % sides], B[(k + 1) % sides], B[k]))
    if matrix is not None:
        xf(bm, matrix, [v for r in rings for v in r])
    return bm


def heart_outline(size, n=28):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * size / 32.0, (y + 2.0) * size / 32.0))
    return pts


ACC = "SH_Sage"
WOOD = "SH_Honey"
BASE_W, BASE_D = 1.38, 0.76
BASE_TOP = 0.1
S = 0.86
UX = 0.37
DISH_Z = 0.075
HOP_Z0 = DISH_Z + 0.09
HOP_Z1 = 0.5


def build_base():
    rings = rbox_rings(BASE_W, BASE_D, 0.085, BASE_D / 2, 0.034, seg=3, Rb=0.016, segb=1)
    fin("BaseFoot", loft(rings, 6), WOOD, angle=60)
    rings = rbox_rings(BASE_W - 0.12, BASE_D - 0.12, BASE_TOP - 0.07, BASE_D / 2 - 0.06, 0.016, seg=2, z0=0.07)
    fin("BaseTop", loft(rings, 6), "SH_Cream", angle=60)


def build_dish():
    z = DISH_Z
    prof = [(0.3, z - 0.004), (0.34, z + 0.03), (0.352, z + 0.1), (0.346, z + 0.118),
            (0.31, z + 0.118), (0.3, z + 0.07), (0.0, z + 0.07)]
    fin("Dish", lathe_bm(prof, 24), ACC, angle=55)
    fin("DishRim", torus_bm(0.334, 0.032, 24, 5, matrix=Matrix.Translation((0, 0, z + 0.118))), ACC, angle=80)


def grain_z(r):
    z = DISH_Z
    if r >= 0.27:
        return z + 0.1
    if r <= 0.17:
        return z + 0.165
    t = (0.27 - r) / 0.1
    return z + 0.1 + 0.065 * t * t


def build_grain(seed):
    z = DISH_Z
    prof = [(0.314, z + 0.06), (0.3, z + 0.104), (0.235, z + 0.116), (0.175, z + 0.165), (0.0, z + 0.17)]
    fin("Grain", lathe_bm(prof, 24), "SH_Straw", angle=70)
    rnd = random.Random(seed)
    bm = bmesh.new()
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.15, 0.15)
        r = rnd.uniform(0.2, 0.29)
        s = rnd.uniform(0.9, 1.2)
        before = set(bm.verts)
        ellipsoid_bm((0, 0, 0), (0.036 * s, 0.032 * s, 0.024 * s), 8, 4, bm=bm)
        rot = Matrix.Rotation(rnd.uniform(0, math.pi), 4, "Z") @ Matrix.Rotation(rnd.uniform(-0.4, 0.4), 4, "X")
        xf(bm, Matrix.Translation((r * math.cos(a), r * math.sin(a), grain_z(r) + 0.006)) @ rot,
           [v for v in bm.verts if v not in before])
    fin("Kibble", bm, WOOD, angle=80)


def build_hopper():
    z0, z1 = HOP_Z0, HOP_Z1
    prof = [(0.16, z0), (0.165, z0 + 0.02), (0.182, z1 - 0.01), (0.17, z1 + 0.01)]
    fin("Hopper", lathe_bm(prof, 20), "SH_Cream", angle=50)
    bm = torus_bm(0.168, 0.026, 16, 5, matrix=Matrix.Translation((0, 0, z0 + 0.075)))
    torus_bm(0.183, 0.026, 16, 5, bm=bm, matrix=Matrix.Translation((0, 0, z1 - 0.03)))
    fin("HopperBands", bm, ACC, angle=80)
    l0 = z1 - 0.02
    prof = [(0.0, l0), (0.205, l0), (0.224, l0 + 0.015), (0.22, l0 + 0.04), (0.195, l0 + 0.066), (0.135, l0 + 0.09),
            (0.06, l0 + 0.1), (0.0, l0 + 0.102)]
    fin("Lid", lathe_bm(prof, 20), ACC, angle=55)


def build_window():
    zc = HOP_Z0 + 0.2
    w, h = 0.13, 0.22
    rs = 0.173
    yb = -math.sqrt(rs * rs - (w / 2) ** 2) + 0.004
    glass = loft(rbox_rings(w, h, 0.03, 0.03, 0.008, seg=2), 3, cap0=False, matrix=front_matrix(0, yb, zc))
    fin("WinGlass", glass, "SH_Glass", angle=60)
    fh = 0.13
    fill = loft(rbox_rings(w - 0.004, fh, 0.03, 0.036, 0.01, seg=2), 3, cap0=False,
                matrix=front_matrix(0, yb, zc - h / 2 + fh / 2))
    fin("WinFill", fill, "SH_Straw", angle=60)
    path = [(x, y, 0.0) for x, y in rrect(w + 0.02, h + 0.02, 0.05, 3)]
    fr = loop_tube_bm(path, 0.022, 5, matrix=front_matrix(0, yb - 0.012, zc))
    fin("WinFrame", fr, ACC, angle=70)


def unit(x, seed):
    G[0] = Matrix.Translation((x, 0, BASE_TOP - 0.004 - (DISH_Z - 0.004) * S)) @ Matrix.Diagonal((S, S, S, 1))
    build_dish()
    build_grain(seed)
    build_hopper()
    build_window()
    G[0] = Matrix.Identity(4)


LID_Z = BASE_TOP - 0.004 + (HOP_Z1 - 0.02 + 0.07 - DISH_Z + 0.004) * S


LID_TOP = BASE_TOP - 0.004 + (HOP_Z1 - 0.02 + 0.102 - DISH_Z + 0.004) * S


def build_yoke():
    zb = BASE_TOP - 0.004 + (HOP_Z1 - 0.03 - DISH_Z + 0.004) * S
    bm = tube_bm([(-UX, 0, zb), (0, 0, zb), (UX, 0, zb)], 0.046, 10)
    fin("Yoke", bm, WOOD, angle=60)
    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((sx * UX, 0.0, LID_TOP + 0.01), (0.07, 0.07, 0.055), 12, 6, bm=bm)
    fin("LidKnobs", bm, "SH_Cream", angle=70)
    hb = badge_bm(heart_outline(0.26, 26), 0.085, 0.026, 2, matrix=front_matrix(0, 0.0425, zb + 0.025 + 0.122))
    fin("Heart", hb, ACC, angle=60)


out, flags = cli()
begin()
build_base()
unit(-UX, 7)
unit(UX, 11)
build_yoke()
ob = join_all("ShopFeederDouble")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.25, 0.35, 0), target=(-0.35, 0.0, 0.42), ortho=2.9)
