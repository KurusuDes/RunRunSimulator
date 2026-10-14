import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

S = 0.60
BASE_Z = 0.145
MAT_Z = BASE_Z + 0.018
COL_Y = 0.2
DIAL_Z = 0.93
DIAL_R = 0.17
DRUM_Y = 0.255


def face_m(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def paw_bm(s, bm):
    ellipsoid_bm((0, 0, -0.022 * s), (0.05 * s, 0.018, 0.042 * s), 12, 6, bm=bm)
    for ang, d, rr in ((-58, 0.064, 0.019), (-20, 0.072, 0.021), (20, 0.072, 0.021), (58, 0.064, 0.019)):
        a = math.radians(90 + ang)
        ellipsoid_bm((math.cos(a) * d * s, 0, 0.01 * s + math.sin(a) * d * s * 0.85),
                     (rr * s, 0.016, rr * 1.15 * s), 10, 5, bm=bm)
    return bm


def build_base():
    finish("Plinth", loft(rbox_rings(S, S, 0.075, 0.1, 0.03, seg=2, Rb=0.014, segb=2, z0=0.0), 3), "SH_Walnut", angle=50)
    finish("Deck", loft(rbox_rings(S - 0.05, S - 0.05, BASE_Z - 0.06, 0.08, 0.035, seg=3, z0=0.06), 3), "SH_Oak", angle=50)
    mat = loft(rbox_rings(0.44, 0.34, 0.03, 0.08, 0.014, seg=2, z0=BASE_Z - 0.012, cy=-0.07), 3)
    finish("Mat", mat, "SH_Sage", angle=55)
    bm = bmesh.new()
    before = set(bm.verts)
    paw_bm(1.35, bm)
    xf(bm, Matrix.Translation((0.0, -0.09, MAT_Z + 0.002)) @ Matrix.Rotation(math.radians(-90), 4, "X") @
       Matrix.Diagonal((1.0, 0.6, 1.0, 1.0)), [v for v in bm.verts if v not in before])
    finish("Paw", bm, "SH_White", angle=70)
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            ellipsoid_bm((sx * (S / 2 - 0.07), sy * (S / 2 - 0.07), 0.035), (0.06, 0.06, 0.035), 10, 4, bm=bm)
    finish("Feet", bm, "SH_Walnut", angle=70)


def build_column():
    z1 = DIAL_Z - DIAL_R - 0.02
    prof = [(0.0, BASE_Z - 0.01), (0.1, BASE_Z - 0.01), (0.11, BASE_Z + 0.015), (0.085, BASE_Z + 0.05), (0.064, BASE_Z + 0.1),
            (0.058, 0.45), (0.064, z1 - 0.07), (0.078, z1), (0.0, z1)]
    finish("Column", lathe_bm(prof, 14, matrix=Matrix.Translation((0, COL_Y, 0))), "SH_Walnut", angle=50)
    bm = bmesh.new()
    for z in (0.46,):
        lathe_bm([(0.0, z - 0.03), (0.074, z - 0.035), (0.085, z), (0.074, z + 0.035), (0.0, z + 0.03)], 14, bm=bm,
                 matrix=Matrix.Translation((0, COL_Y, 0)))
    finish("Collar", bm, "SH_Oak", angle=50)


def build_dial():
    R = DIAL_R
    prof = [(0.0, 0.0), (R + 0.035, 0.0), (R + 0.055, 0.025), (R + 0.058, 0.07), (R + 0.04, 0.105), (R + 0.01, 0.112),
            (0.0, 0.112)]
    m = face_m(0, DRUM_Y, DIAL_Z)
    finish("Drum", lathe_bm(prof, 32, matrix=m), "SH_Oak", angle=50)
    yf = DRUM_Y - 0.112
    torus = torus_bm(R + 0.018, 0.026, 32, 8, matrix=face_m(0, yf + 0.006, DIAL_Z))
    torus_bm(R + 0.02, 0.028, 32, 8, bm=torus, matrix=face_m(0, DRUM_Y + 0.004, DIAL_Z))
    finish("Bezel", torus, "SH_Walnut", angle=70)
    prof = [(0.0, 0.0), (R + 0.01, 0.0), (R + 0.01, 0.012), (0.0, 0.018)]
    finish("Face", lathe_bm(prof, 32, matrix=face_m(0, yf + 0.004, DIAL_Z)), "SH_White", angle=40)
    teal = bmesh.new()
    for k in range(12):
        if k == 0:
            continue
        a = math.pi / 2 - 2 * math.pi * k / 12
        big = k % 3 == 0
        rr = R * 0.8
        L = 0.045 if big else 0.028
        w = 0.022 if big else 0.016
        m = Matrix.Translation((math.cos(a) * rr, yf - 0.012, DIAL_Z + math.sin(a) * rr)) @ Matrix.Rotation(-a + math.pi / 2, 4, "Y")
        rbox_bm((0, 0, 0), (w, 0.016, L), w * 0.45, 1, bm=teal, matrix=m)
    cz = DIAL_Z + R * 0.78
    rbox_bm((0, yf - 0.014, cz), (0.022, 0.018, 0.064), 0.009, 1, bm=teal)
    rbox_bm((0, yf - 0.014, cz), (0.064, 0.018, 0.022), 0.009, 1, bm=teal)
    ellipsoid_bm((0, yf - 0.03, DIAL_Z), (0.034, 0.022, 0.034), 12, 6, bm=teal)
    finish("Ticks", teal, "SH_Teal", angle=60)
    a = math.radians(32)
    d = Vector((math.sin(a), 0, math.cos(a)))
    c = Vector((0, yf - 0.024, DIAL_Z))
    pts = [c - d * 0.03, c + d * 0.04, c + d * 0.09, c + d * R * 0.72]
    finish("Needle", tube_bm(pts, [0.016, 0.018, 0.014, 0.006], 6), "SH_Walnut", angle=60)
    bm = bmesh.new()
    ellipsoid_bm((0, DRUM_Y - 0.056, DIAL_Z + R + 0.07), (0.05, 0.05, 0.045), 12, 6, bm=bm)
    lathe_bm([(0.0, 0.0), (0.035, 0.0), (0.03, 0.03), (0.0, 0.03)], 10, bm=bm,
             matrix=Matrix.Translation((0, DRUM_Y - 0.056, DIAL_Z + R + 0.035)))
    finish("Finial", bm, "SH_Walnut", angle=60)


out, flags = cli()
begin()
build_base()
build_column()
build_dial()
ob = join_all("ShopScale")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.85, -0.3, 0), dragon_rot=25.0, target=(-0.25, 0.0, 0.6), ortho=2.3)
