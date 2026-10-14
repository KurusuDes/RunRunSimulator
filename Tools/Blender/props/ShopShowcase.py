import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

HALF = 1.5
DECK_H = 0.12
CARPET_TOP = DECK_H + 0.022
F = 1.36
POST_R = 0.068
POST_TOP = 0.405
GAP = 0.56
RAIL_Z = 0.37
RAIL_H, RAIL_T = 0.075, 0.075
GLASS_Z0, GLASS_Z1 = DECK_H + 0.03, RAIL_Z - 0.02
SIGN_X = 0.62
SIGN_TOP = 1.5
BAR_Z = 1.42


def face_m(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def star_bm(cx, y, cz, R, r, depth, bm=None):
    bm = bm or bmesh.new()
    prof = [(1.0, 0.0), (1.0, depth * 0.55), (0.86, depth * 0.9), (0.62, depth)]
    rings = []
    for s, d in prof:
        ring = []
        for k in range(10):
            a = math.pi / 2 + math.pi * k / 5
            rad = (R if k % 2 == 0 else r) * s
            ring.append(bm.verts.new((cx + rad * math.cos(a), y - d, cz + rad * math.sin(a))))
        rings.append(ring)
    faces = []
    for A, B in zip(rings, rings[1:]):
        for k in range(10):
            faces.append(bm.faces.new((A[k], A[(k + 1) % 10], B[(k + 1) % 10], B[k])))
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def build_deck():
    rings = rbox_rings(2 * HALF, 2 * HALF, DECK_H, 0.2, 0.04, seg=3, Rb=0.015, segb=1)
    finish("Deck", loft(rings, 4), "SH_WoodDark", angle=50)
    rings = rbox_rings(2.62, 2.62, 0.03, 0.3, 0.012, seg=2, z0=DECK_H - 0.012)
    finish("CarpetBorder", loft(rings, 4), "SH_Cream", angle=50)
    rings = rbox_rings(2.44, 2.44, 0.035, 0.24, 0.014, seg=2, z0=DECK_H - 0.013)
    finish("Carpet", loft(rings, 4), "SH_Coral", angle=50)


def post_bm(x, y, top, r, bm):
    z0 = DECK_H - 0.005
    prof = [(0.0, z0), (r + 0.024, z0), (r + 0.026, z0 + 0.03), (r + 0.006, z0 + 0.06), (r, z0 + 0.085),
            (r, top - 0.03), (r * 0.8, top - 0.006), (r * 0.4, top + 0.004), (0.0, top + 0.006)]
    return lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((x, y, 0)))


def build_rail():
    posts = [(-F, -F), (F, -F), (-F, F), (F, F), (-F, 0.0), (F, 0.0), (-GAP, -F), (GAP, -F)]
    segs = [((-F, F), (-SIGN_X, F)), ((-SIGN_X, F), (SIGN_X, F)), ((SIGN_X, F), (F, F)),
            ((-F, -F), (-F, 0.0)), ((-F, 0.0), (-F, F)), ((F, -F), (F, 0.0)), ((F, 0.0), (F, F)),
            ((-F, -F), (-GAP, -F)), ((GAP, -F), (F, -F))]
    bm = bmesh.new()
    balls = bmesh.new()
    gballs = bmesh.new()
    for x, y in posts:
        post_bm(x, y, POST_TOP, POST_R, bm)
        tgt = gballs if abs(x) == GAP else balls
        ellipsoid_bm((x, y, POST_TOP + 0.05), (0.072, 0.072, 0.062), 10, 6, bm=tgt)
    for x in (-SIGN_X, SIGN_X):
        post_bm(x, F, SIGN_TOP - 0.02, POST_R + 0.008, bm)
        ellipsoid_bm((x, F, SIGN_TOP + 0.03), (0.08, 0.08, 0.068), 10, 6, bm=balls)
    finish("Posts", bm, "SH_WoodDark", angle=40)
    finish("PostBalls", balls, "SH_Cream", angle=80)
    finish("GateBalls", gballs, "SH_Coral", angle=80)

    rails = bmesh.new()
    glass = bmesh.new()
    for a, b in segs:
        a, b = Vector(a), Vector(b)
        d = b - a
        L = d.length
        ang = math.atan2(d.y, d.x)
        c = (a + b) / 2
        rot = Matrix.Rotation(ang, 4, "Z")
        rbox_bm((c.x, c.y, RAIL_Z), (L + 0.02, RAIL_T, RAIL_H), 0.03, 2, bm=rails, matrix=rot)
        gh = GLASS_Z1 - GLASS_Z0
        rbox_bm((c.x, c.y, GLASS_Z0 + gh / 2), (L - 2 * POST_R + 0.02, 0.036, gh), 0.014, 1, bm=glass, matrix=rot)
    finish("Rails", rails, "SH_Wood", angle=50)
    finish("Glass", glass, "SH_Glass", angle=50)


def build_sign():
    bm = bmesh.new()
    rbox_bm((0, F, BAR_Z), (2 * SIGN_X + 0.1, 0.085, 0.085), 0.032, 2, bm=bm)
    finish("Bar", bm, "SH_Wood", angle=50)
    bw, bh = 1.08, 0.44
    bz = BAR_Z - 0.16 - bh / 2
    by = F - 0.005
    frame = rbox_rings(bw, bh, 0.06, 0.08, 0.02, seg=2, z0=-0.03)
    finish("SignFrame", loft(frame, 3, matrix=face_m(0, by, bz)), "SH_WoodDark", angle=50)
    panel = rbox_rings(bw - 0.1, bh - 0.1, 0.02, 0.05, 0.008, seg=2, z0=0.0)
    finish("SignPanel", loft(panel, 3, cap0=False, matrix=face_m(0, by - 0.022, bz)), "SH_Cream", angle=55)
    bm = star_bm(0, by - 0.035, bz + 0.004, 0.19, 0.088, 0.045)
    star_bm(-0.36, by - 0.035, bz + 0.03, 0.065, 0.031, 0.03, bm=bm)
    star_bm(0.36, by - 0.035, bz + 0.03, 0.065, 0.031, 0.03, bm=bm)
    finish("Stars", bm, "SH_Coral", angle=70)
    rope = bmesh.new()
    for sx in (-1, 1):
        x = sx * (bw / 2 - 0.12)
        tube_bm([(x, by, bz + bh / 2 - 0.01), (x, by, BAR_Z - 0.02)], 0.017, 6, bm=rope)
        m = Matrix.Translation((x, F, BAR_Z)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
        torus_bm(0.055, 0.017, 10, 5, bm=rope, matrix=m)
    tx, tz = 0.24, bz - bh / 2
    tag_c = Vector((tx + 0.1, by - 0.02, tz - 0.2))
    tube_bm([(tx - 0.04, by - 0.01, tz + 0.03), (tx + 0.03, by - 0.02, tz - 0.06), tag_c + Vector((-0.06, 0, 0.08))],
            0.011, 6, bm=rope)
    finish("Ropes", rope, "SH_Wood", angle=70)
    tilt = Matrix.Rotation(math.radians(-18), 4, "Y")
    tag = rbox_rings(0.26, 0.2, 0.036, 0.045, 0.014, seg=2, z0=-0.018)
    M = Matrix.Translation(tag_c) @ tilt @ Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    finish("Tag", loft(tag, 3, matrix=M), "SH_Coral", angle=55)
    hole = Matrix.Translation(tag_c) @ tilt @ Matrix.Translation((-0.075, -0.02, 0.055))
    finish("TagHole", xf(ellipsoid_bm((0, 0, 0), (0.022, 0.012, 0.022), 8, 5), hole), "SH_Cream", angle=80)
    coin = Matrix.Translation(tag_c) @ tilt @ Matrix.Translation((0.035, -0.02, -0.015)) @ Matrix.Rotation(math.pi / 2, 4, "X")
    prof = [(0.0, 0.0), (0.058, 0.0), (0.06, 0.01), (0.05, 0.017), (0.0, 0.017)]
    finish("TagCoin", lathe_bm(prof, 14, matrix=coin @ Matrix.Rotation(math.pi, 4, "X")), "SH_Cream", angle=55)


out, flags = cli()
begin()
build_deck()
build_rail()
build_sign()
ob = join_all("ShopShowcase")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(0.35, -0.25, CARPET_TOP))
