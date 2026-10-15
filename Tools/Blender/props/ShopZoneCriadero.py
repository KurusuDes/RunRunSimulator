import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from zone_annex import *

T = 0.3
ZT = 2.7
FT = -0.3
G = -0.41
FX0, FX1, FY0, FY1 = 36.8, 46.0, -22.0, -7.0
YS_IN, YS_OUT = -7.15, -6.85
YN_IN, YN_OUT = -21.85, -22.15
XW_IN, XW_OUT = 45.85, 46.15
DOOR = (40.5, 42.5)
EDGE_X = 36.92

WALLS = {
    "S": Wall("x", FX0, FX1, YS_IN, -1, T, ZT, FT, G),
    "W": Wall("y", FY0, FY1, XW_IN, -1, T, ZT, FT, G),
    "N": Wall("x", FX0, FX1, YN_IN, +1, T, ZT, FT, G),
}
DOOR_W = -13.5
PILASTERS = {"W": [-19.95], "N": [41.8], "S": []}
INNER = {"S2": ("S", FX0, DOOR[0]), "S1": ("S", DOOR[1], XW_IN), "W": ("W", YN_IN + 0.047, YS_IN - 0.047), "N": ("N", FX0, XW_IN)}
PO = 0.06
WINDOWS_N = [39.3, 44.3]
Z_SILL = FT + 1.2
GLASS = []


POSTS = {"S2": [FX0 + 0.14, DOOR[0] - 0.16], "S1": [DOOR[1] + 0.16, XW_IN], "W": [YN_IN, -19.95, YS_IN],
         "N": [FX0 + 0.14, 41.8, XW_IN]}


DHW, DH, DFW, DRISE, ND = 0.8, 2.2, 0.14, 0.2, 10
DRO = DHW + DFW


def seg_arch(c, zl, s, n):
    us = [-c + 2 * c * k / n for k in range(n + 1)]
    if s < 1e-4:
        return [(u, zl) for u in us]
    R = (c * c + s * s) / (2 * s)
    zc = zl + s - R
    return [(u, zc + math.sqrt(max(R * R - u * u, 0.0))) for u in us]


def door_contour(o):
    c = DHW + o
    return [(-c, 0.0)] + seg_arch(c, DH + o, DRISE * max(o, 0.0) / DFW, ND) + [(c, 0.0)]


def cut_hole(B, w, u0, u1, z1, vpad=0.16):
    ua = 0 if w.axis == "x" else 1
    pa = 1 - ua
    lo, hi = sorted((w.P(0, -vpad, 0)[pa], w.P(0, w.T + vpad, 0)[pa]))
    for bm in B.values():
        def near():
            return [f for f in bm.faces if all(lo <= v.co[pa] <= hi for v in f.verts)]
        for val, k in ((u0, ua), (u1, ua), (z1, 2)):
            fs = []
            for f in near():
                cs = [v.co[k] for v in f.verts]
                if not (min(cs) < val - 1e-5 and max(cs) > val + 1e-5):
                    continue
                if k == 2:
                    if not (u0 < f.calc_center_median()[ua] < u1):
                        continue
                elif min(v.co.z for v in f.verts) >= z1:
                    continue
                fs.append(f)
            if not fs:
                continue
            es = list({e for f in fs for e in f.edges})
            vs = list({v for f in fs for v in f.verts})
            co, no = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
            co[k], no[k] = val, 1.0
            bmesh.ops.bisect_plane(bm, geom=vs + es + fs, dist=1e-6, plane_co=co, plane_no=no)
        dead = []
        for f in near():
            c = f.calc_center_median()
            if u0 < c[ua] < u1 and c.z < z1:
                dead.append(f)
        if dead:
            bmesh.ops.delete(bm, geom=dead, context="FACES")


def wring(bm, w, uc, z0, inner, outer, v0, v1):
    def q(p, v):
        return (uc + p[0], v, z0 + p[1])
    for i in range(len(inner) - 1):
        a, b, c, d = inner[i], inner[i + 1], outer[i], outer[i + 1]
        w.face(bm, [q(a, v0), q(b, v0), q(d, v0), q(c, v0)], w.n)
        w.face(bm, [q(a, v1), q(b, v1), q(d, v1), q(c, v1)], -w.n)
        mi = w.P(uc + (a[0] + b[0]) / 2, 0, z0 + (a[1] + b[1]) / 2)
        mo = w.P(uc + (c[0] + d[0]) / 2, 0, z0 + (c[1] + d[1]) / 2)
        w.face(bm, [q(a, v0), q(b, v0), q(b, v1), q(a, v1)], mi - mo)
        w.face(bm, [q(c, v0), q(d, v0), q(d, v1), q(c, v1)], mo - mi)


def wrad(w, ru, rv, rz):
    return (ru, rv, rz) if w.axis == "x" else (rv, ru, rz)


def wpaw(bm, w, uc, zc, v, s=1.0):
    ellipsoid_bm(w.P(uc, v, zc - 0.022 * s), wrad(w, 0.05 * s, 0.014, 0.04 * s), 8, 4, bm=bm)
    for du, dz, r in ((-0.06, 0.028, 0.02), (-0.023, 0.062, 0.021), (0.023, 0.062, 0.021), (0.06, 0.028, 0.02)):
        ellipsoid_bm(w.P(uc + du * s, v, zc + dz * s), wrad(w, r * s, 0.012, r * s * 1.12), 6, 3, bm=bm)


def wrosette(bm, w, uc, zc, v, d):
    M = Matrix.Translation(w.P(uc, v, zc)) @ Vector(d).to_track_quat("Z", "Y").to_matrix().to_4x4()
    lathe_bm([(0.0, 0.0), (0.058, 0.0), (0.064, 0.016), (0.05, 0.032), (0.024, 0.04), (0.0, 0.042)], 8, bm=bm, matrix=M)


def door_frame(B, w, uc, v_sill=0.15):
    z0 = w.fin
    wring(B["SH_Timber"], w, uc, z0, door_contour(0.0), door_contour(DFW), -0.045, w.T + 0.045)
    wring(B["SH_Walnut"], w, uc, z0, door_contour(DFW - 0.04), door_contour(DFW + 0.014), -0.065, w.T + 0.065)
    for sg in (-1, 1):
        a, b = sorted((uc + sg * (DHW + 0.012), uc + sg * (DRO + 0.05)))
        w.box(B["SH_Stone"], a, b, -0.09, w.T + 0.09, w.gout - 0.01, z0 + 0.4, r=0.05, segs=1)
        a, b = sorted((uc + sg * (DHW + 0.012), uc + sg * (DRO + 0.035)))
        w.box(B["SH_Walnut"], a, b, -0.095, w.T + 0.095, z0 + DH - 0.22, z0 + DH - 0.1, r=0.035, segs=1)
        for v, d in ((-0.062, w.n), (w.T + 0.062, -w.n)):
            wrosette(B["SH_Walnut"], w, uc + sg * (DHW + DFW * 0.42), z0 + DH + DFW * 0.42, v, d)
    w.box(B["SH_Walnut"], uc - 0.12, uc + 0.12, -0.085, w.T + 0.085, z0 + DH + 0.06, z0 + DH + 0.44, r=0.035, segs=1)
    wpaw(B["SH_Gold"], w, uc, z0 + DH + 0.24, -0.088)
    wpaw(B["SH_Gold"], w, uc, z0 + DH + 0.24, w.T + 0.088)
    w.box(B["SH_Timber"], uc - DHW, uc + DHW, v_sill, w.T, w.gout - 0.01, z0, r=0.03, segs=1)
    lantern(B, w.P(uc + 1.22, 0.0, z0 + DH), w.n)
    lantern(B, w.P(uc - 1.22, w.T + 0.02, z0 + DH), -w.n)


def barn_x(B, w, u0, u1, z0, z1, m="SH_Timber"):
    d0, d1 = w.T + 0.012, w.T + 0.07
    w.box(B[m], u0 + 0.02, u1 - 0.02, d0, d1 - 0.022, z0, z0 + 0.12, r=0.02, segs=1)
    w.box(B[m], u0 + 0.02, u1 - 0.02, d0, d1 - 0.022, z1 - 0.12, z1, r=0.02, segs=1)
    w.box(B[m], u0, u0 + 0.12, d0, d1, z0 + 0.008, z1 - 0.008, r=0.02, segs=1)
    w.box(B[m], u1 - 0.12, u1, d0, d1, z0 + 0.008, z1 - 0.008, r=0.02, segs=1)
    du, dz = (u1 - u0) - 0.24, (z1 - z0) - 0.24
    L = math.hypot(du, dz)
    for k, sgn in enumerate((1, -1)):
        f, bk = w.T + 0.04 - 0.008 * k, w.T + 0.016
        rotbox(w, B[m], (u0 + u1) / 2, (f + bk) / 2, (z0 + z1) / 2, L, f - bk, 0.12, math.atan2(sgn * dz, du))


def wpost(B, w, uc=0.0, width=0.3, u0=None, u1=None):
    if u0 is None:
        u0, u1 = uc - width / 2, uc + width / 2
    a = w.P(u0, -PO, min(w.fin, w.gout) - 0.01)
    b = w.P(u1, w.T + PO, w.zt + 0.15)
    post3(B, [min(a[i], b[i]) for i in range(3)], [max(a[i], b[i]) for i in range(3)])


def cpost(B, x0, x1, y0, y1, z0, z1):
    post3(B, (x0 - PO, y0 - PO, z0), (x1 + PO, y1 + PO, z1))


def ivy2(B, w, u0, u1, rng, step=0.46):
    u = u0
    k = 0
    while u < u1:
        big = 0.12 if k % 2 == 0 else 0.085
        vv = (0.3 if k % 2 == 0 else 0.72) * w.T
        c = w.P(u, vv, w.zt + 0.075 + big * 0.35)
        ellipsoid_bm(c, (big, big * 0.9, big * 0.66), 6, 3, bm=B["SH_Leaf" if k % 3 else "SH_Moss"])
        if k % 2 == 0:
            r = 0.07
            ellipsoid_bm(w.P(u + 0.06, w.T + 0.07, w.zt - 0.08), (r, r * 0.8, r * 0.95), 6, 4, bm=B["SH_Moss"])
            ellipsoid_bm(w.P(u + 0.02, w.T + 0.055, w.zt - 0.22), (0.05, 0.04, 0.055), 6, 3, bm=B["SH_Leaf"])
        u += step * rng.uniform(0.85, 1.15)
        k += 1


def egg_sign(B, w, uc, z):
    v = w.T + 0.06
    c = w.P(uc, v, z)
    face = Matrix.Rotation(math.pi, 4, "Z") @ Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    rings = rbox_rings(0.78, 0.78, 0.07, 0.39, 0.025, seg=2, z0=-0.035)
    finish("EggPlaque", loft(rings, 4, matrix=Matrix.Translation(c) @ face), "SH_Timber", angle=50)
    ellipsoid_bm(w.P(uc, v + 0.045, z - 0.01), (0.2, 0.07, 0.27), 12, 7, bm=B["SH_Parchment"])
    for dx, dz, m in ((-0.07, 0.07, "SH_Moss"), (0.08, -0.03, "SH_Gold"), (-0.03, -0.12, "SH_Moss")):
        ellipsoid_bm(w.P(uc + dx, v + 0.11, z + dz), (0.045, 0.02, 0.045), 6, 3, bm=B[m])


def build_walls(rng):
    B = Bins()
    W = WALLS
    S = W["S"]
    for u0, u1 in ((FX0, DOOR[0]), (DOOR[1], FX1)):
        wall_body(B, S, inner="SH_Parchment", outer="SH_Honey", u0=u0, u1=u1)
        cap3(B, S, u0 if u0 < DOOR[0] else u0 + 0.012, min(u1, XW_IN - 0.05) if u1 > DOOR[1] else u1 - 0.012)
    for k in ("W", "N"):
        wall_body(B, W[k], inner="SH_Parchment", outer="SH_Honey")
    cap3(B, W["W"], W["W"].a0, W["W"].a1)
    cap3(B, W["N"], W["N"].a0, XW_IN - 0.05)
    S.box(B["SH_Timber"], DOOR[0], DOOR[1], -0.05, T + 0.05, ZT - 0.24, ZT + 0.09, r=0.04, segs=2)
    for key, (k, u0, u1) in INNER.items():
        inner3(B, W[k], u0, u1, "SH_Moss")
        girt3(B, W[k], u0, u1, FT + 2.0)
        knee_braces(B, W[k], POSTS[key], FT + 1.42, FT + 2.0)
    pw = (DOOR[0] - 0.32, DOOR[0] + 0.025, DOOR[1] - 0.025, DOOR[1] + 0.32, FX0 - 0.03, FX0 + 0.3)
    posts = {"S": [(pw[0], pw[1]), (pw[2], pw[3]), (pw[4], pw[5]), (XW_IN - PO, XW_OUT + PO)],
             "W": [(YN_OUT - PO, YN_IN + PO), (-19.95 - 0.15, -19.95 + 0.15), (YS_IN - PO, YS_OUT + PO)],
             "N": [(pw[4], pw[5]), (41.8 - 0.15, 41.8 + 0.15), (XW_IN - PO, XW_OUT + PO)]}
    for k, u0, u1 in (("S", FX0, DOOR[0]), ("S", DOOR[1], XW_OUT), ("W", YN_OUT, YS_OUT), ("N", FX0, XW_OUT)):
        outer3s(B, W[k], u0, u1, rng, posts[k])
    barn_x(B, S, FX0 + 0.45, DOOR[0] - 0.45, G + 0.46, ZT - 0.4)
    barn_x(B, S, DOOR[1] + 0.45, XW_OUT - 0.45, G + 0.46, ZT - 0.4)
    for k, us in PILASTERS.items():
        for u in us:
            wpost(B, W[k], u)
    wpost(B, S, u0=FX0 - 0.03, u1=FX0 + 0.3)
    wpost(B, W["N"], u0=FX0 - 0.03, u1=FX0 + 0.3)
    wpost(B, S, u0=DOOR[0] - 0.32, u1=DOOR[0] + 0.025)
    wpost(B, S, u0=DOOR[1] - 0.025, u1=DOOR[1] + 0.32)
    z0, z1 = G - 0.01, ZT + 0.15
    cpost(B, XW_IN, XW_OUT, YS_IN, YS_OUT, z0, z1)
    cpost(B, XW_IN, XW_OUT, YN_OUT, YN_IN, z0, z1)
    for u in (DOOR[0] - 0.16, DOOR[1] + 0.16):
        lantern(B, S.P(u, T + PIL_OUT, ZT - 0.55), (0, 1, 0))
    ivy2(B, W["N"], FX0 + 0.45, 38.2, rng)
    ivy2(B, W["N"], 42.2, 43.4, rng)
    ivy2(B, S, XW_OUT - 1.7, XW_OUT - 0.4, rng)
    egg_sign(B, S, sum(DOOR) / 2, ZT + 0.2)
    mushroom(B, XW_OUT + 0.18, YN_OUT - 0.2, G, 1.1, "SH_Plum")
    mushroom(B, XW_OUT + 0.22, YN_OUT + 0.12, G, 0.75, "SH_Gold")
    mushroom(B, XW_OUT + 0.2, -15.8, G, 0.9, "SH_Gold")
    cut_hole(B, W["W"], DOOR_W - DRO, DOOR_W + DRO, FT + DH)
    door_frame(B, W["W"], DOOR_W)
    for uc in WINDOWS_N:
        zb = Z_SILL + WIN_FW - 0.02
        cut_window(B, W["N"], uc - WIN_HW, uc + WIN_HW, zb, zb + 2 * WIN_HH)
        cross_window(B, W["N"], uc, Z_SILL, GLASS)
    return B.done("Walls")


def build_floor(rng):
    B = Bins()
    quad_z(B["SH_Timber"], EDGE_X, FX1, FY0, YS_IN + 0.03, FT - 0.008)
    n = int(round((FX1 - EDGE_X) / 0.3))
    pw = (FX1 - EDGE_X) / n
    for i in range(n):
        xa, xb = EDGE_X + i * pw, EDGE_X + (i + 1) * pw
        cuts = [FY0]
        y = FY0 + [0.9, 2.1, 1.5, 0.4, 2.6][i % 5]
        while y < YS_IN - 0.3:
            cuts.append(y)
            y += 2.7
        cuts.append(YS_IN + 0.03)
        for ya, yb in zip(cuts, cuts[1:]):
            chamfer_tile(B["SH_Walnut"], xa + 0.008, xb - 0.008, ya + 0.008, yb - 0.008, FT, ch=0.014, dz=0.008)
    wbox(B["SH_Timber"], (EDGE_X - 0.18, FY0, G - 0.01), (EDGE_X, FY1, FT), r=0.03, segs=1)
    wbox(B["SH_Timber"], (DOOR[0], YS_IN + 0.03, G - 0.01), (DOOR[1], -6.96, FT), r=0.03, segs=1)
    return B.done("Floor", angle=50)


def hay(B, x, y, rng, s=1.0):
    ellipsoid_bm((x, y, FT - 0.012), (0.21 * s, 0.16 * s, 0.032), 8, 3, bm=B["SH_StrawDark"])
    base = rng.uniform(0, math.pi)
    for k in range(5):
        L = rng.uniform(0.2, 0.29) * s
        a = base + k * math.pi / 5 + rng.uniform(-0.2, 0.2)
        d = Vector((math.cos(a), math.sin(a), 0))
        c = Vector((x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.05, 0.05), 0))
        hz = FT + 0.021 + 0.0075 * k
        r = 0.015 + 0.0035 * (k % 3)
        tube_bm([c - d * L + Vector((0, 0, FT + 0.002)), c + Vector((0, 0, hz)), c + d * L + Vector((0, 0, FT + 0.002))],
                [r, r + 0.003, r], 5 + k % 2, bm=B["SH_Gold"])


def build_decor(rng):
    B = Bins()
    spots = [(41.8, -8.4, 1.0), (41.4, -10.9, 0.8), (42.0, -13.1, 1.1), (38.2, -13.0, 0.9), (44.9, -13.2, 0.8),
             (41.6, -16.2, 0.9), (41.9, -19.6, 1.1), (38.3, -20.8, 1.0), (44.8, -20.7, 0.9), (37.3, -9.4, 0.8),
             (40.0, -21.1, 0.7), (43.4, -19.0, 0.7), (37.4, -17.6, 0.7)]
    for x, y, s in spots:
        hay(B, x, y, rng, s)
    return B.done("Decor", angle=70)


rng = random.Random(1533)
out, flags = cli()
begin_env()
walls = build_walls(rng)
floors = build_floor(rng)
decor = build_decor(rng)
check_floor(floors, [(EDGE_X + 0.05, XW_IN - 0.05, YN_IN + 0.05, YS_IN - 0.05)], FT, step=0.3, label="planks")
for key, (k, u0, u1) in INNER.items():
    skip = PILASTERS[k] + ([DOOR_W + d for d in (-1.1, -0.55, 0.0, 0.55, 1.1)] if k == "W" else []) +         ([u + d for u in WINDOWS_N for d in (-0.8, -0.4, 0.0, 0.4, 0.8)] if k == "N" else [])
    check_wall(walls, WALLS[k], u0 + 0.35, u1 - 0.35, skip=skip, label="inner_" + key)
parts_report()
ob = join_all("ShopZoneCriadero")
report(ob)
coplanar_report([ob], "ShopZoneCriadero", show=30, floor_z=FT)
for c, sz in GLASS:
    print("GLASS center=%s size=%s unity_center=(%.3f, %.3f, %.3f)" % (c, sz, -c[0], c[2], -c[1]))
export(ob, flags)
C = (41.4, -14.5, 0.5)
views = [
    ("all", 200, 52, C, 19.0),
    ("allS", 20, 45, C, 19.0),
    ("door", 20, 30, (41.5, -6.5, 1.0), 7.5),
    ("inside", 200, 40, (41.5, -9.0, 0.2), 7.0),
    ("corner", 135, 35, (44.9, -20.9, 0.6), 5.5),
    ("top", 200, 75, (41.4, -14.5, 0.0), 12.0),
    ("doorW_in", 270, 50, (45.9, -13.5, 0.9), 5.0),
    ("doorW_out", 90, 25, (46.1, -13.5, 0.9), 5.0),
]
dragons = [(41.4, -9.4, FT, 200.0), (41.5, -5.9, G, 20.0), (44.4, -20.4, FT, 135.0), (37.6, -13.0, FT, 250.0)]
env_preview(ob, out, ["ZONE_Criadero"], views, dragons, (41.4, -14.5, 0.0), 17.0)
