import sys, random, math
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from env_kit_e2 import *

T, H, HU = 0.3, 2.7, 1.5
YI, YO = -0.15, 0.15
ZOC = 0.13
FR = 0.84
AC0, AC1 = 0.795, 0.885
CR0, CR1 = 0.875, 0.965
GT0, GT1 = 1.95, 2.07
TOP = 2.62
TP0 = 2.6
ST_H = 0.32
EB0, EB1 = 2.42, 2.52
XM = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))

HW, ZS, ZSP, NA = 0.5, 1.13, 1.75, 14
RO = 3 * (2 * HU / 14)
FW = RO - HW
DHW, DH, DFW, DRISE, ND = 0.8, 2.2, 0.14, 0.2, 10
DRO = DHW + DFW


def mkwall():
    return Wall("x", -HU, HU, YI, -1, T, H, 0.0, 0.0)


def xbar(bm, x0, x1, y0, y1, z0, z1, r, m=2):
    w, h = y1 - y0, z1 - z0
    cy, cz = (y0 + y1) / 2, (z0 + z1) / 2
    return loft([(w, h, r, x0, cy, cz), (w, h, r, x1, cy, cz)], m, bm=bm, matrix=XM)


def qf(bm, vs, want):
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def ell(bm, c, radii, R=None, u=8, v=4):
    before = set(bm.verts)
    ellipsoid_bm((0, 0, 0), radii, u, v, bm=bm)
    vs = [x for x in bm.verts if x not in before]
    M = Matrix.Translation(Vector(c)) @ (R if R is not None else Matrix.Identity(4))
    bmesh.ops.transform(bm, matrix=M, verts=vs)
    return bm


def ring(bm, inner, outer, y0, y1, closed=True):
    n = len(inner)
    I0 = [bm.verts.new((u, y0, z)) for u, z in inner]
    I1 = [bm.verts.new((u, y1, z)) for u, z in inner]
    O0 = [bm.verts.new((u, y0, z)) for u, z in outer]
    O1 = [bm.verts.new((u, y1, z)) for u, z in outer]
    for i in (range(n) if closed else range(n - 1)):
        j = (i + 1) % n
        mi = Vector(((inner[i][0] + inner[j][0]) / 2, 0, (inner[i][1] + inner[j][1]) / 2))
        mo = Vector(((outer[i][0] + outer[j][0]) / 2, 0, (outer[i][1] + outer[j][1]) / 2))
        qf(bm, [I0[i], I0[j], O0[j], O0[i]], (0, -1, 0))
        qf(bm, [I1[i], I1[j], O1[j], O1[i]], (0, 1, 0))
        qf(bm, [I0[i], I0[j], I1[j], I1[i]], mi - mo)
        qf(bm, [O0[i], O0[j], O1[j], O1[i]], mo - mi)
    return bm


def prism(bm, pts, y0, y1):
    F = [bm.verts.new((u, y0, z)) for u, z in pts]
    K = [bm.verts.new((u, y1, z)) for u, z in pts]
    qf(bm, F, (0, -1, 0))
    qf(bm, K, (0, 1, 0))
    return bm


def body(B, u0, u1, z0, z1):
    wbox(B["SH_Parchment"], (u0, YI, z0), (u1, 0.0, z1))
    wbox(B["SH_Walnut"], (u0, 0.0, z0), (u1, YO, z1))


def spandrel(B, arch, ztop):
    for (u0, z0), (u1, z1) in zip(arch, arch[1:]):
        for y, mat, want in ((YI, "SH_Parchment", (0, -1, 0)), (YO, "SH_Walnut", (0, 1, 0))):
            pts = [(u0, y, z0), (u1, y, z1), (u1, y, ztop), (u0, y, ztop)]
            out = []
            for p in pts:
                if not out or (Vector(p) - Vector(out[-1])).length > 1e-5:
                    out.append(p)
            if (Vector(out[0]) - Vector(out[-1])).length < 1e-5:
                out.pop()
            if len(out) >= 3:
                oface(B[mat], out, want)


def girt(B, u0, u1):
    xbar(B["SH_Timber"], u0, u1, YI - 0.035, YI + 0.01, GT0, GT1, 0.024)


def inner_run(B, w, u0, u1, with_girt=True):
    w.boards(B["SH_Honey"], B["SH_Walnut"], u0, u1, 0.1, FR)
    xbar(B["SH_Walnut"], u0, u1, YI - 0.035, YI + 0.01, 0.0, ZOC, 0.018)
    xbar(B["SH_Sage"], u0, u1, YI - 0.032, YI + 0.01, AC0, AC1, 0.012, 1)
    xbar(B["SH_Timber"], u0, u1, YI - 0.04, YI + 0.01, CR0, CR1, 0.028)
    if with_girt:
        girt(B, u0, u1)


def top_plate(B, u0=-HU, u1=HU):
    xbar(B["SH_Timber"], u0, u1, YI - 0.035, YO + 0.035, TP0, H, 0.03)


def stones(B, u0, u1, rng, m=0.02):
    for row, (zc, rz) in enumerate(((0.09, 0.072), (0.238, 0.07))):
        u = u0 + m
        first = True
        while True:
            rem = u1 - m - u
            if rem <= 0.12:
                break
            wd = rng.uniform(0.17, 0.25) if (row == 1 and first) else rng.uniform(0.34, 0.5)
            first = False
            if rem < wd + 0.28:
                wd = rem if rem < 0.62 else rem / 2
            ell(B["SH_Stone"], (u + wd / 2, YO + 0.008, zc + rng.uniform(-0.012, 0.012)),
                (wd / 2 * 0.97, 0.03, rz * rng.uniform(0.9, 1.05)), None, 8, 4)
            u += wd + 0.014


def outer_back(B, u0, u1, rng):
    xbar(B["SH_StoneDark"], u0, u1, YO - 0.01, YO + 0.02, 0.0, ST_H, 0.014, 1)
    stones(B, u0, u1, rng)


def band(B, u0, u1):
    xbar(B["SH_Timber"], u0, u1, YO - 0.01, YO + 0.04, EB0, EB1, 0.02)


def board_cols(u0, u1, n, z0, z1):
    bw = (u1 - u0) / n
    return [(u0 + i * bw, u0 + (i + 1) * bw, z0, z0, z1) for i in range(n)]


def ext_boards(B, cols, depth=0.02, groove=0.011, ch=0.016):
    vf = YO + depth
    vg = vf - groove
    bl, bd = B["SH_Honey"], B["SH_Walnut"]
    for a, b, za, zb, z1 in cols:
        def zz(u):
            return za + (zb - za) * (u - a) / (b - a)
        want = (0, 1, 0)
        oface(bd, [(a, vg, zz(a)), (a + ch, vf, zz(a + ch)), (a + ch, vf, z1), (a, vg, z1)], want)
        oface(bl, [(a + ch, vf, zz(a + ch)), (b - ch, vf, zz(b - ch)), (b - ch, vf, z1), (a + ch, vf, z1)], want)
        oface(bd, [(b - ch, vf, zz(b - ch)), (b, vg, zz(b)), (b, vg, z1), (b - ch, vf, z1)], want)
        oface(bd, [(a, YO, z1), (b, YO, z1), (b, vf, z1), (a, vf, z1)], (0, 0, 1))
        oface(bd, [(a, YO, za), (b, YO, zb), (b, vf, zb), (a, vf, za)], (0, 0, -1))
        oface(bd, [(a, YO, za), (a, vg, za), (a, vg, z1), (a, YO, z1)], (-1, 0, 0))
        oface(bd, [(b, YO, zb), (b, vg, zb), (b, vg, z1), (b, YO, z1)], (1, 0, 0))


def rosette(bm, u, z, y, side):
    rot = Matrix.Rotation(math.pi / 2 if side < 0 else -math.pi / 2, 4, "X")
    lathe_bm([(0.0, 0.0), (0.058, 0.0), (0.064, 0.016), (0.05, 0.032), (0.024, 0.04), (0.0, 0.042)], 10, bm=bm,
             matrix=Matrix.Translation((u, y, z)) @ rot)


def paw(bm, uc, zc, y, s=1.0):
    ell(bm, (uc, y, zc - 0.022 * s), (0.05 * s, 0.014, 0.04 * s), None, 10, 5)
    for du, dz, r in ((-0.06, 0.028, 0.02), (-0.023, 0.062, 0.021), (0.023, 0.062, 0.021), (0.06, 0.028, 0.02)):
        ell(bm, (uc + du * s, y, zc + dz * s), (r * s, 0.012, r * s * 1.12), None, 8, 4)


def build_wall(B, rng):
    w = mkwall()
    body(B, -HU, HU, 0.0, TOP)
    inner_run(B, w, -HU, HU)
    top_plate(B)
    wbox(B["SH_Timber"], (-0.1, YI - 0.045, CR1 - 0.01), (0.1, YI + 0.01, TP0 + 0.005), r=0.03, segs=2)
    for sgn in (1, -1):
        dz = 0.42
        rotbox(w, B["SH_Timber"], sgn * (0.1 + dz / 2), -0.02, GT0 - dz / 2, math.hypot(dz, dz) + 0.05, 0.035, 0.1,
               math.radians(45 * sgn), r=0.016)
    outer_back(B, -HU, HU, rng)
    ext_boards(B, board_cols(-HU, HU, 14, ST_H - 0.02, TP0 + 0.005))
    band(B, -HU, HU)
    wbox(B["SH_Timber"], (-0.1, YO - 0.01, ST_H - 0.03), (0.1, YO + 0.045, TP0 + 0.005), r=0.03, segs=2)


def win_contour(o):
    r = HW + o
    return [(-r, ZS - o), (r, ZS - o)] + [(r * math.cos(math.pi * k / NA), ZSP + r * math.sin(math.pi * k / NA))
                                          for k in range(NA + 1)]


def arch_o(u):
    return ZSP + math.sqrt(max(RO * RO - u * u, 0.0))


def flower_pot(B, x, y, z):
    m = Matrix.Translation((x, y, z))
    lathe_bm([(0.0, 0.0), (0.058, 0.0), (0.072, 0.1), (0.0, 0.1)], 10, bm=B["SH_Honey"], matrix=m)
    torus_bm(0.072, 0.017, 12, 5, bm=B["SH_Walnut"], matrix=Matrix.Translation((x, y, z + 0.1)))
    ell(B["SH_Walnut"], (x, y, z + 0.1), (0.062, 0.062, 0.012), None, 8, 3)
    for k, a in enumerate((0.3, 2.4, 4.4)):
        R = Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(math.radians(-52), 4, "Y")
        d = Vector((math.cos(a), math.sin(a), 0))
        ell(B["SH_Leaf"], Vector((x, y, z + 0.13)) + d * 0.045 + Vector((0, 0, 0.03)), (0.055, 0.026, 0.014), R, 6, 3)
    tube_bm([(x, y, z + 0.1), (x + 0.01, y, z + 0.17), (x, y, z + 0.215)], 0.009, 5, bm=B["SH_Leaf"])
    for k in range(5):
        a = 2 * math.pi * k / 5
        ell(B["SH_Gold"], (x + 0.026 * math.cos(a), y + 0.026 * math.sin(a), z + 0.222), (0.024, 0.024, 0.01), None, 6, 3)
    ell(B["SH_Walnut"], (x, y, z + 0.226), (0.016, 0.016, 0.012), None, 6, 3)


def window_box(B, rng):
    y0, y1 = YO + 0.04, YO + 0.2
    zt = ZS - 0.04
    wbox(B["SH_Honey"], (-0.52, y0, zt - 0.18), (0.52, y1, zt), r=0.03, segs=2)
    xbar(B["SH_Walnut"], -0.545, 0.545, y0 - 0.012, y1 + 0.014, zt - 0.03, zt + 0.012, 0.014, 1)
    for sg in (-1, 1):
        wbox(B["SH_Walnut"], (sg * 0.38 - 0.035, YO - 0.01, zt - 0.32), (sg * 0.38 + 0.035, y1 - 0.03, zt - 0.17), r=0.02, segs=1)
    u = -0.44
    k = 0
    while u <= 0.45:
        r = rng.uniform(0.07, 0.09)
        ell(B["SH_Leaf" if k % 3 else "SH_Moss"], (u, (y0 + y1) / 2 + rng.uniform(-0.02, 0.02), zt + 0.02),
            (r, r * 0.85, r * 0.75), None, 7, 4)
        if k % 2 == 0:
            ell(B["SH_Gold"], (u + rng.uniform(-0.03, 0.03), (y0 + y1) / 2 + 0.03, zt + 0.02 + r * 0.7),
                (0.028, 0.028, 0.02), None, 6, 3)
        u += rng.uniform(0.11, 0.15)
        k += 1


def build_window(B, rng):
    w = mkwall()
    body(B, -HU, -RO, 0.0, TOP)
    body(B, RO, HU, 0.0, TOP)
    body(B, -RO, RO, 0.0, ZS - FW)
    body(B, -RO, RO, ZSP + RO, TOP)
    spandrel(B, win_contour(FW)[2:], ZSP + RO)
    inner_run(B, w, -HU, HU, with_girt=False)
    girt(B, -HU, -RO)
    girt(B, RO, HU)
    top_plate(B)
    ring(B["SH_Timber"], win_contour(0.0), win_contour(FW), YI - 0.045, YO + 0.045)
    ring(B["SH_Walnut"], win_contour(FW - 0.04), win_contour(FW + 0.014), YI - 0.065, YO + 0.065)
    prism(B["SH_Glass"], win_contour(0.0), -0.012, 0.012)
    wbox(B["SH_Timber"], (-0.026, -0.03, ZS - 0.01), (0.026, 0.03, ZSP + HW + 0.01), r=0.012, segs=1)
    xbar(B["SH_Timber"], -HW - 0.01, HW + 0.01, -0.03, 0.03, ZSP - 0.026, ZSP + 0.026, 0.012, 1)
    wbox(B["SH_Walnut"], (-0.74, YI - 0.16, ZS - 0.075), (0.74, YI + 0.02, ZS + 0.006), r=0.028, segs=2)
    flower_pot(B, 0.4, YI - 0.085, ZS + 0.004)
    kz = ZSP + RO - 0.03
    loft([(0.16, 0.42, 0.03, kz - 0.13), (0.23, 0.42, 0.035, kz + 0.1)], 2, bm=B["SH_Walnut"])
    for y in (YI - 0.062, YO + 0.062):
        ell(B["SH_Timber"], (0.0, y, kz - 0.005), (0.035, 0.012, 0.045), None, 8, 4)
    for sg in (-1, 1):
        for side, y in ((-1, YI - 0.062), (1, YO + 0.062)):
            rosette(B["SH_Walnut"], sg * (HW + FW * 0.42), ZSP, y, side)
    outer_back(B, -HU, HU, rng)
    n = 14
    bw = 2 * HU / n
    cols = []
    for i in range(n):
        a, b = -HU + i * bw, -HU + (i + 1) * bw
        if b <= -RO + 1e-4 or a >= RO - 1e-4:
            cols.append((a, b, ST_H - 0.02, ST_H - 0.02, TP0 + 0.005))
        else:
            cols.append((a, b, ST_H - 0.02, ST_H - 0.02, ZS - FW + 0.01))
            cols.append((a, b, arch_o(a) - 0.01, arch_o(b) - 0.01, TP0 + 0.005))
    ext_boards(B, cols)
    band(B, -HU, HU)
    window_box(B, rng)


def seg_arch(c, zl, s, n):
    us = [-c + 2 * c * k / n for k in range(n + 1)]
    if s < 1e-4:
        return [(u, zl) for u in us]
    R = (c * c + s * s) / (2 * s)
    zc = zl + s - R
    return [(u, zc + math.sqrt(max(R * R - u * u, 0.0))) for u in us]


def door_contour(o):
    c = DHW + o
    return [(-c, 0.0)] + seg_arch(c, DH + o, DRISE * max(o, 0.0) / DFW, ND) + [(c, 0.0)]


def build_door(B, rng):
    w = mkwall()
    body(B, -HU, -DRO, 0.0, TOP)
    body(B, DRO, HU, 0.0, TOP)
    spandrel(B, door_contour(DFW)[1:-1], TOP)
    for u0, u1 in ((-HU, -DRO), (DRO, HU)):
        inner_run(B, w, u0, u1)
        outer_back(B, u0, u1, rng)
        ext_boards(B, board_cols(u0, u1, 3, ST_H - 0.02, TP0 + 0.005))
        band(B, u0, u1)
    top_plate(B)
    ring(B["SH_Timber"], door_contour(0.0), door_contour(DFW), YI - 0.045, YO + 0.045, closed=False)
    ring(B["SH_Walnut"], door_contour(DFW - 0.04), door_contour(DFW + 0.014), YI - 0.065, YO + 0.065, closed=False)
    for sg in (-1, 1):
        a, b = sg * (DHW + 0.012), sg * (DRO + 0.05)
        wbox(B["SH_Stone"], (min(a, b), YI - 0.09, 0.0), (max(a, b), YO + 0.09, 0.4), r=0.05, segs=2)
        a, b = sg * (DHW + 0.012), sg * (DRO + 0.035)
        wbox(B["SH_Walnut"], (min(a, b), YI - 0.095, DH - 0.22), (max(a, b), YO + 0.095, DH - 0.1), r=0.035, segs=2)
        for side, y in ((-1, YI - 0.062), (1, YO + 0.062)):
            rosette(B["SH_Walnut"], sg * (DHW + DFW * 0.42), DH + DFW * 0.42, y, side)
    wbox(B["SH_Walnut"], (-0.12, YI - 0.085, DH + 0.06), (0.12, YO + 0.085, TP0 + 0.01), r=0.035, segs=2)
    paw(B["SH_Gold"], 0.0, DH + 0.24, YI - 0.088)
    paw(B["SH_Gold"], 0.0, DH + 0.24, YO + 0.088)
    lantern(B, Vector((1.22, YI, DH)), (0, -1, 0))
    lantern(B, Vector((-1.22, YO + 0.02, DH)), (0, 1, 0))


def build_corner(B, rng):
    wbox(B["SH_StoneDark"], (-0.18, -0.18, 0.0), (0.18, 0.18, 0.34), r=0.04, segs=2)
    for k in range(4):
        R = Matrix.Rotation(math.pi / 2 * k, 4, "Z")
        for row, (zc, us) in enumerate(((0.095, (-0.088, 0.088)), (0.25, (-0.12, 0.03, 0.135)))):
            for j, u in enumerate(us):
                wd = 0.16 if row == 0 else (0.085 if j != 1 else 0.19)
                if row == 1:
                    wd = (0.07, 0.165, 0.07)[j]
                c = R @ Vector((u, -0.172, zc + rng.uniform(-0.01, 0.01)))
                ell(B["SH_Stone"], c, (wd / 2 * 0.95, 0.028, 0.068), R, 8, 4)
    wbox(B["SH_Timber"], (-0.17, -0.17, 0.3), (0.17, 0.17, 2.6), r=0.06, segs=2)
    loft([(0.39, 0.39, 0.07, 0.32), (0.39, 0.39, 0.07, 0.4), (0.35, 0.35, 0.06, 0.47)], 2, bm=B["SH_Walnut"])
    for z0, z1 in ((CR0, CR1), (GT0, GT1)):
        wbox(B["SH_Walnut"], (-0.192, -0.192, z0), (0.192, 0.192, z1), r=0.03, segs=2)
    loft([(0.33, 0.33, 0.06, 2.4), (0.36, 0.36, 0.07, 2.46), (0.4, 0.4, 0.08, 2.56), (0.4, 0.4, 0.08, 2.72),
          (0.36, 0.36, 0.065, 2.76)], 2, bm=B["SH_Walnut"])
    xbar(B["SH_Timber"], -0.2, 0.2, -0.2, 0.2, 2.585, 2.625, 0.016, 1)
    lathe_bm([(0.0, 2.75), (0.15, 2.75), (0.165, 2.775), (0.15, 2.81), (0.1, 2.838), (0.0, 2.85)], 14, bm=B["SH_Timber"])


def leaf_top(bm, p, a, rng, s=1.0):
    d = Vector((math.cos(a), math.sin(a), 0))
    R = Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(math.radians(rng.uniform(-18, -6)), 4, "Y")
    ell(bm, Vector(p) + d * 0.068 * s + Vector((0, 0, 0.014)), (0.084 * s, 0.056 * s, 0.022), R, 7, 3)


def leaf_face(bm, p, a, side, s=1.0):
    R = Matrix.Rotation(a, 4, "Y")
    ell(bm, p, (0.07 * s, 0.02, 0.052 * s), R, 7, 3)


def build_trim(B, rng):
    z0 = H
    xbar(B["SH_Walnut"], -HU, HU, -0.2, 0.2, z0, z0 + 0.12, 0.045)
    xbar(B["SH_Timber"], -HU, HU, -0.205, 0.205, z0, z0 + 0.035, 0.014, 1)
    zv = z0 + 0.133
    pts = []
    lim = HU - 0.007
    for k in range(31):
        u = -lim + 2 * lim * k / 30
        pts.append((u, 0.075 * math.sin(2 * math.pi * u / 1.5), zv))
    tube_bm(pts, 0.02, 5, bm=B["SH_Moss"])
    u = -1.32
    k = 0
    while u < 1.32:
        y = 0.075 * math.sin(2 * math.pi * u / 1.5)
        base = rng.uniform(0, 2 * math.pi)
        s = rng.uniform(0.85, 1.15)
        for j in range(3):
            leaf_top(B["SH_Leaf" if (k + j) % 4 else "SH_Moss"], (u, y, zv), base + 2 * math.pi * j / 3, rng, s)
        u += rng.uniform(0.2, 0.28)
        k += 1
    for uc, side, L in ((-1.08, -1, 0.36), (-0.62, 1, 0.28), (0.78, -1, 0.44), (1.15, 1, 0.32), (0.32, 1, 0.22), (-0.3, -1, 0.2)):
        y0 = side * 0.19
        yf = side * 0.224
        p = [(uc, y0, z0 + 0.1), (uc, yf, z0 + 0.04), (uc + 0.03, yf, z0 - L * 0.5), (uc - 0.01, yf, z0 - L)]
        tube_bm(p, 0.016, 5, bm=B["SH_Moss"])
        n = int(L / 0.085) + 1
        for j in range(n):
            t = (j + 0.5) / n
            zz = z0 + 0.03 - (L + 0.02) * t
            du = 0.042 if j % 2 == 0 else -0.042
            leaf_face(B["SH_Leaf" if j % 3 else "SH_Moss"], (uc + du + 0.01, side * 0.23, zz),
                      (0.6 if du > 0 else -0.6) + rng.uniform(-0.2, 0.2), side, rng.uniform(0.9, 1.12))


def build_floor(B, rng):
    n, pw = 10, 0.3
    offs = [0.95, 2.2, 1.45, 0.5, 2.55, 1.2, 0.72, 2.3, 1.8, 0.4]
    knots = {(1, 0): 0.3, (4, 1): 0.6, (6, 0): -0.4, (8, 1): 0.25, (3, 0): 0.0}
    wbox(B["SH_Walnut"], (-HU, -HU, -0.15), (HU, HU, -0.006))
    for i in range(n):
        xa, xb = -HU + i * pw, -HU + (i + 1) * pw
        xc = (xa + xb) / 2
        cuts = [-HU, -HU + offs[i], HU]
        for k, (ya, yb) in enumerate(zip(cuts, cuts[1:])):
            honey = rng.random() < 0.4
            mat = "SH_Honey" if honey else "SH_Oak"
            chamfer_tile(B[mat], xa + 0.007, xb - 0.007, ya + 0.007, yb - 0.007, 0.0, ch=0.016, dz=0.01)
            for ye in (ya + 0.07, yb - 0.07):
                for dx in (-0.085, 0.085):
                    chamfer_tile(B["SH_Timber"], xc + dx - 0.016, xc + dx + 0.016, ye - 0.016, ye + 0.016, 0.005, ch=0.006, dz=0.007)
            if (i, k) in knots:
                ky = (ya + yb) / 2 + knots[(i, k)] * (yb - ya) * 0.4
                kx = xc + (0.05 if (i + k) % 2 else -0.04)
                pts = [(kx + 0.03 * math.cos(2 * math.pi * j / 8), ky + 0.055 * math.sin(2 * math.pi * j / 8), 0.0015) for j in range(8)]
                oface(B["SH_Oak" if honey else "SH_Honey"], pts, (0, 0, 1))
                pts2 = [(kx + 0.013 * math.cos(2 * math.pi * j / 6), ky + 0.024 * math.sin(2 * math.pi * j / 6), 0.0025) for j in range(6)]
                oface(B["SH_Walnut"], pts2, (0, 0, 1))


PIECES = [
    ("K1", "ZoneKitFloor", build_floor, 101, (0.6, 0.4, 0.0), 50.0),
    ("K2", "ZoneKitWall", build_wall, 102, (0.9, -0.9, 0.0), 40.0),
    ("K3", "ZoneKitWallWindow", build_window, 103, (1.0, -0.9, 0.0), 40.0),
    ("K4", "ZoneKitWallDoor", build_door, 104, (0.0, -1.0, 0.0), 40.0),
    ("K5", "ZoneKitCorner", build_corner, 105, (0.75, -0.5, 0.0), 40.0),
    ("K6", "ZoneKitTrimIvy", build_trim, 106, (0.9, -0.9, 0.0), 50.0),
]
BY_KEY = {p[0]: p for p in PIECES}


def make(name, fn, seed, angle):
    B = Bins()
    fn(B, random.Random(seed))
    objs = B.done(name, angle=angle)
    ob = join_all(name, objs)
    PARTS.clear()
    return ob


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def run_piece(key, out, flags):
    _, name, fn, seed, dloc, ang = BY_KEY[key]
    begin()
    ob = make(name, fn, seed, ang)
    report(ob)
    print("TRIS", name, tris(ob))
    export(ob, flags)
    if key == "K6":
        make("CtxWall", build_wall, 102, 40.0)
        preview(ob, out, dloc, target=(0.0, 0.0, 1.9), ortho=4.6)
    elif key == "K5":
        preview(ob, out, dloc, ortho=3.6)
    else:
        preview(ob, out, dloc)


def run_assembly(out):
    begin()
    lay = [
        ("F1", build_floor, 101, 50.0, (0.0, 0.0, 0.0), 0),
        ("F2", build_floor, 101, 50.0, (3.0, 0.0, 0.0), 0),
        ("Wa", build_wall, 102, 40.0, (0.0, 1.5, 0.0), 0),
        ("Wb", build_window, 103, 40.0, (3.0, 1.5, 0.0), 0),
        ("Dc", build_door, 104, 40.0, (4.5, 0.0, 0.0), -90),
        ("C0", build_corner, 105, 40.0, (-1.5, 1.5, 0.0), 0),
        ("C1", build_corner, 105, 40.0, (4.5, 1.5, 0.0), 0),
        ("C2", build_corner, 105, 40.0, (4.5, -1.5, 0.0), 0),
        ("Ta", build_trim, 106, 50.0, (0.0, 1.5, 0.0), 0),
        ("Tb", build_trim, 106, 50.0, (3.0, 1.5, 0.0), 0),
        ("Tc", build_trim, 106, 50.0, (4.5, 0.0, 0.0), -90),
    ]
    for name, fn, seed, ang, loc, rz in lay:
        ob = make(name, fn, seed, ang)
        ob.location = loc
        ob.rotation_euler.z = math.radians(rz)
    setup_scene(floor=24)
    load_dragon((0.5, -0.3, 0.0), 160.0)
    load_dragon((3.0, 0.75, 0.0), 180.0)
    load_dragon((5.4, 0.1, 0.0), 260.0)
    C = (1.6, 0.4, 1.1)
    cells = []
    for tag, az, el, tgt, orth in (("in34", -35, 32, C, 8.4), ("iso", -25, 55, C, 8.4), ("front", 0, 10, C, 8.4),
                                   ("out", 140, 30, C, 8.4), ("door", -70, 22, (3.9, -0.2, 1.1), 5.0),
                                   ("seam", -15, 25, (1.5, 1.2, 1.3), 3.6)):
        f = "ZoneKitAsm_%s.png" % tag
        render(os.path.join(out, f), az, el, tgt, orth)
        cells.append(f)
    contact_sheet(out, cells, os.path.join(out, "ZoneKitAsm_sheet.png"))


out, flags = cli()
keys = [k for k in ("K1", "K2", "K3", "K4", "K5", "K6") if k in flags]
want_asm = "asm" in flags or not keys
if not keys and "asmonly" not in flags:
    keys = [p[0] for p in PIECES]
if "asmonly" in flags:
    keys = []
    want_asm = True
for k in keys:
    run_piece(k, out, flags)
if want_asm and out:
    run_assembly(out)
