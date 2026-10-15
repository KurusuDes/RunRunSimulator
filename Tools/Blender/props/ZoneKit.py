import sys, random, math, bisect
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
E_END = 0.003

WHW, WZ0, WZ1, WFW = 0.52, 1.1, 2.14, 0.12
WZM = (WZ0 + WZ1) / 2
WRO = WHW + WFW
DHW, DH, DFW, DRISE, ND = 0.8, 2.2, 0.14, 0.2, 10
DRO = DHW + DFW


def xbar(bm, x0, x1, y0, y1, z0, z1, r, m=2, e=E_END):
    if x0 <= -HU + 1e-6:
        x0 = -HU + e
    if x1 >= HU - 1e-6:
        x1 = HU - e
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


def obox(bm, u0, u1, y0, y1, z0, z1, faces):
    V = {}
    for i, u in enumerate((u0, u1)):
        for j, y in enumerate((y0, y1)):
            for k, z in enumerate((z0, z1)):
                V[i, j, k] = (u, y, z)
    for f in faces:
        vs, want = {
            "-x": ([V[0, 0, 0], V[0, 1, 0], V[0, 1, 1], V[0, 0, 1]], (-1, 0, 0)),
            "+x": ([V[1, 0, 0], V[1, 1, 0], V[1, 1, 1], V[1, 0, 1]], (1, 0, 0)),
            "-y": ([V[0, 0, 0], V[1, 0, 0], V[1, 0, 1], V[0, 0, 1]], (0, -1, 0)),
            "+y": ([V[0, 1, 0], V[1, 1, 0], V[1, 1, 1], V[0, 1, 1]], (0, 1, 0)),
            "-z": ([V[0, 0, 0], V[1, 0, 0], V[1, 1, 0], V[0, 1, 0]], (0, 0, -1)),
            "+z": ([V[0, 0, 1], V[1, 0, 1], V[1, 1, 1], V[0, 1, 1]], (0, 0, 1)),
        }[f]
        oface(bm, vs, want)
    return bm


def body(B, u0, u1, z0, z1, inner_caps=True):
    caps = [c for c, edge in (("-x", u0 > -HU + 1e-6), ("+x", u1 < HU - 1e-6)) if edge and inner_caps]
    obox(B["SH_Parchment"], u0, u1, YI, 0.0, z0, z1, ["-y", "-z", "+z"] + caps)
    obox(B["SH_Walnut"], u0, u1, 0.0, YO, z0, z1, ["+y", "-z", "+z"] + caps)


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


def iboards(bl, bd, u0, u1, z0, z1, bw=0.17, depth=0.02, groove=0.011, ch=0.014):
    n = max(1, int(round((u1 - u0) / bw)))
    bw = (u1 - u0) / n
    vf, vg = YI - depth, YI - depth + groove
    want = (0, -1, 0)
    for i in range(n):
        a = u0 + i * bw
        b = a + bw
        oface(bd, [(a, vg, z0), (a + ch, vf, z0), (a + ch, vf, z1), (a, vg, z1)], want)
        oface(bl, [(a + ch, vf, z0), (b - ch, vf, z0), (b - ch, vf, z1), (a + ch, vf, z1)], want)
        oface(bd, [(b - ch, vf, z0), (b, vg, z0), (b, vg, z1), (b - ch, vf, z1)], want)
    if u0 > -HU + 1e-6:
        oface(bd, [(u0, YI, z0), (u0, vg, z0), (u0, vg, z1), (u0, YI, z1)], (-1, 0, 0))
    if u1 < HU - 1e-6:
        oface(bd, [(u1, YI, z0), (u1, vg, z0), (u1, vg, z1), (u1, YI, z1)], (1, 0, 0))
    oface(bd, [(u0, YI, z1), (u1, YI, z1), (u1, vf, z1), (u0, vf, z1)], (0, 0, 1))


def girt(B, u0, u1):
    xbar(B["SH_Timber"], u0, u1, YI - 0.03, YI + 0.01, GT0, GT1, 0.024)


def inner_run(B, u0, u1, with_girt=True):
    iboards(B["SH_Honey"], B["SH_Walnut"], u0, u1, 0.1, FR)
    xbar(B["SH_Walnut"], u0, u1, YI - 0.03, YI + 0.01, 0.0, ZOC, 0.018)
    xbar(B["SH_Sage"], u0, u1, YI - 0.03, YI + 0.01, AC0, AC1, 0.012, 1, e=0.012)
    xbar(B["SH_Timber"], u0, u1, YI - 0.03, YI + 0.01, CR0, CR1, 0.026)
    if with_girt:
        girt(B, u0, u1)


def top_plate(B, u0=-HU, u1=HU):
    xbar(B["SH_Timber"], u0, u1, YI - 0.03, YO + 0.03, TP0, H, 0.03)


def stones(B, u0, u1, rng, m=0.02):
    for row, (zc, rz) in enumerate(((0.09, 0.072), (0.236, 0.068))):
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
            ell(B["SH_Stone"], (u + wd / 2, YO + 0.01, zc + rng.uniform(-0.01, 0.01)),
                (wd / 2 * 0.97, 0.022, rz * rng.uniform(0.9, 1.0)), None, 8, 4)
            u += wd + 0.014


def outer_back(B, u0, u1, rng):
    xbar(B["SH_StoneDark"], u0, u1, YO - 0.01, YO + 0.012, 0.0, ST_H, 0.01, 1)
    stones(B, u0, u1, rng)


def band(B, u0, u1):
    xbar(B["SH_Timber"], u0, u1, YO - 0.01, YO + 0.03, EB0, EB1, 0.02)


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
        if a > -HU + 1e-6:
            oface(bd, [(a, YO, za), (a, vg, za), (a, vg, z1), (a, YO, z1)], (-1, 0, 0))
        if b < HU - 1e-6:
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
    w = Wall("x", -HU, HU, YI, -1, T, H, 0.0, 0.0)
    body(B, -HU, HU, 0.0, TOP)
    inner_run(B, -HU, HU)
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


def wrect(o, r):
    pts = rrect(2 * (WHW + o), (WZ1 - WZ0) + 2 * o, r, 3, 0.0, WZM)
    return pts


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
    y0, y1 = YO + 0.015, YO + 0.17
    zt = WZ0 - WFW - 0.012
    wbox(B["SH_Honey"], (-0.52, y0, zt - 0.17), (0.52, y1, zt), r=0.03, segs=2)
    xbar(B["SH_Walnut"], -0.545, 0.545, y0 + 0.005, y1 + 0.014, zt - 0.03, zt + 0.012, 0.014, 1)
    for sg in (-1, 1):
        wbox(B["SH_Walnut"], (sg * 0.38 - 0.035, YO - 0.01, zt - 0.31), (sg * 0.38 + 0.035, y1 - 0.03, zt - 0.16), r=0.02, segs=1)
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
    ro = WRO - 0.03
    body(B, -HU, -ro, 0.0, TOP, False)
    body(B, ro, HU, 0.0, TOP, False)
    body(B, -ro, ro, 0.0, WZ0 - WFW + 0.03, False)
    body(B, -ro, ro, WZ1 + WFW - 0.03, TOP, False)
    inner_run(B, -HU, HU, with_girt=False)
    girt(B, -HU, -WRO + 0.02)
    girt(B, WRO - 0.02, HU)
    top_plate(B)
    ring(B["SH_Timber"], wrect(0.0, 0.08), wrect(WFW, 0.03), YI - 0.05, YO + 0.05)
    ring(B["SH_Walnut"], wrect(WFW - 0.035, 0.03), wrect(WFW + 0.028, 0.035), YI - 0.072, YO + 0.072)
    prism(B["SH_Glass"], wrect(0.006, 0.084), -0.012, 0.012)
    wbox(B["SH_Timber"], (-0.046, -0.062, WZ0 - 0.02), (0.046, 0.062, WZ1 + 0.02), r=0.026, segs=2)
    wbox(B["SH_Timber"], (-WHW - 0.02, -0.046, WZM - 0.046), (WHW + 0.02, 0.046, WZM + 0.046), r=0.024, segs=2)
    wbox(B["SH_Walnut"], (-0.078, -0.08, WZM - 0.078), (0.078, 0.08, WZM + 0.078), r=0.032, segs=2)
    for y in (-0.093, 0.093):
        ell(B["SH_Gold"], (0.0, y, WZM), (0.03, 0.016, 0.03), None, 10, 5)
    wbox(B["SH_Walnut"], (-0.75, YI - 0.215, WZ0 - WFW - 0.05), (0.75, YI + 0.04, WZ0 - WFW + 0.03), r=0.03, segs=2)
    for sg in (-1, 1):
        wbox(B["SH_Walnut"], (sg * 0.5 - 0.04, YI - 0.15, WZ0 - WFW - 0.2), (sg * 0.5 + 0.04, YI - 0.02, WZ0 - WFW - 0.04),
             r=0.02, segs=1)
    flower_pot(B, 0.36, YI - 0.16, WZ0 - WFW + 0.026)
    wbox(B["SH_Walnut"], (-0.74, YI - 0.085, WZ1 + WFW - 0.02), (0.74, YO + 0.085, WZ1 + WFW + 0.07), r=0.035, segs=2)
    outer_back(B, -HU, HU, rng)
    n = 14
    bw = 2 * HU / n
    cols = []
    for i in range(n):
        a, b = -HU + i * bw, -HU + (i + 1) * bw
        if b <= -WRO + 1e-4 or a >= WRO - 1e-4:
            cols.append((a, b, ST_H - 0.02, ST_H - 0.02, TP0 + 0.005))
        else:
            cols.append((a, b, ST_H - 0.02, ST_H - 0.02, WZ0 - WFW + 0.01))
            cols.append((a, b, WZ1 + WFW - 0.01, WZ1 + WFW - 0.01, TP0 + 0.005))
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
    body(B, -HU, -DRO, 0.0, TOP)
    body(B, DRO, HU, 0.0, TOP)
    spandrel(B, door_contour(DFW)[1:-1], TOP)
    for u0, u1 in ((-HU, -DRO), (DRO, HU)):
        inner_run(B, u0, u1)
        outer_back(B, u0, u1, rng)
        ext_boards(B, board_cols(u0, u1, 3, ST_H - 0.02, TP0 + 0.005))
        band(B, u0 if u0 < 0 else u0 + 0.012, u1 if u1 > 0 else u1 - 0.012)
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
    wbox(B["SH_StoneDark"], (-0.19, -0.19, -0.02), (0.19, 0.19, 0.36), r=0.04, segs=2)
    for k in range(4):
        R = Matrix.Rotation(math.pi / 2 * k, 4, "Z")
        for zc, row in ((0.1, ((-0.088, 0.16), (0.088, 0.16))), (0.255, ((-0.122, 0.07), (0.0, 0.15), (0.122, 0.07)))):
            for u, wd in row:
                ell(B["SH_Stone"], R @ Vector((u, -0.176, zc)), (wd / 2 * 0.95, 0.022, 0.066), R, 8, 4)
    loft([(0.38, 0.38, 0.05, 0.33), (0.38, 0.38, 0.05, 2.42)], 2, bm=B["SH_Timber"])
    loft([(0.4, 0.4, 0.06, 0.34), (0.4, 0.4, 0.06, 0.42), (0.35, 0.35, 0.055, 0.48)], 2, bm=B["SH_Walnut"])
    for z0, z1 in ((0.85, 0.99), (1.93, 2.09)):
        loft([(0.38, 0.38, 0.06, z0), (0.4, 0.4, 0.065, z0 + 0.025), (0.4, 0.4, 0.065, z1 - 0.025),
              (0.38, 0.38, 0.06, z1)], 2, bm=B["SH_Walnut"])
    loft([(0.35, 0.35, 0.055, 2.38), (0.4, 0.4, 0.07, 2.44), (0.4, 0.4, 0.07, 2.8), (0.37, 0.37, 0.07, 2.835),
          (0.3, 0.3, 0.06, 2.85)], 2, bm=B["SH_Walnut"])


def leaf_top(bm, p, a, rng, s=1.0):
    d = Vector((math.cos(a), math.sin(a), 0))
    R = Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(math.radians(rng.uniform(-18, -6)), 4, "Y")
    ell(bm, Vector(p) + d * 0.068 * s + Vector((0, 0, 0.014)), (0.084 * s, 0.056 * s, 0.022), R, 7, 3)


def leaf_face(bm, p, a, side, s=1.0):
    R = Matrix.Rotation(a, 4, "Y")
    ell(bm, p, (0.07 * s, 0.02, 0.052 * s), R, 7, 3)


def build_trim(B, rng):
    z0 = H
    xbar(B["SH_Timber"], -HU, HU, -0.19, 0.19, z0, z0 + 0.045, 0.014, 1)
    xbar(B["SH_Walnut"], -HU, HU, -0.18, 0.18, z0 + 0.035, z0 + 0.12, 0.04, e=0.012)
    zv = z0 + 0.133
    pts = []
    lim = HU - 0.02
    for k in range(31):
        u = -lim + 2 * lim * k / 30
        pts.append((u, 0.07 * math.sin(2 * math.pi * u / 1.5), zv))
    tube_bm(pts, 0.02, 5, bm=B["SH_Moss"])
    u = -1.3
    k = 0
    while u < 1.3:
        y = 0.07 * math.sin(2 * math.pi * u / 1.5)
        base = rng.uniform(0, 2 * math.pi)
        s = rng.uniform(0.85, 1.1)
        for j in range(3):
            leaf_top(B["SH_Leaf" if (k + j) % 4 else "SH_Moss"], (u, y, zv), base + 2 * math.pi * j / 3, rng, s)
        u += rng.uniform(0.2, 0.28)
        k += 1
    for uc, side, L in ((-1.08, -1, 0.36), (-0.62, 1, 0.28), (0.78, -1, 0.44), (1.15, 1, 0.32), (0.32, 1, 0.22), (-0.3, -1, 0.2)):
        y0 = side * 0.17
        yf = side * 0.212
        p = [(uc, y0, z0 + 0.1), (uc, yf, z0 + 0.04), (uc + 0.03, yf, z0 - L * 0.5), (uc - 0.01, yf, z0 - L)]
        tube_bm(p, 0.016, 5, bm=B["SH_Moss"])
        n = int(L / 0.085) + 1
        for j in range(n):
            t = (j + 0.5) / n
            zz = z0 + 0.03 - (L + 0.02) * t
            du = 0.042 if j % 2 == 0 else -0.042
            leaf_face(B["SH_Leaf" if j % 3 else "SH_Moss"], (uc + du + 0.01, side * 0.222, zz),
                      (0.6 if du > 0 else -0.6) + rng.uniform(-0.2, 0.2), side, rng.uniform(0.9, 1.12))


def mound(bm, cx, cy, rx, ry, ztop, zbot, n=8, k=0.8):
    top = [(cx + rx * k * math.cos(2 * math.pi * j / n), cy + ry * k * math.sin(2 * math.pi * j / n), ztop) for j in range(n)]
    bot = [(cx + rx * math.cos(2 * math.pi * j / n), cy + ry * math.sin(2 * math.pi * j / n), zbot) for j in range(n)]
    oface(bm, top, (0, 0, 1))
    for j in range(n):
        j1 = (j + 1) % n
        oface(bm, [bot[j], bot[j1], top[j1], top[j]], (top[j][0] - cx, top[j][1] - cy, 0.3))


def build_floor(B, rng):
    n, pw = 10, 0.3
    offs = [0.95, 2.2, 1.45, 0.5, 2.55, 1.2, 0.72, 2.3, 1.8, 0.4]
    knots = {(1, 0): 0.3, (4, 1): 0.6, (6, 0): -0.4, (8, 1): 0.25, (3, 0): 0.0}
    e = 0.0025
    wbox(B["SH_Walnut"], (-HU + e, -HU + e, -0.15), (HU - e, HU - e, -0.006))
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
                    chamfer_tile(B["SH_Timber"], xc + dx - 0.016, xc + dx + 0.016, ye - 0.016, ye + 0.016, 0.011, ch=0.008, dz=0.016)
            if (i, k) in knots:
                ky = (ya + yb) / 2 + knots[(i, k)] * (yb - ya) * 0.4
                kx = xc + (0.05 if (i + k) % 2 else -0.04)
                mound(B["SH_Oak" if honey else "SH_Honey"], kx, ky, 0.034, 0.06, 0.008, -0.004)
                mound(B["SH_Walnut"], kx, ky, 0.014, 0.025, 0.017, 0.0, 6)


PITCH = math.radians(38.0)
CP, SP, TPI = math.cos(PITCH), math.sin(PITCH), math.tan(PITCH)
RZ0, RX0 = 2.86, 4.72
RY = 4.74
DECK = 0.14


def zu(x):
    return RZ0 + (RX0 - abs(x)) * TPI


def RP(sg, s, n, y):
    return Vector((sg * (RX0 - s * CP + n * SP), y, RZ0 + s * SP + n * CP))


def s_ridge(n):
    return (RX0 + n * SP) / CP


def s_at_x(x, n):
    return (RX0 - x + n * SP) / CP


def beam(bm, p0, p1, w, h, r, up, m=2, re=0.0):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    L = d.length
    zt = d.normalized()
    yt = Vector(up)
    yt = (yt - zt * yt.dot(zt)).normalized()
    xt = yt.cross(zt)
    M = Matrix(((xt.x, yt.x, zt.x, p0.x), (xt.y, yt.y, zt.y, p0.y), (xt.z, yt.z, zt.z, p0.z), (0, 0, 0, 1)))
    if re > 0:
        rings = [(w * 0.5, h * 0.5, r * 0.5, 0.0), (w * 0.86, h * 0.86, r * 0.86, re * 0.3), (w, h, r, re),
                 (w, h, r, L - re), (w * 0.86, h * 0.86, r * 0.86, L - re * 0.3), (w * 0.5, h * 0.5, r * 0.5, L)]
    else:
        rings = [(w, h, r, 0.0), (w, h, r, L)]
    return loft(rings, m, bm=bm, matrix=M)


def roof_planks(B, sg):
    s1 = s_ridge(0.0)
    pw, gap, ch = 0.27, 0.012, 0.016
    Uw = Vector((-sg * CP, 0, SP))
    Nw = Vector((sg * SP, 0, CP))
    s = 0.0
    while s < s1 - 1e-4:
        a, b = s, min(s + pw - gap, s1)
        for y0, y1 in ((-RY, RY),):
            oface(B["SH_Oak"], [RP(sg, a + ch, 0.0, y0), RP(sg, b - ch, 0.0, y0), RP(sg, b - ch, 0.0, y1), RP(sg, a + ch, 0.0, y1)], -Nw)
            oface(B["SH_Oak"], [RP(sg, a, 0.008, y0), RP(sg, a + ch, 0.0, y0), RP(sg, a + ch, 0.0, y1), RP(sg, a, 0.008, y1)], -Nw - Uw * 0.5)
            oface(B["SH_Oak"], [RP(sg, b - ch, 0.0, y0), RP(sg, b, 0.008, y0), RP(sg, b, 0.008, y1), RP(sg, b - ch, 0.0, y1)], -Nw + Uw * 0.5)
        s += pw
    sb = s_ridge(0.014)
    oface(B["SH_Walnut"], [RP(sg, 0.0, 0.014, -RY), RP(sg, sb, 0.014, -RY), RP(sg, sb, 0.014, RY), RP(sg, 0.0, 0.014, RY)], -Nw)
    sd = s_ridge(DECK)
    oface(B["SH_Timber"], [RP(sg, 0.0, DECK, -RY), RP(sg, sd, DECK, -RY), RP(sg, sd, DECK, RY), RP(sg, 0.0, DECK, RY)], Nw)
    oface(B["SH_Walnut"], [RP(sg, 0.0, 0.0, -RY), RP(sg, 0.0, DECK, -RY), RP(sg, 0.0, DECK, RY), RP(sg, 0.0, 0.0, RY)], -Uw)




def shingle(bm, sg, s0, n0, y0, y1, prof):
    Uw = Vector((-sg * CP, 0, SP))
    Nw = Vector((sg * SP, 0, CP))
    A = [bm.verts.new(RP(sg, s0 + ds, n0 + dn, y0)) for ds, dn in prof]
    Bv = [bm.verts.new(RP(sg, s0 + ds, n0 + dn, y1)) for ds, dn in prof]
    qf(bm, A, (0, -1, 0))
    qf(bm, Bv, (0, 1, 0))
    m = len(prof)
    cx = sum(p[0] for p in prof) / m
    cy = sum(p[1] for p in prof) / m
    for i in range(1, m):
        j = (i + 1) % m
        mx = (prof[i][0] + prof[j][0]) / 2 - cx
        my = (prof[i][1] + prof[j][1]) / 2 - cy
        qf(bm, [A[i], A[j], Bv[j], Bv[i]], Uw * mx + Nw * my)


def roof_shingles(B, sg, rng):
    step, plen, gap = 0.4, 0.95, 0.035
    smax = s_ridge(DECK)
    k = 0
    while True:
        s0 = 0.04 + k * step
        if s0 > smax - 0.12:
            break
        ws = min(0.56, smax + 0.02 - s0)
        prof = [(0.0, 0.0), (ws, 0.0), (ws, 0.016), (0.0, 0.1)]
        mat = "SH_Honey" if k % 4 == 3 else "SH_Walnut"
        y = -RY - (plen / 2 if k % 2 else 0.0)
        while y < RY:
            a, b = max(y, -RY), min(y + plen - gap, RY)
            if b - a > 0.08:
                shingle(B[mat], sg, s0, DECK - 0.006, a, b, prof)
            y += plen
        k += 1


def truss(B, y, tie_x, gable=False):
    tz0, tz1 = 2.8, 3.02
    tw = 0.26 if gable else 0.22
    beam(B["SH_Timber"], (-tie_x, y, (tz0 + tz1) / 2), (tie_x, y, (tz0 + tz1) / 2), tw, tz1 - tz0, 0.05, (0, 0, 1), re=0.14)
    apex = zu(0.0)
    beam(B["SH_Timber"], (0.0, y, tz1 - 0.02), (0.0, y, apex + 0.01), 0.2, tw - 0.02, 0.04, (0, 1, 0))
    for sg in (-1, 1):
        a = RP(sg, s_at_x(4.45, -0.1), -0.1, y)
        b = RP(sg, s_ridge(-0.1), -0.1, y)
        beam(B["SH_Timber"], a, b, tw - 0.03, 0.2, 0.04, Vector((sg * SP, 0, CP)), m=1)
        top = RP(sg, s_at_x(2.0, -0.1), -0.1, y)
        beam(B["SH_Timber"], (0.0, y, 3.45), top, 0.15, tw - 0.06, 0.035, (0, 1, 0), m=1)


def gable_boards(B, gy):
    zb = 2.98
    xt = RX0 - (zb - RZ0 - 0.01) / TPI
    for face, yv in ((1, gy * 4.5 + gy * 0.08), (-1, gy * 4.5 - gy * 0.08)):
        want = Vector((0, gy * face, 0))
        vg = yv - want.y * 0.011
        bw = 0.25
        edges = []
        x = 0.0
        while x < xt - 1e-4:
            edges.append((x, min(x + bw, xt)))
            x += bw
        edges = [(-b, -a) for a, b in reversed(edges)] + edges

        def zt(xx):
            return zu(xx) + 0.008 / CP
        ch = 0.016
        for a, b in edges:
            if b - a < 0.05:
                continue
            oface(B["SH_Walnut"], [(a, vg, zb), (a + ch, yv, zb), (a + ch, yv, zt(a + ch)), (a, vg, zt(a))], want)
            oface(B["SH_Honey"], [(a + ch, yv, zb), (b - ch, yv, zb), (b - ch, yv, zt(b - ch)), (a + ch, yv, zt(a + ch))], want)
            oface(B["SH_Walnut"], [(b - ch, yv, zb), (b, vg, zb), (b, vg, zt(b)), (b - ch, yv, zt(b - ch))], want)
            if abs(a) < 1e-6 or abs(b) < 1e-6:
                pass


def build_roof(B, rng):
    for sg in (-1, 1):
        roof_planks(B, sg)
        roof_shingles(B, sg, rng)
        Nw = Vector((sg * SP, 0, CP))
        beam(B["SH_Walnut"], (sg * (RX0 + 0.03), -RY - 0.02, RZ0 + 0.06), (sg * (RX0 + 0.03), RY + 0.02, RZ0 + 0.06),
             0.09, 0.3, 0.035, (0, 0, 1), m=2)
        beam(B["SH_Walnut"], (sg * 4.655, -4.62, 2.9), (sg * 4.655, 4.62, 2.9), 0.09, 0.22, 0.03, (0, 0, 1), m=1)
        for gy in (-1, 1):
            a = RP(sg, 0.08, 0.09, gy * 4.76)
            b = RP(sg, s_ridge(0.09) + 0.06, 0.09, gy * 4.76)
            beam(B["SH_Walnut"], a, b, 0.08, 0.34, 0.035, Nw, m=2, re=0.0)
        Uw = Vector((-sg * CP, 0, SP))
        Vw = Nw.cross(Uw)
        R = Matrix(((Uw.x, Vw.x, Nw.x, 0), (Uw.y, Vw.y, Nw.y, 0), (Uw.z, Vw.z, Nw.z, 0), (0, 0, 0, 1)))
        for j in range(3):
            s = rng.uniform(0.4, 2.6)
            y = rng.uniform(-3.8, 3.8)
            for q in range(3):
                ds, dy = rng.uniform(-0.18, 0.18), rng.uniform(-0.25, 0.25)
                r = rng.uniform(0.13, 0.2)
                c = RP(sg, s + ds, DECK + 0.1 + 0.012 * q, y + dy)
                ell(B["SH_Moss"], c, (r, r * 1.2, 0.055), R, 7, 3)
    zr = RP(1, s_ridge(DECK), DECK, 0.0).z
    beam(B["SH_Timber"], (0.0, -4.76, zr + 0.03), (0.0, 4.76, zr + 0.03), 0.3, 0.24, 0.1, (0, 0, 1), m=2, re=0.1)
    beam(B["SH_Timber"], (0.0, -4.54, zu(0.0) - 0.12), (0.0, 4.54, zu(0.0) - 0.12), 0.24, 0.28, 0.05, (0, 0, 1), m=1)
    for gy in (-1, 1):
        truss(B, gy * 4.5, 4.62, gable=True)
        gable_boards(B, gy)
        lathe_bm([(0.0, 0.0), (0.07, 0.0), (0.085, 0.06), (0.05, 0.14), (0.06, 0.2), (0.0, 0.24)], 10, bm=B["SH_Timber"],
                 matrix=Matrix.Translation((0.0, gy * 4.76, zr + 0.1)))
        ell(B["SH_Gold"], (0.0, gy * 4.76, zr + 0.36), (0.08, 0.08, 0.09), None, 10, 6)
    for y in (-3.0, 0.0, 3.0):
        truss(B, y, 4.45)


PIECES = [
    ("K1", "ZoneKitFloor", build_floor, 101, (0.6, 0.4, 0.0), 50.0),
    ("K2", "ZoneKitWall", build_wall, 102, (0.9, -0.9, 0.0), 40.0),
    ("K3", "ZoneKitWallWindow", build_window, 103, (1.0, -0.9, 0.0), 40.0),
    ("K4", "ZoneKitWallDoor", build_door, 104, (0.0, -1.0, 0.0), 40.0),
    ("K5", "ZoneKitCorner", build_corner, 105, (0.75, -0.5, 0.0), 40.0),
    ("K6", "ZoneKitTrimIvy", build_trim, 106, (0.9, -0.9, 0.0), 50.0),
    ("K7", "ZoneKitRoof", build_roof, 107, (1.5, -1.0, 0.0), 40.0),
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
    if "nopreview" in flags:
        return
    if key == "K6":
        make("CtxWall", build_wall, 102, 40.0)
        preview(ob, out, dloc, target=(0.0, 0.0, 1.9), ortho=4.6)
    elif key == "K5":
        preview(ob, out, dloc, ortho=3.6)
    elif key == "K3":
        preview(ob, out, dloc, target=(0.0, 0.0, 1.45), ortho=3.6)
    else:
        preview(ob, out, dloc)


def place(name, fn, seed, ang, loc, rz=0.0):
    ob = make(name, fn, seed, ang)
    ob.location = loc
    ob.rotation_euler.z = math.radians(rz)
    return ob


def tri_list(obs):
    bpy.context.view_layer.update()
    T = []
    for pid, ob in enumerate(obs):
        me = ob.data
        me.calc_loop_triangles()
        mw = ob.matrix_world
        V = [mw @ v.co for v in me.vertices]
        mats = [m.name if m else "-" for m in me.materials]
        for lt in me.loop_triangles:
            a, b, c = (V[i] for i in lt.vertices)
            n = (b - a).cross(c - a)
            if n.length < 2e-7:
                continue
            n.normalize()
            lo = Vector((min(a.x, b.x, c.x), min(a.y, b.y, c.y), min(a.z, b.z, c.z)))
            hi = Vector((max(a.x, b.x, c.x), max(a.y, b.y, c.y), max(a.z, b.z, c.z)))
            T.append((pid, mats[lt.material_index], a, b, c, n, n.dot(a), lo, hi))
    return T


def _inside(p, t, eps):
    a, b, c, n = t[2], t[3], t[4], t[5]
    p = p - n * (n.dot(p) - t[6])
    for u, v in ((a, b), (b, c), (c, a)):
        e = v - u
        if n.dot(e.cross(p - u)) < eps * e.length:
            return None
    return p


def _samples(t):
    c = (t[2] + t[3] + t[4]) / 3
    return [c] + [c + (v - c) * 0.75 for v in (t[2], t[3], t[4])]


def _hit(t, s, eps):
    for p, q in ((t, s), (s, t)):
        for x in _samples(p):
            h = _inside(x, q, eps)
            if h is not None and _inside(x, p, eps) is not None:
                return h
    return None


def overlaps(obs, label, tol=0.006, eps=0.0005, verbose=True):
    from mathutils.bvhtree import BVHTree
    T = tri_list(obs)
    bvh = BVHTree.FromPolygons([v for t in T for v in (t[2], t[3], t[4])],
                               [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(T))])
    buckets = {}
    for i, t in enumerate(T):
        n = t[5]
        buckets.setdefault((round(n.x * 20), round(n.y * 20), round(n.z * 20)), []).append(i)
    sb = {k: sorted(v, key=lambda i: T[i][6]) for k, v in buckets.items()}
    ds = {k: [T[i][6] for i in v] for k, v in sb.items()}
    groups = {}
    tot = {"internal": 0, "joint": 0, "samemat": 0, "hidden": 0}
    for k, lst in buckets.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    k2 = (k[0] + dx, k[1] + dy, k[2] + dz)
                    if k2 not in sb or k2 < k:
                        continue
                    L2, D2 = sb[k2], ds[k2]
                    for i in lst:
                        t = T[i]
                        for j in L2[bisect.bisect_left(D2, t[6] - tol):bisect.bisect_right(D2, t[6] + tol)]:
                            if k2 == k and j <= i:
                                continue
                            s = T[j]
                            if t[5].dot(s[5]) < 0.998:
                                continue
                            if any(t[7][q] > s[8][q] + tol or s[7][q] > t[8][q] + tol for q in range(3)):
                                continue
                            h = _hit(t, s, eps)
                            if h is None:
                                continue
                            if t[1] == s[1] and abs(t[6] - s[6]) < 2e-4:
                                tot["samemat"] += 1
                                continue
                            n = t[5]
                            st = h + n * (max(t[6], s[6]) - n.dot(h) + 0.0015)
                            loc, nh, idx, dist = bvh.ray_cast(st, n, 1.5)
                            if loc is not None and (nh.dot(n) > 0 or dist < 0.003):
                                tot["hidden"] += 1
                                continue
                            kind = "internal" if t[0] == s[0] else "joint"
                            tot[kind] += 1
                            na, nb = sorted((obs[t[0]].name, obs[s[0]].name))
                            key = (kind, na, nb, "/".join(sorted((t[1], s[1]))))
                            g = groups.setdefault(key, [0, 9.0, -9.0, None])
                            g[0] += 1
                            g[1] = min(g[1], h.z)
                            g[2] = max(g[2], h.z)
                            g[3] = g[3] or tuple(round(x, 3) for x in h)
    print("OVERLAP %-22s tris=%6d visible_internal=%d visible_joint=%d hidden=%d samemat=%d" % (
        label, len(T), tot["internal"], tot["joint"], tot["hidden"], tot["samemat"]))
    if verbose:
        for key, g in sorted(groups.items(), key=lambda kv: -kv[1][0])[:30]:
            print("   %-8s %-10s x %-10s %-26s n=%4d z=%.3f..%.3f e.g.%s" % (key[0], key[1], key[2], key[3], g[0], g[1], g[2], g[3]))
    return tot


SPEC = {
    "Floor": (build_floor, 101, 50.0),
    "Wall": (build_wall, 102, 40.0),
    "Window": (build_window, 103, 40.0),
    "Door": (build_door, 104, 40.0),
    "Corner": (build_corner, 105, 40.0),
    "Trim": (build_trim, 106, 50.0),
    "Roof": (build_roof, 107, 40.0),
}


def put(kind, loc, rz=0.0, tag=""):
    fn, seed, ang = SPEC[kind]
    return place(kind + tag, fn, seed, ang, loc, rz)


def lot_objects(roof=True, extra_corners=False):
    obs = []
    for x in (-3.0, 0.0, 3.0):
        for y in (-3.0, 0.0, 3.0):
            obs.append(put("Floor", (x, y, 0.0)))
    for x, kind in ((-3.0, "Wall"), (0.0, "Window"), (3.0, "Wall")):
        obs.append(put(kind, (x, 4.5, 0.0)))
        obs.append(put("Trim", (x, 4.5, 0.0)))
    for sx, rz in ((4.5, -90.0), (-4.5, 90.0)):
        for y in (-3.0, 0.0, 3.0):
            obs.append(put("Wall", (sx, y, 0.0), rz))
            obs.append(put("Trim", (sx, y, 0.0), rz))
    for cx in (-4.5, 4.5):
        for cy in (-4.5, 4.5):
            obs.append(put("Corner", (cx, cy, 0.0)))
            if extra_corners:
                obs.append(put("Corner", (cx, cy, 0.0), 90.0, "B"))
    if roof:
        obs.append(put("Roof", (0.0, 0.0, 0.0)))
    return obs


def run_checks():
    total = 0
    for kind in SPEC:
        begin()
        r = overlaps([put(kind, (0.0, 0.0, 0.0))], "single " + kind)
        total += r["internal"] + r["joint"]
    for a, b, off, rz in (("Floor", "Floor", (3.0, 0.0, 0.0), 0.0), ("Floor", "Floor", (0.0, 3.0, 0.0), 0.0),
                          ("Wall", "Wall", (3.0, 0.0, 0.0), 0.0), ("Window", "Window", (3.0, 0.0, 0.0), 0.0),
                          ("Wall", "Window", (3.0, 0.0, 0.0), 0.0), ("Door", "Wall", (3.0, 0.0, 0.0), 0.0),
                          ("Trim", "Trim", (3.0, 0.0, 0.0), 0.0), ("Corner", "Corner", (0.0, 0.0, 0.0), 90.0)):
        begin()
        r = overlaps([put(a, (0.0, 0.0, 0.0)), put(b, off, rz, "B")], "pair %s x %s" % (a, b))
        total += r["joint"]
    begin()
    r = overlaps(lot_objects(extra_corners=True), "lot 9x9")
    print("CHECK_SUMMARY pieces+pairs=%d lot_joint=%d lot_internal=%d" % (total, r["joint"], r["internal"]))


def render_persp(path, loc, target, lens=20.0, res=(640, 640)):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("pcam")
    cd.lens = lens
    cd.clip_start = 0.05
    cd.clip_end = 200
    cam = bpy.data.objects.new("pcam", cd)
    sc.collection.objects.link(cam)
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def run_lot(out, tag="lot"):
    begin()
    lot_objects()
    setup_scene(floor=40)
    load_dragon((0.8, 1.2, 0.0), 200.0)
    load_dragon((-2.2, -6.4, 0.0), 160.0)
    cells = []
    shots = [
        ("ext_front", "p", (-9.5, -15.0, 4.2), (0.0, 0.0, 2.6), 26.0),
        ("ext_back", "p", (12.0, 13.5, 6.5), (0.0, 0.0, 2.8), 26.0),
        ("ext_iso", "o", (-35, 34), (0.0, 0.0, 2.6), 15.5),
        ("in_window", "p", (0.0, -3.6, 1.6), (0.0, 4.5, 1.75), 16.0),
        ("in_ceiling", "p", (1.2, -2.6, 1.6), (-0.6, 2.0, 4.6), 14.0),
        ("in_corner", "p", (-1.6, 1.4, 1.6), (-4.5, 4.5, 1.9), 18.0),
        ("in_window_close", "p", (0.5, 2.4, 1.6), (0.0, 4.5, 1.55), 22.0),
        ("ext_corner", "p", (6.6, 6.9, 1.9), (4.5, 4.5, 1.7), 24.0),
        ("ext_gable", "p", (1.5, -8.5, 1.6), (0.0, -4.5, 3.6), 20.0),
    ]
    for name, kind, a, tgt, p in shots:
        f = "%s_%s.png" % (tag, name)
        if kind == "p":
            render_persp(os.path.join(out, f), a, tgt, p)
        else:
            render(os.path.join(out, f), a[0], a[1], tgt, p)
        cells.append(f)
    contact_sheet(out, cells, os.path.join(out, "%s_sheet.png" % tag))


out, flags = cli()
if "check" in flags:
    run_checks()
    sys.exit(0)
keys = [k for k in ("K1", "K2", "K3", "K4", "K5", "K6", "K7") if k in flags]
if not keys and "lotonly" not in flags:
    keys = [p[0] for p in PIECES]
for k in keys:
    run_piece(k, out, flags)
if out and ("lot" in flags or "lotonly" in flags):
    run_lot(out)
