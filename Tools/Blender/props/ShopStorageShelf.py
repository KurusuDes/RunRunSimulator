import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

W = 2.0
D = 0.6
POST = 0.09
PX = W / 2 - POST / 2
PY = D / 2 - POST / 2
DECKS = (0.13, 0.75, 1.35, 1.9)
BOARD_T = 0.05
BW = W - 0.12
BD = 0.52
LIP_Y = -0.272
TOP = 1.955

FRONT = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def fin(name, bm, mat, angle=50.0, smooth=True):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, smooth=smooth, angle=angle)


def paw_bm(M, s, t=0.014, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    ellipsoid_bm((0.0, -0.28 * s, 0.0), (0.62 * s, 0.5 * s, t), useg=9, vseg=3, bm=bm)
    for a, rr, k in ((-62, 0.92, 0.9), (-21, 1.0, 1.0), (21, 1.0, 1.0), (62, 0.92, 0.9)):
        ra = math.radians(a)
        ellipsoid_bm((rr * s * math.sin(ra), -0.28 * s + rr * s * math.cos(ra) + 0.12 * s, 0.0),
                     (0.24 * s * k, 0.28 * s * k, t), useg=6, vseg=3, bm=bm)
    xf(bm, M, [v for v in bm.verts if v not in before])
    return bm


def stack(rings, axis, m=2, rf=0.42, bm=None, matrix=None):
    bm = bm or bmesh.new()
    vr = []
    for t, a, b, c, wav in rings:
        pts = rrect(a, b, min(a, b) * rf, m)
        n = len(pts)
        ring = []
        for k, (u, v) in enumerate(pts):
            s = 1.0 + wav * math.sin(2 * math.pi * k * 3 / n)
            if axis == "Z":
                ring.append(bm.verts.new((u * s, v * s, t)))
            else:
                ring.append(bm.verts.new((t, u * s, c + v * s)))
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


def standing_sack(Ws, Ds, H, M, bm, ties, wav=0.2):
    body = [(0.0, 0.9, 0.86), (0.03, 1.0, 0.96), (0.12, 1.07, 1.04), (0.3, 1.07, 1.02), (0.5, 1.03, 0.96),
            (0.66, 0.97, 0.84), (0.77, 0.82, 0.62)]
    rings = [(H * f, Ws * sw, Ds * sd, 0.0, 0.0) for f, sw, sd in body]
    zn = H * 0.84
    nw = 0.13
    rings += [(zn, nw, nw, 0.0, 0.0), (zn + 0.025, 0.19, 0.17, 0.0, 0.14), (zn + 0.06, 0.26, 0.23, 0.0, wav),
              (zn + 0.085, 0.22, 0.2, 0.0, wav), (zn + 0.095, 0.1, 0.09, 0.0, 0.1)]
    stack(rings, "Z", rf=0.38, bm=bm, matrix=M)
    torus_bm(nw / 2 + 0.008, 0.022, 10, 4, bm=ties, matrix=M @ Matrix.Translation((0, 0, zn + 0.004)))


def lying_sack(L, Ws, H, tied, M, bm, ties):
    body = [(0.0, 0.94, 0.14), (0.04, 0.95, 0.5), (0.11, 0.98, 0.8), (0.24, 1.0, 0.95), (0.4, 1.0, 1.0),
            (0.6, 1.0, 1.0), (0.76, 1.0, 0.95)]
    body += [(0.87, 0.93, 0.82), (0.95, 0.42, 0.46)] if tied else [(0.89, 0.98, 0.8), (0.96, 0.95, 0.5), (1.0, 0.94, 0.14)]
    rings = []
    for f, sw, sh in body:
        h = H * sh
        rings.append((-L / 2 + f * L, Ws * sw, h, 0.5 * h + 0.32 * H * (1 - sh), 0.0))
    if tied:
        zc = rings[-1][3] + 0.01
        x0 = rings[-1][0]
        nw = 0.12
        rings += [(x0 + 0.035, nw, nw, zc, 0.0), (x0 + 0.06, 0.18, 0.17, zc + 0.005, 0.14),
                  (x0 + 0.1, 0.25, 0.23, zc + 0.01, 0.2), (x0 + 0.122, 0.21, 0.19, zc + 0.01, 0.2),
                  (x0 + 0.132, 0.09, 0.085, zc + 0.01, 0.1)]
        torus_bm(nw / 2 + 0.008, 0.022, 10, 4, bm=ties,
                 matrix=M @ Matrix.Translation((x0 + 0.035, 0, zc)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
    stack(rings, "X", rf=0.46, bm=bm, matrix=M)


def crate(loc, w, d, h, rz, body, frame, studs=None):
    M = Matrix.Translation(loc) @ Matrix.Rotation(math.radians(rz), 4, "Z")
    b0 = len(body.verts)
    rbox_bm((0, 0, h / 2), (w, d, h), 0.025, 2, bm=body)
    xf(body, M, list(body.verts)[b0:])
    b0 = len(frame.verts)
    for sy in (-1,):
        y = sy * (d / 2 + 0.004)
        rbox_bm((0, y, 0.03), (w + 0.012, 0.03, 0.06), 0.012, 1, bm=frame)
        rbox_bm((0, y, h - 0.03), (w + 0.012, 0.03, 0.06), 0.012, 1, bm=frame)
        dl = math.hypot(w - 0.09, h - 0.1)
        ang = math.atan2(h - 0.1, w - 0.09)
        rbox_bm((0, 0, 0), (dl, 0.026, 0.05), 0.01, 1, bm=frame,
                matrix=Matrix.Translation((0, y, h / 2)) @ Matrix.Rotation(sy * ang, 4, "Y"))
    xf(frame, M, list(frame.verts)[b0:])
    if studs is not None:
        s0 = len(studs.verts)
        for sx in (-1, 1):
            for z in (0.03, h - 0.03):
                lathe_bm([(0.0, 0.0), (0.018, 0.0), (0.018, 0.006), (0.011, 0.015), (0.0, 0.017)], 6, bm=studs,
                         matrix=Matrix.Translation((sx * (w / 2 - 0.035), -d / 2 - 0.02, z)) @ FRONT)
        xf(studs, M, list(studs.verts)[s0:])
    return M


def build_frame():
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            rbox_bm((sx * PX, sy * PY, TOP / 2), (POST, POST, TOP), 0.028, 2, bm=bm)
        for z in DECKS[:3]:
            rbox_bm((sx * PX, 0, z - 0.035), (0.07, D - 0.1, 0.06), 0.02, 1, bm=bm)
    for i, z in enumerate(DECKS):
        lh = 0.13 if i == 3 else 0.085
        rbox_bm((0, LIP_Y, z - lh / 2 + 0.015), (BW, 0.05, lh), 0.022, 1, bm=bm)
    fin("Frame", bm, "SH_Walnut", angle=45)

    bm = bmesh.new()
    for z in DECKS:
        rbox_bm((0, -0.01, z - BOARD_T / 2), (BW + 0.02, BD, BOARD_T), 0.018, 1, bm=bm)
    n = 7
    pw = (BW - 0.02) / n
    for i in range(n):
        x = -BW / 2 + 0.01 + pw * (i + 0.5)
        rbox_bm((x, 0.235, (DECKS[0] + DECKS[3]) / 2), (pw - 0.012, 0.04, DECKS[3] - DECKS[0]), 0.012, 1, bm=bm)
    fin("Boards", bm, "SH_Oak", angle=45)

    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((sx * PX, -PY * 0 - PY, TOP + 0.01), (0.048, 0.048, 0.045), 8, 4, bm=bm)
        ellipsoid_bm((sx * PX, PY, TOP + 0.01), (0.048, 0.048, 0.045), 8, 4, bm=bm)
        for z in DECKS[:3]:
            rbox_bm((sx * PX, -PY - POST / 2 - 0.006, z - 0.03), (0.075, 0.025, 0.11), 0.01, 1, bm=bm)
    zc = DECKS[3] - 0.035
    lathe_bm([(0.0, 0.0), (0.11, 0.0), (0.115, 0.01), (0.105, 0.02), (0.0, 0.022)], 16, bm=bm,
             matrix=Matrix.Translation((0, LIP_Y - 0.022, zc)) @ FRONT)
    fin("Gold", bm, "SH_Gold", angle=60)
    return zc


def build_contents(medal_z):
    sacks = bmesh.new()
    ties = bmesh.new()
    paws = bmesh.new()
    cbody = bmesh.new()
    cframe = bmesh.new()

    d0 = DECKS[0]
    M = Matrix.Translation((-0.46, -0.02, d0 - 0.004)) @ Matrix.Rotation(math.radians(2), 4, "Z")
    lying_sack(0.8, 0.44, 0.25, False, M, sacks, ties)
    M = Matrix.Translation((-0.52, -0.04, d0 + 0.2)) @ Matrix.Rotation(math.radians(-4), 4, "Z")
    lying_sack(0.66, 0.42, 0.23, True, M, sacks, ties)
    paw_bm(Matrix.Translation((-0.6, -0.05, d0 + 0.2 + 0.23 + 0.004)) @ Matrix.Rotation(math.radians(8), 4, "X"), 0.075, 0.022, bm=paws)
    crate((0.47, 0.0, d0 - 0.004), 0.62, 0.44, 0.47, -3, cbody, cframe)

    d1 = DECKS[1]
    for x, rz, paw in ((-0.72, 7, False), (-0.38, -5, True), (0.7, 4, True)):
        M = Matrix.Translation((x, -0.02, d1 - 0.004)) @ Matrix.Rotation(math.radians(rz), 4, "Z")
        standing_sack(0.3, 0.26, 0.44, M, sacks, ties)
        if paw:
            paw_bm(M @ Matrix.Translation((0, -0.26 / 2 * 1.035 + 0.002, 0.44 * 0.36)) @ FRONT, 0.068, 0.02, bm=paws)
    for loc, w, d, h, rz in (((0.16, 0.0, d1 - 0.004), 0.42, 0.4, 0.27, 2), ((0.18, -0.01, d1 + 0.262), 0.34, 0.32, 0.22, 11)):
        crate(loc, w, d, h, rz, cbody, cframe)

    d2 = DECKS[2]
    for loc, w, d, h, rz in (((-0.64, 0.0, d2 - 0.004), 0.44, 0.38, 0.32, -4), ((0.66, 0.0, d2 - 0.004), 0.38, 0.36, 0.28, 6)):
        crate(loc, w, d, h, rz, cbody, cframe)
    M = Matrix.Translation((0.0, -0.03, d2 - 0.004)) @ Matrix.Rotation(math.radians(-6), 4, "Z")
    lying_sack(0.56, 0.4, 0.24, True, M, sacks, ties)
    paw_bm(Matrix.Translation((-0.06, -0.045, d2 + 0.24 + 0.004)) @ Matrix.Rotation(math.radians(-6), 4, "Z") @
           Matrix.Rotation(math.radians(8), 4, "X"), 0.072, 0.022, bm=paws)

    paw_bm(Matrix.Translation((0, LIP_Y - 0.044, medal_z)) @ FRONT, 0.06, 0.012, bm=paws)

    fin("Sacks", sacks, "SH_Beige", angle=None)
    fin("Ties", ties, "SH_Gold", angle=70)
    fin("Paws", paws, "SH_Walnut", angle=None)
    fin("Crates", cbody, "SH_Honey", angle=45)
    fin("CrateFrames", cframe, "SH_Walnut", angle=45)


out, flags = cli()
begin()
mz = build_frame()
build_contents(mz)
ob = join_all("ShopStorageShelf")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.55, -0.35, 0), target=(-0.3, 0.0, 0.95), ortho=3.4)
