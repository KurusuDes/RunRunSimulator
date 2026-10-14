import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

HX, HY = 2.5, 1.8
STEP_H = 0.1
STEP_IN = 0.2
DECK_H = 0.22
CARPET_TOP = DECK_H + 0.022
DX, DY = HX - STEP_IN, HY - STEP_IN
FX, FY = DX - 0.14, DY - 0.14
POST_R = 0.068
POST_TOP = DECK_H + 0.285
CORNER_R = 0.085
CORNER_TOP = DECK_H + 0.36
GAP = 0.7
STAR_R = 0.12
RAIL_Z = DECK_H + 0.25
RAIL_H, RAIL_T = 0.075, 0.075
GLASS_Z0, GLASS_Z1 = DECK_H + 0.03, RAIL_Z - 0.02
SIGN_X = 0.98
SIGN_TOP = 2.02
BAR_Z = 1.92


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


def flat_star_bm(x, y, z, R, r, h, bm):
    rings = []
    for s, d in ((1.0, 0.0), (0.78, h)):
        ring = []
        for k in range(10):
            a = math.pi / 2 + math.pi * k / 5
            rad = (R if k % 2 == 0 else r) * s
            ring.append(bm.verts.new((x + rad * math.cos(a), y + rad * math.sin(a), z + d)))
        rings.append(ring)
    A, B = rings
    for k in range(10):
        bm.faces.new((A[k], A[(k + 1) % 10], B[(k + 1) % 10], B[k]))
    bm.faces.new(B)
    return bm


def slab(w, d, h, rc, z0, R=0.01):
    return loft(rbox_rings(w, d, h, rc, R, seg=1, z0=z0), 3, cap0=False)


def build_deck():
    rings = rbox_rings(2 * HX, 2 * HY, STEP_H, 0.3, 0.035, seg=2, Rb=0.015, segb=1)
    finish("Step", loft(rings, 4), "SH_Wood", angle=50)
    finish("GoldTrim", slab(2 * DX + 0.04, 2 * DY + 0.04, 0.035, 0.26, STEP_H - 0.01, 0.014), "SH_Gold", angle=50)
    rings = rbox_rings(2 * DX, 2 * DY, DECK_H - STEP_H + 0.02, 0.24, 0.04, seg=3, z0=STEP_H - 0.02)
    finish("Deck", loft(rings, 4), "SH_WoodDark", angle=50)
    cw, cd = 2 * DX - 0.38, 2 * DY - 0.38
    finish("CarpetBorder", slab(cw, cd, 0.03, 0.3, DECK_H - 0.012, 0.012), "SH_Cream", angle=50)
    finish("Carpet", slab(cw - 0.18, cd - 0.18, 0.035, 0.24, DECK_H - 0.013, 0.014), "SH_Sage", angle=50)
    finish("CarpetBand", slab(cw - 0.4, cd - 0.4, 0.04, 0.2, DECK_H - 0.013, 0.012), "SH_Gold", angle=50)
    finish("CarpetIn", slab(cw - 0.6, cd - 0.6, 0.045, 0.16, DECK_H - 0.013, 0.012), "SH_Sage", angle=50)

    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (cw / 2 - 0.45), sy * (cd / 2 - 0.45)
            flat_star_bm(x, y, DECK_H + 0.026, STAR_R, STAR_R * 0.48, 0.02, bm)
    finish("CarpetStars", bm, "SH_Gold", angle=70)


def post_bm(x, y, top, r, bm, segs=8):
    z0 = DECK_H - 0.005
    prof = [(0.0, z0), (r + 0.026, z0), (r + 0.022, z0 + 0.045), (r, z0 + 0.08),
            (r, top), (0.0, top + 0.006)]
    return lathe_bm(prof, segs, bm=bm, matrix=Matrix.Translation((x, y, 0)))


def onion_bm(x, y, z, s, bm):
    prof = [(0.0, 0.0), (0.06, 0.0), (0.05, 0.03), (0.086, 0.08), (0.07, 0.135), (0.035, 0.175), (0.02, 0.21),
            (0.0, 0.235)]
    return lathe_bm([(r * s, h * s) for r, h in prof], 8, bm=bm, matrix=Matrix.Translation((x, y, z)))


def build_rail():
    mx = (FX + GAP) / 2
    bx = (FX + SIGN_X) / 2
    front = [-FX, -mx, -GAP, GAP, mx, FX]
    back = [-FX, -bx, -SIGN_X, SIGN_X, bx, FX]
    sides = [-FY, 0.0, FY]
    posts = [(x, -FY) for x in front] + [(x, FY) for x in back if abs(x) != SIGN_X]
    posts += [(sx * FX, 0.0) for sx in (-1, 1)]
    segs = []
    for a, b in zip(front, front[1:]):
        if a == -GAP:
            continue
        segs.append(((a, -FY), (b, -FY)))
    for a, b in zip(back, back[1:]):
        segs.append(((a, FY), (b, FY)))
    for sx in (-1, 1):
        for a, b in zip(sides, sides[1:]):
            segs.append(((sx * FX, a), (sx * FX, b)))
    bm = bmesh.new()
    balls = bmesh.new()
    gold = bmesh.new()
    for x, y in posts:
        if abs(x) == GAP and y < 0:
            post_bm(x, y, POST_TOP + 0.06, POST_R + 0.008, bm)
            prof = [(0.0, 0.0), (0.05, 0.0), (0.05, 0.03), (0.0, 0.035)]
            lathe_bm(prof, 10, bm=gold, matrix=Matrix.Translation((x, y, POST_TOP + 0.06)))
            star_bm(x, y + 0.035, POST_TOP + 0.21, 0.15, 0.072, 0.07, bm=gold)
        elif abs(x) == FX and abs(y) == FY:
            post_bm(x, y, CORNER_TOP, CORNER_R, bm)
            onion_bm(x, y, CORNER_TOP - 0.004, 1.15, gold)
        else:
            post_bm(x, y, POST_TOP, POST_R, bm)
            ellipsoid_bm((x, y, POST_TOP + 0.05), (0.072, 0.072, 0.062), 8, 4, bm=balls)
    for x in (-SIGN_X, SIGN_X):
        post_bm(x, FY, SIGN_TOP - 0.02, POST_R + 0.016, bm)
        onion_bm(x, FY, SIGN_TOP - 0.024, 1.2, gold)
    finish("Posts", bm, "SH_WoodDark", angle=40)
    finish("PostBalls", balls, "SH_Cream", angle=80)
    finish("GoldFinials", gold, "SH_Gold", angle=70)

    rails = bmesh.new()
    glass = bmesh.new()
    for a, b in segs:
        a, b = Vector(a), Vector(b)
        d = b - a
        L = d.length
        ang = math.atan2(d.y, d.x)
        c = (a + b) / 2
        rot = Matrix.Rotation(ang, 4, "Z")
        rbox_bm((c.x, c.y, RAIL_Z), (L + 0.02, RAIL_T, RAIL_H), 0.03, 1, bm=rails, matrix=rot)
        gh = GLASS_Z1 - GLASS_Z0
        loft([(L - 2 * POST_R + 0.02, 0.036, 0.016, GLASS_Z0), (L - 2 * POST_R + 0.02, 0.036, 0.016, GLASS_Z1)], 1,
             bm=glass, matrix=Matrix.Translation((c.x, c.y, 0)) @ rot)
    finish("Rails", rails, "SH_Wood", angle=50)
    finish("Glass", glass, "SH_Glass", angle=50)


CROWN_S = 1.7


def crown_bm(x, y, z, s, bm):
    M = Matrix.Translation((x, y, z)) @ Matrix.Scale(s, 4)
    prof = [(0.0, 0.0), (0.13, 0.0), (0.136, 0.015), (0.13, 0.075), (0.0, 0.075)]
    lathe_bm(prof, 12, bm=bm, matrix=M)
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        prof = [(0.0, 0.0), (0.042, 0.0), (0.03, 0.06), (0.012, 0.1), (0.0, 0.11)]
        lathe_bm(prof, 6, bm=bm, matrix=M @ Matrix.Translation((math.cos(a) * 0.105, math.sin(a) * 0.105, 0.06)))
    return bm


def build_sign():
    bm = bmesh.new()
    rbox_bm((0, FY, BAR_Z), (2 * SIGN_X + 0.12, 0.1, 0.1), 0.038, 2, bm=bm)
    finish("Bar", bm, "SH_Wood", angle=50)
    cz = BAR_Z + 0.04
    finish("Crown", crown_bm(0, FY, cz, CROWN_S, bmesh.new()), "SH_Gold", angle=60)
    gems = bmesh.new()
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        r = 0.105 * CROWN_S
        ellipsoid_bm((math.cos(a) * r, FY + math.sin(a) * r, cz + 0.175 * CROWN_S), (0.034, 0.034, 0.03), 6, 4, bm=gems)
    ellipsoid_bm((0, FY - 0.138 * CROWN_S, cz + 0.04 * CROWN_S), (0.045, 0.024, 0.045), 8, 4, bm=gems)
    by = FY - 0.005
    bw, bh = 1.64, 0.52
    bz = BAR_Z - 0.18 - bh / 2
    sw, sh = 1.2, 0.32
    sz = bz - bh / 2 - 0.1 - sh / 2
    frames = bmesh.new()
    panels = bmesh.new()
    loft(rbox_rings(bw, bh, 0.065, 0.12, 0.022, seg=2, z0=-0.032), 3, bm=frames, matrix=face_m(0, by, bz))
    loft(rbox_rings(sw, sh, 0.06, 0.1, 0.02, seg=2, z0=-0.03), 3, bm=frames, matrix=face_m(0, by, sz))
    finish("SignFrames", frames, "SH_WoodDark", angle=50)
    loft(rbox_rings(bw - 0.11, bh - 0.11, 0.02, 0.07, 0.008, seg=2, z0=0.0), 3, cap0=False, bm=panels,
         matrix=face_m(0, by - 0.024, bz))
    loft(rbox_rings(sw - 0.1, sh - 0.1, 0.02, 0.05, 0.008, seg=2, z0=0.0), 3, cap0=False, bm=panels,
         matrix=face_m(0, by - 0.022, sz))
    finish("SignPanels", panels, "SH_Cream", angle=55)
    bm = star_bm(0, by - 0.037, bz + 0.005, 0.2, 0.094, 0.05)
    star_bm(-0.4, by - 0.037, bz + 0.0, 0.13, 0.062, 0.04, bm=bm)
    star_bm(0.4, by - 0.037, bz + 0.0, 0.13, 0.062, 0.04, bm=bm)
    for x in (-0.3, 0.0, 0.3):
        star_bm(x, by - 0.035, sz, 0.088, 0.042, 0.035, bm=bm)
    finish("Stars", bm, "SH_Gold", angle=70)
    for x in (-0.15, 0.15):
        ellipsoid_bm((x, by - 0.03, sz), (0.026, 0.016, 0.026), 6, 4, bm=gems)
    finish("Gems", gems, "SH_Cream", angle=80)

    rope = bmesh.new()
    for sx in (-1, 1):
        x = sx * (bw / 2 - 0.16)
        tube_bm([(x, by, bz + bh / 2 - 0.01), (x, by, BAR_Z - 0.02)], 0.019, 6, bm=rope)
        m = Matrix.Translation((x, FY, BAR_Z)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
        torus_bm(0.062, 0.019, 8, 4, bm=rope, matrix=m)
        x2 = sx * (sw / 2 - 0.14)
        tube_bm([(x2, by, sz + sh / 2 - 0.01), (x2, by, bz - bh / 2 + 0.02)], 0.016, 6, bm=rope)
    tx, tz = sw / 2 - 0.1, sz - sh / 2
    tag_c = Vector((tx + 0.1, by - 0.02, tz - 0.19))
    tube_bm([(tx - 0.04, by - 0.01, tz + 0.03), (tx + 0.03, by - 0.02, tz - 0.06), tag_c + Vector((-0.06, 0, 0.08))],
            0.011, 6, bm=rope)
    finish("Ropes", rope, "SH_Wood", angle=70)
    tilt = Matrix.Rotation(math.radians(-18), 4, "Y")
    tag = rbox_rings(0.27, 0.21, 0.036, 0.045, 0.014, seg=2, z0=-0.018)
    M = Matrix.Translation(tag_c) @ tilt @ Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    finish("Tag", loft(tag, 3, matrix=M), "SH_Gold", angle=55)
    hole = Matrix.Translation(tag_c) @ tilt @ Matrix.Translation((-0.078, -0.02, 0.058))
    finish("TagHole", xf(ellipsoid_bm((0, 0, 0), (0.022, 0.012, 0.022), 8, 5), hole), "SH_Cream", angle=80)
    coin = Matrix.Translation(tag_c) @ tilt @ Matrix.Translation((0.035, -0.02, -0.015)) @ Matrix.Rotation(math.pi / 2, 4, "X")
    prof = [(0.0, 0.0), (0.058, 0.0), (0.06, 0.01), (0.05, 0.017), (0.0, 0.017)]
    finish("TagCoin", lathe_bm(prof, 14, matrix=coin @ Matrix.Rotation(math.pi, 4, "X")), "SH_Cream", angle=55)


out, flags = cli()
begin()
build_deck()
build_rail()
build_sign()
ob = join_all("ShopShowcaseL3")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(0.5, -0.35, CARPET_TOP + 0.02))
