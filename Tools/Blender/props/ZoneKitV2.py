import sys, random, math
sys.path.insert(0, r"E:\GitHub\RunRunSimulator\Tools\Blender\props")
from env_kit_e2 import *

KITV2_DIR = os.path.join(MODELS_DIR, "KitV2")
V1_DIR = MODELS_DIR

EXT_MATS = {
    "SH_Plaster_Ext": "EFE3C4",
    "SH_Timber_Ext": "7B4D2C",
    "SH_Stone_Ext": "CFC7B6",
    "SH_Sill_Ext": "B9844C",
}

T, H, HU = 0.3, 2.7, 1.5
YI, YO = -0.15, 0.15
ZOC = 0.13
FR = 0.84
AC0, AC1 = 0.795, 0.885
CR0, CR1 = 0.875, 0.965
GT0, GT1 = 1.95, 2.07
TOP = 2.62
TP0 = 2.6
XM = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
E_END = 0.003

WHW, WZ0, WZ1, WFW = 0.52, 1.1, 2.14, 0.12
WZM = (WZ0 + WZ1) / 2
WRO = WHW + WFW
DHW, DH, DFW, DRISE, ND = 0.8, 2.2, 0.14, 0.2, 10
DRO = DHW + DFW

UE = HU - E_END
YB = YO - 0.006
YF = YO + 0.045
ST_TOP = 0.48
SOLE0, SOLE1 = 0.42, 0.54
RAIL0, RAIL1 = 0.98, 1.08
RAILC = (RAIL0 + RAIL1) / 2
HEAD0 = 2.44
PAN_TOP = 2.5
BULGE = 0.02


# ---------- interior (copia fiel de ZoneKit v1) ----------

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


def body_int(B, u0, u1, z0, z1, inner_caps=True):
    caps = [c for c, edge in (("-x", u0 > -HU + 1e-6), ("+x", u1 < HU - 1e-6)) if edge and inner_caps]
    obox(B["SH_Parchment"], u0, u1, YI, 0.0, z0, z1, ["-y", "-z", "+z"] + caps)
    obox(B["SH_Plaster_Ext"], u0, u1, 0.0, YO, z0, z1, ["-z", "+z"] + caps)


def spandrel_int(B, arch, ztop):
    for (u0, z0), (u1, z1) in zip(arch, arch[1:]):
        pts = [(u0, YI, z0), (u1, YI, z1), (u1, YI, ztop), (u0, YI, ztop)]
        out = []
        for p in pts:
            if not out or (Vector(p) - Vector(out[-1])).length > 1e-5:
                out.append(p)
        if (Vector(out[0]) - Vector(out[-1])).length < 1e-5:
            out.pop()
        if len(out) >= 3:
            oface(B["SH_Parchment"], out, (0, -1, 0))


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


def top_plate_int(B):
    xbar(B["SH_Timber"], -HU, HU, YI - 0.03, 0.0, TP0, H, 0.03)


def rosette(bm, u, z, y, side):
    rot = Matrix.Rotation(math.pi / 2 if side < 0 else -math.pi / 2, 4, "X")
    lathe_bm([(0.0, 0.0), (0.058, 0.0), (0.064, 0.016), (0.05, 0.032), (0.024, 0.04), (0.0, 0.042)], 10, bm=bm,
             matrix=Matrix.Translation((u, y, z)) @ rot)


def paw(bm, uc, zc, y, s=1.0):
    ell(bm, (uc, y, zc - 0.022 * s), (0.05 * s, 0.014, 0.04 * s), None, 10, 5)
    for du, dz, r in ((-0.06, 0.028, 0.02), (-0.023, 0.062, 0.021), (0.023, 0.062, 0.021), (0.06, 0.028, 0.02)):
        ell(bm, (uc + du * s, y, zc + dz * s), (r * s, 0.012, r * s * 1.12), None, 8, 4)


def wrect(o, r):
    return rrect(2 * (WHW + o), (WZ1 - WZ0) + 2 * o, r, 3, 0.0, WZM)


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


def int_wall(B, rng):
    w = Wall("x", -HU, HU, YI, -1, T, H, 0.0, 0.0)
    body_int(B, -HU, HU, 0.0, TOP)
    inner_run(B, -HU, HU)
    top_plate_int(B)
    wbox(B["SH_Timber"], (-0.1, YI - 0.045, CR1 - 0.01), (0.1, YI + 0.01, TP0 + 0.005), r=0.03, segs=2)
    for sgn in (1, -1):
        dz = 0.42
        rotbox(w, B["SH_Timber"], sgn * (0.1 + dz / 2), -0.02, GT0 - dz / 2, math.hypot(dz, dz) + 0.05, 0.035, 0.1,
               math.radians(45 * sgn), r=0.016)


def int_window(B, rng):
    ro = WRO - 0.03
    body_int(B, -HU, -ro, 0.0, TOP, False)
    body_int(B, ro, HU, 0.0, TOP, False)
    body_int(B, -ro, ro, 0.0, WZ0 - WFW + 0.03, False)
    body_int(B, -ro, ro, WZ1 + WFW - 0.03, TOP, False)
    inner_run(B, -HU, HU, with_girt=False)
    girt(B, -HU, -WRO + 0.02)
    girt(B, WRO - 0.02, HU)
    top_plate_int(B)
    ring(B["SH_Timber"], wrect(0.0, 0.08), wrect(WFW, 0.03), YI - 0.05, 0.0)
    ring(B["SH_Walnut"], wrect(WFW - 0.035, 0.03), wrect(WFW + 0.028, 0.035), YI - 0.072, 0.0)
    prism(B["SH_Glass"], wrect(0.006, 0.084), -0.012, 0.012)
    wbox(B["SH_Timber"], (-0.046, -0.062, WZ0 - 0.02), (0.046, 0.012, WZ1 + 0.02), r=0.026, segs=2)
    wbox(B["SH_Timber"], (-WHW - 0.02, -0.046, WZM - 0.046), (WHW + 0.02, 0.012, WZM + 0.046), r=0.024, segs=2)
    wbox(B["SH_Walnut"], (-0.078, -0.08, WZM - 0.078), (0.078, 0.0, WZM + 0.078), r=0.032, segs=2)
    ell(B["SH_Gold"], (0.0, -0.093, WZM), (0.03, 0.016, 0.03), None, 10, 5)
    wbox(B["SH_Walnut"], (-0.75, YI - 0.215, WZ0 - WFW - 0.05), (0.75, YI + 0.04, WZ0 - WFW + 0.03), r=0.03, segs=2)
    for sg in (-1, 1):
        wbox(B["SH_Walnut"], (sg * 0.5 - 0.04, YI - 0.15, WZ0 - WFW - 0.2), (sg * 0.5 + 0.04, YI - 0.02, WZ0 - WFW - 0.04),
             r=0.02, segs=1)
    flower_pot(B, 0.36, YI - 0.16, WZ0 - WFW + 0.026)
    wbox(B["SH_Walnut"], (-0.74, YI - 0.085, WZ1 + WFW - 0.02), (0.74, 0.0, WZ1 + WFW + 0.07), r=0.035, segs=2)


def int_door(B, rng):
    body_int(B, -HU, -DRO, 0.0, TOP)
    body_int(B, DRO, HU, 0.0, TOP)
    spandrel_int(B, door_contour(DFW)[1:-1], TOP)
    for u0, u1 in ((-HU, -DRO), (DRO, HU)):
        inner_run(B, u0, u1)
    top_plate_int(B)
    ring(B["SH_Timber"], door_contour(0.0), door_contour(DFW), YI - 0.045, 0.0, closed=False)
    ring(B["SH_Walnut"], door_contour(DFW - 0.04), door_contour(DFW + 0.014), YI - 0.065, 0.0, closed=False)
    for sg in (-1, 1):
        a, b = sg * (DHW + 0.012), sg * (DRO + 0.05)
        wbox(B["SH_Stone"], (min(a, b), YI - 0.09, 0.0), (max(a, b), 0.0, 0.4), r=0.05, segs=2)
        a, b = sg * (DHW + 0.012), sg * (DRO + 0.035)
        wbox(B["SH_Walnut"], (min(a, b), YI - 0.095, DH - 0.22), (max(a, b), 0.0, DH - 0.1), r=0.035, segs=2)
        rosette(B["SH_Walnut"], sg * (DHW + DFW * 0.42), DH + DFW * 0.42, YI - 0.062, -1)
    wbox(B["SH_Walnut"], (-0.12, YI - 0.085, DH + 0.06), (0.12, 0.0, TP0 + 0.01), r=0.035, segs=2)
    paw(B["SH_Gold"], 0.0, DH + 0.24, YI - 0.088)
    lantern(B, Vector((1.22, YI, DH)), (0, -1, 0))


# ---------- exterior v2 (estilo Fantasy Village) ----------

def orient(f, want):
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def close_sweep(bm, rings, cap=True):
    faces = []
    n = len(rings[0])
    for A, Bv in zip(rings, rings[1:]):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(bm.faces.new((A[k], A[k1], Bv[k1], Bv[k])))
    if cap:
        faces.append(bm.faces.new(list(reversed(rings[0]))))
        faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return faces


def beam_prof(y0, y1, z0, z1, c=0.022, sag_top=False, flat_back=True):
    pr = [(y0, z0, 1.0), (y1 - c, z0, 1.0), (y1 - c * 0.3, z0 + c * 0.3, 1.0), (y1, z0 + c, 1.0),
          (y1, z1 - c, 1.0 if sag_top else 0.0), (y1 - c * 0.3, z1 - c * 0.3, 1.0 if sag_top else 0.0),
          (y1 - c, z1, 1.0 if sag_top else 0.0), (y0, z1, 1.0 if sag_top else 0.0)]
    return pr


def bay_sag(supports, amp):
    sup = sorted(supports)

    def f(u):
        for a, b in zip(sup, sup[1:]):
            if a - 1e-6 <= u <= b + 1e-6:
                return -amp * math.sin(math.pi * (u - a) / (b - a))
        return 0.0
    return f


def xbeam(bm, u0, u1, prof, sag=None, n=None, wob=0.0, seed=0, shrink0=0.0, shrink1=0.0):
    n = n or max(2, int(round((u1 - u0) / 0.25)))
    rng = random.Random(seed)
    ph1, ph2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    us = [u0 + (u1 - u0) * i / n for i in range(n + 1)]
    if shrink0 > 0:
        us.insert(1, u0 + 0.035)
    if shrink1 > 0:
        us.insert(len(us) - 1, u1 - 0.035)
    n = len(us) - 1
    yc = sum(p[0] for p in prof) / len(prof)
    zc = sum(p[1] for p in prof) / len(prof)
    rings = []
    for i, u in enumerate(us):
        dz = sag(u) if sag else 0.0
        dy = wob * math.sin(u * 3.1 + ph1)
        dzw = wob * 0.8 * math.sin(u * 2.3 + ph2)
        s = 1.0
        if i == 0 and shrink0 > 0:
            s = 1.0 - shrink0
        if i == n and shrink1 > 0:
            s = 1.0 - shrink1
        ring_v = []
        for y, z, k in prof:
            yy = y + (dy if y > yc else 0.0)
            zz = z + dz * k + dzw * k
            if s < 1.0:
                yy = yc + (yy - yc) * s if y > yc else yy
                zz = zc + (zz - zc) * s
            ring_v.append(bm.verts.new((u, yy, zz)))
        rings.append(ring_v)
    close_sweep(bm, rings)
    return bm


def zpost(bm, prof_uy, z0, z1, n=6, bow=0.0, seed=0):
    rng = random.Random(seed)
    ph = rng.uniform(0, 6.28)
    rings = []
    for i in range(n + 1):
        z = z0 + (z1 - z0) * i / n
        t = (z - z0) / (z1 - z0)
        du = bow * math.sin(math.pi * t) + bow * 0.35 * math.sin(6.0 * t + ph)
        rings.append([bm.verts.new((u + du * k, y, z)) for u, y, k in prof_uy])
    close_sweep(bm, rings)
    return bm


def post_prof(u0, u1, y0, y1, c=0.024, chamfer_l=True, chamfer_r=True, k=1.0):
    pr = []
    if chamfer_l:
        pr += [(u0, y0, k), (u0, y1 - c, k), (u0 + c * 0.3, y1 - c * 0.3, k), (u0 + c, y1, k)]
    else:
        pr += [(u0, y0, 0.0), (u0, y1, 0.0)]
    if chamfer_r:
        pr += [(u1 - c, y1, k), (u1 - c * 0.3, y1 - c * 0.3, k), (u1, y1 - c, k), (u1, y0, k)]
    else:
        pr += [(u1, y1, 0.0), (u1, y0, 0.0)]
    return pr


def bezier(p0, p1, p2, n):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


def brace(bm, pts, w=0.12, y0=YB, y1=YO + 0.04, c=0.022, taper=0.0):
    rings = []
    n = len(pts)
    for i, (u, z) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        tu, tz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tu, tz)
        tu, tz = tu / L, tz / L
        nu, nz = -tz, tu
        hw = w / 2 * (1.0 - taper * math.sin(math.pi * i / (n - 1)))
        prof = [(-hw, y0), (-hw, y1 - c), (-hw + c, y1), (hw - c, y1), (hw, y1 - c), (hw, y0)]
        rings.append([bm.verts.new((u + nu * a_, y, z + nz * a_)) for a_, y in prof])
    close_sweep(bm, rings)
    return bm


def panel(bm, u0, u1, z0, z1, b=BULGE, step=0.19, y=YO):
    nu = max(2, int(round((u1 - u0) / step)))
    nz = max(2, int(round((z1 - z0) / step)))
    V = {}
    for i in range(nu + 1):
        for j in range(nz + 1):
            s, t = i / nu, j / nz
            bb = b * (math.sin(math.pi * s) * math.sin(math.pi * t)) ** 0.75
            V[i, j] = bm.verts.new((u0 + (u1 - u0) * s, y + bb, z0 + (z1 - z0) * t))
    for i in range(nu):
        for j in range(nz):
            orient(bm.faces.new((V[i, j], V[i + 1, j], V[i + 1, j + 1], V[i, j + 1])), (0, 1, 0))
    return bm


def flat_strip(bm, u0, u1, z0, z1, y=YO):
    return oface(bm, [(u0, y, z0), (u1, y, z0), (u1, y, z1), (u0, y, z1)], (0, 1, 0))


def spandrel_ext(bm, zfun, u0, u1, ztop, n=12, y=YO):
    us = [u0 + (u1 - u0) * i / n for i in range(n + 1)]
    for a, b in zip(us, us[1:]):
        oface(bm, [(a, y, zfun(a)), (b, y, zfun(b)), (b, y, ztop), (a, y, ztop)], (0, 1, 0))


def pillow(bm, cu, cz, w, h, yb, yf, mapf=None, m=3):
    r = min(w, h) * 0.42
    rings_def = [(w, h, r, yb), (w, h, r, yf - 0.018), (w - 0.026, h - 0.026, r - 0.013, yf - 0.005),
                 (w - 0.07, h - 0.06, r - 0.033, yf)]
    rings = []
    for ww, hh, rr, y in rings_def:
        rings.append([(u, y, z) for u, z in rrect(ww, hh, rr, m, cu, cz)])
    if mapf:
        rings = [[mapf(p) for p in rg] for rg in rings]
    V = [[bm.verts.new(p) for p in rg] for rg in rings]
    cen = mapf((cu, yb, cz)) if mapf else (cu, yb, cz)
    out = mapf((cu, yf, cz)) if mapf else (cu, yf, cz)
    nrm = Vector(out) - Vector(cen)
    nrm.normalize()
    k = len(V[0])
    for A, Bv in zip(V, V[1:]):
        for i in range(k):
            j = (i + 1) % k
            f = bm.faces.new((A[i], A[j], Bv[j], Bv[i]))
            c = f.calc_center_median()
            rad = c - Vector(cen)
            rad = rad - nrm * rad.dot(nrm)
            orient(f, rad + nrm * 0.4)
    orient(bm.faces.new(V[-1]), nrm)
    return bm


def stone_row(B, segs, rng):
    rows = ((0.012, 0.222), (0.232, 0.442))
    for ri, (z0, z1) in enumerate(rows):
        for a, b in segs:
            u = a + 0.008
            first = True
            while u < b - 0.05:
                rem = b - 0.008 - u
                wd = rng.uniform(0.2, 0.3) if (ri == 1 and first) else rng.uniform(0.36, 0.56)
                first = False
                if rem < wd + 0.22:
                    wd = rem if rem < 0.62 else rem / 2
                if wd < 0.1:
                    break
                hh = (z1 - z0) - rng.uniform(0.0, 0.025)
                zc = (z0 + z1) / 2 + rng.uniform(-0.006, 0.006)
                pillow(B["SH_Stone_Ext"], u + wd / 2, zc, wd - 0.014, hh, YO - 0.012, YO + rng.uniform(0.03, 0.038))
                u += wd


def peg(B, u, z, y=YF):
    ell(B["SH_Sill_Ext"], (u, min(y, YF) - 0.004, z), (0.022, 0.009, 0.022), None, 8, 4)


def head_beam(B, sag, seed):
    xbeam(B["SH_Timber_Ext"], -UE, UE, beam_prof(-0.01, YF, HEAD0, H - 0.0005, c=0.026), sag=sag, n=14, wob=0.003, seed=seed)


def sole_beam(B, u0, u1, seed, s0=0.0, s1=0.0):
    xbeam(B["SH_Timber_Ext"], u0, u1, beam_prof(YB, YO + 0.04, SOLE0, SOLE1, c=0.022), n=max(2, int((u1 - u0) / 0.3)),
          wob=0.004, seed=seed, shrink0=s0, shrink1=s1)


def rail(B, u0, u1, sag, seed, s0=0.0, s1=0.0):
    xbeam(B["SH_Timber_Ext"], u0, u1, beam_prof(YB, YO + 0.038, RAIL0, RAIL1, c=0.022, sag_top=True), sag=sag,
          n=max(2, int((u1 - u0) / 0.25)), wob=0.003, seed=seed, shrink0=s0, shrink1=s1)


def half_posts(B, seed):
    zb, zt = SOLE1 - 0.03, HEAD0 + 0.04
    zpost(B["SH_Timber_Ext"], post_prof(-UE, -UE + 0.09, YB, YF, chamfer_l=False), zb, zt, n=2)
    zpost(B["SH_Timber_Ext"], post_prof(UE - 0.09, UE, YB, YF, chamfer_r=False), zb, zt, n=2)


def backing(B, segs):
    for a, b in segs:
        flat_strip(B["SH_Plaster_Ext"], a, b, 0.0, ST_TOP)


def arch_brace(B, p0, p2, bow):
    mu, mz = (p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2
    du, dz = p2[0] - p0[0], p2[1] - p0[1]
    L = math.hypot(du, dz)
    nu, nz = -dz / L, du / L
    p1 = (mu + nu * bow, mz + nz * bow)
    pts = bezier(p0, p1, p2, 9)
    brace(B["SH_Timber_Ext"], pts)
    return pts


def ext_wall(B, rng):
    backing(B, [(-HU, HU)])
    stone_row(B, [(-HU, HU)], rng)
    for a, b in ((-HU, 0.0), (0.0, HU)):
        panel(B["SH_Plaster_Ext"], a, b, ST_TOP, RAILC)
        panel(B["SH_Plaster_Ext"], a, b, RAILC, PAN_TOP)
    sole_beam(B, -UE, UE, 11)
    rail(B, -UE, UE, bay_sag((-HU, 0.0, HU), 0.01), 12)
    head_beam(B, bay_sag((-HU, 0.0, HU), 0.02), 13)
    half_posts(B, 14)
    zpost(B["SH_Timber_Ext"], post_prof(-0.1, 0.1, YB, YF), SOLE1 - 0.03, HEAD0 + 0.04, n=6, bow=0.006, seed=15)
    for sg in (-1, 1):
        arch_brace(B, (sg * 1.36, RAIL1 - 0.03), (sg * 0.13, HEAD0 - 0.03), -sg * 0.2)
    for z in ((SOLE0 + SOLE1) / 2, RAILC, HEAD0 + 0.11):
        for du in (-0.045, 0.045):
            peg(B, du, z)


def rr_contour(hw, zb, zt, r, m, ntop):
    pts = []
    cs = ((hw - r, zb + r, 270), (hw - r, zt - r, 0))
    for cx, cz, a0 in cs:
        for j in range(m + 1):
            a = math.radians(a0 + 90 * j / m)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    for k in range(1, ntop + 1):
        pts.append(((hw - r) - 2 * (hw - r) * k / (ntop + 1), zt))
    for cx, cz, a0 in ((-(hw - r), zt - r, 90), (-(hw - r), zb + r, 180)):
        for j in range(m + 1):
            a = math.radians(a0 + 90 * j / m)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def ring2(bm, inner, outer, y0, y1, c=0.02, closed=True):
    n = len(inner)
    IF, OF = [], []
    for I, O in zip(inner, outer):
        d = math.hypot(O[0] - I[0], O[1] - I[1])
        t = min(0.35, c / max(d, 1e-6))
        IF.append((I[0] + (O[0] - I[0]) * t, I[1] + (O[1] - I[1]) * t))
        OF.append((O[0] + (I[0] - O[0]) * t, O[1] + (I[1] - O[1]) * t))
    L = [[bm.verts.new((u, y0, z)) for u, z in inner],
         [bm.verts.new((u, y1 - c, z)) for u, z in inner],
         [bm.verts.new((u, y1, z)) for u, z in IF],
         [bm.verts.new((u, y1, z)) for u, z in OF],
         [bm.verts.new((u, y1 - c, z)) for u, z in outer],
         [bm.verts.new((u, y0, z)) for u, z in outer]]
    for i in (range(n) if closed else range(n - 1)):
        j = (i + 1) % n
        mi = Vector(((inner[i][0] + inner[j][0]) / 2, 0, (inner[i][1] + inner[j][1]) / 2))
        mo = Vector(((outer[i][0] + outer[j][0]) / 2, 0, (outer[i][1] + outer[j][1]) / 2))
        din = (mi - mo).normalized()
        wants = [din, din + Vector((0, 1, 0)), Vector((0, 1, 0)), -din + Vector((0, 1, 0)), -din, Vector((0, -1, 0))]
        for q in range(6):
            A, Bv = L[q], L[(q + 1) % 6]
            qf(bm, [A[i], A[j], Bv[j], Bv[i]], wants[q])
    if not closed:
        for idx, want in ((0, (0, 0, -1)), (n - 1, (0, 0, -1))):
            pass
    return bm


W_AP, W_SP, W_US = 2.47, 2.26, WRO


def w_arch(u):
    t = min(1.0, abs(u) / W_US)
    return W_AP - (W_AP - W_SP) * t * t


def ext_window(B, rng):
    backing(B, [(-HU, HU)])
    stone_row(B, [(-HU, HU)], rng)
    for sg in (-1, 1):
        a, b = sorted((sg * 0.6, sg * HU))
        panel(B["SH_Plaster_Ext"], a, b, ST_TOP, RAILC)
        panel(B["SH_Plaster_Ext"], a, b, RAILC, PAN_TOP)
    panel(B["SH_Plaster_Ext"], -0.6, 0.6, ST_TOP, WZ0 - WFW + 0.03, b=0.01)
    spandrel_ext(B["SH_Plaster_Ext"], lambda u: w_arch(u) - 0.03, -0.6, 0.6, PAN_TOP)
    sole_beam(B, -UE, UE, 21)
    for sg in (-1, 1):
        a, b = sorted((sg * (WRO - 0.02), sg * UE))
        rail(B, a, b, bay_sag((a, b), 0.008), 22 + sg)
    head_beam(B, bay_sag((-HU, HU), 0.022), 23)
    half_posts(B, 24)
    inner = rr_contour(WHW, WZ0, WZ1, 0.08, 3, 11)
    outer = rr_contour(WRO, WZ0 - WFW, WZ1 + WFW, 0.03, 3, 11)
    outer = [(u, max(z, w_arch(u)) if z > WZM else z) for u, z in outer]
    ring2(B["SH_Timber_Ext"], inner, outer, -0.004, YF, c=0.022)
    wbox(B["SH_Timber_Ext"], (-0.046, -0.012, WZ0 - 0.02), (0.046, 0.062, WZ1 + 0.02), r=0.026, segs=2)
    wbox(B["SH_Timber_Ext"], (-WHW - 0.02, -0.012, WZM - 0.046), (WHW + 0.02, 0.062, WZM + 0.046), r=0.024, segs=2)
    wbox(B["SH_Sill_Ext"], (-0.07, 0.0, WZM - 0.07), (0.07, 0.078, WZM + 0.07), r=0.034, segs=2)
    xbeam(B["SH_Sill_Ext"], -0.8, 0.8, beam_prof(YB, YO + 0.08, 0.9, 1.045, c=0.034), n=6, wob=0.002, seed=25,
          shrink0=0.35, shrink1=0.35)
    for sg in (-1, 1):
        u = sg * 0.48
        prof = [(YB, 0.905), (YO + 0.066, 0.905), (YO + 0.064, 0.875), (YO + 0.05, 0.835), (YO + 0.026, 0.8),
                (YB, 0.77)]
        rings = []
        for uu in (u - 0.05, u + 0.05):
            rings.append([B["SH_Timber_Ext"].verts.new((uu, y, z)) for y, z in prof])
        close_sweep(B["SH_Timber_Ext"], rings)
        a, b = sorted((sg * 1.37, sg * (WRO + 0.06)))
        arch_brace(B, (sg * 1.37, RAIL1 - 0.03), (sg * (WRO + 0.05), HEAD0 - 0.04), -sg * 0.16)
    ell(B["SH_Sill_Ext"], (0.0, YF - 0.004, W_AP - 0.1), (0.05, 0.012, 0.05), None, 10, 5)


D_SP, D_RISE = 2.25, 0.21
D_ARCH = seg_arch(DRO, D_SP, D_RISE, 14)


def d_arch(u):
    c = DRO
    s = D_RISE
    R = (c * c + s * s) / (2 * s)
    zc = D_SP + s - R
    return zc + math.sqrt(max(R * R - u * u, 0.0))


def ext_door(B, rng):
    for sg in (-1, 1):
        a, b = sorted((sg * 0.88, sg * HU))
        backing(B, [(a, b)])
        stone_row(B, [sorted((sg * (DRO + 0.05), sg * HU))], rng)
        panel(B["SH_Plaster_Ext"], a, b, ST_TOP, RAILC)
        panel(B["SH_Plaster_Ext"], a, b, RAILC, PAN_TOP)
        a2, b2 = sorted((sg * (DRO - 0.02), sg * UE))
        sole_beam(B, a2, b2, 31 + sg)
        rail(B, a2, b2, bay_sag((a2, b2), 0.006), 33 + sg)
    spandrel_ext(B["SH_Plaster_Ext"], lambda u: d_arch(u) - 0.03, -0.88, 0.88, PAN_TOP)
    head_beam(B, bay_sag((-HU, HU), 0.022), 35)
    half_posts(B, 36)
    inner = [(-DHW, 0.0)] + [(-DHW + 2 * DHW * k / 14, DH) for k in range(15)] + [(DHW, 0.0)]
    outer = [(-DRO, 0.0)] + D_ARCH + [(DRO, 0.0)]
    ring2(B["SH_Timber_Ext"], inner, outer, -0.004, YF, c=0.024, closed=False)
    for sg in (-1, 1):
        a, b = sg * (DHW + 0.012), sg * (DRO + 0.05)
        pillow(B["SH_Stone_Ext"], (a + b) / 2, 0.21, abs(b - a) + 0.02, 0.42, -0.004, YO + 0.07, m=3)
        wbox(B["SH_Stone_Ext"], (min(a, b) + 0.01, -0.004, 0.0), (max(a, b) - 0.01, YO + 0.03, 0.4), r=0.04, segs=2)
        a, b = sg * (DHW + 0.012), sg * (DRO + 0.035)
        xbeam(B["SH_Timber_Ext"], min(a, b), max(a, b), beam_prof(-0.004, YO + 0.07, DH - 0.22, DH - 0.1, c=0.03), n=2,
              shrink0=0.12 if sg < 0 else 0.0, shrink1=0.12 if sg > 0 else 0.0)
        u0, u1 = sorted((sg * (DRO + 0.04), sg * 1.42))
        arch_brace(B, (sg * 1.42, HEAD0 - 0.45), (sg * (DRO + 0.04), HEAD0 - 0.02), sg * 0.1)

    wbox(B["SH_Timber_Ext"], (-0.12, -0.004, DH + 0.05), (0.12, YO + 0.07, H - 0.03), r=0.04, segs=2)
    paw(B["SH_Sill_Ext"], 0.0, DH + 0.24, YO + 0.064, 0.95)


def corner_stones(B, rng):
    wbox(B["SH_Stone_Ext"], (-0.178, -0.178, -0.02), (0.178, 0.178, 0.44), r=0.04, segs=2)
    for k in range(4):
        R = Matrix.Rotation(math.pi / 2 * k, 4, "Z")

        def mp(p, R=R):
            return tuple(R @ Vector((p[0], -p[1], p[2])))
        for zc, hh, row in ((0.11, 0.2, ((-0.088, 0.17), (0.088, 0.17))),
                            (0.325, 0.2, ((-0.13, 0.08), (0.0, 0.17), (0.13, 0.08)))):
            for u, wd in row:
                pillow(B["SH_Stone_Ext"], u, zc, wd - 0.012, hh - 0.014, 0.17, 0.199, mapf=mp, m=2)


def build_corner(B, rng):
    corner_stones(B, rng)
    tb = B["SH_Timber_Ext"]
    loft([(0.33, 0.33, 0.1, 0.42), (0.345, 0.345, 0.105, 1.55), (0.335, 0.335, 0.1, 2.62)], 3, bm=tb)
    loft([(0.36, 0.36, 0.07, SOLE0 - 0.01), (0.39, 0.39, 0.085, SOLE0 + 0.015), (0.39, 0.39, 0.085, SOLE1 - 0.01),
          (0.36, 0.36, 0.07, SOLE1 + 0.01)], 3, bm=tb)
    loft([(0.355, 0.355, 0.075, RAIL0 - 0.005), (0.38, 0.38, 0.085, RAIL0 + 0.018), (0.38, 0.38, 0.085, RAIL1 - 0.018),
          (0.355, 0.355, 0.075, RAIL1 + 0.005)], 3, bm=tb)
    loft([(0.36, 0.36, 0.075, HEAD0 - 0.01), (0.395, 0.395, 0.09, HEAD0 + 0.03), (0.395, 0.395, 0.09, H - 0.02),
          (0.4, 0.4, 0.095, H + 0.02), (0.4, 0.4, 0.095, H + 0.06), (0.37, 0.37, 0.09, H + 0.105),
          (0.29, 0.29, 0.08, H + 0.137), (0.16, 0.16, 0.06, 2.85)], 3, bm=tb)
    for k in range(4):
        R = Matrix.Rotation(math.pi / 2 * k, 4, "Z")
        for z in ((SOLE0 + SOLE1) / 2, (RAIL0 + RAIL1) / 2, HEAD0 + 0.13):
            for du in (-0.07, 0.07):
                p = R @ Vector((du, -0.191, z))
                ell(B["SH_Sill_Ext"], tuple(p), (0.02, 0.008, 0.02), R, 8, 4)
    ell(B["SH_Sill_Ext"], (0.0, 0.0, 2.837), (0.07, 0.07, 0.012), None, 10, 3)


def build_wall(B, rng):
    int_wall(B, rng)
    ext_wall(B, rng)


def build_window(B, rng):
    int_window(B, rng)
    ext_window(B, rng)


def build_door(B, rng):
    int_door(B, rng)
    ext_door(B, rng)


PIECES = {
    "W": ("ZoneKitWall_v2", build_wall, 202, "ZoneKitWall"),
    "N": ("ZoneKitWallWindow_v2", build_window, 203, "ZoneKitWallWindow"),
    "D": ("ZoneKitWallDoor_v2", build_door, 204, "ZoneKitWallDoor"),
    "C": ("ZoneKitCorner_v2", build_corner, 205, "ZoneKitCorner"),
}


def begin_v2():
    begin()
    for k, v in EXT_MATS.items():
        add_mat(k, v)


def box_uv(ob):
    me = ob.data
    uv = me.uv_layers.new(name="UVMap")
    for p in me.polygons:
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if ax == 1:
                uvv = (-co.x if n.y > 0 else co.x, co.z)
            elif ax == 0:
                uvv = (co.y if n.x > 0 else -co.y, co.z)
            else:
                uvv = (co.x, co.y if n.z > 0 else -co.y)
            uv.data[li].uv = uvv


def make(name, fn, seed):
    B = Bins()
    fn(B, random.Random(seed))
    objs = B.done(name, angle=40.0)
    ob = join_all(name, objs)
    PARTS.clear()
    box_uv(ob)
    return ob


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def bounds(ob):
    vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]


def export_v2(ob, flags):
    if "noexport" in flags:
        return
    os.makedirs(KITV2_DIR, exist_ok=True)
    path = os.path.join(KITV2_DIR, ob.name + ".fbx")
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"},
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                             apply_unit_scale=True, use_mesh_modifiers=True, bake_space_transform=True,
                             mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)
    print("EXPORTED", path)


def import_v1(name, loc):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(V1_DIR, name + ".fbx"))
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.parent is None:
            o.location = Vector(loc)
        if o.type == "MESH":
            for i, m in enumerate(o.data.materials):
                if m is None:
                    continue
                base = m.name.split(".")[0]
                if base in MATS:
                    o.data.materials[i] = MATS[base]
    bpy.context.view_layer.update()
    return [o for o in new if o.type == "MESH"]


VIEWS = (("ext34", 215, 22), ("ext_front", 180, 5), ("ext_iso", 150, 48),
         ("int34", 35, 22), ("int_front", 0, 5), ("side", 90, 8))


def light_for(az):
    ext = 90 < az % 360 < 270
    bpy.context.scene.display.light_direction = (-0.35, 0.45, 0.82) if ext else (0.35, -0.45, 0.82)


def piece_preview(ob, out, key):
    setup_scene()
    if key == "C":
        load_dragon((0.75, 0.6, 0.0), 160.0)
        tgt, orth = (0.0, 0.0, 1.35), 3.4
    else:
        load_dragon((1.75, 0.75, 0.0), 160.0)
        tgt, orth = (0.0, 0.0, 1.35), 4.1
    cells = []
    for tag, az, el in VIEWS:
        f = "%s_%s.png" % (ob.name, tag)
        light_for(az)
        render(os.path.join(out, f), az, el, tgt, orth)
        cells.append(f)
    contact_sheet(out, cells, os.path.join(out, ob.name + "_sheet.png"))


def run_piece(key, out, flags):
    name, fn, seed, v1 = PIECES[key]
    begin_v2()
    ob = make(name, fn, seed)
    report(ob)
    mn, mx = bounds(ob)
    print("TRIS", name, tris(ob))
    print("BOUNDS_V2", name, [round(x, 3) for x in mn], [round(x, 3) for x in mx])
    print("SLOTS", name, [m.name for m in ob.data.materials])
    export_v2(ob, flags)
    if out and "nopreview" not in flags:
        os.makedirs(out, exist_ok=True)
        piece_preview(ob, out, key)


def stack_rows(out, files, path, pad=8):
    imgs = [read_png(os.path.join(out, f)) for f in files]
    W = max(i.shape[1] for i in imgs) + 2 * pad
    Hh = sum(i.shape[0] for i in imgs) + pad * (len(imgs) + 1)
    canvas = np.ones((Hh, W, 4), dtype=np.float32)
    canvas[..., :3] = 0.16
    top = Hh - pad
    for im in imgs:
        h, w = im.shape[:2]
        canvas[top - h:top, pad:pad + w] = im
        top -= h + pad
    img = bpy.data.images.new("stack", W, Hh, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    print("SHEET", path)


ROW = (("C", -4.5), ("W", -3.0), ("N", 0.0), ("D", 3.0), ("C", 4.5))


def run_compare(out, uvcheck=False):
    begin_v2()
    v2 = []
    for key, x in ROW:
        name, fn, seed, v1 = PIECES[key]
        ob = make(name + "_%d" % int(x * 10), fn, seed)
        ob.location = (x, 0.0, 0.0)
        v2.append(ob)
    v1 = []
    for key, x in ROW:
        v1 += import_v1(PIECES[key][3], (x, 0.0, 0.0))
    setup_scene(floor=40)
    drag = load_dragon((-1.6, 1.1, 0.0), 160.0) + load_dragon((1.8, -1.0, 0.0), 20.0)
    res = (1700, 620)
    shots = (("ext", 180, 8, 10.6), ("int", 0, 8, 10.6), ("ext34", 205, 24, 11.0))
    files = []
    for tag, az, el, orth in shots:
        for lab, show, hide in (("v1", v1, v2), ("v2", v2, v1)):
            for o in show:
                o.hide_render = False
            for o in hide:
                o.hide_render = True
            f = "cmp_%s_%s.png" % (tag, lab)
            light_for(az)
            render(os.path.join(out, f), az, el, (0.0, 0.0, 1.4), orth, res=res)
            files.append(f)
    for o in v1:
        o.hide_render = True
    for o in v2:
        o.hide_render = False
    sc = bpy.context.scene
    grid = bpy.data.images.new("uvgrid", 1024, 1024)
    grid.generated_type = "UV_GRID"
    for name in ("SH_Plaster_Ext", "SH_Stone_Ext"):
        m = MATS[name]
        m.use_nodes = True
        nt = m.node_tree
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = grid
        nt.nodes.active = tex
    sc.display.shading.color_type = "TEXTURE"
    for o in drag:
        o.hide_render = True
    f = "cmp_uvcheck_v2.png"
    light_for(195)
    render(os.path.join(out, f), 195, 14, (0.0, 0.0, 1.4), 10.6, res=res)
    files.append(f)
    stack_rows(out, files, os.path.join(out, "KitV2_compare_sheet.png"))


out, flags = cli()
keys = [k for k in ("W", "N", "D", "C") if k in flags]
if not keys and "compareonly" not in flags:
    keys = ["W", "N", "D", "C"]
for k in keys:
    run_piece(k, out, flags)
if out and ("compare" in flags or "compareonly" in flags):
    run_compare(out)
