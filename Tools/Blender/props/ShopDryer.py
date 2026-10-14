import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


def front_matrix(x, y, z, rz=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ M


def fin(name, bm, mat, angle=50.0, recalc=True):
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def offset2d(pts, d):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        t = (p2 - p0).normalized()
        nin = Vector((-t.y, t.x)) * s
        out.append((p1.x + nin.x * d, p1.y + nin.y * d))
    return out


def badge_bm(outline, t, bev, steps=2, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = [(0.0, 0.0), (0.0, t - bev)]
    for j in range(1, steps + 1):
        a = math.pi / 2 * j / steps
        rings.append((bev * (1 - math.cos(a)), t - bev + bev * math.sin(a)))
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    vr = []
    for d, z in rings:
        vr.append([bm.verts.new((x, y, z)) for x, y in offset2d(outline, d)])
    n = len(outline)
    for A, B in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    c0 = bm.verts.new((cx, cy, 0.0))
    c1 = bm.verts.new((cx, cy, t))
    for k in range(n):
        bm.faces.new((vr[0][(k + 1) % n], vr[0][k], c0))
        bm.faces.new((vr[-1][k], vr[-1][(k + 1) % n], c1))
    if matrix is not None:
        xf(bm, matrix, [v for r in vr for v in r] + [c0, c1])
    return bm


def drop_outline(size, n=24):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 0.86 * math.sin(t) * math.sin(t / 2) ** 0.8
        y = math.cos(t)
        pts.append((x * size / 2.0, y * size / 2.0))
    return pts


def orient_radial(bm, outward=True):
    for f in bm.faces:
        f.normal_update()
    score = 0.0
    for f in bm.faces:
        c = f.calc_center_median()
        score += f.normal.dot(Vector((c.x, c.y, 0.0)))
    if (score > 0) != outward:
        for f in bm.faces:
            f.normal_flip()
    return bm


ACC = "SH_Teal"
TILT = -36.0
PY = 0.18
HOOD = (Matrix.Translation((0.0, -0.06, 1.02)) @ Matrix.Rotation(math.radians(TILT), 4, "X")
        @ Matrix.Diagonal((1.0, 1.0, 1.18, 1.0)))


def build_base():
    prof = [(0.0, 0.03), (0.25, 0.03), (0.282, 0.045), (0.292, 0.07), (0.282, 0.095), (0.24, 0.115), (0.12, 0.125),
            (0.0, 0.128)]
    fin("Base", lathe_bm(prof, 28), "SH_Oak", angle=50)
    fin("BaseBand", torus_bm(0.284, 0.022, 28, 5, matrix=Matrix.Translation((0, 0, 0.07))), ACC, angle=80)
    bm = bmesh.new()
    for k in range(5):
        a = math.radians(90 + 72 * k)
        ellipsoid_bm((0.2 * math.cos(a), 0.2 * math.sin(a), 0.035), (0.045, 0.045, 0.035), 10, 5, bm=bm)
    fin("Feet", bm, "SH_Gold", angle=80)


def build_pole():
    prof = [(0.0, 0.11), (0.06, 0.11), (0.046, 0.16), (0.04, 0.5), (0.04, 0.82), (0.0, 0.82)]
    fin("Pole", lathe_bm(prof, 14, matrix=Matrix.Translation((0, PY, 0))), "SH_Oak", angle=50)
    bm = lathe_bm([(0.0, 0.12), (0.085, 0.12), (0.095, 0.14), (0.08, 0.165), (0.05, 0.18), (0.0, 0.18)], 18)
    lathe_bm([(0.0, 0.5), (0.055, 0.5), (0.062, 0.52), (0.062, 0.56), (0.055, 0.58), (0.0, 0.58)], 16, bm=bm)
    lathe_bm([(0.0, 0.79), (0.058, 0.79), (0.066, 0.815), (0.058, 0.845), (0.0, 0.85)], 16, bm=bm)
    fin("Collars", xf(bm, Matrix.Translation((0, PY, 0))), "SH_Gold", angle=60)
    m = Matrix.Translation((0.06, 0, 0.54)) @ Matrix.Rotation(math.radians(90), 4, "Y")
    bm = lathe_bm([(0.0, 0.0), (0.02, 0.0), (0.02, 0.03), (0.0, 0.03)], 8, matrix=m)
    ellipsoid_bm((0.112, 0, 0.54), (0.032, 0.04, 0.04), 10, 5, bm=bm)
    fin("TightKnob", xf(bm, Matrix.Translation((0, PY, 0))), "SH_White", angle=70)


def hood_pt(x, y, z):
    return HOOD @ Vector((x, y, z))


def build_hood():
    prof = [(0.255, 0.0), (0.268, 0.05), (0.27, 0.13), (0.252, 0.2), (0.205, 0.26), (0.13, 0.298), (0.05, 0.31),
            (0.0, 0.312)]
    bm = orient_radial(lathe_bm(prof, 28), True)
    fin("Hood", xf(bm, HOOD), ACC, angle=50, recalc=False)
    prof = [(0.0, 0.25), (0.1, 0.24), (0.17, 0.2), (0.215, 0.12), (0.23, 0.0)]
    bm = orient_radial(lathe_bm(prof, 28), False)
    fin("HoodInner", xf(bm, HOOD), "SH_White", angle=60, recalc=False)
    fin("HoodRim", torus_bm(0.245, 0.042, 28, 6, matrix=HOOD), "SH_White", angle=80)
    fin("HoodBand", torus_bm(0.27, 0.02, 28, 5, matrix=HOOD @ Matrix.Translation((0, 0, 0.135))), "SH_Gold", angle=80)
    bm = lathe_bm([(0.0, 0.29), (0.06, 0.29), (0.07, 0.31), (0.055, 0.34), (0.0, 0.345)], 14)
    ellipsoid_bm((0, 0, 0.375), (0.05, 0.05, 0.045), 12, 6, bm=bm)
    fin("HoodCap", xf(bm, HOOD), "SH_Gold", angle=60)
    bm = bmesh.new()
    for k in range(6):
        a = math.radians(30 + 60 * k)
        r = 0.16
        z = 0.268
        rot = Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((r, 0, z)) @ Matrix.Rotation(math.radians(38), 4, "Y")
        rbox_bm((0, 0, 0), (0.1, 0.045, 0.034), 0.016, 2, bm=bm, matrix=rot)
    fin("Vents", xf(bm, HOOD), "SH_White", angle=60)
    m = HOOD @ front_matrix(0, -0.258, 0.13)
    fin("Drop", badge_bm(drop_outline(0.13), 0.035, 0.014, 2, matrix=m), "SH_White", angle=60)
    m = HOOD @ Matrix.Translation((0.262, 0, 0.12)) @ Matrix.Rotation(math.radians(90), 4, "Y")
    bm = lathe_bm([(0.0, -0.01), (0.07, -0.01), (0.075, 0.012), (0.065, 0.025), (0.0, 0.027)], 18, matrix=m)
    fin("Dial", bm, "SH_White", angle=60)
    bm = lathe_bm([(0.0, 0.02), (0.032, 0.02), (0.035, 0.045), (0.025, 0.06), (0.0, 0.062)], 12, matrix=m)
    rbox_bm((0, 0.045, 0.035), (0.022, 0.05, 0.02), 0.009, 1, bm=bm, matrix=m)
    fin("DialKnob", bm, "SH_Gold", angle=60)


def build_arm():
    back = hood_pt(0, 0.262, 0.1)
    ctrl = [(0, PY, 0.82), (0, PY + 0.02, 0.9), (0, back.y + 0.07, back.z - 0.04), (back.x, back.y - 0.03, back.z)]
    pts = catmull(ctrl, 3)
    fin("Arm", tube_bm(pts, [0.036] * len(pts), 8), "SH_Gold", angle=60)
    fin("ArmJoint", ellipsoid_bm((back.x, back.y + 0.025, back.z), (0.055, 0.05, 0.055), 12, 6), "SH_Gold", angle=70)


out, flags = cli()
begin()
build_base()
build_pole()
build_hood()
build_arm()
ob = join_all("ShopDryer")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.95, -0.2, 0), target=(-0.35, 0.0, 0.7), ortho=2.6)
