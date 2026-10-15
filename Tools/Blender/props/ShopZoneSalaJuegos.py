import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from zone_annex import *

T = 0.3
ZT = 2.7
FT = -0.3
G = -0.41
FX0, FX1, FY0, FY1 = 16.0, 22.6, -17.0, -7.0
XE_IN, XE_OUT = 16.15, 15.85
YN_IN, YN_OUT = -16.65, -16.95
YS_IN, YS_OUT = -7.15, -6.85
DOOR = (18.5, 20.0)
EDGE_X = 22.46

WALLS = {
    "E": Wall("y", FY0, FY1, XE_IN, +1, T, ZT, FT, G),
    "N": Wall("x", FX0, FX1, YN_IN, +1, T, ZT, FT, G),
    "S": Wall("x", FX0, FX1, YS_IN, -1, T, ZT, FT, G),
}
DOOR_E = -11.5
PILASTERS = {"E": [], "N": [19.4], "S": []}
INNER = {"E": ("E", YN_IN + 0.047, YS_IN - 0.047), "N": ("N", XE_IN, FX1), "S2": ("S", XE_IN, DOOR[0]), "S1": ("S", DOOR[1], FX1)}
POSTS = {"E": [YN_IN, YS_IN], "N": [XE_IN, 19.4, FX1 - 0.15], "S2": [XE_IN, DOOR[0] - 0.16], "S1": [DOOR[1] + 0.16, FX1 - 0.15]}
RUG_C = (19.3, -12.0)
PO = 0.06
WINDOWS_N = [17.78, 20.92]
Z_SILL = FT + 1.2
GLASS = []


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


def build_walls(rng):
    B = Bins()
    W = WALLS
    S = W["S"]
    for u0, u1 in ((FX0, DOOR[0]), (DOOR[1], FX1)):
        wall_body(B, S, inner="SH_Parchment", outer="SH_Honey", u0=u0, u1=u1)
        cap3(B, S, XE_IN + 0.05 if u0 < DOOR[0] else u0 + 0.012, u1 - 0.012 if u1 < DOOR[1] + 0.1 else u1)
    for k in ("E", "N"):
        wall_body(B, W[k], inner="SH_Parchment", outer="SH_Honey")
    cap3(B, W["E"], W["E"].a0, W["E"].a1)
    cap3(B, W["N"], XE_IN + 0.05, W["N"].a1)
    S.box(B["SH_Timber"], DOOR[0], DOOR[1], -0.05, T + 0.05, ZT - 0.24, ZT + 0.09, r=0.04, segs=2)
    for key, (k, u0, u1) in INNER.items():
        inner3(B, W[k], u0, u1, "SH_Plum", board="SH_Oak", groove="SH_Honey")
        girt3(B, W[k], u0, u1, FT + 2.0)
        knee_braces(B, W[k], POSTS[key], FT + 1.5, FT + 2.0)
    cor = (XE_OUT - PO, XE_IN + PO)
    endp = (FX1 - 0.3, FX1 + 0.03)
    posts = {"E": [(YN_OUT - PO, YN_IN + PO), (YS_IN - PO, YS_OUT + PO)],
             "N": [cor, (19.4 - 0.15, 19.4 + 0.15), endp],
             "S": [cor, (DOOR[0] - 0.32, DOOR[0] + 0.025), (DOOR[1] - 0.025, DOOR[1] + 0.32), endp]}
    for k, u0, u1 in (("E", FY0 + 0.02, YS_OUT), ("N", XE_OUT, FX1), ("S", XE_OUT, DOOR[0]), ("S", DOOR[1], FX1)):
        outer3s(B, W[k], u0, u1, rng, posts[k])
    for k, us in PILASTERS.items():
        for u in us:
            wpost(B, W[k], u)
    wpost(B, W["N"], u0=endp[0], u1=endp[1])
    wpost(B, S, u0=endp[0], u1=endp[1])
    wpost(B, S, u0=DOOR[0] - 0.32, u1=DOOR[0] + 0.025)
    wpost(B, S, u0=DOOR[1] - 0.025, u1=DOOR[1] + 0.32)
    z0, z1 = G - 0.01, ZT + 0.15
    cpost(B, XE_OUT, XE_IN, YN_OUT, YN_IN, z0, z1)
    cpost(B, XE_OUT, XE_IN, YS_IN, YS_OUT, z0, z1)
    for u in (DOOR[0] - 0.16, DOOR[1] + 0.16):
        lantern(B, S.P(u, T + PIL_OUT, ZT - 0.55), (0, 1, 0))
    ivy2(B, S, XE_OUT + 0.4, DOOR[0] - 0.55, rng)
    mushroom(B, XE_OUT - 0.2, YN_OUT - 0.15, G, 1.1, "SH_Gold")
    mushroom(B, XE_OUT - 0.12, YN_OUT + 0.22, G, 0.75, "SH_Plum")
    cut_hole(B, W["E"], DOOR_E - DRO, DOOR_E + DRO, FT + DH)
    door_frame(B, W["E"], DOOR_E)
    for uc in WINDOWS_N:
        zb = Z_SILL + WIN_FW - 0.02
        cut_window(B, W["N"], uc - WIN_HW, uc + WIN_HW, zb, zb + 2 * WIN_HH)
        cross_window(B, W["N"], uc, Z_SILL, GLASS)
    return B.done("Walls")


def stars_on(B, w, u0, u1, z, k0=0, outer=False, R=0.3):
    L = u1 - u0
    n = max(1, int(L / 1.5))
    for i in range(n):
        uc = u0 + (i + 0.5) * L / n
        star_local(w, B["SH_Plum" if (k0 + i) % 2 == 0 else "SH_Gold"], uc, z, R, R * 0.47, 0.045, outer=outer)


def build_deco_walls():
    B = Bins()
    W = WALLS
    zs = FT + 1.48
    stars_on(B, W["E"], YN_IN + 0.8, -11.9 - 0.8, zs, 0)
    for i, uc in enumerate((-9.75, -8.45)):
        star_local(W["E"], B["SH_Plum" if (1 + i) % 2 == 0 else "SH_Gold"], uc, zs, 0.3, 0.3 * 0.47, 0.045)
    stars_on(B, W["S"], XE_IN + 0.75, DOOR[0] - 0.85, zs, 0)
    stars_on(B, W["S"], DOOR[1] + 0.85, FX1 - 0.9, zs, 1)
    S = W["S"]
    star_local(S, B["SH_Gold"], (XE_OUT + DOOR[0]) / 2, G + 1.55, 0.34, 0.16, 0.05, outer=True)
    star_local(S, B["SH_Gold"], (DOOR[1] + FX1) / 2, G + 1.55, 0.34, 0.16, 0.05, outer=True)
    uc = sum(DOOR) / 2
    c = S.P(uc, T + 0.06, ZT + 0.2)
    face = Matrix.Rotation(math.pi, 4, "Z") @ Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    rings = rbox_rings(0.78, 0.78, 0.07, 0.39, 0.025, seg=2, z0=-0.035)
    finish("StarPlaque", loft(rings, 4, matrix=Matrix.Translation(c) @ face), "SH_Timber", angle=50)
    tmp = Wall("x", 0, 0, YS_IN, -1, T + 0.095, ZT, FT, G)
    star_local(tmp, B["SH_Gold"], uc, ZT + 0.2, 0.28, 0.13, 0.05, outer=True)
    return B.done("Deco", angle=60)


def annulus(bm, cx, cy, r0, r1, z, n=40, zo=None):
    zo = z if zo is None else zo
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        p = [(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0), z), (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0), zo),
             (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), zo), (cx + r0 * math.cos(a1), cy + r0 * math.sin(a1), z)]
        if r0 <= 1e-6:
            oface(bm, [p[0], p[1], p[2]], (0, 0, 1))
        else:
            oface(bm, p, (0, 0, 1))


def build_rug():
    B = Bins()
    cx, cy = RUG_C
    R = 2.0
    zt, zg = FT + 0.009, FT + 0.0055
    cyc = ["SH_Gold", "SH_Parchment", "SH_Sage", "SH_Plum", "SH_Parchment", "SH_Gold", "SH_Sage", "SH_Plum", "SH_Parchment",
           "SH_Plum"]
    g = 0.009
    w = (R - 0.05) / len(cyc)
    for i, m in enumerate(cyc):
        r0, r1 = i * w, (i + 1) * w
        a0 = r0 + (g if i > 0 else 0.0)
        a1 = r1 - g if i < len(cyc) - 1 else r1
        if i > 0:
            annulus(B["SH_Walnut"], cx, cy, r0, a0, zg, n=32, zo=zt)
        annulus(B[m], cx, cy, a0, a1, zt, n=32)
        if i < len(cyc) - 1:
            annulus(B["SH_Walnut"], cx, cy, a1, r1, zt, n=32, zo=zg)
    annulus(B["SH_Walnut"], cx, cy, R - 0.05, R, zt, n=32, zo=FT - 0.004)
    return B.done("Rug", angle=60)


def build_floor():
    B = Bins()
    y0, y1 = FY0, YS_IN + 0.03
    quad_z(B["SH_Honey"], FX0, EDGE_X, y0, y1, FT - 0.008)
    n = int(round((EDGE_X - FX0) / 0.3))
    pw = (EDGE_X - FX0) / n
    for i in range(n):
        xa, xb = FX0 + i * pw, FX0 + (i + 1) * pw
        cuts = [y0]
        y = y0 + [0.7, 1.9, 1.3, 0.3, 2.4][i % 5]
        while y < y1 - 0.3:
            cuts.append(y)
            y += 2.6
        cuts.append(y1)
        for ya, yb in zip(cuts, cuts[1:]):
            chamfer_tile(B["SH_Oak"], xa + 0.008, xb - 0.008, ya + 0.008, yb - 0.008, FT, ch=0.014, dz=0.008)
    wbox(B["SH_Timber"], (EDGE_X, FY0, G - 0.01), (EDGE_X + 0.18, FY1, FT), r=0.03, segs=1)
    wbox(B["SH_Timber"], (DOOR[0], YS_IN + 0.03, G - 0.01), (DOOR[1], -6.96, FT), r=0.03, segs=1)
    return B.done("Floor", angle=50)


out, flags = cli()
begin_env()
rng = random.Random(1534)
walls = build_walls(rng)
deco = build_deco_walls()
floors = build_floor()
rug = build_rug()
check_floor(floors + rug, [(XE_IN + 0.05, EDGE_X - 0.05, YN_IN + 0.05, YS_IN - 0.05)], FT, step=0.3, label="planks+rug")
for key, (k, u0, u1) in INNER.items():
    skip = PILASTERS[k] + ([DOOR_E + d for d in (-1.1, -0.55, 0.0, 0.55, 1.1)] if k == "E" else []) + ([u + d for u in WINDOWS_N for d in (-0.8, -0.4, 0.0, 0.4, 0.8)] if k == "N" else [])
    check_wall(walls, WALLS[k], u0 + 0.35, u1 - 0.35, skip=skip, label="inner_" + key)
parts_report()
ob = join_all("ShopZoneSalaJuegos")
report(ob)
coplanar_report([ob], "ShopZoneSalaJuegos", show=30, floor_z=FT)
for c, sz in GLASS:
    print("GLASS center=%s size=%s unity_center=(%.3f, %.3f, %.3f)" % (c, sz, -c[0], c[2], -c[1]))
export(ob, flags)
C = (19.3, -12.0, 0.5)
views = [
    ("all", 200, 52, C, 14.0),
    ("allS", 20, 45, C, 14.0),
    ("door", 200, 30, (19.25, -6.6, 1.0), 6.5),
    ("inside", 20, 35, (19.0, -8.5, 0.6), 6.5),
    ("corner", 160, 50, (16.8, -15.9, 0.6), 6.0),
    ("top", 200, 75, (19.3, -12.0, 0.0), 11.0),
    ("doorE_in", 90, 50, (16.1, -11.5, 0.9), 5.0),
    ("doorE_out", 270, 25, (15.9, -11.5, 0.9), 5.0),
]
dragons = [(19.2, -12.8, FT, 200.0), (19.25, -5.9, G, 200.0), (17.0, -15.6, FT, 110.0), (20.6, -9.0, FT, 20.0)]
env_preview(ob, out, ["ZONE_SalaJuegos"], views, dragons, (19.3, -12.0, 0.0), 11.5)
