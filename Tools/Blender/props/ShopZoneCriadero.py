import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from env_kit_e2 import *

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
PILASTERS = {"W": [-13.05, -19.95], "N": [41.8], "S": []}
INNER = {"S2": ("S", FX0, DOOR[0]), "S1": ("S", DOOR[1], XW_IN), "W": ("W", YN_IN, YS_IN), "N": ("N", FX0, XW_IN)}


POSTS = {"S2": [FX0 + 0.14, DOOR[0] - 0.16], "S1": [DOOR[1] + 0.16, XW_IN], "W": [YN_IN, -19.95, -13.05, YS_IN],
         "N": [FX0 + 0.14, 41.8, XW_IN]}


def barn_x(B, w, u0, u1, z0, z1, m="SH_Timber"):
    d0, d1 = w.T + 0.012, w.T + 0.05
    w.box(B[m], u0, u1, d0, d1, z0, z0 + 0.12, r=0.02, segs=1)
    w.box(B[m], u0, u1, d0, d1, z1 - 0.12, z1, r=0.02, segs=1)
    w.box(B[m], u0, u0 + 0.12, d0, d1, z0, z1, r=0.02, segs=1)
    w.box(B[m], u1 - 0.12, u1, d0, d1, z0, z1, r=0.02, segs=1)
    du, dz = (u1 - u0) - 0.24, (z1 - z0) - 0.24
    L = math.hypot(du, dz)
    for sgn in (1, -1):
        rotbox(w, B[m], (u0 + u1) / 2, (d0 + d1) / 2 - 0.006, (z0 + z1) / 2, L, abs(d1 - d0) - 0.012, 0.12, math.atan2(sgn * dz, du))


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
        cap3(B, S, u0, u1)
    for k in ("W", "N"):
        wall_body(B, W[k], inner="SH_Parchment", outer="SH_Honey")
        cap3(B, W[k], W[k].a0, W[k].a1)
    S.box(B["SH_Timber"], DOOR[0] - 0.05, DOOR[1] + 0.05, -0.05, T + 0.05, ZT - 0.24, ZT + 0.09, r=0.04, segs=2)
    for key, (k, u0, u1) in INNER.items():
        inner3(B, W[k], u0, u1, "SH_Moss")
        girt3(B, W[k], u0, u1, FT + 2.0)
        knee_braces(B, W[k], POSTS[key], FT + 1.42, FT + 2.0)
    for k, u0, u1 in (("S", FX0, DOOR[0]), ("S", DOOR[1], XW_OUT), ("W", YN_OUT, YS_OUT), ("N", FX0, XW_OUT)):
        outer3(B, W[k], u0, u1, rng)
    barn_x(B, S, FX0 + 0.45, DOOR[0] - 0.45, G + 0.46, ZT - 0.4)
    barn_x(B, S, DOOR[1] + 0.45, XW_OUT - 0.45, G + 0.46, ZT - 0.4)
    for k, us in PILASTERS.items():
        for u in us:
            wall_post3(B, W[k], u)
    wall_post3(B, S, u0=FX0 - 0.02, u1=FX0 + 0.3)
    wall_post3(B, W["N"], u0=FX0 - 0.02, u1=FX0 + 0.3)
    wall_post3(B, S, u0=DOOR[0] - 0.32, u1=DOOR[0])
    wall_post3(B, S, u0=DOOR[1], u1=DOOR[1] + 0.32)
    z0, z1 = G - 0.01, ZT + 0.15
    corner_post3(B, XW_IN, XW_OUT, YS_IN, YS_OUT, z0, z1)
    corner_post3(B, XW_IN, XW_OUT, YN_OUT, YN_IN, z0, z1)
    for u in (DOOR[0] - 0.16, DOOR[1] + 0.16):
        lantern(B, S.P(u, T + PIL_OUT, ZT - 0.55), (0, 1, 0))
    ivy(B, W["N"], FX0 + 0.4, 40.6, rng)
    ivy(B, W["W"], -21.6, -16.5, rng)
    ivy(B, S, XW_OUT - 1.6, XW_OUT - 0.3, rng)
    egg_sign(B, S, sum(DOOR) / 2, ZT + 0.2)
    mushroom(B, XW_OUT + 0.18, YN_OUT - 0.2, G, 1.1, "SH_Plum")
    mushroom(B, XW_OUT + 0.22, YN_OUT + 0.12, G, 0.75, "SH_Gold")
    mushroom(B, XW_OUT + 0.2, -15.8, G, 0.9, "SH_Gold")
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
    tgt = B["SH_StrawDark"]
    before = set(tgt.verts)
    ellipsoid_bm((x, y, FT), (0.2 * s, 0.15 * s, 0.022), 8, 3, bm=tgt)
    base = rng.uniform(0, math.pi)
    for k in range(5):
        r = rng.uniform(0.2, 0.3) * s
        m = Matrix.Translation((x + rng.uniform(-0.06, 0.06), y + rng.uniform(-0.06, 0.06), 0)) @             Matrix.Rotation(base + k * math.pi / 5 + rng.uniform(-0.2, 0.2), 4, "Z")
        tgt = B["SH_Gold"]
        before = set(tgt.verts)
        ellipsoid_bm((0, 0, FT + 0.004), (r, 0.035 * s, 0.026), 6, 3, bm=tgt)
        xf(tgt, m, [v for v in tgt.verts if v not in before])


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
    check_wall(walls, WALLS[k], u0 + 0.35, u1 - 0.35, skip=PILASTERS[k], label="inner_" + key)
parts_report()
ob = join_all("ShopZoneCriadero")
report(ob)
export(ob, flags)
C = (41.4, -14.5, 0.5)
views = [
    ("all", 200, 52, C, 19.0),
    ("allS", 20, 45, C, 19.0),
    ("door", 20, 30, (41.5, -6.5, 1.0), 7.5),
    ("inside", 200, 40, (41.5, -9.0, 0.2), 7.0),
    ("corner", 135, 35, (44.9, -20.9, 0.6), 5.5),
    ("top", 200, 75, (41.4, -14.5, 0.0), 12.0),
]
dragons = [(41.4, -9.4, FT, 200.0), (41.5, -5.9, G, 20.0), (44.4, -20.4, FT, 135.0), (37.6, -13.0, FT, 250.0)]
env_preview(ob, out, ["ZONE_Criadero"], views, dragons, (41.4, -14.5, 0.0), 17.0)
