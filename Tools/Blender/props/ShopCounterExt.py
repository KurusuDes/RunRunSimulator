import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

CW, CD, CH = 1.0, 0.8, 0.8
TOP_T = 0.075
BW, BD = 0.88, 0.66


def face_m(x, y, z, facing=-1):
    if facing < 0:
        return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
    return Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))


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


def paw_bm(cx, y, cz, s, bm=None):
    bm = bm or bmesh.new()
    ellipsoid_bm((cx, y, cz - 0.022 * s), (0.05 * s, 0.018, 0.04 * s), 12, 6, bm=bm)
    for ang, d, rr in ((-58, 0.062, 0.019), (-20, 0.07, 0.021), (20, 0.07, 0.021), (58, 0.062, 0.019)):
        a = math.radians(90 + ang)
        ellipsoid_bm((cx + math.cos(a) * d * s, y, cz + 0.01 * s + math.sin(a) * d * s * 0.85),
                     (rr * s, 0.016, rr * 1.15 * s), 10, 5, bm=bm)
    return bm


def build_counter():
    rings = rbox_rings(CW, CD, TOP_T, 0.09, 0.032, seg=3, Rb=0.02, segb=2, z0=CH - TOP_T)
    finish("Top", loft(rings, 3), "SH_WoodDark", angle=50)
    rings = rbox_rings(BW, BD, CH - TOP_T - 0.05 + 0.01, 0.06, 0.012, seg=1, z0=0.06)
    finish("Body", loft(rings, 3), "SH_Wood", angle=50)
    rings = rbox_rings(BW + 0.05, BD + 0.05, 0.085, 0.08, 0.025, seg=2, z0=0.0)
    finish("Plinth", loft(rings, 3), "SH_WoodDark", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (BW / 2 - 0.035), sy * (BD / 2 - 0.035)
            prof = [(0.0, 0.07), (0.058, 0.07), (0.058, CH - TOP_T + 0.005), (0.0, CH - TOP_T + 0.005)]
            lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((x, y, 0)))
    finish("Pilasters", bm, "SH_WoodDark", angle=50)
    yf = -BD / 2
    zc = 0.4
    pw, ph = 0.6, 0.46
    panel = rbox_rings(pw, ph, 0.03, 0.06, 0.014, seg=2)
    finish("FrontPanel", loft(panel, 3, cap0=False, matrix=face_m(0, yf + 0.008, zc)), "SH_Cream", angle=55)
    prof = [(0.0, 0.0), (0.13, 0.0), (0.135, 0.02), (0.128, 0.034), (0.11, 0.036), (0.1, 0.03), (0.0, 0.03)]
    finish("Coin", lathe_bm(prof, 20, matrix=face_m(0, yf - 0.018, zc)), "SH_Gold", angle=50)
    finish("Paw", paw_bm(0, yf - 0.05, zc, 1.25), "SH_Cream", angle=70)
    for sx in (-1, 1):
        side = rbox_rings(0.44, 0.46, 0.03, 0.06, 0.014, seg=2)
        m = Matrix.Translation((sx * (BW / 2 - 0.008), 0, zc)) @ Matrix.Rotation(sx * math.pi / 2, 4, "Y") @ \
            Matrix.Rotation(math.pi / 2, 4, "Z")
        finish("SidePanel", loft(side, 3, cap0=False, matrix=m), "SH_Cream", angle=55)
    bm = bmesh.new()
    for sx in (-1, 1):
        back = rbox_rings(0.285, ph, 0.03, 0.05, 0.014, seg=2)
        loft(back, 3, cap0=False, bm=bm, matrix=face_m(sx * 0.157, BD / 2 - 0.008, zc, facing=1))
    finish("BackDoors", bm, "SH_Cream", angle=55)
    prof = [(0.0, 0.0), (0.038, 0.0), (0.038, 0.02), (0.026, 0.034), (0.0, 0.036)]
    bm = bmesh.new()
    for sx in (-1, 1):
        lathe_bm(prof, 12, bm=bm, matrix=face_m(sx * 0.06, BD / 2 + 0.018, zc, facing=1))
    finish("BackKnobs", bm, "SH_Gold", angle=60)


def build_bell():
    x, y, z = -0.28, -0.18, CH - 0.004
    prof = [(0.0, 0.0), (0.085, 0.0), (0.088, 0.014), (0.079, 0.027), (0.0, 0.027)]
    finish("BellBase", lathe_bm(prof, 16, matrix=Matrix.Translation((x, y, z)) @ Matrix.Scale(1.25, 4)), "SH_WoodDark", angle=50)
    prof = [(0.0, 0.02), (0.07, 0.02), (0.072, 0.034), (0.064, 0.066), (0.046, 0.09), (0.022, 0.101), (0.0, 0.104)]
    finish("BellDome", lathe_bm(prof, 16, matrix=Matrix.Translation((x, y, z)) @ Matrix.Scale(1.25, 4)), "SH_Gold", angle=60)
    finish("BellNub", ellipsoid_bm((x, y, z + 0.141), (0.025, 0.025, 0.022), 8, 5), "SH_Cream", angle=80)


def coin_m(x, y, z, rx, ry):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rx), 4, "X") @ Matrix.Rotation(math.radians(ry), 4, "Y")


def build_jar():
    x, y, z = 0.2, 0.04, CH - 0.004
    J = Matrix.Translation((x, y, z)) @ Matrix.Scale(1.3, 4)
    prof = [(0.0, 0.0), (0.072, 0.0), (0.084, 0.012), (0.09, 0.04), (0.09, 0.125), (0.08, 0.148),
            (0.066, 0.158), (0.066, 0.17), (0.0, 0.17)]
    finish("Jar", lathe_bm(prof, 16, matrix=J), "SH_Glass", angle=60)
    finish("JarRim", lathe_bm([(0.074, 0.158), (0.079, 0.168), (0.079, 0.182), (0.07, 0.19), (0.062, 0.186),
                                (0.062, 0.162)], 16, matrix=J), "SH_WoodDark", angle=60)
    prof = [(0.093, 0.055), (0.095, 0.065), (0.095, 0.1), (0.093, 0.11)]
    finish("Label", lathe_bm(prof, 16, matrix=J), "SH_Cream", angle=60)
    bm = xf(star_bm(0, -0.094, 0.0825, 0.03, 0.014, 0.012), J)
    cp = [(0.0, -0.007), (0.036, -0.007), (0.038, 0.0), (0.036, 0.007), (0.0, 0.007)]
    for cx, cy, cz, rx, ry in ((0.0, 0.0, 0.012, 8, 0), (-0.03, 0.02, 0.02, -14, 18), (0.032, 0.012, 0.022, 10, -22),
                               (0.008, -0.03, 0.03, 32, 6), (0.0, 0.006, 0.05, -18, 52)):
        lathe_bm(cp, 14, bm=bm, matrix=J @ coin_m(cx, cy, 0.172 + cz, rx, ry))
    for cx, cy, rz in ((-0.17, -0.18, 0.0), (-0.17, -0.18, 0.014), (-0.165, -0.177, 0.028), (-0.105, -0.2, 0.0)):
        lathe_bm([(0.0, 0.0), (0.034, 0.0), (0.036, 0.007), (0.034, 0.014), (0.0, 0.014)], 14, bm=bm,
                 matrix=Matrix.Translation((x + cx, y + cy, z + rz)))
    finish("Coins", bm, "SH_Gold", angle=55)

out, flags = cli()
begin()
build_counter()
build_bell()
build_jar()
ob = join_all("ShopCounterExt")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(1.3, -0.35, 0))
