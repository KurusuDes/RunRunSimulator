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
    fin("MoonPillow", bm, "SH_Straw", angle=80)


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

out, flags = cli()
begin()
plinth(PLINTH_R, ACC)
build_bolster()
build_cushion()
build_moon()
build_blanket()
ob = join_all("ShopBed")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.05, 0.25, 0), target=(-0.45, 0.0, 0.4), ortho=2.6)
