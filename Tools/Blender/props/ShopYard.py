import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from env_kit_e2 import *

T = 0.5
ZT = 1.5
FIN = 0.0
GOUT = -0.41
XW_IN, XW_OUT = 15.928, 15.428
XE_IN, XE_OUT = 45.062, 45.562
YS_IN, YS_OUT = -38.031, -38.531
YNW_IN, YNW_OUT = -17.928, -17.428
YNE_IN, YNE_OUT = -24.93, -24.43
X_NW_END = 23.684
X_NE_END = 36.45
X_BLD_W, X_BLD_E, Y_BLD_S = 23.5, 36.5, -25.0
X_SPLIT = 32.0

DECK = (16.9, 24.1, -36.9, -32.6)
PAD = (38.4, XE_IN, YS_IN, YNE_IN)
RAMP = (21.3, 23.6, -24.2, -21.5)
PATH_OFFICE = [(21.0, -23.0), (20.6, -25.6), (20.3, -29.0), (20.5, -32.5)]
PATH_CARE = [(20.75, -25.1), (23.4, -26.6), (27.5, -27.3), (32.0, -27.4), (36.0, -27.2), (38.5, -27.4)]

WALLS = {
    "W": Wall("y", YS_OUT, YNW_OUT, XW_IN, +1, T, ZT, FIN, GOUT),
    "S": Wall("x", XW_OUT, XE_OUT, YS_IN, +1, T, ZT, FIN, GOUT),
    "NW": Wall("x", XW_OUT, X_NW_END, YNW_IN, -1, T, ZT, FIN, GOUT),
    "E": Wall("y", YS_OUT, YNE_OUT, XE_IN, -1, T, ZT, FIN, GOUT),
    "NE": Wall("x", X_NE_END, XE_OUT, YNE_IN, -1, T, ZT, FIN, GOUT),
}
PILASTERS = {
    "W": [-34.0, -30.0, -26.0, -21.6],
    "S": [20.0, 24.0, 28.0, X_SPLIT, 36.0, 40.2],
    "NW": [19.8],
    "E": [-34.0, -30.0, -27.0],
    "NE": [40.5],
}


FENCE_H = 1.56


def build_walls(rng):
    B = Bins()
    W = WALLS
    inner = {"W": [(YS_IN, YNW_IN, "SH_Teal")], "NW": [(XW_IN, X_BLD_W, "SH_Teal")],
             "S": [(XW_IN, X_SPLIT, "SH_Teal"), (X_SPLIT, XE_IN, "SH_Gold")], "E": [(YS_IN, YNE_IN, "SH_Gold")],
             "NE": [(X_BLD_E, XE_IN, "SH_Gold")]}
    outer = {"W": (YS_OUT, YNW_OUT), "S": (XW_OUT, XE_OUT), "NW": (XW_OUT, X_BLD_W), "E": (YS_OUT, YNE_OUT), "NE": (X_BLD_E, XE_OUT)}
    for k, w in W.items():
        for u0, u1, acc in inner[k]:
            fence_face(B, w, u0, u1, FIN - 0.01, FENCE_H, False, rng, bw=0.38)
            for zr in (FIN + 0.3, FIN + 1.0):
                w.box(B["SH_Timber"], u0, u1, -0.05, -0.015, zr, zr + 0.13, r=0.02, segs=1)
            w.box(B[acc], u0, u1, -0.056, -0.04, FIN + 1.04, FIN + 1.09, r=0.008, segs=1)
        u0, u1 = outer[k]
        stone_base(B, w, u0, u1, 0.3, step=1.3, rng=rng)
        fence_face(B, w, u0, u1, GOUT + 0.28, FENCE_H, True, rng, bw=0.42)
        w.box(B["SH_Timber"], u0, u1, w.T + 0.015, w.T + 0.05, FIN + 0.9, FIN + 1.0, r=0.02, segs=1)
        hedge(B["SH_Leaf"], w, w.a0, w.a1, 1.3, 1.76, rng, v0=0.035, v1=T - 0.035, step=0.75)
    for k, us in PILASTERS.items():
        for u in us:
            wall_post3(B, W[k], u, width=0.26, z1=1.86)
    z0, z1 = GOUT - 0.01, 1.92
    corner_post3(B, XW_OUT, XW_IN, YS_OUT, YS_IN, z0, z1)
    corner_post3(B, XE_IN, XE_OUT, YS_OUT, YS_IN, z0, z1)
    corner_post3(B, XW_OUT, XW_IN, YNW_IN, YNW_OUT, z0, z1)
    corner_post3(B, XE_IN, XE_OUT, YNE_IN, YNE_OUT, z0, z1)
    for x, y, dx, dy in ((XW_IN + 0.04, YS_IN + 0.04, 1, 1), (XE_IN - 0.04, YS_IN + 0.04, -1, 1),
                         (XW_IN + 0.04, YNW_IN - 0.04, 1, -1), (XE_IN - 0.04, YNE_IN - 0.04, -1, -1)):
        lantern(B, (x, y, 1.62), (dx, dy, 0))
    for x, y in ((XW_OUT - 0.2, YS_OUT - 0.15), (XE_OUT + 0.18, YS_OUT - 0.2), (XE_OUT + 0.2, YNE_OUT + 0.18)):
        mushroom(B, x, y, GOUT, 1.1, "SH_Plum")
        mushroom(B, x + 0.2, y + 0.06, GOUT, 0.7, "SH_Gold")
    return B.done("Walls")


def build_floor(rng):
    B = Bins()
    g = B["SH_Grass"]
    quad_z(g, XW_IN - 0.06, XE_IN + 0.06, YS_IN - 0.06, Y_BLD_S + 0.12, FIN)
    quad_z(g, XW_IN - 0.06, X_BLD_W + 0.06, Y_BLD_S + 0.12, YNW_IN + 0.06, FIN)

    x0, x1, y0, y1 = DECK
    quad_z(B["SH_Timber"], x0, x1, y0, y1, FIN + 0.002)
    n = int(round((y1 - y0) / 0.3))
    pw = (y1 - y0) / n
    for j in range(n):
        ya, yb = y0 + j * pw, y0 + (j + 1) * pw
        mat = "SH_Honey" if j % 2 == 0 else "SH_Walnut"
        cut = x0 + (1.6 if j % 3 == 0 else 3.3 if j % 3 == 1 else 5.1)
        for xa, xb in ((x0, cut), (cut, x1)):
            chamfer_tile(B[mat], xa + 0.008, xb - 0.008, ya + 0.01, yb - 0.01, FIN + 0.009, ch=0.014, dz=0.006)
    for ya, yb in ((y0 - 0.1, y0 + 0.02), (y1 - 0.02, y1 + 0.1)):
        wbox(B["SH_Walnut"], (x0 - 0.1, ya, FIN - 0.03), (x1 + 0.1, yb, FIN + 0.01), r=0.015, segs=1)
    for xa, xb in ((x0 - 0.1, x0 + 0.02), (x1 - 0.02, x1 + 0.1)):
        wbox(B["SH_Walnut"], (xa, y0 - 0.1, FIN - 0.03), (xb, y1 + 0.1, FIN + 0.01), r=0.015, segs=1)

    x0, x1, y0, y1 = PAD
    quad_z(B["SH_StoneDark"], x0 - 0.04, x1, y0, y1, FIN + 0.002)
    flag_stones2(B["SH_Stone"], x0, x1, y0, y1, FIN + 0.009, rng, cell=1.05)

    path_stones2(B["SH_Stone"], PATH_OFFICE, FIN + 0.01, rng)
    path_stones2(B["SH_Stone"], PATH_CARE, FIN + 0.01, rng)
    return B.done("Floor", angle=50)


def blocked_rects():
    mk = markers()
    rects = [DECK, PAD, RAMP]
    for name, (x, y, z, sx, sy, sz) in mk.items():
        if name.startswith("ROOM") or sx <= 0:
            continue
        if XW_IN <= x <= XE_IN and YS_IN <= y <= YNW_IN:
            rects.append((x - sx / 2 - 0.25, x + sx / 2 + 0.25, y - sy / 2 - 0.25, y + sy / 2 + 0.25))
    return rects


def in_yard(x, y, pad):
    if not (XW_IN + pad <= x <= XE_IN - pad and YS_IN + pad <= y):
        return False
    if y <= Y_BLD_S - pad:
        return True
    return x <= X_BLD_W - pad and y <= YNW_IN - pad


def bush(B, x, y, rng, s=1.0):
    for k in range(2):
        a = math.pi * k + rng.uniform(-0.4, 0.4)
        r = 0.16 * s * rng.uniform(0.85, 1.1)
        ellipsoid_bm((x + math.cos(a) * 0.12 * s, y + math.sin(a) * 0.12 * s, FIN + r * 0.55), (r, r, r * 0.85), 6, 4, bm=B["SH_Leaf"])


def build_decor(rng):
    B = Bins()
    rects = blocked_rects()

    def ok(x, y, pad=0.35):
        return in_yard(x, y, pad) and not in_rects(x, y, rects, 0.1) and             poly_dist((x, y), PATH_OFFICE) > 0.55 and poly_dist((x, y), PATH_CARE) > 0.55

    pet = [("SH_Gold", "SH_Parchment"), ("SH_Parchment", "SH_Gold"), ("SH_Plum", "SH_Parchment"), ("SH_Sage", "SH_Gold")]
    corners = [(16.32, -18.32, 1.0), (23.1, -18.32, 0.9), (16.32, -37.63, 0.9), (37.0, -25.33, 0.9), (16.32, -24.6, 0.8)]
    for x, y, sc in corners:
        bush(B, x, y, rng, sc)
        for k in range(3):
            a = 2 * math.pi * k / 3 + 0.5
            pc, cc = pet[(k + int(x)) % 4]
            flower(B[pc], B[cc], x + math.cos(a) * 0.13 * sc, y + math.sin(a) * 0.13 * sc, FIN + 0.24 * sc, rng, R=0.07)
    beds = [(19.0, -37.62), (27.0, -37.62), (35.4, -37.62), (16.32, -31.8), (16.32, -28.0), (19.8, -18.32),
            (30.0, -25.42), (26.0, -25.42)]
    for bi, (cx, cy) in enumerate(beds):
        along_x = abs(cx - 16.32) > 0.05
        for k in range(5):
            t = (k - 2) * 0.25 + rng.uniform(-0.05, 0.05)
            x = cx + (t if along_x else rng.uniform(-0.07, 0.07))
            y = cy + (rng.uniform(-0.07, 0.07) if along_x else t)
            if not ok(x, y, 0.1):
                continue
            tuft(B["SH_Leaf"], x, y, FIN, rng, 0.17)
            if k % 3 == 0:
                pc, cc = pet[(bi + k) % 4]
                flower(B[pc], B[cc], x + 0.03, y - 0.02, FIN + 0.09, rng, R=0.1)
    placed = 0
    tries = 0
    while placed < 25 and tries < 3000:
        tries += 1
        x = rng.uniform(XW_IN, XE_IN)
        y = rng.uniform(YS_IN, YNW_IN)
        if not ok(x, y):
            continue
        tuft(B["SH_Leaf"], x, y, FIN, rng, rng.uniform(0.1, 0.15))
        placed += 1
    return B.done("Decor", angle=70)


rng = random.Random(153)
out, flags = cli()
begin_env()
walls = build_walls(rng)
floors = build_floor(rng)
decor = build_decor(rng)
floor_objs = [o for o in floors if "Grass" in o.name or "Beige" in o.name or "Wood" in o.name or "Cream" in o.name]
dev_f = check_floor([o for o in floors if o.name.endswith("Grass")], [(16.2, 38.0, -37.7, -25.4), (16.2, 23.2, -25.0, -18.3)], FIN, label="grass")
dev_f2 = check_floor([o for o in floors if not o.name.endswith("Grass")], [DECK, PAD], FIN, label="deck+pad")
skips = {k: v + [] for k, v in PILASTERS.items()}
for k, w in WALLS.items():
    a, b = {"W": (YS_IN, YNW_IN), "S": (XW_IN, XE_IN), "NW": (XW_IN, X_BLD_W), "E": (YS_IN, YNE_IN), "NE": (X_BLD_E, XE_IN)}[k]
    check_wall(walls, w, a + 0.3, b - 0.3, skip=PILASTERS[k], label="inner_" + k)
parts_report()
ob = join_all("ShopYard")
report(ob)
export(ob, flags)
C = (30.5, -27.9, 0.0)
views = [
    ("all", 200, 50, C, 33.0),
    ("allS", 20, 40, C, 34.0),
    ("office", 200, 45, (20.3, -33.5, 0.4), 8.5),
    ("care", 160, 45, (41.6, -31.5, 0.4), 10.0),
    ("corner", 225, 35, (17.6, -36.9, 0.6), 5.5),
    ("ext", 20, 25, (30.5, -38.6, 0.4), 9.0),
]
dragons = [(20.0, -31.2, FIN, 190.0), (39.6, -30.8, FIN, 160.0), (17.6, -36.0, FIN, 220.0), (30.0, -39.8, GOUT, 20.0)]
env_preview(ob, out, ["Parque"], views, dragons, C, 32.0)
