import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

TW, TD = 1.40, 0.70
LEG_X, LEG_Y = 0.60, 0.25
LEG_TOP = 0.46
APRON_Z0, APRON_Z1 = 0.42, 0.62
RIM_Z0, RIM_Z1 = 0.595, 0.645
CUSH_Z0, CUSH_Z1 = 0.632, 0.745
SHELF_Z = 0.16


def face_m(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def pillow_bm(center, radii, p=0.45, useg=16, vseg=9, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg, radius=1.0)
    for v in [v for v in bm.verts if v not in before]:
        c = [math.copysign(abs(v.co[i]) ** p, v.co[i]) for i in range(3)]
        v.co = Vector((c[0] * radii[0], c[1] * radii[1], c[2] * radii[2])) + Vector(center)
    return bm


def cross_badge(x, y, z, R, mat_disc, mat_rim, mat_cross):
    prof = [(0.0, 0.0), (R + 0.012, 0.0), (R + 0.016, 0.014), (R + 0.008, 0.028), (R, 0.026), (0.0, 0.026)]
    finish("BadgeRim", lathe_bm(prof, 24, matrix=face_m(x, y, z)), mat_rim, angle=55)
    prof = [(0.0, 0.0), (R - 0.004, 0.0), (R - 0.004, 0.03), (R - 0.016, 0.036), (0.0, 0.036)]
    finish("BadgeDisc", lathe_bm(prof, 24, matrix=face_m(x, y - 0.002, z)), mat_disc, angle=55)
    a, b = R * 1.25, R * 0.42
    bm = bmesh.new()
    rbox_bm((x, y - 0.046, z), (b, 0.03, a), 0.012, 2, bm=bm)
    rbox_bm((x, y - 0.046, z), (a, 0.03, b), 0.012, 2, bm=bm)
    finish("Cross", bm, mat_cross, angle=55)


def build_legs():
    prof = [(0.0, 0.0), (0.06, 0.0), (0.072, 0.03), (0.066, 0.065), (0.046, 0.11), (0.044, 0.16), (0.056, 0.24),
            (0.06, 0.3), (0.05, 0.37), (0.05, LEG_TOP), (0.0, LEG_TOP)]
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            lathe_bm(prof, 12, bm=bm, matrix=Matrix.Translation((sx * LEG_X, sy * LEG_Y, 0)))
    finish("Legs", bm, "SH_Walnut", angle=55)


def build_shelf():
    rings = rbox_rings(2 * LEG_X + 0.04, 2 * LEG_Y + 0.04, 0.05, 0.05, 0.02, seg=2, Rb=0.012, z0=SHELF_Z - 0.025)
    finish("Shelf", loft(rings, 3), "SH_Oak", angle=50)
    bm = bmesh.new()
    for x, y, r, L in ((-0.3, -0.08, 0.07, 0.36), (-0.3, 0.08, 0.07, 0.36)):
        prof = [(0.0, -L / 2), (r - 0.02, -L / 2), (r, -L / 2 + 0.02), (r, L / 2 - 0.02), (r - 0.02, L / 2), (0.0, L / 2)]
        m = Matrix.Translation((x, y, SHELF_Z + 0.025 + r - 0.006)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
        lathe_bm(prof, 14, bm=bm, matrix=m)
    r = 0.07
    prof = [(0.0, -0.2), (r - 0.02, -0.2), (r, -0.18), (r, 0.18), (r - 0.02, 0.2), (0.0, 0.2)]
    m = Matrix.Translation((-0.3, 0.0, SHELF_Z + 0.025 + 2 * r + r - 0.025)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
    lathe_bm(prof, 14, bm=bm, matrix=m)
    finish("Towels", bm, "SH_White", angle=60)
    bm = bmesh.new()
    for y, dz in ((-0.08, 0.0), (0.08, 0.0), (0.0, 0.121)):
        zc = SHELF_Z + 0.025 + 0.064 + dz
        prof = [(0.0, -0.035), (0.075, -0.035), (0.075, 0.035), (0.0, 0.035)]
        m = Matrix.Translation((-0.3, y, zc)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
        lathe_bm(prof, 14, bm=bm, matrix=m)
    finish("TowelBands", bm, "SH_Sage", angle=60)
    bx, by = 0.3, 0.0
    bm = bmesh.new()
    rbox_bm((bx, by, SHELF_Z + 0.025 + 0.09), (0.3, 0.26, 0.18), 0.04, 2, bm=bm)
    finish("Kit", bm, "SH_White", angle=50)
    bm = bmesh.new()
    rbox_bm((bx, by, SHELF_Z + 0.025 + 0.15), (0.31, 0.27, 0.05), 0.022, 2, bm=bm)
    a = 0.1
    rbox_bm((bx, by - 0.135, SHELF_Z + 0.025 + 0.075), (0.032, 0.02, a), 0.009, 1, bm=bm)
    rbox_bm((bx, by - 0.135, SHELF_Z + 0.025 + 0.075), (a, 0.02, 0.032), 0.009, 1, bm=bm)
    tube_bm([(bx - 0.06, by, SHELF_Z + 0.025 + 0.172), (bx - 0.05, by, SHELF_Z + 0.025 + 0.23),
             (bx, by, SHELF_Z + 0.025 + 0.25), (bx + 0.05, by, SHELF_Z + 0.025 + 0.23),
             (bx + 0.06, by, SHELF_Z + 0.025 + 0.172)], 0.016, 6, bm=bm)
    finish("KitLid", bm, "SH_Teal", angle=50)


def build_body():
    rings = rbox_rings(TW - 0.08, TD - 0.08, APRON_Z1 - APRON_Z0, 0.06, 0.012, seg=1, z0=APRON_Z0)
    finish("Apron", loft(rings, 3), "SH_Oak", angle=50)
    rings = rbox_rings(TW, TD, RIM_Z1 - RIM_Z0, 0.09, 0.022, seg=2, Rb=0.018, segb=2, z0=RIM_Z0)
    finish("Rim", loft(rings, 3), "SH_Walnut", angle=50)
    bm = bmesh.new()
    rings = rbox_rings(TW - 0.04, TD - 0.04, 0.035, 0.08, 0.012, seg=1, Rb=0.012, z0=APRON_Z0 - 0.02)
    loft(rings, 3, bm=bm)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ellipsoid_bm((sx * LEG_X, sy * LEG_Y, LEG_TOP + 0.03), (0.075, 0.075, 0.06), 10, 5, bm=bm)
    finish("Corners", bm, "SH_Walnut", angle=55)
    cross_badge(0.0, -(TD - 0.08) / 2 - 0.004, (APRON_Z0 + APRON_Z1) / 2 - 0.005, 0.082, "SH_White", "SH_Walnut", "SH_Teal")


def build_cushion():
    bm = bmesh.new()
    loft(rbox_rings(TW - 0.06, TD - 0.06, CUSH_Z1 - CUSH_Z0, 0.11, 0.055, seg=4, Rb=0.03, segb=2, z0=CUSH_Z0), 4, bm=bm)
    finish("Cushion", bm, "SH_Sage", angle=70)
    bm = bmesh.new()
    for x in (-0.14, 0.14, 0.42):
        for y in (-0.15, 0.15):
            ellipsoid_bm((x, y, CUSH_Z1 - 0.004), (0.036, 0.036, 0.02), 10, 5, bm=bm)
    finish("Tufts", bm, "SH_Teal", angle=80)
    finish("Pillow", pillow_bm((-0.47, 0.0, CUSH_Z1 + 0.035), (0.17, 0.26, 0.058), p=0.42), "SH_White", angle=80)


out, flags = cli()
begin()
build_legs()
build_shelf()
build_body()
build_cushion()
ob = join_all("ShopExamTable")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.25, -0.35, 0), dragon_rot=25.0, target=(-0.3, 0.0, 0.42), ortho=3.0)
