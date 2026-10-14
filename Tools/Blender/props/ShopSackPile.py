import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

PAL_H = 0.1
SACK_L = 0.9
SACK_W = 0.41
SACK_H = 0.3


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


def ring_stack(rings, m=3, bm=None, matrix=None):
    bm = bm or bmesh.new()
    vr = []
    for x, w, h, zc, wav in rings:
        r = min(w, h) * 0.46
        pts = rrect(w, h, r, m)
        n = len(pts)
        ring = []
        for k, (py, pz) in enumerate(pts):
            s = 1.0 + wav * math.sin(2 * math.pi * k * 3 / n)
            ring.append(bm.verts.new((x, py * s, zc + pz * s)))
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


def lying_sack(L, W, H, tied=True, sag=0.0):
    body = [(0.0, 0.94, 0.14), (0.04, 0.95, 0.5), (0.11, 0.98, 0.8), (0.24, 1.0, 0.95), (0.4, 1.0, 1.0),
            (0.6, 1.0, 1.0), (0.76, 1.0, 0.95)]
    if tied:
        body += [(0.87, 0.93, 0.82), (0.95, 0.42, 0.46)]
    else:
        body += [(0.89, 0.98, 0.8), (0.96, 0.95, 0.5), (1.0, 0.94, 0.14)]
    rings = []
    for f, sw, sh in body:
        h = H * sh
        zc = 0.5 * h + 0.32 * H * (1 - sh)
        rings.append((-L / 2 + f * L, W * sw, h, zc, 0.0))
    tie = None
    if tied:
        zc = rings[-1][3] + 0.01
        x0 = rings[-1][0]
        nw = 0.12
        rings += [(x0 + 0.035, nw, nw, zc, 0.0), (x0 + 0.06, 0.18, 0.17, zc + 0.005, 0.14),
                  (x0 + 0.1, 0.26, 0.24, zc + 0.01, 0.2), (x0 + 0.125, 0.22, 0.2, zc + 0.01, 0.2),
                  (x0 + 0.135, 0.09, 0.085, zc + 0.01, 0.1)]
        tie = (x0 + 0.035, zc, nw / 2)
    return ring_stack(rings), tie


def place(bm, M):
    return xf(bm, M)


def tie_bm(tie, M, bm):
    x, zc, r = tie
    torus_bm(r + 0.01, 0.026, 14, 5, bm=bm,
             matrix=M @ Matrix.Translation((x, 0, zc)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
    before = set(bm.verts)
    for s in (1, -1):
        p0 = Vector((x, s * 0.02, zc - r - 0.01))
        tube_bm([p0, p0 + Vector((-0.02, s * 0.03, -0.05)), p0 + Vector((-0.01, s * 0.05, -0.09))],
                [0.017, 0.015, 0.013], 5, bm=bm)
        ellipsoid_bm((x - 0.01, s * 0.07, zc - r - 0.11), (0.028, 0.028, 0.032), 8, 4, bm=bm)
    xf(bm, M, [v for v in bm.verts if v not in before])


def build_pallet():
    bm = bmesh.new()
    for y in (-0.31, 0.0, 0.31):
        rbox_bm((0, y, 0.033), (1.0, 0.12, 0.066), 0.02, 1, bm=bm)
    n, pw = 5, 0.17
    gap = (1.0 - n * pw) / (n - 1)
    for i in range(n):
        x = -0.5 + pw / 2 + i * (pw + gap)
        rbox_bm((x, 0, PAL_H - 0.019), (pw, 0.8, 0.04), 0.014, 1, bm=bm)
    fin("Pallet", bm, "SH_Walnut", angle=50)


def build_sacks():
    specs = [("SackFront", "SH_Parchment", (0.04, -0.2, PAL_H - 0.006), 183.0, True, SACK_H),
             ("SackBack", "SH_Beige", (0.0, 0.195, PAL_H - 0.006), -2.0, False, SACK_H),
             ("SackTop", "SH_Beige", (-0.02, -0.02, PAL_H + SACK_H * 0.5), -13.0, True, SACK_H * 0.92)]
    ties = bmesh.new()
    paws = bmesh.new()
    tops = []
    for name, mat, loc, rz, tied, h in specs:
        bm, tie = lying_sack(SACK_L if not tied else SACK_L * 0.86, SACK_W, h, tied)
        M = Matrix.Translation(loc) @ Matrix.Rotation(math.radians(rz), 4, "Z")
        place(bm, M)
        fin(name, bm, mat, angle=None)
        if tie:
            tie_bm(tie, M, ties)
        top = Vector(loc) + Vector((0, 0, h))
        tops.append((top, rz))
        if name == "SackTop":
            pm = Matrix.Translation(top + Vector((-0.06, -0.025, -0.003))) @ Matrix.Rotation(math.radians(rz), 4, "Z") \
                @ Matrix.Rotation(math.radians(8), 4, "X")
            paw_bm(pm, 0.085, 0.02, bm=paws)
        elif name == "SackFront":
            r = min(SACK_W, h) * 0.46
            yf = loc[1] - SACK_W / 2 + r - r * math.sin(math.radians(50)) - 0.002
            zf = loc[2] + h - r + r * math.cos(math.radians(50)) - 0.002
            pm = Matrix.Translation((-0.2, yf, zf)) @ Matrix.Rotation(math.radians(-40), 4, "X") @ \
                Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
            paw_bm(pm, 0.075, 0.02, bm=paws)
    fin("Ties", ties, "SH_Gold", angle=70)
    fin("Paws", paws, "SH_Walnut", angle=None)
    return tops


def build_scoop(top):
    c = top + Vector((0.24, 0.05, -0.04))
    M = Matrix.Translation(c) @ Matrix.Rotation(math.radians(-25), 4, "Z") @ Matrix.Rotation(math.radians(112), 4, "X")
    prof = [(0.0, 0.0), (0.06, 0.004), (0.078, 0.03), (0.082, 0.075), (0.064, 0.078), (0.06, 0.04), (0.0, 0.034)]
    bm = lathe_bm(prof, 14, matrix=M)
    rim = torus_bm(0.072, 0.012, 14, 5, matrix=M @ Matrix.Translation((0, 0, 0.076)))
    hb = bmesh.new()
    p0 = M @ Vector((0, 0.0, 0.0))
    d = (M.to_3x3() @ Vector((0, 0, -1))).normalized()
    tube_bm([p0 + d * 0.0, p0 + d * 0.08, p0 + d * 0.16], [0.022, 0.022, 0.021], 6, bm=hb)
    ellipsoid_bm(p0 + d * 0.17, (0.03, 0.03, 0.03), 8, 4, bm=hb)
    fin("Scoop", bm, "SH_Gold", angle=60)
    fin("ScoopRim", rim, "SH_Gold", angle=80)
    fin("ScoopHandle", hb, "SH_Walnut", angle=70)


out, flags = cli()
begin()
build_pallet()
tops = build_sacks()
build_scoop(tops[2][0])
ob = join_all("ShopSackPile")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.05, 0.55, 0), target=(-0.35, 0.0, 0.4), ortho=2.4)
