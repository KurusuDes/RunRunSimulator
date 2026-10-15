import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *
import random
import coplanar_check

SCRATCH = r"C:\Users\Docente\AppData\Local\Temp\claude\C--Users-Docente-Desktop-UnityProyects-RunRunSimulator\4d55ec4f-97d7-4ab7-b7aa-aab8024c682a\scratchpad"
OBJ_PATH = os.path.join(SCRATCH, "shop_env", "shop_env.obj")
BUILDING_FBX = os.path.join(MODELS_DIR, "ShopBuilding.fbx")

FLOOR = 0.5
TOP = 5.5
X0, X1, XC = 23.5, 36.5, 30.0
YF, YB = -7.0, -25.0
OVER = 0.5
GOVER = 0.45
TAN = 0.62
ZU0 = 5.72
PITCH = math.atan(TAN)
CP, SP = math.cos(PITCH), math.sin(PITCH)
YMIN, YMAX = YB - GOVER, YF + GOVER
SLEN = (XC - X0 + OVER) / CP
PLANK_T, DECK0, DECK1 = 0.045, 0.03, 0.16
GABLES = [dict(y_out=-7.08, y_in=-7.42, s=1), dict(y_out=-24.92, y_in=-24.58, s=-1)]
TRUSSES = [-11.0, -14.5, -18.25, -21.5]
OCULUS = (XC, 7.75, 0.45)

PARTS_BY = {}


def B(mat):
    if mat not in PARTS_BY:
        PARTS_BY[mat] = bmesh.new()
    return PARTS_BY[mat]


def zu(x):
    return ZU0 + (min(x, 2 * XC - x) - X0) * TAN


def newell(cs):
    n = Vector((0, 0, 0))
    for i in range(len(cs)):
        a, b = cs[i], cs[(i + 1) % len(cs)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def face(bm, verts, n):
    if newell([v.co for v in verts]).dot(Vector(n)) < 0:
        verts = list(reversed(verts))
    return bm.faces.new(verts)


class Slope:
    def __init__(self, sgn):
        self.sgn = sgn
        xe = X0 - OVER if sgn < 0 else X1 + OVER
        self.E = Vector((xe, 0.0, zu(xe if sgn < 0 else 2 * XC - xe)))
        self.d = Vector((-sgn * CP, 0.0, SP))
        self.n = Vector((sgn * SP, 0.0, CP))
        self.Y = Vector((0.0, -sgn, 0.0))

    def P(self, s, y, o):
        return self.E + self.d * s + self.n * o + Vector((0.0, y, 0.0))

    def rot(self):
        m = Matrix.Identity(4)
        for i, col in enumerate((self.d, self.Y, self.n)):
            for r in range(3):
                m[r][i] = col[r]
        return m

    def obox(self, mat, s0, s1, y0, y1, o0, o1, r, segs=1):
        c = self.P((s0 + s1) / 2, (y0 + y1) / 2, (o0 + o1) / 2)
        size = (s1 - s0, y1 - y0, o1 - o0)
        r = min(r, size[0] * 0.49, size[1] * 0.49, size[2] * 0.49)
        rbox_bm(c, size, r, segs=segs, bm=B(mat), matrix=self.rot())

    def box(self, mat, s0, s1, y0, y1, o0, o1, skip=()):
        bm = B(mat)
        c = [bm.verts.new(self.P(s, y, o)) for s in (s0, s1) for y in (y0, y1) for o in (o0, o1)]
        V = lambda i, j, k: c[i * 4 + j * 2 + k]
        Yw = Vector((0, 1, 0))
        sides = {"-s": ([V(0, 0, 0), V(0, 1, 0), V(0, 1, 1), V(0, 0, 1)], -self.d),
                 "+s": ([V(1, 0, 0), V(1, 1, 0), V(1, 1, 1), V(1, 0, 1)], self.d),
                 "-y": ([V(0, 0, 0), V(1, 0, 0), V(1, 0, 1), V(0, 0, 1)], -Yw),
                 "+y": ([V(0, 1, 0), V(1, 1, 0), V(1, 1, 1), V(0, 1, 1)], Yw),
                 "-o": ([V(0, 0, 0), V(1, 0, 0), V(1, 1, 0), V(0, 1, 0)], -self.n),
                 "+o": ([V(0, 0, 1), V(1, 0, 1), V(1, 1, 1), V(0, 1, 1)], self.n)}
        for k, (vs, nn) in sides.items():
            if k not in skip:
                face(bm, vs, nn)

    def local(self, p):
        q = Vector(p) - self.E
        return q.dot(self.d), q.y, q.dot(self.n)

    def solid(self, mat, poly, ob, ot, skip_edges=(), bottom=False):
        bm = B(mat)
        bot = [bm.verts.new(self.P(s, y, ob(s))) for s, y in poly]
        top = [bm.verts.new(self.P(s, y, ot(s))) for s, y in poly]
        face(bm, top, self.n)
        if bottom:
            face(bm, bot, -self.n)
        cen = Vector((sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)))
        k = len(poly)
        for i in range(k):
            j = (i + 1) % k
            if i in skip_edges:
                continue
            ms = (poly[i][0] + poly[j][0]) / 2 - cen.x
            my = (poly[i][1] + poly[j][1]) / 2 - cen.y
            face(bm, [bot[i], bot[j], top[j], top[i]], self.d * ms + Vector((0, my, 0)))


def clip(poly, axis, val, keep_less):
    out = []
    k = len(poly)
    for i in range(k):
        a, b = poly[i], poly[(i + 1) % k]
        ina = (a[axis] <= val) if keep_less else (a[axis] >= val)
        inb = (b[axis] <= val) if keep_less else (b[axis] >= val)
        if ina:
            out.append(a)
        if ina != inb:
            t = (val - a[axis]) / (b[axis] - a[axis])
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def scale_tile(s0, yc, w, L, nseg=3):
    r = w / 2
    pts = [(s0 + L, yc - r)]
    for k in range(nseg + 1):
        a = math.pi * k / nseg
        pts.append((s0 + r - r * math.sin(a), yc - r * math.cos(a)))
    pts.append((s0 + L, yc + r))
    return pts


def build_slope(sl, rnd):
    e, L, W, G, T, LIFT = 0.5, 0.74, 0.86, 0.035, 0.055, 0.06
    s = -0.1
    row = 0
    smax = SLEN + 0.06
    while s < smax - 0.05:
        off = 0.0 if row % 2 == 0 else (W + G) / 2
        mat = "SH_Honey" if row % 4 == 2 else "SH_Walnut"
        yc = YMIN + W / 2 + off - (W + G) if off else YMIN + W / 2
        while yc - W / 2 < YMAX:
            poly = scale_tile(s, yc, W, L)
            poly = clip(poly, 1, YMIN + 0.01, False)
            poly = clip(poly, 1, YMAX - 0.01, True)
            poly = clip(poly, 0, smax, True)
            if len(poly) >= 3 and (max(p[1] for p in poly) - min(p[1] for p in poly)) > 0.12:
                s0 = s
                lift = LIFT
                ob = lambda q, s0=s0, lift=lift: DECK1 - 0.01 + lift * max(0.0, 1 - (q - s0) / L)
                ot = lambda q, ob=ob: ob(q) + T
                head = [i for i in range(len(poly)) if abs(poly[i][0] - (s0 + L)) < 1e-6 and
                        abs(poly[(i + 1) % len(poly)][0] - (s0 + L)) < 1e-6]
                sl.solid(mat, poly, ob, ot, skip_edges=head, bottom=row == 0)
            yc += W + G
        s += e
        row += 1


def build_planks(sl):
    w, g = 0.3, 0.012
    n = int(round(SLEN / w))
    step = SLEN / n
    for i in range(n):
        s0 = i * step + (g / 2 if i > 0 else 0.0)
        s1 = (i + 1) * step - (g / 2 if i < n - 1 else -0.02)
        sl.box("SH_Oak" if i % 2 == 0 else "SH_Honey", s0, s1, YMIN + 0.012, YMAX - 0.012, 0.0, PLANK_T, skip=("+o",))
    sl.obox("SH_Walnut", -0.02, SLEN + 0.12, YMIN + 0.004, YMAX - 0.004, DECK0, DECK1, 0.004)
    sl.obox("SH_Timber", -0.06, 0.1, YMIN + 0.02, YMAX - 0.02, -0.04, 0.2, 0.035)


def barge(sl):
    for yy, sg in ((YMAX, 1), (YMIN, -1)):
        y0, y1 = (yy - 0.004, yy + 0.12) if sg > 0 else (yy - 0.12, yy + 0.004)
        sl.obox("SH_Timber", -0.16, SLEN + 0.02, y0, y1, -0.12, 0.36, 0.04)
        c = sl.P(-0.16, (y0 + y1) / 2, 0.12)
        ellipsoid_bm(c, (0.17, 0.09, 0.17), 10, 6, bm=B("SH_Walnut"))


def ridge():
    zr = zu(XC) + (DECK1 + 0.1) / CP + 0.02
    tube_bm([(XC, YMIN - 0.1, zr), (XC, YMAX + 0.1, zr)], 0.2, 10, bm=B("SH_Timber"))
    for y in (YMIN - 0.12, YMAX + 0.12):
        ellipsoid_bm((XC, y, zr), (0.25, 0.1, 0.25), 12, 6, bm=B("SH_Walnut"))
    yf = YMAX + 0.2
    tube_bm([(XC, yf, zr + 0.2), (XC, yf, zr + 0.55)], 0.05, 6, bm=B("SH_Timber"))
    ellipsoid_bm((XC, yf, zr + 0.62), (0.13, 0.13, 0.13), 10, 6, bm=B("SH_Gold"))
    lathe_bm([(0.0, zr + 0.15), (0.11, zr + 0.15), (0.12, zr + 0.22), (0.06, zr + 0.3), (0.0, zr + 0.31)], 8,
             bm=B("SH_Walnut"), matrix=Matrix.Translation((XC, yf, 0)))


def frieze():
    for xa, xb in ((X0 - 0.1, X0 - 0.02), (X1 + 0.02, X1 + 0.1)):
        xm = (xa + xb) / 2
        top = zu(xm) + 0.035
        rbox_bm((xm, (YB + YF) / 2, (5.47 + top) / 2), (xb - xa, YF - YB + 0.1, top - 5.47), 0.015, segs=1,
                bm=B("SH_Timber"))


def gable_poly(ylo, yhi):
    R = OCULUS[2]
    zb = TOP + 0.1
    top = lambda x: zu(x) + 0.05
    left = [(XC, zb), (X0, zb), (X0, top(X0)), (XC, top(XC)), (XC, OCULUS[1] + R)]
    for k in range(1, 8):
        a = math.pi * k / 8
        left.append((XC - R * math.sin(a), OCULUS[1] + R * math.cos(a)))
    left.append((XC, OCULUS[1] - R))
    right = [(2 * XC - x, z) for x, z in left]
    return left, right


def xz_prism(mat, pts, y0, y1, tri=True):
    bm = B(mat)
    a = [bm.verts.new((x, y0, z)) for x, z in pts]
    b = [bm.verts.new((x, y1, z)) for x, z in pts]
    fa = face(bm, a, (0, -1 if y0 < y1 else 1, 0))
    fb = face(bm, b, (0, 1 if y0 < y1 else -1, 0))
    cx = sum(p[0] for p in pts) / len(pts)
    cz = sum(p[1] for p in pts) / len(pts)
    k = len(pts)
    for i in range(k):
        j = (i + 1) % k
        mx = (pts[i][0] + pts[j][0]) / 2
        mz = (pts[i][1] + pts[j][1]) / 2
        ex, ez = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]
        nx, nz = ez, -ex
        if nx * (mx - cx) + nz * (mz - cz) < 0:
            nx, nz = -nx, -nz
        face(bm, [a[i], a[j], b[j], b[i]], (nx, 0, nz))
    if tri:
        bmesh.ops.triangulate(bm, faces=[fa, fb])


def ybox(mat, x0, x1, y0, y1, z0, z1, r, rot=None):
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    rbox_bm(c, (x1 - x0, y1 - y0, z1 - z0), r, segs=1, bm=B(mat), matrix=rot)


def beam_between(mat, a, b, w, ylo, yhi, r):
    a, b = Vector(a), Vector(b)
    v = b - a
    L = v.length
    ang = math.atan2(v.z, v.x)
    rot = Matrix.Rotation(-ang, 4, "Y")
    c = (a + b) / 2
    rbox_bm((c.x, (ylo + yhi) / 2, c.z), (L, yhi - ylo, w), r, segs=1, bm=B(mat), matrix=rot)


def oy(face_y, sg, a, b):
    return tuple(sorted((face_y + sg * a, face_y + sg * b)))


def gable_halves(x0, x1, R, zb):
    oz = OCULUS[1]
    top = lambda x: zu(x) + 0.05
    left = [(XC, zb), (x0, zb), (x0, top(x0)), (XC, top(XC)), (XC, oz + R)]
    for k in range(1, 8):
        a = math.pi * k / 8
        left.append((XC - R * math.sin(a), oz + R * math.cos(a)))
    left.append((XC, oz - R))
    right = [(2 * XC - x, z) for x, z in reversed(left)]
    return left, right


def gable_boards(face_y, sg):
    R, oz = OCULUS[2], OCULUS[1]
    mats = ["SH_Honey", "SH_Oak", "SH_Honey", "SH_Honey", "SH_Oak"]
    y0, y1 = oy(face_y, sg, -0.02, 0.025)
    n = int(round((X1 - X0) / 0.3))
    step = (X1 - X0 - 0.024) / n
    ztop = lambda x: zu(x) + 0.045
    for i in range(n):
        xa = X0 + 0.012 + i * step + (0.007 if i > 0 else 0.0)
        xb = X0 + 0.012 + (i + 1) * step - (0.007 if i < n - 1 else 0.0)
        tops = [(xb, ztop(xb)), (XC, ztop(XC)), (xa, ztop(xa))] if xa < XC < xb else [(xb, ztop(xb)), (xa, ztop(xa))]
        m = mats[i % len(mats)]
        if xb > XC - R - 0.02 and xa < XC + R + 0.02:
            xm = min(max(XC, xa), xb)
            hh = math.sqrt(max(R * R - (xm - XC) ** 2, 0.0)) + 0.03
            xz_prism(m, [(xa, TOP + 0.125), (xb, TOP + 0.125), (xb, oz - hh), (xa, oz - hh)], y0, y1)
            xz_prism(m, [(xa, oz + hh), (xb, oz + hh)] + tops, y0, y1)
        else:
            xz_prism(m, [(xa, TOP + 0.125), (xb, TOP + 0.125)] + tops, y0, y1)


def gable_frame(face_y, sg):
    R, oz = OCULUS[2], OCULUS[1]
    xg = X0 + (6.75 - ZU0) / TAN + 0.05
    ybox("SH_Timber", xg, 2 * XC - xg, *oy(face_y, sg, -0.02, 0.075), 6.55, 6.73, 0.03)
    yp = oy(face_y, sg, -0.02, 0.055)
    for x in (26.6, 33.4):
        ybox("SH_Timber", x - 0.09, x + 0.09, *yp, 6.71, zu(x) + 0.04, 0.025)
    ybox("SH_Timber", XC - 0.09, XC + 0.09, *yp, 6.71, oz - R - 0.06, 0.025)
    ybox("SH_Timber", XC - 0.09, XC + 0.09, *yp, oz + R + 0.06, zu(XC) + 0.04, 0.025)
    yb = oy(face_y, sg, -0.02, 0.04)
    for sx in (-1, 1):
        beam_between("SH_Timber", (XC + sx * 2.2, 0, 6.7), (XC + sx * 0.42, 0, oz - 0.3), 0.14, *yb, 0.02)
    cy = face_y + sg * 0.05
    torus_bm(R + 0.05, 0.075, 16, 6, bm=B("SH_Timber"),
             matrix=Matrix.Translation((XC, cy, oz)) @ Matrix.Rotation(math.pi / 2, 4, "X"))


def gable(g):
    yo, yi, s = g["y_out"], g["y_in"], g["s"]
    R, oz = OCULUS[2], OCULUS[1]
    for poly in gable_halves(X0, X1, R, TOP + 0.1):
        xz_prism("SH_Walnut", poly, min(yo, yi), max(yo, yi))
    for poly in gable_halves(X0 + 0.012, X1 - 0.012, R + 0.012, TOP + 0.115):
        xz_prism("SH_Parchment", poly, *oy(yi, -s, -0.02, 0.02))
    gable_boards(yo, s)
    gable_frame(yo, s)
    gable_frame(yi, -s)
    ym = (yo + yi) / 2
    lathe_bm([(0.0, -0.012), (R + 0.02, -0.012), (R + 0.02, 0.012), (0.0, 0.012)], 16, bm=B("SH_Glass"),
             matrix=Matrix.Translation((XC, ym, oz)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    ybox("SH_Timber", XC - 0.05, XC + 0.05, ym - 0.06, ym + 0.06, oz - R - 0.03, oz + R + 0.03, 0.02)
    ybox("SH_Timber", XC - R - 0.03, XC + R + 0.03, ym - 0.05, ym + 0.05, oz - 0.05, oz + 0.05, 0.02)
    ellipsoid_bm((XC, ym, oz), (0.09, 0.085, 0.09), 10, 6, bm=B("SH_Walnut"))


def lantern(x, y, ztop):
    tube_bm([(x, y, ztop), (x, y, ztop - 0.45)], 0.018, 5, bm=B("SH_Timber"))
    torus_bm(0.05, 0.014, 8, 4, bm=B("SH_Walnut"),
             matrix=Matrix.Translation((x, y, ztop - 0.47)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    z = ztop - 1.2
    m = Matrix.Translation((x, y, z)) @ Matrix.Scale(1.4, 4) @ Matrix.Translation((0, 0, -z))
    lathe_bm([(0.0, z), (0.08, z), (0.12, z + 0.04), (0.0, z + 0.05)], 8, bm=B("SH_Walnut"), matrix=m)
    lathe_bm([(0.0, z + 0.04), (0.11, z + 0.04), (0.135, z + 0.17), (0.115, z + 0.32), (0.0, z + 0.33)], 8,
             bm=B("SH_Gold"), matrix=m)
    lathe_bm([(0.0, z + 0.31), (0.17, z + 0.31), (0.15, z + 0.36), (0.07, z + 0.45), (0.025, z + 0.5), (0.0, z + 0.51)],
             8, bm=B("SH_Walnut"), matrix=m)


def truss(y, west, east, lamp):
    for sl in (west, east):
        sf = (24.12 - (X0 - OVER)) / CP
        sr = (XC - 0.14 - (X0 - OVER)) / CP + 0.03
        sl.obox("SH_Timber", sf, sr, y - 0.1, y + 0.1, -0.24, 0.02, 0.04)
    for xa, xb in ((23.98, 24.32), (35.68, 36.02)):
        ybox("SH_Walnut", xa, xb, y - 0.12, y + 0.12, 5.3, 5.92, 0.05)
    zc = 7.35
    xc0 = X0 + (zc + 0.11 / CP - ZU0) / TAN
    ybox("SH_Timber", xc0, 2 * XC - xc0, y - 0.085, y + 0.085, zc - 0.09, zc + 0.09, 0.04)
    ybox("SH_Timber", XC - 0.09, XC + 0.09, y - 0.075, y + 0.075, zc + 0.05, zu(XC) - 0.3, 0.035)
    for x in (xc0, 2 * XC - xc0):
        for sy in (-1, 1):
            ellipsoid_bm((x, y + sy * 0.1, zc), (0.045, 0.03, 0.045), 8, 4, bm=B("SH_Walnut"))
    if lamp:
        lantern(XC + 0.6, y, zc - 0.08)


def build():
    rnd = random.Random(7)
    west, east = Slope(-1), Slope(1)
    SLOPES.extend((west, east))
    for sl in (west, east):
        build_planks(sl)
        build_slope(sl, rnd)
        barge(sl)
    ridge()
    frieze()
    ybox("SH_Timber", XC - 0.14, XC + 0.14, YB + 0.4, YF - 0.4, zu(XC) - 0.37, zu(XC) - 0.03, 0.04)
    for g in GABLES:
        gable(g)
    for y in TRUSSES:
        truss(y, west, east, y != -18.25)


def solid_roof(p):
    for g in GABLES:
        y0, y1 = sorted((g["y_out"], g["y_in"]))
        if y0 < p.y < y1 and X0 < p.x < X1 and TOP + 0.1 < p.z < zu(p.x) + 0.05:
            if (p.x - XC) ** 2 + (p.z - OCULUS[1]) ** 2 > OCULUS[2] ** 2:
                return True
    for sl in SLOPES:
        s, y, o = sl.local(p)
        if 0.0 < o < DECK1 and -0.02 < s < SLEN + 0.1 and YMIN < y < YMAX and (p.x - XC) * sl.sgn >= -0.05:
            return True
    return False


SLOPES = []


def materialize():
    objs = []
    for m, bm in PARTS_BY.items():
        if len(bm.faces):
            objs.append(finish("ShopRoof__" + m, bm, m, angle=40))
    return objs


def scene_setup():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_object_outline = True
    sh.object_outline_color = (0.12, 0.1, 0.09)
    sh.show_backface_culling = True
    sh.show_shadows = True
    sh.shadow_intensity = 0.25
    sc.display.light_direction = (0.35, -0.45, 0.82)
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.35
    sc.world = sc.world or bpy.data.worlds.new("World")
    sc.world.color = (0.55, 0.68, 0.8)


def import_context():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=BUILDING_FBX)
    for o in [o for o in bpy.data.objects if o not in before]:
        if o.type == "MESH":
            for slot in o.material_slots:
                if slot.material:
                    base = slot.material.name.split(".")[0]
                    if base in MATS:
                        slot.material = MATS[base]
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=OBJ_PATH, forward_axis="Y", up_axis="Z")
    cm = bpy.data.materials.new("Ctx")
    cm.diffuse_color = (0.62, 0.63, 0.66, 1)
    for o in [o for o in bpy.data.objects if o not in before]:
        if "PetShop" in o.name:
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(cm)
    load_dragon((30.0, -11.5, FLOOR), 160)
    load_dragon((29.0, -5.6, 0.0), 200)
    load_dragon((28.5, -21.6, FLOOR), 20)


def cam(path, loc, look, lens=None, ortho=None, res=900):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    else:
        cd.lens = lens or 18
    cd.clip_start = 0.05
    cd.clip_end = 400
    c = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(c)
    c.location = Vector(loc)
    c.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = c
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c)


SHOTS = [
    ("ext_front", (30.0, 6.0, 2.0), (30.0, -10.0, 5.6), 22),
    ("ext_back", (22.0, -42.0, 3.5), (30.5, -22.0, 5.5), 22),
    ("ext_iso", (6.0, 8.0, 20.0), (30.0, -16.0, 4.5), 24),
    ("int_up_shop", (30.0, -8.2, FLOOR + 1.6), (30.0, -14.0, 7.6), 14),
    ("int_front_win", (31.0, -15.5, FLOOR + 1.6), (30.0, -7.0, 3.2), 14),
    ("int_back_room", (31.0, -19.2, FLOOR + 1.6), (30.0, -25.0, 3.6), 14),
    ("int_east_win", (30.5, -21.0, FLOOR + 1.6), (36.0, -23.4, 2.8), 16),
    ("int_up_back", (26.0, -22.0, FLOOR + 1.6), (31.0, -19.0, 8.5), 13),
    ("ext_roof", (40.0, -2.0, 12.5), (31.0, -12.0, 8.0), 30),
]


def previews(out):
    os.makedirs(out, exist_ok=True)
    scene_setup()
    import_context()
    cells = []
    for tag, loc, look, lens in SHOTS:
        f = "ShopRoof_%s.png" % tag
        cam(os.path.join(out, f), loc, look, lens)
        cells.append(f)
    contact_sheet(out, cells, os.path.join(out, "ShopRoof_sheet.png"), cell=900, cols=3)


out, flags = cli()
begin()
build()
objs = materialize()
ob = join_all("ShopRoof", objs)
report(ob)
coplanar_check.check(ob, "ShopRoof", os.path.join(out, "ShopRoof_coplanar.txt") if out else None, solid=solid_roof)
export(ob, flags)
if out and "nopreview" not in flags:
    previews(out)
