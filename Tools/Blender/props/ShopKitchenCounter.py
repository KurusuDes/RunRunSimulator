import sys, random
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

CW, CD, CH = 1.6, 0.7, 0.95
TOP_T = 0.09
BW, BD = 1.48, 0.58
TOP_Z = CH
COL_X = 0.37
COL_W = 0.6
WOOD = "SH_Oak"
DARK = "SH_Walnut"
PAINT = "SH_Sage"
ACC = "SH_Gold"
CERAMIC = "SH_Cream"


def fin(name, bm, mat, angle=50.0):
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def face_m(x, y, z, facing=-1):
    if facing < 0:
        return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
    return Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def bone_bm(length, r, flat=1.0, bm=None, matrix=None, useg=10):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    hx = length / 2 - r * 0.9
    tube_bm([(-hx, 0, 0), (hx, 0, 0)], r * 0.62, 8, bm=bm)
    for sx in (-1, 1):
        for sz in (-1, 1):
            ellipsoid_bm((sx * hx, 0, sz * r * 0.62), (r * 0.72, r * 0.72, r * 0.72), useg, max(4, useg // 2 + 1), bm=bm)
    new = [v for v in bm.verts if v not in before]
    m = Matrix.Diagonal((1.0, flat, 1.0, 1.0))
    if matrix is not None:
        m = matrix @ m
    xf(bm, m, new)
    return bm


def build_cabinet():
    rings = rbox_rings(CW, CD, TOP_T, 0.1, 0.035, seg=3, Rb=0.022, segb=2, z0=CH - TOP_T)
    fin("Top", loft(rings, 3), DARK, angle=50)
    rings = rbox_rings(BW, BD, CH - TOP_T - 0.05 + 0.01, 0.06, 0.012, seg=1, z0=0.06)
    fin("Body", loft(rings, 3), WOOD, angle=50)
    rings = rbox_rings(BW + 0.05, BD + 0.05, 0.085, 0.08, 0.025, seg=2, z0=0.0)
    fin("Plinth", loft(rings, 3), DARK, angle=50)
    bm = bmesh.new()
    prof = [(0.0, 0.07), (0.056, 0.07), (0.056, CH - TOP_T + 0.005), (0.0, CH - TOP_T + 0.005)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((sx * (BW / 2 - 0.035), sy * (BD / 2 - 0.035), 0)))
    lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((0, -BD / 2 + 0.03, 0)))
    fin("Pilasters", bm, DARK, angle=50)
    rings = rbox_rings(BW - 0.02, 0.05, 0.03, 0.02, 0.012, seg=1)
    fin("Rail", loft(rings, 2, cap0=False, matrix=face_m(0, -BD / 2 + 0.006, 0.635)), DARK, angle=55)

    yf = -BD / 2
    pan = bmesh.new()
    for s in (-1, 1):
        loft(rbox_rings(COL_W - 0.06, 0.15, 0.03, 0.04, 0.012, seg=2), 3, cap0=False, bm=pan,
             matrix=face_m(s * COL_X, yf + 0.008, 0.745))
        loft(rbox_rings(COL_W - 0.06, 0.46, 0.03, 0.06, 0.014, seg=2), 3, cap0=False, bm=pan,
             matrix=face_m(s * COL_X, yf + 0.008, 0.355))
    for sx in (-1, 1):
        m = Matrix.Translation((sx * (BW / 2 - 0.008), 0, 0.45)) @ Matrix.Rotation(sx * math.pi / 2, 4, "Y") @ \
            Matrix.Rotation(math.pi / 2, 4, "Z")
        loft(rbox_rings(0.42, 0.6, 0.03, 0.06, 0.014, seg=2), 3, cap0=False, bm=pan, matrix=m)
    for s in (-1, 1):
        loft(rbox_rings(COL_W - 0.06, 0.62, 0.03, 0.06, 0.014, seg=2), 3, cap0=False, bm=pan,
             matrix=face_m(s * COL_X, BD / 2 - 0.008, 0.45, facing=1))
    fin("Panels", pan, PAINT, angle=55)

    bm = bmesh.new()
    for s in (-1, 1):
        bone_bm(0.16, 0.028, 0.6, bm=bm, matrix=Matrix.Translation((s * COL_X, yf - 0.04, 0.745)), useg=8)
        for x in (s * COL_X - 0.045, s * COL_X + 0.045):
            tube_bm([(x, yf - 0.015, 0.745), (x, yf - 0.04, 0.745)], 0.012, 6, bm=bm)
        ellipsoid_bm((s * 0.11, yf - 0.03, 0.43), (0.044, 0.036, 0.044), 10, 6, bm=bm)
    fin("Pulls", bm, ACC, angle=60)


def build_board():
    x, y = -0.36, -0.03
    rot = Matrix.Translation((x, y, TOP_Z - 0.004)) @ Matrix.Rotation(math.radians(-6), 4, "Z")
    bm = loft(rbox_rings(0.58, 0.38, 0.045, 0.08, 0.016, seg=2), 3)
    loft(rbox_rings(0.14, 0.12, 0.045, 0.05, 0.016, seg=2, cx=-0.32), 3, bm=bm)
    xf(bm, rot)
    fin("Board", bm, CERAMIC, angle=55)
    ring = torus_bm(0.03, 0.012, 12, 5, matrix=rot @ Matrix.Translation((-0.345, 0, 0.047)))
    fin("BoardHole", ring, DARK, angle=70)
    bm = bmesh.new()
    for dx, dy, a in ((-0.1, 0.07, 18), (0.12, 0.075, -12), (0.01, -0.08, 35)):
        m = rot @ Matrix.Translation((dx, dy, 0.045 + 0.022)) @ Matrix.Rotation(math.radians(a), 4, "Z") @ \
            Matrix.Rotation(math.pi / 2, 4, "X")
        bone_bm(0.17, 0.036, 0.55, bm=bm, matrix=m, useg=8)
    fin("Cookies", bm, ACC, angle=60)
    py, pz = 0.235, TOP_Z + 0.042
    m = Matrix.Translation((-0.42, py, pz)) @ Matrix.Rotation(math.radians(4), 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "Y")
    prof = [(0.0, -0.15), (0.034, -0.15), (0.042, -0.135), (0.042, 0.135), (0.034, 0.15), (0.0, 0.15)]
    fin("PinBarrel", lathe_bm(prof, 12, matrix=m), WOOD, angle=55)
    prof = [(0.0, 0.14), (0.02, 0.14), (0.02, 0.19), (0.028, 0.205), (0.024, 0.235), (0.0, 0.24)]
    bm = lathe_bm(prof, 10, matrix=m)
    lathe_bm(prof, 10, bm=bm, matrix=m @ Matrix.Rotation(math.pi, 4, "X"))
    fin("PinHandles", bm, DARK, angle=55)


def bowl_prof(r, h, z, t=0.022):
    return [(0.0, z), (r * 0.5, z), (r * 0.6, z + 0.012), (r * 0.9, z + h * 0.42), (r, z + h * 0.82), (r + 0.004, z + h),
            (r - t * 0.5, z + h + 0.008), (r - t, z + h * 0.94), (r - t - 0.006, z + h * 0.8), (r * 0.82, z + h * 0.42),
            (0.0, z + h * 0.32)]


def build_bowls():
    x, y = 0.3, 0.02
    r, h = 0.215, 0.165
    fin("BigBowl", lathe_bm(bowl_prof(r, h, TOP_Z - 0.004), 20, matrix=Matrix.Translation((x, y, 0))), PAINT, angle=50)
    bm = ellipsoid_bm((x - 0.01, y, TOP_Z + h * 0.62), (0.175, 0.165, 0.095), 14, 7)
    ellipsoid_bm((x + 0.03, y - 0.02, TOP_Z + h * 0.95), (0.09, 0.085, 0.06), 10, 5, bm=bm)
    fin("Dough", bm, WOOD, angle=70)
    sp = [(x + 0.02, y + 0.04, TOP_Z + h * 0.8), (x + 0.11, y + 0.1, TOP_Z + h + 0.045), (x + 0.2, y + 0.15, TOP_Z + h + 0.09)]
    bm = tube_bm(sp, [0.02, 0.021, 0.023], 8)
    ellipsoid_bm(sp[-1], (0.032, 0.032, 0.032), 8, 5, bm=bm)
    fin("Spoon", bm, DARK, angle=60)
    x2, y2 = 0.61, -0.17
    r2, h2 = 0.13, 0.1
    fin("SmallBowl", lathe_bm(bowl_prof(r2, h2, TOP_Z - 0.004, 0.018), 18, matrix=Matrix.Translation((x2, y2, 0))),
        CERAMIC, angle=50)
    bm = bmesh.new()
    for dx, dy, dz, rz, rx in ((-0.03, 0.0, 0.08, 20, 70), (0.03, -0.015, 0.11, -35, 55), (0.0, 0.035, 0.135, 70, 30)):
        m = Matrix.Translation((x2 + dx, y2 + dy, TOP_Z + dz)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ \
            Matrix.Rotation(math.radians(rx), 4, "X")
        bone_bm(0.14, 0.033, 0.55, bm=bm, matrix=m, useg=8)
    fin("BowlCookies", bm, ACC, angle=60)


out, flags = cli()
begin()
build_cabinet()
build_board()
build_bowls()
ob = join_all("ShopKitchenCounter")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.25, -0.25, 0), dragon_rot=20.0, target=(-0.25, 0, 0.55), ortho=2.7)
