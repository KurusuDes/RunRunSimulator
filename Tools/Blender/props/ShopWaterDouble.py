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


def drop_outline(size, n=24):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 0.86 * math.sin(t) * math.sin(t / 2) ** 0.8
        y = math.cos(t)
        pts.append((x * size / 2.0, y * size / 2.0))
    return pts


ACC = "SH_Sky"
WOOD = "SH_Honey"
BASE_W, BASE_D = 1.38, 0.76
BASE_TOP = 0.1
S = 0.86
UX = 0.37
DISH_Z = 0.075
WATER_Z = DISH_Z + 0.095
COL_TOP = 0.31
NECK_Z = 0.24
FILL_Z = 0.55
BOT_R = 0.2
BOT_TOP = 0.635
TR_W, TR_D = 1.22, 0.62
TR_Z = BASE_TOP - 0.004
TR_WATER = TR_Z + 0.085


def build_base():
    rings = rbox_rings(BASE_W, BASE_D, 0.085, BASE_D / 2, 0.034, seg=3, Rb=0.016, segb=1)
    fin("BaseFoot", loft(rings, 6), WOOD, angle=60)
    rings = rbox_rings(BASE_W - 0.12, BASE_D - 0.12, BASE_TOP - 0.07, BASE_D / 2 - 0.06, 0.016, seg=2, z0=0.07)
    fin("BaseTop", loft(rings, 6), "SH_Cream", angle=60)


def ring(inset, z):
    return (TR_W - 2 * inset, TR_D - 2 * inset, TR_D / 2 - inset, z)


def build_trough():
    z = TR_Z
    rings = [ring(0.045, z), ring(0.012, z + 0.03), ring(0.0, z + 0.085), ring(0.006, z + 0.1),
             ring(0.04, z + 0.1), ring(0.05, z + 0.065)]
    fin("Trough", loft(rings, 6), ACC, angle=55)
    path = [(x, y, z + 0.1) for x, y in rrect(TR_W - 0.046, TR_D - 0.046, TR_D / 2 - 0.023, 6)]
    fin("TroughRim", loop_tube_bm(path, 0.03, 6), ACC, angle=80)
    rings = [ring(0.048, z + 0.06), ring(0.05, TR_WATER)]
    fin("Water", loft(rings, 6, cap0=False), "SH_Water", angle=70)
    bm = bmesh.new()
    for sx in (-1, 1):
        m = Matrix.Translation((sx * UX, 0, TR_WATER)) @ Matrix.Diagonal((1, 1, 0.45, 1))
        torus_bm(0.165, 0.017, 20, 4, bm=bm, matrix=m)
    fin("Ripple", bm, "SH_Glass", angle=80)


def build_column():
    z0 = WATER_Z - 0.02
    prof = [(0.13, z0), (0.11, z0 + 0.035), (0.095, COL_TOP - 0.05), (0.0, COL_TOP)]
    fin("Column", lathe_bm(prof, 16), "SH_Cream", angle=55)
    c0 = COL_TOP - 0.055
    prof = [(0.09, c0), (0.14, c0 + 0.01), (0.165, c0 + 0.04), (0.168, c0 + 0.075), (0.145, c0 + 0.088),
            (0.1, c0 + 0.06), (0.0, c0 + 0.06)]
    fin("Collar", lathe_bm(prof, 20), "SH_Cream", angle=55)
    fin("CollarRim", torus_bm(0.16, 0.028, 20, 5, matrix=Matrix.Translation((0, 0, c0 + 0.082))), ACC, angle=80)


def build_bottle(seed):
    z = NECK_Z
    R = BOT_R
    prof = [(0.0, z), (0.07, z), (0.075, z + 0.06), (0.11, z + 0.1), (0.17, z + 0.135), (R - 0.004, z + 0.18),
            (R, z + 0.23), (R, FILL_Z)]
    fin("BottleWater", lathe_bm(prof, 20), "SH_Water", angle=60)
    top = BOT_TOP
    prof = [(R, FILL_Z), (R, top - 0.06), (R - 0.016, top - 0.022), (R - 0.06, top - 0.003), (0.0, top)]
    fin("BottleGlass", lathe_bm(prof, 20), "SH_Glass", angle=60)
    bm = torus_bm(R + 0.004, 0.02, 16, 5, matrix=Matrix.Translation((0, 0, 0.475)))
    torus_bm(R + 0.004, 0.02, 16, 5, bm=bm, matrix=Matrix.Translation((0, 0, 0.585)))
    fin("BottleRibs", bm, "SH_Glass", angle=80)
    rnd = random.Random(seed)
    bm = bmesh.new()
    for a, zz, s in ((240, 0.5, 0.034), (262, 0.44, 0.024), (300, 0.52, 0.028), (60, 0.48, 0.03)):
        a += rnd.uniform(-25, 25)
        r = R - 0.008
        ellipsoid_bm((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), zz), (s, s, s), 8, 4, bm=bm)
    fin("Bubbles", bm, "SH_Glass", angle=80)


def build_cap():
    z = BOT_TOP - 0.012
    prof = [(0.0, z), (0.1, z), (0.112, z + 0.014), (0.105, z + 0.034), (0.07, z + 0.05), (0.0, z + 0.054)]
    fin("Cap", lathe_bm(prof, 16), ACC, angle=55)
    d = badge_bm(drop_outline(0.14), 0.07, 0.022, 2, matrix=front_matrix(0, 0.035, z + 0.05 + 0.056))
    fin("DropKnob", d, "SH_Cream", angle=60)


def unit(x, seed):
    G[0] = Matrix.Translation((x, 0, TR_Z + 0.06 - (DISH_Z + 0.07) * S)) @ Matrix.Diagonal((S, S, S, 1))
    build_column()
    build_bottle(seed)
    build_cap()
    G[0] = Matrix.Identity(4)


def build_yoke():
    zb = TR_Z + 0.06 + (COL_TOP - 0.055 + 0.045 - DISH_Z - 0.07) * S
    bm = tube_bm([(-UX, 0, zb), (0, 0, zb), (UX, 0, zb)], 0.044, 10)
    fin("Yoke", bm, WOOD, angle=60)
    d = badge_bm(drop_outline(0.27, 28), 0.085, 0.026, 2, matrix=front_matrix(0, 0.0425, zb + 0.025 + 0.135))
    fin("Drop", d, ACC, angle=60)


out, flags = cli()
begin()
build_base()
build_trough()
unit(-UX, 3)
unit(UX, 5)
build_yoke()
ob = join_all("ShopWaterDouble")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.25, 0.35, 0), target=(-0.35, 0.0, 0.42), ortho=2.9)
