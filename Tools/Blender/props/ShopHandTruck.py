import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

WHEEL_R = 0.145
WHEEL_Y = 0.16
WHEEL_X = 0.235
RAIL_X = 0.165
RAIL_B = (0.07, 0.07)
RAIL_T = (0.2, 1.08)
PLATE_Z = 0.038
SACK_W = 0.36
SACK_D = 0.28
SACK_H = 0.6
SACK_Y = -0.08
SACK_TILT = 5.0


def fin(name, bm, mat, angle=50.0, smooth=True):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, smooth=smooth, angle=angle)


def paw_bm(M, s, t=0.014, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    ellipsoid_bm((0.0, -0.28 * s, 0.0), (0.62 * s, 0.5 * s, t), useg=10, vseg=4, bm=bm)
    for a, rr, k in ((-62, 0.92, 0.9), (-21, 1.0, 1.0), (21, 1.0, 1.0), (62, 0.92, 0.9)):
        ra = math.radians(a)
        ellipsoid_bm((rr * s * math.sin(ra), -0.28 * s + rr * s * math.cos(ra) + 0.12 * s, 0.0),
                     (0.24 * s * k, 0.28 * s * k, t), useg=8, vseg=4, bm=bm)
    xf(bm, M, [v for v in bm.verts if v not in before])
    return bm


FRONT = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def z_stack(rings, m=3, rf=0.4, bm=None, matrix=None):
    bm = bm or bmesh.new()
    vr = []
    for z, w, d, wav in rings:
        pts = rrect(w, d, min(w, d) * rf, m)
        n = len(pts)
        ring = []
        for k, (px, py) in enumerate(pts):
            s = 1.0 + wav * math.sin(2 * math.pi * k * 3 / n)
            ring.append(bm.verts.new((px * s, py * s, z)))
        vr.append(ring)
    n = len(vr[0])
    for A, B in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    bm.faces.new(list(reversed(vr[0])))
    bm.faces.new(vr[-1])
    if matrix is not None:
        xf(bm, matrix, [v for r in vr for v in r])
    return bm


def standing_sack(W, D, H):
    body = [(0.0, 0.9, 0.86), (0.03, 1.0, 0.96), (0.12, 1.07, 1.04), (0.3, 1.07, 1.02), (0.5, 1.03, 0.96),
            (0.66, 0.97, 0.84), (0.77, 0.82, 0.62)]
    rings = [(H * f, W * sw, D * sd, 0.0) for f, sw, sd in body]
    zn = H * 0.855
    nw = 0.15
    rings += [(zn, nw, nw, 0.0), (zn + 0.03, 0.22, 0.2, 0.14), (zn + 0.075, 0.31, 0.27, 0.2),
              (zn + 0.105, 0.27, 0.24, 0.2), (zn + 0.118, 0.12, 0.11, 0.1)]
    return z_stack(rings, rf=0.36), (zn, nw / 2)


def sack_matrix():
    return Matrix.Translation((0, SACK_Y, PLATE_Z - 0.004)) @ Matrix.Rotation(math.radians(-SACK_TILT), 4, "X")


def build_sack():
    bm, (zn, nr) = standing_sack(SACK_W, SACK_D, SACK_H)
    M = sack_matrix()
    xf(bm, M)
    fin("Sack", bm, "SH_Beige", angle=None)
    tie = torus_bm(nr + 0.008, 0.024, 14, 5, matrix=M @ Matrix.Translation((0, 0, zn + 0.004)))
    before = set(tie.verts)
    for s in (1, -1):
        p0 = Vector((s * 0.025, -nr - 0.012, zn))
        tube_bm([p0, p0 + Vector((s * 0.03, -0.03, -0.035)), p0 + Vector((s * 0.05, -0.05, -0.06))],
                [0.017, 0.016, 0.014], 5, bm=tie)
        ellipsoid_bm((s * 0.055, -nr - 0.065, zn - 0.07), (0.028, 0.028, 0.032), 8, 4, bm=tie)
    xf(tie, M, [v for v in tie.verts if v not in before])
    fin("SackTie", tie, "SH_Gold", angle=70)
    zc = SACK_H * 0.36
    yf = -SACK_D / 2 * 1.035 + 0.002
    fin("SackPaw", paw_bm(M @ Matrix.Translation((0, yf, zc)) @ FRONT, 0.078, 0.02), "SH_Walnut", angle=None)


def rail_points(s):
    b = Vector((s * RAIL_X, RAIL_B[0], RAIL_B[1]))
    t = Vector((s * RAIL_X, RAIL_T[0], RAIL_T[1]))
    return b, t


def build_frame():
    bm = bmesh.new()
    for s in (1, -1):
        b, t = rail_points(s)
        d = t - b
        L = d.length
        ang = math.atan2(d.y, d.z)
        M = Matrix.Translation((b + t) / 2) @ Matrix.Rotation(-ang, 4, "X")
        rbox_bm((0, 0, 0), (0.075, 0.072, L), 0.026, 2, bm=bm, matrix=M)
    fin("Rails", bm, "SH_Honey", angle=50)

    bm = bmesh.new()
    for f in (0.36, 0.7):
        b, t = rail_points(1)
        p = b.lerp(t, f)
        rbox_bm((0, p.y + 0.005, p.z), (2 * RAIL_X + 0.03, 0.06, 0.07), 0.024, 2, bm=bm)
    pts = []
    for k in range(9):
        a = math.pi * k / 8
        pts.append((-RAIL_X * math.cos(a), RAIL_T[0] + 0.01 + 0.015 * math.sin(a), RAIL_T[1] - 0.04 + 0.13 * math.sin(a)))
    tube_bm(pts, 0.036, 8, bm=bm)
    for s in (1, -1):
        rbox_bm((s * RAIL_X, WHEEL_Y - 0.03, WHEEL_R + 0.005), (0.075, 0.13, 0.11), 0.03, 2, bm=bm)
    tube_bm([(-WHEEL_X + 0.03, WHEEL_Y, WHEEL_R), (WHEEL_X - 0.03, WHEEL_Y, WHEEL_R)], 0.026, 8, bm=bm)
    fin("Bars", bm, "SH_Walnut", angle=50)

    bm = bmesh.new()
    gp = [p for p in pts[2:7]]
    tube_bm(gp, 0.045, 8, bm=bm)
    for s in (1, -1):
        for f in (0.36, 0.7):
            b, t = rail_points(s)
            p = b.lerp(t, f)
            lathe_bm([(0.0, 0.0), (0.02, 0.0), (0.02, 0.006), (0.013, 0.016), (0.0, 0.019)], 8, bm=bm,
                     matrix=Matrix.Translation((s * RAIL_X, p.y - 0.022, p.z)) @ FRONT)
    fin("Grip", bm, "SH_Gold", angle=60)


def build_plate():
    bm = bmesh.new()
    loft(rbox_rings(0.46, 0.36, PLATE_Z, 0.06, 0.014, seg=2, Rb=0.006, cy=-0.09), 3, bm=bm)
    rbox_bm((0, -0.265, 0.045), (0.46, 0.04, 0.08), 0.018, 2, bm=bm)
    rbox_bm((0, 0.075, 0.06), (2 * RAIL_X + 0.06, 0.06, 0.11), 0.022, 2, bm=bm)
    fin("Plate", bm, "SH_Gold", angle=45)


def build_wheels():
    tire = bmesh.new()
    disc = bmesh.new()
    hub = bmesh.new()
    for s in (1, -1):
        M = Matrix.Translation((s * WHEEL_X, WHEEL_Y, WHEEL_R)) @ Matrix.Rotation(math.radians(90 * s), 4, "Y")
        lathe_bm([(0.1, -0.036), (0.128, -0.04), (WHEEL_R, -0.018), (WHEEL_R, 0.018), (0.128, 0.04), (0.1, 0.036)], 20,
                 bm=tire, matrix=M)
        lathe_bm([(0.0, -0.026), (0.108, -0.026), (0.108, 0.026), (0.0, 0.028)], 20, bm=disc, matrix=M)
        lathe_bm([(0.0, 0.02), (0.05, 0.02), (0.05, 0.034), (0.036, 0.055), (0.0, 0.062)], 12, bm=hub, matrix=M)
        for k in range(5):
            a = 2 * math.pi * k / 5
            lathe_bm([(0.0, 0.02), (0.014, 0.02), (0.014, 0.03), (0.0, 0.036)], 6, bm=hub,
                     matrix=M @ Matrix.Translation((0.078 * math.cos(a), 0.078 * math.sin(a), 0.0)))
    fin("Tires", tire, "SH_Walnut", angle=40)
    fin("Discs", disc, "SH_Honey", angle=50)
    fin("Hubs", hub, "SH_Gold", angle=60)


out, flags = cli()
begin()
build_plate()
build_frame()
build_wheels()
build_sack()
ob = join_all("ShopHandTruck")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.95, 0.35, 0), target=(-0.35, 0.0, 0.6), ortho=2.4)
