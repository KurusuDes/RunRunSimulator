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


ACC = "SH_Lilac"
PLINTH_R = 0.465
ZB = 0.07
RC = 0.345
HALF_W = 0.115
H_TOP = 0.26
H_DIP = 0.15
LOBES = 10
SEGS = 50
SEC = 10


def bolster_h(th):
    d = math.atan2(math.sin(th + math.pi / 2), math.cos(th + math.pi / 2))
    return H_TOP - (H_TOP - H_DIP) * math.exp(-(d / 0.62) ** 2)


def build_bolster():
    bm = bmesh.new()
    rings = []
    for i in range(SEGS):
        th = 2 * math.pi * i / SEGS
        puff = 1.0 + 0.07 * math.cos(LOBES * th)
        h = bolster_h(th) * (1.0 + 0.05 * math.cos(LOBES * th))
        hh = h / 2
        a = HALF_W * puff
        ring = []
        for j in range(SEC):
            ph = 2 * math.pi * j / SEC - math.pi / 2
            r = RC + a * math.cos(ph) * (1.0 + 0.12 * max(0.0, math.sin(ph)))
            z = ZB + hh + hh * math.sin(ph) * 1.0
            z = max(z, ZB)
            if math.sin(ph) > 0:
                r += 0.025 * math.sin(ph) * math.cos(ph)
            ring.append(bm.verts.new((r * math.cos(th), r * math.sin(th), z)))
        rings.append(ring)
    for i in range(SEGS):
        A, B = rings[i], rings[(i + 1) % SEGS]
        for j in range(SEC):
            j1 = (j + 1) % SEC
            bm.faces.new((A[j], A[j1], B[j1], B[j]))
    fin("Bolster", bm, ACC, angle=70)


CUSH_TOP = ZB + 0.16


def cushion_z(x, y):
    r = math.hypot(x, y)
    t = min(r / 0.26, 1.0)
    return ZB + 0.11 + (CUSH_TOP - ZB - 0.11) * (1 - t * t)


def bolster_z(x, y):
    r = math.hypot(x, y)
    th = math.atan2(y, x)
    a = HALF_W * (1.0 + 0.07 * math.cos(LOBES * th))
    hh = bolster_h(th) * (1.0 + 0.05 * math.cos(LOBES * th)) / 2
    q = (r - RC) / a
    if abs(q) >= 1.0:
        return -1.0
    return ZB + hh + hh * math.sqrt(1 - q * q)


def build_cushion():
    prof = [(RC, ZB - 0.005), (0.27, ZB + 0.09), (0.25, ZB + 0.125), (0.19, ZB + 0.148), (0.1, CUSH_TOP - 0.004),
            (0.0, CUSH_TOP)]
    fin("Cushion", lathe_bm(prof, 24), "SH_Cream", angle=70)


def build_moon():
    R = 0.16
    rin = R * 0.76
    off = R * 0.38
    n = 17
    pts, rad = [], []
    lim = math.acos((R * R + off * off - rin * rin) / (2 * R * off))
    for k in range(n):
        u = k / (n - 1)
        phi = lim + (2 * math.pi - 2 * lim) * u
        dx, dy = math.cos(phi), math.sin(phi)
        b = dx * off
        disc = b * b - (off * off - rin * rin)
        tin = b + math.sqrt(disc) if disc > 0 else 0.0
        tin = min(tin, R)
        w = max(R - tin, 0.03)
        mid = (R + tin) / 2 if tin < R else R - 0.006
        pts.append((-dx * mid, dy * mid, 0.0))
        rad.append(w / 2)
    bm = tube_bm(pts, rad, 10)
    xf(bm, Matrix.Diagonal((1, 1, 0.75, 1)))
    m = (Matrix.Translation((-0.03, 0.1, CUSH_TOP + 0.06)) @ Matrix.Rotation(math.radians(30), 4, "X")
         @ Matrix.Rotation(math.radians(-10), 4, "Z"))
    xf(bm, m)
    fin("MoonPillow", bm, "SH_Gold", angle=80)


def surf_z(x, y):
    r = math.hypot(x, y)
    lim = RC + 0.06
    over = 0.0
    if r > lim:
        over = r - lim
        x, y = x * lim / r, y * lim / r
        r = lim
    z = max(cushion_z(x, y) if r < RC else -1.0, bolster_z(x, y))
    if z < 0:
        z = ZB + 0.05
    return z - over * 1.6


def build_blanket():
    nu, nv = 11, 9
    W, D, T = 0.4, 0.34, 0.05
    ang = math.radians(-16)
    ca, sa = math.cos(ang), math.sin(ang)
    cx, cy = 0.06, -0.24
    P = []
    H = []
    for j in range(nv):
        rp, rh = [], []
        for i in range(nu):
            u = (i / (nu - 1) - 0.5) * W
            v = (j / (nv - 1) - 0.5) * D
            x = cx + u * ca - v * sa
            y = cy + u * sa + v * ca
            rp.append((x, y, u))
            rh.append(surf_z(x, y))
        P.append(rp)
        H.append(rh)
    for _ in range(3):
        H2 = [row[:] for row in H]
        for j in range(nv):
            for i in range(nu):
                acc, n = 0.0, 0
                for dj in (-1, 0, 1):
                    for di in (-1, 0, 1):
                        jj, ii = j + dj, i + di
                        if 0 <= jj < nv and 0 <= ii < nu:
                            acc += H[jj][ii]
                            n += 1
                H2[j][i] = max(acc / n, H[j][i])
        H = H2
    bm = bmesh.new()
    top, bot = [], []
    for j in range(nv):
        rt, rb = [], []
        for i in range(nu):
            x, y, u = P[j][i]
            z = H[j][i] + 0.002 + 0.008 * math.sin(u * 18.0)
            edge = i in (0, nu - 1) or j in (0, nv - 1)
            rt.append(bm.verts.new((x, y, z + (T * 0.55 if edge else T))))
            rb.append(bm.verts.new((x, y, z)))
        top.append(rt)
        bot.append(rb)
    for j in range(nv - 1):
        for i in range(nu - 1):
            bm.faces.new((top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]))
            bm.faces.new((bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]))
    ring = [(0, i) for i in range(nu)] + [(j, nu - 1) for j in range(1, nv)] + \
           [(nv - 1, i) for i in range(nu - 2, -1, -1)] + [(j, 0) for j in range(nv - 2, 0, -1)]
    for k in range(len(ring)):
        a, b = ring[k], ring[(k + 1) % len(ring)]
        bm.faces.new((bot[a[0]][a[1]], bot[b[0]][b[1]], top[b[0]][b[1]], top[a[0]][a[1]]))
    fin("Blanket", bm, "SH_Peach", angle=70)



WOOD = "SH_Honey"
BED_S = 0.9
BED_Y = -0.035
PL_R = 0.49
POST_Y = 0.39
CROWN = Vector((0.0, 0.2, 1.12))
HEM_C = Vector((0.0, 0.0, 0.52))
R0, R1 = 0.12, 0.44
OPEN = math.radians(62)
T_FAB = 0.032


def star_outline(R, r, n=5, rot=90.0):
    pts = []
    for k in range(2 * n):
        a = math.radians(rot) + math.pi * k / n
        rr = R if k % 2 == 0 else r
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return pts


def plinth2():
    R = PL_R
    prof = [(0.0, 0.0), (R - 0.03, 0.0), (R, 0.03), (R - 0.022, 0.062), (0.0, 0.062)]
    fin("PlinthFoot", lathe_bm(prof, 28), WOOD, angle=60)
    r2 = R - 0.035
    prof = [(r2, 0.05), (r2, 0.072), (r2 - 0.024, 0.088), (0.0, 0.088)]
    fin("PlinthTop", lathe_bm(prof, 28), "SH_Cream", angle=60)


def edge_w(th):
    th0 = -math.pi / 2 + OPEN
    th1 = 3 * math.pi / 2 - OPEN
    d = min(th - th0, th1 - th)
    return max(0.0, 1.0 - d / math.radians(38))


def canopy_frame(th, v):
    c = CROWN.lerp(HEM_C, v)
    f = math.sin(v * math.pi / 2) ** 0.75
    r = R0 + (R1 - R0) * f
    w = edge_w(th)
    r *= 1.0 + 0.05 * v * math.cos(9 * th)
    r *= 1.0 - 0.24 * w * w * math.exp(-((v - 0.72) / 0.24) ** 2)
    d = Vector((math.cos(th), math.sin(th) * 1.02, 0.0))
    z = c.z - 0.16 * w * v * v
    if v > 0.999:
        z += 0.025 * math.cos(9 * th)
    p = Vector((c.x, c.y, z)) + d * r
    return p, d


def build_canopy():
    th0 = -math.pi / 2 + OPEN
    th1 = 3 * math.pi / 2 - OPEN
    NU, NV = 28, 13
    bm = bmesh.new()
    O, I = [], []
    for j in range(NV):
        v = j / (NV - 1)
        ro, ri = [], []
        for i in range(NU):
            th = th0 + (th1 - th0) * i / (NU - 1)
            p, d = canopy_frame(th, v)
            ro.append(bm.verts.new(p))
            ri.append(bm.verts.new(p - d * T_FAB))
        O.append(ro)
        I.append(ri)
    for j in range(NV - 1):
        for i in range(NU - 1):
            bm.faces.new((O[j][i], O[j][i + 1], O[j + 1][i + 1], O[j + 1][i]))
            bm.faces.new((I[j][i], I[j + 1][i], I[j + 1][i + 1], I[j][i + 1]))
    for i in range(NU - 1):
        bm.faces.new((O[0][i], I[0][i], I[0][i + 1], O[0][i + 1]))
        bm.faces.new((O[-1][i], O[-1][i + 1], I[-1][i + 1], I[-1][i]))
    for j in range(NV - 1):
        bm.faces.new((O[j][0], O[j + 1][0], I[j + 1][0], I[j][0]))
        bm.faces.new((O[j][-1], I[j][-1], I[j + 1][-1], O[j + 1][-1]))
    fin("Canopy", bm, "SH_Cream", angle=60)
    pts = []
    for j in range(1, NV - 1):
        p, d = canopy_frame(th0, j / (NV - 1))
        pts.append(p - d * (T_FAB * 0.5))
    for i in range(NU):
        th = th0 + (th1 - th0) * i / (NU - 1)
        p, d = canopy_frame(th, 1.0)
        pts.append(p - d * (T_FAB * 0.5))
    for j in range(NV - 2, 0, -1):
        p, d = canopy_frame(th1, j / (NV - 1))
        pts.append(p - d * (T_FAB * 0.5))
    fin("Hem", tube_bm(pts, 0.026, 6), ACC, angle=70)
    bm = bmesh.new()
    for th, v, s in ((90, 0.6, 0.17), (40, 0.42, 0.12), (140, 0.42, 0.12),
                     (65, 0.84, 0.1), (115, 0.84, 0.1)):
        t = math.radians(th)
        p, d = canopy_frame(t, v)
        n = d.normalized()
        x = UP.cross(n).normalized()
        y = n.cross(x).normalized()
        M = Matrix(((x.x, y.x, n.x, p.x - n.x * 0.006), (x.y, y.y, n.y, p.y - n.y * 0.006),
                    (x.z, y.z, n.z, p.z - n.z * 0.006), (0, 0, 0, 1)))
        badge_bm(star_outline(s / 2, s / 4.0), 0.04, 0.014, 2, bm=bm, matrix=M)
    fin("Stars", bm, "SH_Gold", angle=60)
    bm = bmesh.new()
    for th in (th0, th1):
        p, d = canopy_frame(th, 0.72)
        ellipsoid_bm(p - d * (T_FAB * 0.5), (0.07, 0.07, 0.05), 10, 5, bm=bm)
    fin("TieBacks", bm, ACC, angle=70)


def build_post():
    pts = [(0.0, POST_Y, 0.04), (0.0, POST_Y, 0.4), (0.0, POST_Y, 0.62), (0.0, 0.37, 0.8), (0.0, 0.31, 0.95),
           (0.0, 0.24, 1.06), (0.0, CROWN.y, 1.12)]
    pts = catmull(pts, 3)
    fin("Post", tube_bm(pts, 0.05, 10), WOOD, angle=60)
    prof = [(0.0, 0.055), (0.09, 0.055), (0.095, 0.075), (0.072, 0.1), (0.0, 0.1)]
    fin("PostFoot", lathe_bm(prof, 16, matrix=Matrix.Translation((0, POST_Y, 0))), WOOD, angle=60)
    z = CROWN.z
    prof = [(0.0, z - 0.03), (R0 + 0.02, z - 0.03), (R0 + 0.045, z), (R0 + 0.03, z + 0.045),
            (R0 - 0.01, z + 0.085), (0.05, z + 0.125), (0.0, z + 0.135)]
    fin("Crown", lathe_bm(prof, 20, matrix=Matrix.Translation((CROWN.x, CROWN.y, 0))), WOOD, angle=55)
    fin("CrownBand", torus_bm(R0 + 0.035, 0.026, 18, 5, matrix=Matrix.Translation((CROWN.x, CROWN.y, z + 0.005))),
        "SH_Gold", angle=80)
    st = badge_bm(star_outline(0.095, 0.045), 0.055, 0.018, 2, matrix=front_matrix(0, CROWN.y + 0.0275, z + 0.21))
    fin("TopStar", st, "SH_Gold", angle=60)


out, flags = cli()
begin()
plinth2()
G[0] = Matrix.Translation((0, BED_Y, 0.082 - ZB * BED_S)) @ Matrix.Diagonal((BED_S, BED_S, BED_S, 1))
build_bolster()
build_cushion()
build_moon()
build_blanket()
G[0] = Matrix.Identity(4)
build_post()
build_canopy()
ob = join_all("ShopBedCanopy")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.15, 0.3, 0), target=(-0.4, 0.0, 0.6), ortho=3.0)
