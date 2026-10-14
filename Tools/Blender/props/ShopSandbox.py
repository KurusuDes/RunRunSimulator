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


def star_outline(ro, rin, n=5):
    pts = []
    for k in range(2 * n):
        a = math.pi / 2 + math.pi * k / n
        r = ro if k % 2 == 0 else rin
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


HALF = 1.0
STUMP = 0.875
STUMP_R = 0.125
STUMP_H = 0.37
LOG_R = 0.092
LOG_Z = (LOG_R, LOG_R * 2.8)
SAND_IN = 0.83
SAND_Z = 0.19
CASTLE = (-0.32, 0.28)
BUCKET = (0.42, -0.36)
DIG = (0.38, -0.05)

rng = random.Random(154)


def build_stumps():
    bark, top, ring = bmesh.new(), bmesh.new(), bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = STUMP_H + rng.uniform(-0.02, 0.015)
            m = Matrix.Translation((sx * STUMP, sy * STUMP, 0)) @ Matrix.Rotation(rng.uniform(0, 6.28), 4, "Z")
            R = STUMP_R
            prof = [(0.0, 0.0), (R + 0.022, 0.0), (R + 0.012, 0.05), (R, 0.11), (R, h - 0.03), (R - 0.012, h - 0.004),
                    (R - 0.03, h)]
            lathe_bm(prof, 12, bm=bark, matrix=m)
            prof = [(R - 0.034, h - 0.012), (R - 0.03, h + 0.004), (R - 0.05, h + 0.012), (0.0, h + 0.014)]
            lathe_bm(prof, 12, bm=top, matrix=m)
            torus_bm(0.052, 0.009, 14, 4, bm=ring, matrix=Matrix.Translation((sx * STUMP, sy * STUMP, h + 0.012)))
    fin("StumpBark", bark, "SH_Timber", angle=55)
    fin("StumpTop", top, "SH_Oak", angle=55)
    fin("StumpRing", ring, "SH_Timber", angle=80)


def log_bm(a, b, r, bm, cut=False, caps=None):
    a, b = Vector(a), Vector(b)
    n = 7
    pts, rad = [], []
    bend = Vector((0, 0, rng.uniform(0.004, 0.012)))
    for i in range(n):
        t = i / (n - 1)
        p = a.lerp(b, t) + bend * math.sin(math.pi * t)
        pts.append(p)
        rad.append(r * (1.0 + 0.05 * math.sin(7.0 * t + rng.uniform(0, 3))))
    tube_bm(pts, rad, 10, bm=bm)


def build_logs():
    bark = bmesh.new()
    L = STUMP - 0.03
    for i, z in enumerate(LOG_Z):
        for s in (-1, 1):
            y = s * (STUMP - 0.005)
            log_bm((-L, y, z), (L, y, z), LOG_R, bark)
            x = s * (STUMP - 0.005)
            log_bm((x, -L, z + 0.006 * i), (x, L, z + 0.006 * i), LOG_R, bark)
    fin("Logs", bark, "SH_Walnut", angle=55)
    knots = bmesh.new()
    for s, x in ((-1, -0.35), (1, 0.42), (-1, 0.2)):
        y = s * (STUMP - 0.005 + LOG_R * 0.92)
        ellipsoid_bm((x, y, LOG_Z[1]), (0.035, 0.022, 0.028), 8, 4, bm=knots)
    for s, y in ((1, -0.3), (-1, 0.45)):
        x = s * (STUMP - 0.005 + LOG_R * 0.92)
        ellipsoid_bm((x, y, LOG_Z[1] + 0.006), (0.022, 0.035, 0.028), 8, 4, bm=knots)
    fin("Knots", knots, "SH_Timber", angle=80)


def sand_h(x, y):
    h = SAND_Z
    h += 0.012 * math.sin(3.1 * x + 0.7) * math.cos(2.7 * y - 0.4)
    h += 0.07 * math.exp(-(((x - CASTLE[0]) ** 2 + (y - CASTLE[1]) ** 2) / 0.09))
    h -= 0.06 * math.exp(-(((x - DIG[0]) ** 2 + (y - DIG[1]) ** 2) / 0.018))
    h += 0.035 * math.exp(-(((x - DIG[0] - 0.2) ** 2 + (y - DIG[1] + 0.02) ** 2) / 0.012))
    e = max(abs(x), abs(y))
    h += 0.05 * max(0.0, (e - 0.6) / 0.23) ** 2
    return h


def build_sand():
    n = 18
    bm = bmesh.new()
    V = []
    for j in range(n + 1):
        row = []
        for i in range(n + 1):
            x = -SAND_IN + 2 * SAND_IN * i / n
            y = -SAND_IN + 2 * SAND_IN * j / n
            row.append(bm.verts.new((x, y, sand_h(x, y))))
        V.append(row)
    for j in range(n):
        for i in range(n):
            bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    print("PART Sand tris=%d" % (2 * n * n))
    finish("Sand", bm, "SH_Straw", angle=80)


def build_castle():
    cx, cy = CASTLE
    zb = sand_h(cx, cy) - 0.03
    sand = bmesh.new()

    def tower(x, y, rb, rt, h, merl, bm):
        z0 = sand_h(x, y) - 0.03
        prof = [(0.0, z0), (rb + 0.02, z0), (rb, z0 + 0.03), (rt, z0 + h - 0.012), (rt + 0.012, z0 + h - 0.006),
                (rt + 0.006, z0 + h), (rt - 0.03, z0 + h), (rt - 0.03, z0 + h - 0.02), (0.0, z0 + h - 0.02)]
        lathe_bm(prof, 12, bm=bm, matrix=Matrix.Translation((x, y, 0)))
        for k in range(merl):
            a = 2 * math.pi * k / merl + 0.3
            rbox_bm((x + math.cos(a) * (rt - 0.012), y + math.sin(a) * (rt - 0.012), z0 + h + 0.022),
                    (0.045, 0.045, 0.05), 0.014, 1, bm=bm,
                    matrix=Matrix.Rotation(a, 4, "Z"))
        return z0 + h

    top = tower(cx, cy, 0.135, 0.105, 0.2, 5, sand)
    tower(cx + 0.2, cy - 0.12, 0.09, 0.07, 0.13, 4, sand)
    tower(cx - 0.17, cy - 0.15, 0.08, 0.062, 0.1, 4, sand)
    fin("Castle", sand, "SH_Straw", angle=50)
    pole = tube_bm([(cx, cy, top - 0.03), (cx, cy, top + 0.2)], 0.016, 6)
    ellipsoid_bm((cx, cy, top + 0.205), (0.024, 0.024, 0.024), 8, 4, bm=pole)
    fin("FlagPole", pole, "SH_Oak", angle=60)
    flag = [(0.0, 0.0), (0.13, -0.035), (0.0, -0.08)]
    fl = []
    for k in range(9):
        t = k / 8
        if t <= 0.5:
            p = Vector(flag[0]).lerp(Vector(flag[1]), t * 2)
        else:
            p = Vector(flag[1]).lerp(Vector(flag[2]), (t - 0.5) * 2)
        fl.append((p.x, p.y))
    fl += [(-0.004, -0.06), (-0.004, -0.02)]
    fin("Flag", badge_bm(fl, 0.028, 0.01, 1, matrix=front_matrix(cx + 0.012, cy + 0.014, top + 0.19, 25)), "SH_Teal", angle=60)


def build_bucket():
    bx, by = BUCKET
    z0 = sand_h(bx, by) - 0.025
    h = 0.19
    rb, rt, t = 0.095, 0.125, 0.025
    prof = [(0.0, z0), (rb, z0), (rb + 0.006, z0 + 0.012), (rt, z0 + h - 0.02), (rt + 0.012, z0 + h - 0.012),
            (rt + 0.012, z0 + h + 0.004), (rt - 0.004, z0 + h + 0.012), (rt - t, z0 + h), (rt - t, z0 + h - 0.06)]
    bm = lathe_bm(prof, 16, matrix=Matrix.Translation((bx, by, 0)))
    for s in (-1, 1):
        ellipsoid_bm((bx + s * (rt + 0.008), by, z0 + h - 0.035), (0.016, 0.03, 0.03), 8, 4, bm=bm)
    fin("Bucket", bm, "SH_Teal", angle=50)
    fill = lathe_bm([(rt - t + 0.004, z0 + h - 0.065), (rt - t - 0.01, z0 + h - 0.03), (0.06, z0 + h - 0.012),
                     (0.0, z0 + h - 0.002)], 16, matrix=Matrix.Translation((bx, by, 0)))
    fin("BucketSand", fill, "SH_Straw", angle=70)
    pts = []
    for k in range(13):
        a = math.pi * k / 12
        pts.append((bx + math.cos(a) * (rt + 0.012), by + 0.0 + math.sin(a) * 0.06 - 0.06 * math.sin(a) * 0.0,
                    z0 + h - 0.035 + math.sin(a) * 0.15))
    m = Matrix.Translation((bx, by, z0 + h - 0.035)) @ Matrix.Rotation(math.radians(-55), 4, "X") @ \
        Matrix.Translation((-bx, -by, -(z0 + h - 0.035)))
    hb = tube_bm([(p[0], by, p[2]) for p in pts], 0.018, 6)
    xf(hb, m)
    fin("Handle", hb, "SH_Oak", angle=70)


def build_shovel():
    x, y = DIG[0] + 0.22, DIG[1] + 0.03
    z = sand_h(x, y) + 0.1
    hm = (Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(35), 4, "Z") @
          Matrix.Rotation(math.radians(-28), 4, "X") @ front_matrix(0, 0, 0))
    blade = [(0.09, 0.03), (0.035, 0.05), (-0.035, 0.05), (-0.09, 0.03)]
    for k in range(13):
        a = math.pi + math.pi * k / 12
        blade.append((math.cos(a) * 0.1, -0.06 + math.sin(a) * 0.15))
    bm = badge_bm(blade, 0.034, 0.013, 2)
    for v in bm.verts:
        v.co.z -= 0.04 * (1 - (v.co.x / 0.1) ** 2) - 0.017
    xf(bm, hm)
    fin("Blade", bm, "SH_Teal", angle=60)
    h = tube_bm([hm @ Vector((0, 0.0, 0)), hm @ Vector((0, 0.34, 0))], 0.03, 8)
    fin("ShovelHandle", h, "SH_Oak", angle=60)
    grip = ellipsoid_bm(tuple(hm @ Vector((0, 0.36, 0))), (0.055, 0.055, 0.055), 10, 6)
    fin("ShovelGrip", grip, "SH_Oak", angle=80)


def build_star():
    x, y = -0.42, -0.42
    z = sand_h(x, y) - 0.012
    st = badge_bm(star_outline(0.13, 0.065), 0.05, 0.016, 2, matrix=Matrix.Translation((x, y, z)) @ Matrix.Rotation(0.4, 4, "Z"))
    fin("StarMold", st, "SH_Teal", angle=60)


out, flags = cli()
begin()
build_stumps()
build_logs()
build_sand()
build_castle()
build_bucket()
build_shovel()
build_star()
ob = join_all("ShopSandbox")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.55, -0.2, 0), target=(-0.3, 0.0, 0.3), ortho=3.6)
