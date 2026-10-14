import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from env_kit_e2 import *

SX0, SX1 = 16.026, 46.026
SY0, SY1 = -4.59, -1.59
ST = -0.21
G = -0.41
BX0, BX1, BY0, BY1 = 15.5, 46.5, -43.0, 7.0
CURB = 0.22
ROAD_Y1 = 5.9
CROSS_X = (28.6, 31.4)
RAMP_X = (28.3, 31.7)
ZONE_DOORS = [19.25, 41.5]


def build_sidewalk(rng):
    B = Bins()
    wbox(B["SH_StoneDark"], (SX0, SY1 - CURB, G - 0.01), (SX1, SY1, ST), r=0.05, segs=2)
    wbox(B["SH_StoneDark"], (SX0, SY0, G - 0.01), (SX1, SY0 + CURB, ST), r=0.05, segs=2)
    wbox(B["SH_StoneDark"], (SX0, SY0 + CURB - 0.02, G - 0.01), (SX0 + CURB, SY1 - CURB + 0.02, ST), r=0.05, segs=2)
    wbox(B["SH_StoneDark"], (SX1 - CURB, SY0 + CURB - 0.02, G - 0.01), (SX1, SY1 - CURB + 0.02, ST), r=0.05, segs=2)
    x0, x1, y0, y1 = SX0 + CURB, SX1 - CURB, SY0 + CURB, SY1 - CURB
    quad_z(B["SH_StoneDark"], x0 - 0.01, x1 + 0.01, y0 - 0.01, y1 + 0.01, ST - 0.008)
    rows = 3
    th = (y1 - y0) / rows
    nx = int(round((x1 - x0) / 0.82))
    tw = (x1 - x0) / nx
    for j in range(rows):
        ya, yb = y0 + j * th, y0 + (j + 1) * th
        off = 0.0 if j % 2 == 0 else tw / 2
        edges = [x0] + [x0 + off + i * tw for i in range(-1, nx + 2) if x0 + 0.2 < x0 + off + i * tw < x1 - 0.2] + [x1]
        for t, (xa, xb) in enumerate(zip(edges, edges[1:])):
            accent = rng.random() < 0.14
            chamfer_tile(B["SH_Stone" if accent else "SH_Parchment"], xa + 0.011, xb - 0.011, ya + 0.011, yb - 0.011, ST, ch=0.016, dz=0.008)
    return B.done("Sidewalk", angle=50)


def build_road():
    B = Bins()
    quad_z(B["SH_Dark"], BX0, BX1, SY1 - 0.05, ROAD_Y1, G)
    yc = (SY1 + ROAD_Y1) / 2
    x = BX0 + 0.5
    while x + 1.4 < BX1:
        if not (CROSS_X[0] - 0.6 < x + 0.7 < CROSS_X[1] + 0.6):
            chamfer_tile(B["SH_Gold"], x, x + 1.4, yc - 0.08, yc + 0.08, G + 0.006, ch=0.02, dz=0.006)
        x += 2.8
    for ya in (SY1 + 0.22, ROAD_Y1 - 0.34):
        for xa, xb in ((BX0, CROSS_X[0] - 0.25), (CROSS_X[1] + 0.25, BX1)):
            chamfer_tile(B["SH_Parchment"], xa, xb, ya, ya + 0.12, G + 0.006, ch=0.02, dz=0.006)
    y = SY1 + 0.3
    while y + 0.45 < ROAD_Y1 - 0.25:
        chamfer_tile(B["SH_Parchment"], CROSS_X[0], CROSS_X[1], y, y + 0.45, G + 0.006, ch=0.03, dz=0.006)
        y += 0.85
    for mx, my in ((22.5, 3.3), (37.8, 0.6)):
        disc(B["SH_StoneDark"], mx, my, 0.36, 0.43, G + 0.007, G - 0.004, 16)
        for k in (-2, -1, 0, 1, 2):
            chamfer_tile(B["SH_Dark"], mx - 0.24, mx + 0.24, my + k * 0.1 - 0.025, my + k * 0.1 + 0.025, G + 0.0085, ch=0.008, dz=0.002)
    for gx in (20.0, 34.0, 43.5):
        wbox(B["SH_StoneDark"], (gx - 0.42, SY1 + 0.01, G - 0.01), (gx + 0.42, SY1 + 0.36, G + 0.006), r=0.012, segs=1)
        for k in range(6):
            xa = gx - 0.33 + k * 0.12
            chamfer_tile(B["SH_Dark"], xa, xa + 0.06, SY1 + 0.07, SY1 + 0.3, G + 0.0075, ch=0.006, dz=0.002)
    return B.done("Road", angle=50)


def build_ground(rng):
    B = Bins()
    g = B["SH_Grass"]
    quad_z(g, BX0, BX1, BY0, SY0 + 0.05, G)
    quad_z(g, BX0, SX0 + 0.05, SY0 + 0.05, SY1 - 0.05, G)
    quad_z(g, SX1 - 0.05, BX1, SY0 + 0.05, SY1 - 0.05, G)
    quad_z(g, BX0, BX1, ROAD_Y1, BY1, G)
    chamfer_tile(B["SH_StoneDark"], BX0, BX1, ROAD_Y1 - 0.02, ROAD_Y1 + 0.16, G + 0.006, ch=0.02, dz=0.006)
    for zx in ZONE_DOORS:
        path_stones2(B["SH_Stone"], [(zx, SY0 - 0.05), (zx, -6.95)], G + 0.008, rng, step=0.7, w=0.66, d=0.54)
    return B.done("Ground", angle=50)


def build_decor(rng):
    B = Bins()
    pet = [("SH_Gold", "SH_Parchment"), ("SH_Parchment", "SH_Gold"), ("SH_Plum", "SH_Parchment"), ("SH_Sage", "SH_Gold")]

    def lawn_ok(x, y):
        if RAMP_X[0] - 0.2 < x < RAMP_X[1] + 0.2:
            return False
        if any(abs(x - zx) < 0.65 for zx in ZONE_DOORS):
            return False
        return True

    beds = [(17.2, -6.62), (21.6, -6.62), (25.6, -6.62), (34.2, -6.62), (38.6, -6.62), (44.4, -6.62)]
    for bi, (cx, cy) in enumerate(beds):
        for k in range(7):
            x = cx + (k - 3) * 0.22 + rng.uniform(-0.05, 0.05)
            y = cy + rng.uniform(-0.07, 0.07)
            if not lawn_ok(x, y):
                continue
            tuft(B["SH_Leaf"], x, y, G, rng, 0.17)
            if k % 2 == 0:
                pc, cc = pet[(bi + k) % 4]
                flower(B[pc], B[cc], x + 0.03, y - 0.02, G + 0.09, rng, R=0.1)
    areas = [((16.0, 46.0), (-6.7, -4.8), 28), ((15.6, 46.4), (-42.8, -38.8), 26), ((15.6, 46.4), (6.1, 6.9), 14),
             ((22.75, 23.35), (-16.8, -7.4), 5), ((45.7, 46.4), (-38.0, -7.4), 8)]
    for (xa, xb), (ya, yb), n in areas:
        placed = tries = 0
        while placed < n and tries < 500:
            tries += 1
            x, y = rng.uniform(xa, xb), rng.uniform(ya, yb)
            if not lawn_ok(x, y):
                continue
            tuft(B["SH_Leaf"], x, y, G, rng, rng.uniform(0.1, 0.15))
            placed += 1
    return B.done("Decor", angle=70)


rng = random.Random(1532)
out, flags = cli()
begin_env()
side = build_sidewalk(rng)
road = build_road()
ground = build_ground(rng)
decor = build_decor(rng)
check_floor(side, [(SX0 + 0.3, SX1 - 0.3, SY0 + 0.3, SY1 - 0.3)], ST, step=0.2, label="sidewalk")
check_floor(side, [(SX0 + 0.06, SX1 - 0.06, SY1 - 0.17, SY1 - 0.06), (SX0 + 0.06, SX1 - 0.06, SY0 + 0.06, SY0 + 0.17)], ST, step=0.1, label="curbs")
check_floor(road + ground, [(BX0 + 0.1, BX1 - 0.1, SY1 + 0.05, BY1 - 0.1), (BX0 + 0.1, BX1 - 0.1, BY0 + 0.1, SY0 - 0.05)], G, step=0.45, label="basefloor")
parts_report()
ob = join_all("ShopStreet")
report(ob)
export(ob, flags)
C = (31.0, -1.5, -0.3)
views = [
    ("all", 200, 45, C, 34.0),
    ("allS", 20, 40, (31.0, -14.0, 0.0), 40.0),
    ("cross", 200, 42, (30.0, -2.4, -0.3), 9.0),
    ("curb", 150, 30, (17.2, -3.0, -0.3), 5.0),
    ("zone", 20, 40, (19.3, -5.0, -0.3), 7.0),
    ("end", 70, 25, (45.6, -3.1, -0.3), 5.0),
]
dragons = [(30.0, -3.2, ST, 200.0), (17.4, -3.1, ST, 160.0), (19.25, -5.6, G, 20.0), (45.2, -0.6, G, 70.0)]
env_preview(ob, out, ["Street", "BaseFloor"], views, dragons, (31.0, -18.0, 0.0), 51.0)
