import sys, random
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


def front_matrix(x, y, z, rz=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ M


def fin(name, bm, mat, angle=50.0):
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


def plinth(R, accent):
    prof = [(0.0, 0.0), (R - 0.025, 0.0), (R, 0.024), (R - 0.02, 0.05), (0.0, 0.05)]
    fin("PlinthFoot", lathe_bm(prof, 24), accent, angle=60)
    r2 = R - 0.022
    prof = [(r2, 0.04), (r2, 0.062), (r2 - 0.024, 0.08), (0.0, 0.08)]
    fin("PlinthTop", lathe_bm(prof, 24), "SH_Cream", angle=60)


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
PLINTH_R = 0.37
DISH_Z = 0.075
WATER_Z = DISH_Z + 0.095
COL_TOP = 0.31
NECK_Z = 0.24
FILL_Z = 0.55
BOT_R = 0.2
BOT_TOP = 0.635


def build_dish():
    z = DISH_Z
    prof = [(0.3, z - 0.004), (0.34, z + 0.03), (0.352, z + 0.1), (0.346, z + 0.118),
            (0.31, z + 0.118), (0.3, z + 0.07), (0.0, z + 0.07)]
    fin("Dish", lathe_bm(prof, 24), ACC, angle=55)
    fin("DishRim", torus_bm(0.334, 0.032, 24, 5, matrix=Matrix.Translation((0, 0, z + 0.118))), ACC, angle=80)
    prof = [(0.314, z + 0.06), (0.31, WATER_Z), (0.0, WATER_Z)]
    fin("Water", lathe_bm(prof, 24), "SH_Water", angle=70)
    m = Matrix.Translation((0, 0, WATER_Z)) @ Matrix.Diagonal((1, 1, 0.45, 1))
    rip = torus_bm(0.205, 0.018, 20, 4, matrix=m)
    fin("Ripple", rip, "SH_Glass", angle=80)


def build_column():
    z0 = WATER_Z - 0.02
    prof = [(0.13, z0), (0.11, z0 + 0.035), (0.095, COL_TOP - 0.05), (0.0, COL_TOP)]
    fin("Column", lathe_bm(prof, 16), "SH_Cream", angle=55)
    c0 = COL_TOP - 0.055
    prof = [(0.09, c0), (0.14, c0 + 0.01), (0.165, c0 + 0.04), (0.168, c0 + 0.075), (0.145, c0 + 0.088),
            (0.1, c0 + 0.06), (0.0, c0 + 0.06)]
    fin("Collar", lathe_bm(prof, 20), "SH_Cream", angle=55)
    fin("CollarRim", torus_bm(0.16, 0.028, 20, 5, matrix=Matrix.Translation((0, 0, c0 + 0.082))), ACC, angle=80)


def build_bottle():
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
    bm = bmesh.new()
    for a, zz, s in ((240, 0.5, 0.034), (262, 0.44, 0.024), (300, 0.52, 0.028), (60, 0.48, 0.03)):
        r = R - 0.008
        ellipsoid_bm((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), zz), (s, s, s), 8, 4, bm=bm)
    fin("Bubbles", bm, "SH_Glass", angle=80)


def build_cap():
    z = BOT_TOP - 0.012
    prof = [(0.0, z), (0.1, z), (0.112, z + 0.014), (0.105, z + 0.034), (0.07, z + 0.05), (0.0, z + 0.054)]
    fin("Cap", lathe_bm(prof, 16), ACC, angle=55)
    d = badge_bm(drop_outline(0.14), 0.07, 0.022, 2, matrix=front_matrix(0, 0.035, z + 0.05 + 0.056))
    fin("DropKnob", d, "SH_Cream", angle=60)


out, flags = cli()
begin()
plinth(PLINTH_R, ACC)
build_dish()
build_column()
build_bottle()
build_cap()
ob = join_all("ShopWater")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.95, 0.25, 0), target=(-0.4, 0.0, 0.42), ortho=2.5)
