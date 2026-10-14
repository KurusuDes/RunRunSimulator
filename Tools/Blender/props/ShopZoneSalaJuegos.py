import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from env_kit_e2 import *

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
PILASTERS = {"E": [-11.9], "N": [19.4], "S": []}
INNER = {"E": ("E", YN_IN, YS_IN), "N": ("N", XE_IN, FX1), "S2": ("S", XE_IN, DOOR[0]), "S1": ("S", DOOR[1], FX1)}
POSTS = {"E": [YN_IN, -11.9, YS_IN], "N": [XE_IN, 19.4, FX1 - 0.15], "S2": [XE_IN, DOOR[0] - 0.16], "S1": [DOOR[1] + 0.16, FX1 - 0.15]}
RUG_C = (19.3, -12.0)


def build_walls(rng):
    B = Bins()
    W = WALLS
    S = W["S"]
    for u0, u1 in ((FX0, DOOR[0]), (DOOR[1], FX1)):
        wall_body(B, S, inner="SH_Parchment", outer="SH_Honey", u0=u0, u1=u1)
        cap3(B, S, u0, u1)
    for k in ("E", "N"):
        wall_body(B, W[k], inner="SH_Parchment", outer="SH_Honey")
        cap3(B, W[k], W[k].a0, W[k].a1)
    S.box(B["SH_Timber"], DOOR[0] - 0.05, DOOR[1] + 0.05, -0.05, T + 0.05, ZT - 0.24, ZT + 0.09, r=0.04, segs=2)
    for key, (k, u0, u1) in INNER.items():
        inner3(B, W[k], u0, u1, "SH_Plum", board="SH_Oak", groove="SH_Honey")
        girt3(B, W[k], u0, u1, FT + 2.0)
        knee_braces(B, W[k], POSTS[key], FT + 1.5, FT + 2.0)
    for k, u0, u1 in (("E", FY0, YS_OUT), ("N", XE_OUT, FX1), ("S", XE_OUT, DOOR[0]), ("S", DOOR[1], FX1)):
        outer3(B, W[k], u0, u1, rng)
    for k, us in PILASTERS.items():
        for u in us:
            wall_post3(B, W[k], u)
    wall_post3(B, W["N"], u0=FX1 - 0.3, u1=FX1 + 0.02)
    wall_post3(B, S, u0=FX1 - 0.3, u1=FX1 + 0.02)
    wall_post3(B, S, u0=DOOR[0] - 0.32, u1=DOOR[0])
    wall_post3(B, S, u0=DOOR[1], u1=DOOR[1] + 0.32)
    z0, z1 = G - 0.01, ZT + 0.15
    corner_post3(B, XE_OUT, XE_IN, YN_OUT, YN_IN, z0, z1)
    corner_post3(B, XE_OUT, XE_IN, YS_IN, YS_OUT, z0, z1)
    for u in (DOOR[0] - 0.16, DOOR[1] + 0.16):
        lantern(B, S.P(u, T + PIL_OUT, ZT - 0.55), (0, 1, 0))
    ivy(B, W["E"], -16.6, -13.0, rng)
    ivy(B, S, XE_OUT + 0.3, DOOR[0] - 0.5, rng)
    mushroom(B, XE_OUT - 0.2, YN_OUT - 0.15, G, 1.1, "SH_Gold")
    mushroom(B, XE_OUT - 0.12, YN_OUT + 0.22, G, 0.75, "SH_Plum")
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
    stars_on(B, W["E"], -11.9 + 0.8, YS_IN - 0.8, zs, 1)
    stars_on(B, W["N"], XE_IN + 0.8, 19.4 - 0.8, zs, 1)
    stars_on(B, W["N"], 19.4 + 0.8, FX1 - 0.9, zs, 0)
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
    top = FT + 0.009
    R = 2.0
    annulus(B["SH_Walnut"], cx, cy, 0.0, R - 0.05, FT + 0.004, n=36)
    annulus(B["SH_Walnut"], cx, cy, R - 0.05, R, FT + 0.004, n=36, zo=FT + 0.001)
    cyc = ["SH_Gold", "SH_Parchment", "SH_Sage", "SH_Plum", "SH_Parchment", "SH_Sage", "SH_Gold", "SH_Plum", "SH_Parchment",
           "SH_Sage", "SH_Plum", "SH_Gold", "SH_Plum"]
    r = 0.0
    w = (R - 0.06) / len(cyc)
    for i, m in enumerate(cyc):
        r0 = r + (0.0 if i == 0 else 0.008)
        r1 = r + w - 0.008
        annulus(B[m], cx, cy, r0, r1, top, n=36)
        r += w
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
    check_wall(walls, WALLS[k], u0 + 0.35, u1 - 0.35, skip=PILASTERS[k], label="inner_" + key)
parts_report()
ob = join_all("ShopZoneSalaJuegos")
report(ob)
export(ob, flags)
C = (19.3, -12.0, 0.5)
views = [
    ("all", 200, 52, C, 14.0),
    ("allS", 20, 45, C, 14.0),
    ("door", 200, 30, (19.25, -6.6, 1.0), 6.5),
    ("inside", 20, 35, (19.0, -8.5, 0.6), 6.5),
    ("corner", 160, 50, (16.8, -15.9, 0.6), 6.0),
    ("top", 200, 75, (19.3, -12.0, 0.0), 11.0),
]
dragons = [(19.2, -12.8, FT, 200.0), (19.25, -5.9, G, 200.0), (17.0, -15.6, FT, 110.0), (20.6, -9.0, FT, 20.0)]
env_preview(ob, out, ["ZONE_SalaJuegos"], views, dragons, (19.3, -12.0, 0.0), 11.5)
