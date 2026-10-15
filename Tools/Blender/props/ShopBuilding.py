import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *
import random
from mathutils.bvhtree import BVHTree
import coplanar_check

SCRATCH = r"C:\Users\Docente\AppData\Local\Temp\claude\C--Users-Docente-Desktop-UnityProyects-RunRunSimulator\4d55ec4f-97d7-4ab7-b7aa-aab8024c682a\scratchpad"
OBJ_PATH = os.path.join(SCRATCH, "shop_env", "shop_env.obj")

FLOOR = 0.5
TOP = 5.5
GROUND = -0.42
ZOC = 0.62
RAIL0, RAIL1 = 1.36, 1.46


WALLS = [
    dict(name="front", axis="x", a=(23.5, 36.5), t=(-7.5, -7.0),
         holes=[(24.33, 28.27, 0.75, 4.25), (28.5, 31.5, 0.5, 4.5), (31.85, 35.71, 0.79, 4.23)],
         sides=[dict(plane=-7.5, s=-1, kind="in", rooms=[(24.0, 36.0, "shop")]),
                dict(plane=-7.0, s=1, kind="out", ext=(23.5, 36.5), extend=True,
                     pilasters=[(23.5, "c0"), (36.5, "c1")])]),
    dict(name="back", axis="x", a=(23.5, 36.5), t=(-25.0, -24.5), holes=[(25.14, 26.34, 1.8, 3.2), (33.66, 34.86, 1.8, 3.2)],
         sides=[dict(plane=-24.5, s=1, kind="in", rooms=[(24.0, 36.0, "back")]),
                dict(plane=-25.0, s=-1, kind="out", ext=(23.5, 36.5), extend=True,
                     pilasters=[(23.5, "c0"), (36.5, "c1"), (27.83, "m"), (32.17, "m")])]),
    dict(name="west", axis="y", a=(-25.0, -7.0), t=(23.5, 24.0), holes=[(-24.0, -21.75, 0.5, 4.5)],
         sides=[dict(plane=24.0, s=1, kind="in", rooms=[(-24.5, -18.5, "back"), (-18.0, -7.5, "shop")]),
                dict(plane=23.5, s=-1, kind="out", ext=(-25.0, -7.0), extend=False,
                     pilasters=[(-25.0, "c0"), (-7.0, "c1"), (-18.25, "m"), (-12.6, "m")])]),
    dict(name="east", axis="y", a=(-25.0, -7.0), t=(36.0, 36.5), holes=[(-23.95, -22.85, 1.8, 3.2)],
         sides=[dict(plane=36.0, s=-1, kind="in", rooms=[(-24.5, -18.5, "back"), (-18.0, -7.5, "shop")]),
                dict(plane=36.5, s=1, kind="out", ext=(-25.0, -7.0), extend=False,
                     pilasters=[(-25.0, "c0"), (-7.0, "c1"), (-21.4, "m"), (-18.25, "m"), (-12.6, "m")])]),
    dict(name="mid", axis="x", a=(24.0, 36.0), t=(-18.5, -18.0), holes=[(33.38, 35.25, 0.5, 4.5)],
         sides=[dict(plane=-18.5, s=-1, kind="in", rooms=[(24.0, 36.0, "back")]),
                dict(plane=-18.0, s=1, kind="in", rooms=[(24.0, 36.0, "shop")])]),
]

GROUPS = {}
CUR = ["misc"]


def group(name):
    CUR[0] = name


def B(mat):
    g = GROUPS.setdefault(CUR[0], {})
    if mat not in g:
        g[mat] = bmesh.new()
    return g[mat]


def newell(cs):
    n = Vector((0, 0, 0))
    for i in range(len(cs)):
        a, b = cs[i], cs[(i + 1) % len(cs)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def face(bm, verts, n):
    cs = [v.co for v in verts]
    if newell(cs).dot(Vector(n)) < 0:
        verts = list(reversed(verts))
    return bm.faces.new(verts)


def quad(mat, pts, n):
    bm = B(mat)
    face(bm, [bm.verts.new(p) for p in pts], n)


def abox(mat, lo, hi, skip=()):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    if x1 - x0 < 1e-5 or y1 - y0 < 1e-5 or z1 - z0 < 1e-5:
        return
    P = lambda i, j, k: (x1 if i else x0, y1 if j else y0, z1 if k else z0)
    sides = {
        "-x": ([P(0, 0, 0), P(0, 1, 0), P(0, 1, 1), P(0, 0, 1)], (-1, 0, 0)),
        "+x": ([P(1, 0, 0), P(1, 1, 0), P(1, 1, 1), P(1, 0, 1)], (1, 0, 0)),
        "-y": ([P(0, 0, 0), P(1, 0, 0), P(1, 0, 1), P(0, 0, 1)], (0, -1, 0)),
        "+y": ([P(0, 1, 0), P(1, 1, 0), P(1, 1, 1), P(0, 1, 1)], (0, 1, 0)),
        "-z": ([P(0, 0, 0), P(1, 0, 0), P(1, 1, 0), P(0, 1, 0)], (0, 0, -1)),
        "+z": ([P(0, 0, 1), P(1, 0, 1), P(1, 1, 1), P(0, 1, 1)], (0, 0, 1)),
    }
    for k, (pts, n) in sides.items():
        if k in skip:
            continue
        m = mat[k] if isinstance(mat, dict) else mat
        if m:
            quad(m, pts, n)


def wn(wall):
    return Vector((0, 1, 0)) if wall["axis"] == "x" else Vector((1, 0, 0))


def wu(wall):
    return Vector((1, 0, 0)) if wall["axis"] == "x" else Vector((0, 1, 0))


def wp(wall, side, u, off, z):
    t = side["plane"] + side["s"] * off
    return Vector((u, t, z)) if wall["axis"] == "x" else Vector((t, u, z))


def waabb(wall, side, u0, u1, off0, off1, z0, z1):
    a = wp(wall, side, u0, off0, z0)
    b = wp(wall, side, u1, off1, z1)
    return (Vector((min(a.x, b.x), min(a.y, b.y), z0)), Vector((max(a.x, b.x), max(a.y, b.y), z1)))


def wbox(mat, wall, side, u0, u1, off0, off1, z0, z1):
    lo, hi = waabb(wall, side, u0, u1, off0, off1, z0, z1)
    abox(mat, lo, hi)


def wrbox(mat, wall, side, u0, u1, off0, off1, z0, z1, r):
    lo, hi = waabb(wall, side, u0, u1, off0, off1, z0, z1)
    size = hi - lo
    r = min(r, size.x * 0.49, size.y * 0.49, size.z * 0.49)
    rbox_bm((lo + hi) * 0.5, tuple(size), r, segs=1, bm=B(mat))


def extrude(mat, wall, side, u0, u1, prof):
    if u1 - u0 < 1e-4:
        return
    bm = B(mat)
    cu = sum(p[0] for p in prof) / len(prof)
    cz = sum(p[1] for p in prof) / len(prof)
    nrm = wn(wall) * side["s"]
    ud = wu(wall)
    A = [bm.verts.new(wp(wall, side, u0, o, z)) for o, z in prof]
    Bv = [bm.verts.new(wp(wall, side, u1, o, z)) for o, z in prof]
    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        (o0, z0), (o1, z1) = prof[i], prof[j]
        mo, mz = (o0 + o1) / 2 - cu, (z0 + z1) / 2 - cz
        eo, ez = o1 - o0, z1 - z0
        no, nz = ez, -eo
        if no * mo + nz * mz < 0:
            no, nz = -no, -nz
        face(bm, [A[i], A[j], Bv[j], Bv[i]], nrm * no + Vector((0, 0, nz)))
    face(bm, A, -ud)
    face(bm, Bv, ud)


def rect_minus(u0, u1, z0, z1, holes):
    cuts = {u0, u1}
    for h in holes:
        for c in (h[0], h[1]):
            if u0 < c < u1:
                cuts.add(c)
    cuts = sorted(cuts)
    cols = []
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 1e-4:
            continue
        m = (a + b) / 2
        zs = [(z0, z1)]
        for h in holes:
            if h[0] < m < h[1]:
                nz = []
                for p, q in zs:
                    if h[3] <= p or h[2] >= q:
                        nz.append((p, q))
                        continue
                    if h[2] > p:
                        nz.append((p, h[2]))
                    if h[3] < q:
                        nz.append((h[3], q))
                zs = nz
        zs = [(p, q) for p, q in zs if q - p > 1e-4]
        if cols and cols[-1][1] == a and cols[-1][2] == zs:
            cols[-1] = (cols[-1][0], b, zs)
        else:
            cols.append((a, b, zs))
    return [(a, b, p, q) for a, b, zs in cols for p, q in zs]


def grow(holes, e=0.02):
    return [(h[0] - e, h[1] + e, h[2] if h[2] <= FLOOR + 1e-4 else h[2] - e, h[3] + e) for h in holes]


def neighbors(holes, h):
    left = [g[1] for g in holes if g is not h and g[1] <= h[0] and h[0] - g[1] < 0.6]
    right = [g[0] for g in holes if g is not h and g[0] >= h[1] and g[0] - h[1] < 0.6]
    return (max(left) if left else None), (min(right) if right else None)


def u_segments(u0, u1, z0, z1, holes):
    return [(a, b) for a, b, p, q in rect_minus(u0, u1, z0, z1, holes) if abs(p - z0) < 1e-5 and abs(q - z1) < 1e-5]



ACCENT = {"shop": "SH_Sage", "back": "SH_Teal"}
MIDRAIL = 3.3
PLATE0, PLATE1 = 5.1, 5.42

DECOR = {}


def decor_zone(wall, side, u0, u1, low=True):
    DECOR.setdefault((wall["name"], side["plane"]), []).append((u0, u1, low))


def zones(wall, side):
    return DECOR.get((wall["name"], side["plane"]), [])


def R3(wall, ru, roff, rz):
    return (ru, roff, rz) if wall["axis"] == "x" else (roff, ru, rz)


def prism(mat, A, Bp):
    bm = B(mat)
    cen = sum(A + Bp, Vector()) / (len(A) + len(Bp))
    va = [bm.verts.new(p) for p in A]
    vb = [bm.verts.new(p) for p in Bp]
    face(bm, va, sum(A, Vector()) / len(A) - cen)
    face(bm, vb, sum(Bp, Vector()) / len(Bp) - cen)
    n = len(A)
    for k in range(n):
        k1 = (k + 1) % n
        m = (A[k] + A[k1] + Bp[k] + Bp[k1]) / 4
        face(bm, [va[k], va[k1], vb[k1], vb[k]], m - cen)


def face_prism(mat, wall, side, pts, off0, off1):
    prism(mat, [wp(wall, side, u, off0, z) for u, z in pts], [wp(wall, side, u, off1, z) for u, z in pts])


def brace(mat, wall, side, ua, za, ub, zb, w, off):
    d = Vector((ub - ua, zb - za))
    n = Vector((-d.y, d.x)).normalized() * (w / 2)
    pts = [(ua - n.x, za - n.y), (ub - n.x, zb - n.y), (ub + n.x, zb + n.y), (ua + n.x, za + n.y)]
    face_prism(mat, wall, side, pts, -0.02, off)


def arch(mat, wall, side, u0, u1, zb, rise, w, off):
    pts_o, pts_i = [], []
    n = 10
    for k in range(n + 1):
        t = k / n
        u = u0 + (u1 - u0) * t
        z = zb + rise * math.sin(math.pi * t)
        pts_o.append((u, z + w))
        pts_i.append((u, z))
    for k in range(n):
        face_prism(mat, wall, side, [pts_i[k], pts_i[k + 1], pts_o[k + 1], pts_o[k]], -0.02, off)
    for u in (u0, u1):
        wrbox("SH_Timber", wall, side, u - 0.07, u + 0.07, -0.02, off + 0.045, zb - 0.02, zb + w + 0.06, 0.02)


def boards(mats, wall, side, a, b, p, q, w=0.2, gap=0.014, off=0.02, base="SH_Walnut"):
    n = max(1, int(round((b - a) / w)))
    step = (b - a) / n
    wbox(base, wall, side, a + 0.01, b - 0.01, -0.02, 0.009, p + 0.01, q - 0.01)
    for i in range(n):
        u0 = a + i * step + (gap / 2 if i > 0 else 0)
        u1 = a + (i + 1) * step - (gap / 2 if i < n - 1 else 0)
        lo, hi = waabb(wall, side, u0, u1, -0.02, off, p, q)
        back = ("-" if side["s"] > 0 else "+") + ("y" if wall["axis"] == "x" else "x")
        abox(mats[i % len(mats)], lo, hi, skip=(back, "-z"))


def build_core(wall):
    group(wall["name"] + "_core")
    a0, a1 = wall["a"]
    t0, t1 = wall["t"]
    holes = wall["holes"]
    sd = {}
    for side in wall["sides"]:
        key = ("+" if side["s"] > 0 else "-") + ("y" if wall["axis"] == "x" else "x")
        sd[key] = "SH_Parchment" if side["kind"] == "in" else "SH_Honey"
    ua = "x" if wall["axis"] == "x" else "y"
    for a, b, p, q in rect_minus(a0, a1, 0.0, TOP, holes):
        mats = dict(sd)
        edge_u = lambda u: any(abs(u - h[0]) < 1e-5 or abs(u - h[1]) < 1e-5 for h in holes)
        mats["-" + ua] = "SH_Oak" if edge_u(a) else None
        mats["+" + ua] = "SH_Oak" if edge_u(b) else None
        below = any(h[0] <= a + 1e-5 and h[1] >= b - 1e-5 and abs(h[3] - p) < 1e-5 for h in holes)
        above = any(h[0] <= a + 1e-5 and h[1] >= b - 1e-5 and abs(h[2] - q) < 1e-5 and h[2] > FLOOR + 1e-4
                    for h in holes)
        mats["-z"] = "SH_Oak" if below else None
        mats["+z"] = "SH_Oak" if above else None
        if wall["axis"] == "x":
            abox(mats, (a, t0, p), (b, t1, q))
        else:
            abox(mats, (t0, a, p), (t1, b, q))
    for h in holes:
        if h[2] > FLOOR + 1e-4:
            glazing(wall, h)


GLASS = []


def glazing(wall, h):
    group(wall["name"] + "_win")
    u0, u1, z0, z1 = h
    t0, t1 = wall["t"]
    side = dict(plane=t0, s=1)
    m = (t1 - t0) / 2
    big = z1 - z0 > 2.5
    fw = 0.12 if big else 0.09
    mw = 0.2 if big else 0.14
    lo, hi = waabb(wall, side, u0 - 0.03, u1 + 0.03, m - 0.012, m + 0.012, z0 - 0.03, z1 + 0.03)
    abox("SH_Glass", lo, hi)
    GLASS.append((wall["name"], tuple(lo), tuple(hi)))
    for a, b in ((u0 - 0.03, u0 + fw), (u1 - fw, u1 + 0.03)):
        wrbox("SH_Timber", wall, side, a, b, m - 0.085, m + 0.085, z0 - 0.03, z1 + 0.03, 0.025)
    for p, q in ((z0 - 0.03, z0 + fw), (z1 - fw, z1 + 0.03)):
        wrbox("SH_Timber", wall, side, u0 - 0.03, u1 + 0.03, m - 0.07, m + 0.07, p, q, 0.025)
    uc = (u0 + u1) / 2
    zm = z0 + (z1 - z0) * (0.6 if big else 0.5)
    wrbox("SH_Timber", wall, side, uc - mw / 2, uc + mw / 2, m - 0.1, m + 0.1, z0 + fw - 0.02, z1 - fw + 0.02, 0.035)
    wrbox("SH_Timber", wall, side, u0 + fw - 0.02, u1 - fw + 0.02, m - 0.115, m + 0.115, zm - mw / 2, zm + mw / 2,
          0.035)
    for sg in (-1, 1):
        ellipsoid_bm(wp(wall, side, uc, m + sg * 0.115, zm), R3(wall, mw * 0.55, 0.04, mw * 0.55), 10, 5,
                     bm=B("SH_Walnut"))


def alfeizar(wall, side, h, front):
    u0, u1, z0, z1 = h
    m = (wall["t"][1] - wall["t"][0]) / 2
    wrbox("SH_Oak", wall, side, u0 - 0.1, u1 + 0.1, -m + 0.06, front, z0 - 0.045, z0 + 0.035, 0.022)


def zoc_prof():
    return [(-0.02, FLOOR), (0.035, FLOOR), (0.035, ZOC - 0.03), (0.02, ZOC), (-0.02, ZOC)]


def chair_prof():
    return [(-0.02, RAIL0), (0.024, RAIL0), (0.032, RAIL0 + 0.025), (0.032, RAIL1 - 0.03), (0.024, RAIL1),
            (-0.02, RAIL1)]


def beam_prof(z0, z1, off):
    return [(-0.02, z0), (off - 0.012, z0), (off, z0 + 0.02), (off, z1 - 0.02), (off - 0.012, z1), (-0.02, z1)]


def post_positions(spans, ends_fixed, zlist, spacing=2.3):
    out = []
    for a, b in spans:
        L = b - a
        n = int(L // spacing)
        for k in range(1, n + 1):
            u = a + L * k / (n + 1)
            for z0, z1, low in zlist:
                if z0 - 0.15 < u < z1 + 0.15:
                    u = z0 - 0.15 if u - z0 < z1 - u else z1 + 0.15
            if a + 0.4 < u < b - 0.4:
                out.append(u)
    return sorted(out)


def build_interior_side(wall, side):
    holes = grow(wall["holes"])
    for ru0, ru1, room in side["rooms"]:
        group(wall["name"] + "_in")
        acc = ACCENT[room]
        fm = ["SH_Honey", "SH_Oak"] if room == "shop" else ["SH_Oak", "SH_Honey"]
        for a, b in u_segments(ru0, ru1, FLOOR, ZOC, holes):
            extrude("SH_Walnut", wall, side, a, b, zoc_prof())
        for a, b, p, q in rect_minus(ru0, ru1, ZOC, RAIL0, holes):
            boards(fm, wall, side, a, b, p, q, w=0.2 if room == "shop" else 0.28)
        for a, b in u_segments(ru0, ru1, RAIL0, RAIL1, holes):
            extrude(acc, wall, side, a, b, chair_prof())
        for a, b in u_segments(ru0, ru1, PLATE0, PLATE1, holes):
            extrude("SH_Timber", wall, side, a, b, beam_prof(PLATE0, PLATE1, 0.045))
        spans = u_segments(ru0, ru1, RAIL1, MIDRAIL + 0.1, holes)
        for a, b in spans:
            extrude("SH_Timber", wall, side, a, b, beam_prof(MIDRAIL - 0.07, MIDRAIL + 0.07, 0.03))
        zl = zones(wall, side) + [(h[0] - 0.4, h[1] + 0.4, True) for h in wall["holes"] if h[2] > FLOOR + 1e-4]
        posts = post_positions(spans, True, zl)
        for u in posts:
            timber_post(wall, side, u, 0.18, 0.045, ZOC, PLATE0)
        for a, b in spans:
            cuts = [a] + [u for u in posts if a < u < b] + [b]
            for k, (p0, p1) in enumerate(zip(cuts, cuts[1:])):
                if p1 - p0 < 1.1:
                    continue
                if any(z0 < p1 and z1 > p0 and low for z0, z1, low in zl):
                    continue
                i0, i1 = p0 + 0.09, p1 - 0.09
                if k % 2 == 0:
                    brace("SH_Timber", wall, side, i0, RAIL1 + 0.02, i0 + min(1.2, i1 - i0), MIDRAIL - 0.06, 0.13, 0.018)
                else:
                    brace("SH_Timber", wall, side, i1, RAIL1 + 0.02, i1 - min(1.2, i1 - i0), MIDRAIL - 0.06, 0.13, 0.018)
        for h in wall["holes"]:
            if h[0] >= ru0 - 1e-5 and h[1] <= ru1 + 1e-5:
                casing_in(wall, side, h, *neighbors(wall["holes"], h))
                if h[2] > FLOOR + 1e-4:
                    alfeizar(wall, side, h, 0.09)


def timber_post(wall, side, u, w, off, z0, z1):
    wrbox("SH_Timber", wall, side, u - w / 2, u + w / 2, -0.02, off, z0, z1, 0.022)
    wbox("SH_Walnut", wall, side, u - w / 2 - 0.025, u + w / 2 + 0.025, -0.02, off + 0.008, z1 - 0.12, z1)


def casing_in(wall, side, h, left=None, right=None):
    u0, u1, z0, z1 = h
    W, O = 0.18, 0.045
    P = 0.008
    door = z0 <= FLOOR + 1e-4
    zb = FLOOR + 0.17 if door else z0 - 0.07
    if left is None:
        wrbox("SH_Timber", wall, side, u0 - W - P, u0 - P, -0.02, O, zb, z1 + 0.2, 0.022)
    if right is None:
        wrbox("SH_Timber", wall, side, u1 + P, u1 + W + P, -0.02, O, zb, z1 + 0.2, 0.022)
    else:
        wrbox("SH_Timber", wall, side, u1 + P, right - P, -0.02, O, min(zb, FLOOR + 0.2), z1 + 0.2, 0.022)
    la = u0 - W - 0.12 if left is None else left + P + 0.03
    lb = u1 + W + 0.12 if right is None else right - P - 0.03
    wrbox("SH_Timber", wall, side, la, lb, -0.02, O + 0.015, z1 + P, z1 + 0.22, 0.03)
    for u in ((u0 - W - 0.12,) if left is None else ()) + ((u1 + W + 0.12,) if right is None else ()):
        wrbox("SH_Walnut", wall, side, u - 0.05, u + 0.05, -0.02, O + 0.035, z1 + 0.02, z1 + 0.2, 0.035)
    if door:
        for a, b in ((u0 - W - 0.03, u0 + P), (u1 - P, u1 + W + 0.03)):
            wrbox("SH_Walnut", wall, side, a, b, -0.02, O + 0.015, FLOOR, FLOOR + 0.22, 0.02)
    else:
        wrbox("SH_Timber", wall, side, max(la, u0 - W - 0.06), min(lb, u1 + W + 0.06), -0.02, O + 0.005, z0 - 0.09,
              z0 - 0.012, 0.02)
    rise = min(0.3, PLATE0 - (z1 + 0.22) - 0.1)
    if rise > 0.12:
        arch("SH_Walnut", wall, side, u0 - 0.05, u1 + 0.05, z1 + 0.22, rise, 0.1, 0.035)


STONE_RNG = random.Random(11)


def ext_ends(segs, E0, E1, d=0.012):
    return [(a - d if abs(a - E0) < 1e-5 else a, b + d if abs(b - E1) < 1e-5 else b) for a, b in segs]


def build_exterior_side(wall, side):
    group(wall["name"] + "_out")
    holes = grow(wall["holes"])
    e0, e1 = side["ext"]
    ext = 0.12 if side["extend"] else 0.0
    E0, E1 = e0 - ext, e1 + ext
    holes_low = [(h[0], h[1], -5.0 if h[2] <= FLOOR + 1e-4 else h[2], h[3]) for h in holes]
    base = [(-0.02, GROUND), (0.045, GROUND), (0.045, 0.6), (-0.02, 0.6)]
    for a, b in u_segments(E0, E1, GROUND, 0.6, holes_low):
        extrude("SH_StoneDark", wall, side, a, b, base)
        for row, zc in enumerate((0.06,)):
            u = a
            while u < b - 0.12:
                L = STONE_RNG.uniform(0.55, 0.8)
                u0, u1 = max(u + 0.03, a + 0.02), min(u + L - 0.03, b - 0.02)
                if u1 - u0 > 0.18:
                    zb = GROUND + STONE_RNG.uniform(0.05, 0.12)
                    zt = 0.5 - STONE_RNG.uniform(0.0, 0.08)
                    wrbox("SH_Stone", wall, side, u0, u1, -0.01, 0.085, zb, zt, 0.07)
                u += L
    for a, b, p, q in rect_minus(E0 + 0.0, E1 - 0.0, 0.7, 4.9, holes):
        boards(["SH_Honey", "SH_Honey", "SH_Oak", "SH_Honey", "SH_Oak"], wall, side, a, b, p, q, w=0.3, gap=0.012,
               off=0.018, base="SH_Walnut")
    for a, b in ext_ends(u_segments(E0, E1, 0.6, 0.76, holes_low), E0, E1):
        extrude("SH_Timber", wall, side, a, b, beam_prof(0.6, 0.76, 0.048))
    for a, b in ext_ends(u_segments(E0, E1, 4.86, 5.1, holes), E0, E1):
        extrude("SH_Timber", wall, side, a, b, beam_prof(4.86, 5.1, 0.048))
    spans = u_segments(E0, E1, 0.76, 4.86, holes)
    if wall["name"] != "front":
        for a, b in ext_ends(spans, E0, E1):
            extrude("SH_Timber", wall, side, a, b, beam_prof(2.8, 2.98, 0.055))
    PW = 0.3
    posts = []
    for u, kind in side.get("pilasters", []):
        if kind == "c0":
            a, b = (u - (0.06 if side["extend"] else 0.0), u + PW)
        elif kind == "c1":
            a, b = (u - PW, u + (0.06 if side["extend"] else 0.0))
        else:
            a, b = u - PW / 2, u + PW / 2
        posts.append((a, b))
        wrbox("SH_Timber", wall, side, a, b, -0.02, 0.065, 0.62, 5.08, 0.03)
    if wall["name"] != "front":
        cuts = sorted([0.5 * (a + b) for a, b in posts])
        for k, (p0, p1) in enumerate(zip(cuts, cuts[1:])):
            if any(h[0] < p1 and h[1] > p0 for h in holes):
                continue
            i0, i1 = p0 + 0.16, p1 - 0.16
            brace("SH_Timber", wall, side, i0, 0.8, (i0 + i1) / 2 - 0.08, 2.76, 0.15, 0.05)
            brace("SH_Timber", wall, side, i1, 0.8, (i0 + i1) / 2 + 0.08, 2.76, 0.15, 0.05)
            brace("SH_Timber", wall, side, i0, 4.82, (i0 + i1) / 2 - 0.08, 3.02, 0.15, 0.05)
            brace("SH_Timber", wall, side, i1, 4.82, (i0 + i1) / 2 + 0.08, 3.02, 0.15, 0.05)
    for h in wall["holes"]:
        casing_out(wall, side, h, *neighbors(wall["holes"], h))
        if h[2] > FLOOR + 1e-4:
            alfeizar(wall, side, h, 0.16)
    eave(wall, side, E0 - (0.38 if side["extend"] else 0.0), E1 + (0.38 if side["extend"] else 0.0))


def casing_out(wall, side, h, left=None, right=None):
    u0, u1, z0, z1 = h
    W, O = 0.2, 0.07
    P = 0.008
    door = z0 <= FLOOR + 1e-4
    zb = FLOOR if door else z0 - 0.08
    if left is None:
        wrbox("SH_Timber", wall, side, u0 - W - P, u0 - P, -0.02, O, zb, z1 + 0.2, 0.025)
    if right is None:
        wrbox("SH_Timber", wall, side, u1 + P, u1 + W + P, -0.02, O, zb, z1 + 0.2, 0.025)
    else:
        wrbox("SH_Timber", wall, side, u1 + P, right - P, -0.02, O, min(zb, FLOOR), z1 + 0.2, 0.025)
    la = u0 - W - 0.1 if left is None else left + P + 0.03
    lb = u1 + W + 0.1 if right is None else right - P - 0.03
    wrbox("SH_Timber", wall, side, la, lb, -0.02, O + 0.02, z1 + P, z1 + 0.22, 0.035)
    for u in ((u0 - W - 0.1,) if left is None else ()) + ((u1 + W + 0.1,) if right is None else ()):
        wrbox("SH_Walnut", wall, side, u - 0.055, u + 0.055, -0.02, O + 0.045, z1 + 0.02, z1 + 0.2, 0.04)
    if not door:
        wrbox("SH_Timber", wall, side, max(la, u0 - W - 0.06), min(lb, u1 + W + 0.06), -0.02, 0.13, z0 - 0.1,
              z0 - 0.012, 0.03)
        rise = min(0.22, 4.86 - (z1 + 0.22) - 0.04)
        if rise > 0.1:
            arch("SH_Walnut", wall, side, u0 + 0.1, u1 - 0.1, z1 + 0.22, rise, 0.09, 0.06)


def eave(wall, side, u0, u1):
    D = 0.42
    prof = [(-0.02, 5.18), (0.08, 5.18), (D, 5.24), (D + 0.02, 5.28), (D, 5.32), (0.0, 5.52), (-0.02, 5.52)]
    extrude("SH_Walnut", wall, side, u0, u1, prof)
    n = max(2, int((u1 - u0) / 1.6))
    for k in range(n + 1):
        u = u0 + 0.25 + (u1 - u0 - 0.5) * k / n
        pts = [(0.0, 4.86), (0.07, 4.9), (0.2, 5.08), (0.3, 5.21), (0.0, 5.21)]
        prism("SH_Timber", [wp(wall, side, u - 0.06, o, z) for o, z in pts],
              [wp(wall, side, u + 0.06, o, z) for o, z in pts])


def build_cap(wall, u0, u1, garland=True):
    group("cap_" + wall["name"])
    t0, t1 = wall["t"]
    w = t1 - t0
    side = dict(plane=t0, s=1)
    prof = [(-0.05, TOP - 0.06), (w + 0.05, TOP - 0.06), (w + 0.05, TOP + 0.04), (w + 0.025, TOP + 0.11),
            (w - 0.03, TOP + 0.135), (0.03, TOP + 0.135), (-0.025, TOP + 0.11), (-0.05, TOP + 0.04)]
    extrude("SH_Walnut", wall, side, u0, u1, prof)
    if not garland:
        return
    rnd = random.Random(len(wall["name"]) * 31 + int(u0))
    zc = TOP + 0.15
    vine = [wp(wall, side, u, w / 2 + 0.06 * math.sin(u * 2.3), zc) for u in
            [u0 + 0.05 + (u1 - u0 - 0.1) * k / max(2, int((u1 - u0) / 0.6)) for k in range(max(2, int((u1 - u0) / 0.6)) + 1)]]
    tube_bm(vine, 0.025, 4, bm=B("SH_Moss"))
    u = u0 + 0.12
    k = 0
    ud, nd = wu(wall), wn(wall)
    while u < u1 - 0.12:
        sgn = 1 if k % 2 == 0 else -1
        ang = math.radians(38) * sgn
        dvec = ud * math.cos(ang) + nd * math.sin(ang)
        c = wp(wall, side, u, w / 2 + 0.06 * math.sin(u * 2.3), zc) + dvec * 0.11 + Vector((0, 0, 0.015))
        m = "SH_Leaf" if k % 5 not in (2,) else "SH_Moss"
        bmL = B(m)
        before = set(bmL.verts)
        ellipsoid_bm((0, 0, 0), (0.13, 0.075, 0.035), 5, 3, bm=bmL)
        rot = Matrix.Rotation(math.atan2(dvec.y, dvec.x), 4, "Z")
        bmesh.ops.transform(bmL, matrix=Matrix.Translation(c) @ rot, verts=[v for v in bmL.verts if v not in before])
        if k % 9 == 4:
            ellipsoid_bm(wp(wall, side, u, w / 2, zc + 0.05), (0.045, 0.045, 0.04), 6, 4, bm=B("SH_Gold"))
        u += rnd.uniform(0.21, 0.25)
        k += 1


def corner_posts():
    group("pilasters")
    corners = [(24.0, -7.5, 1, -1), (36.0, -7.5, -1, -1), (24.0, -18.0, 1, 1), (36.0, -18.0, -1, 1),
               (24.0, -18.5, 1, -1), (36.0, -18.5, -1, -1), (24.0, -24.5, 1, 1), (36.0, -24.5, -1, 1)]
    W, O = 0.2, 0.065
    for cx, cy, dx, dy in corners:
        for lo, hi in (((cx, cy), (cx + dx * W, cy + dy * O)), ((cx, cy), (cx + dx * O, cy + dy * W))):
            x0, x1 = sorted((lo[0] - dx * 0.02, hi[0]))
            y0, y1 = sorted((lo[1] - dy * 0.02, hi[1]))
            c = ((x0 + x1) / 2, (y0 + y1) / 2, (FLOOR + PLATE0) / 2)
            rbox_bm(c, (x1 - x0, y1 - y0, PLATE0 - FLOOR), 0.02, segs=1, bm=B("SH_Timber"))
        group("lanterns")
        lantern(cx, cy, dx, dy)
        group("pilasters")


def lantern(cx, cy, dx, dy):
    d = Vector((dx, dy, 0)).normalized()
    base = Vector((cx, cy, 4.75))
    tip = base + d * 0.27
    tube_bm([base - d * 0.02, base + d * 0.12 + Vector((0, 0, 0.05)), tip + Vector((0, 0, 0.02))], 0.024, 6,
            bm=B("SH_Walnut"))
    tube_bm([base + Vector((0, 0, -0.25)), base + d * 0.13 + Vector((0, 0, 0.02))], 0.02, 6, bm=B("SH_Walnut"))
    c = Vector((tip.x, tip.y, 0))
    tube_bm([(c.x, c.y, 4.77), (c.x, c.y, 4.55)], 0.012, 5, bm=B("SH_Timber"))
    m = Matrix.Translation(c)
    lathe_bm([(0.0, 4.2), (0.05, 4.2), (0.075, 4.23), (0.0, 4.24)], 8, bm=B("SH_Walnut"), matrix=m)
    lathe_bm([(0.0, 4.23), (0.07, 4.23), (0.085, 4.32), (0.075, 4.44), (0.0, 4.45)], 8, bm=B("SH_Gold"), matrix=m)
    lathe_bm([(0.0, 4.43), (0.1, 4.43), (0.09, 4.47), (0.04, 4.53), (0.015, 4.56), (0.0, 4.57)], 8,
             bm=B("SH_Walnut"), matrix=m)


def plank_floor(x0, x1, y0, y1, along, W, mats, seed, gapmat):
    quad(gapmat, [(x0, y0, FLOOR - 0.01), (x1, y0, FLOOR - 0.01), (x1, y1, FLOOR - 0.01), (x0, y1, FLOOR - 0.01)],
         (0, 0, 1))
    rnd = random.Random(seed)
    g = 0.008
    if along == "x":
        A0, A1, C0, C1 = x0, x1, y0, y1
    else:
        A0, A1, C0, C1 = y0, y1, x0, x1
    rows = int(round((C1 - C0) / W))
    Wr = (C1 - C0) / rows
    nails = B("SH_Timber")
    for r in range(rows):
        ca, cb = C0 + r * Wr + g, C0 + (r + 1) * Wr - g
        s = A0 - rnd.uniform(0.0, 1.8)
        k = r
        while s < A1:
            L = rnd.uniform(1.8, 3.2)
            a, b = max(s, A0), min(s + L, A1)
            if b - a > 0.25:
                m = mats[k % len(mats)]
                pa, pb = a + (g if a > A0 else 0), b - (g if b < A1 else 0)
                if along == "x":
                    chamfer_tile(m, pa, pb, ca, cb, FLOOR, FLOOR - 0.01, 0.012)
                else:
                    chamfer_tile(m, ca, cb, pa, pb, FLOOR, FLOOR - 0.01, 0.012)
                if b < A1:
                    e = pb - 0.07
                    for cc in (ca + 0.07, cb - 0.07):
                        p = (e, cc) if along == "x" else (cc, e)
                        lathe_bm([(0.018, FLOOR - 0.002), (0.0, FLOOR + 0.004)], 4, bm=nails,
                                 matrix=Matrix.Translation((p[0], p[1], 0)))
            s += L
            k += 1


def chamfer_tile(mat, x0, x1, y0, y1, ztop, zbot, c):
    bm = B(mat)
    o = [bm.verts.new(p) for p in ((x0, y0, zbot), (x1, y0, zbot), (x1, y1, zbot), (x0, y1, zbot))]
    i = [bm.verts.new(p) for p in ((x0 + c, y0 + c, ztop), (x1 - c, y0 + c, ztop), (x1 - c, y1 - c, ztop),
                                   (x0 + c, y1 - c, ztop))]
    face(bm, i, (0, 0, 1))
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    for k in range(4):
        k1 = (k + 1) % 4
        face(bm, [o[k], o[k1], i[k1], i[k]], (dirs[k][0], dirs[k][1], 1))


def build_floors():
    group("floor_shop")
    plank_floor(24.0, 36.0, -18.0, -7.5, "y", 0.34, ["SH_Oak", "SH_Honey"], 5, "SH_Timber")
    group("floor_back")
    plank_floor(24.0, 36.0, -24.5, -18.5, "x", 0.3, ["SH_Honey", "SH_Walnut"], 7, "SH_Timber")
    group("thresholds")
    for lo, hi in (((28.5, -7.5), (31.5, -7.0)), ((33.38, -18.5), (35.25, -18.0)), ((23.5, -24.0), (24.0, -21.75))):
        abox("SH_Walnut", (lo[0], lo[1], FLOOR - 0.06), (hi[0], hi[1], FLOOR), skip=("-z",))


def ramp(name, axis, lo, hi, W0, W1):
    group(name)
    L0, L1 = lo, hi
    f = lambda s: FLOOR * (s - L0) / (L1 - L0)

    def P(s, w, z):
        return Vector((w, s, z)) if axis == "y" else Vector((s, w, z))

    nrm_top = (P(0, 0, 1) - P(1, 0, 0) * (FLOOR / (L1 - L0))).normalized()
    smin, smax = min(L0, L1), max(L0, L1)
    quad("SH_Timber", [P(smin, W0, f(smin) - 0.012), P(smax, W0, f(smax) - 0.012), P(smax, W1, f(smax) - 0.012),
                       P(smin, W1, f(smin) - 0.012)], nrm_top)
    n = int(round((smax - smin) / 0.32))
    step = (smax - smin) / n
    for k in range(n):
        s0, s1 = smin + k * step + (0.01 if k > 0 else 0), smin + (k + 1) * step - (0.01 if k < n - 1 else 0)
        bm = B("SH_Oak" if k % 2 == 0 else "SH_Honey")
        c = 0.012
        o = [bm.verts.new(P(s0, W0, f(s0) - 0.012)), bm.verts.new(P(s1, W0, f(s1) - 0.012)),
             bm.verts.new(P(s1, W1, f(s1) - 0.012)), bm.verts.new(P(s0, W1, f(s0) - 0.012))]
        i = [bm.verts.new(P(s0 + c, W0 + c, f(s0 + c))), bm.verts.new(P(s1 - c, W0 + c, f(s1 - c))),
             bm.verts.new(P(s1 - c, W1 - c, f(s1 - c))), bm.verts.new(P(s0 + c, W1 - c, f(s0 + c)))]
        face(bm, i, nrm_top)
        cen = sum((v.co for v in o), Vector()) / 4
        for a in range(4):
            b = (a + 1) % 4
            mid = (o[a].co + o[b].co) / 2
            face(bm, [o[a], o[b], i[b], i[a]], (mid - cen).normalized() + nrm_top)
    for w, wo in ((W0, W0 - 0.1), (W1, W1 + 0.1)):
        a, b = sorted((w, wo))
        top = lambda s: f(s) + 0.04
        pts = [(smin, GROUND), (smax, GROUND), (smax, top(smax)), (smin, top(smin))]
        prism("SH_StoneDark", [P(s, a, z) for s, z in pts], [P(s, b, z) for s, z in pts])
        t0 = smin - (0.012 if L0 < L1 else 0.0)
        t1 = smax + (0.012 if L0 > L1 else 0.0)
        prism("SH_Timber", [P(s, a - 0.01, z) for s, z in ((t0, top(smin) - 0.02), (t1, top(smax) - 0.02),
                                                             (t1, top(smax) + 0.03), (t0, top(smin) + 0.03))],
              [P(s, b + 0.01, z) for s, z in ((t0, top(smin) - 0.02), (t1, top(smax) - 0.02),
                                              (t1, top(smax) + 0.03), (t0, top(smin) + 0.03))])
    quad("SH_StoneDark", [P(L0, W0, GROUND), P(L0, W1, GROUND), P(L0, W1, f(L0) - 0.012),
                          P(L0, W0, f(L0) - 0.012)], P(1 if L0 > L1 else -1, 0, 0))


def shelf(wall, side, u0, u1, z, depth=0.26):
    decor_zone(wall, side, u0, u1)
    wrbox("SH_Oak", wall, side, u0, u1, -0.02, depth, z - 0.05, z, 0.018)
    for u in (u0 + 0.18, u1 - 0.18):
        pts = [(-0.02, z - 0.05), (depth - 0.05, z - 0.05), (0.0, z - 0.32)]
        prism("SH_Walnut", [wp(wall, side, u - 0.035, o, zz) for o, zz in pts],
              [wp(wall, side, u + 0.035, o, zz) for o, zz in pts])


def food_bag(wall, side, u, z, mat, h=0.3):
    c = wp(wall, side, u, 0.13, z + h / 2)
    sz = R3(wall, 0.2, 0.15, h)
    rbox_bm((c.x, c.y, c.z), sz, 0.045, segs=1, bm=B(mat))
    cc = wp(wall, side, u, 0.13, z + h - 0.01)
    rbox_bm((cc.x, cc.y, cc.z), R3(wall, 0.21, 0.12, 0.035), 0.012, segs=1, bm=B("SH_Parchment"))
    lc = wp(wall, side, u, 0.205, z + h * 0.48)
    ellipsoid_bm(lc, R3(wall, 0.06, 0.012, 0.06), 8, 4, bm=B("SH_Parchment"))
    for du, dz in ((-0.03, 0.035), (0.0, 0.05), (0.03, 0.035)):
        ellipsoid_bm(wp(wall, side, u + du, 0.215, z + h * 0.48 + dz), R3(wall, 0.014, 0.008, 0.016), 5, 3,
                     bm=B("SH_Walnut"))
    ellipsoid_bm(wp(wall, side, u, 0.215, z + h * 0.48 - 0.012), R3(wall, 0.026, 0.008, 0.022), 6, 3,
                 bm=B("SH_Walnut"))


def bone(a, b, r, bm):
    a, b = Vector(a), Vector(b)
    tube_bm([a, b], r, 6, bm=bm)
    d = (b - a).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 0.1:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    for p in (a, b):
        for s in (-1, 1):
            ellipsoid_bm(p + side * s * r * 0.9, (r * 1.25, r * 1.25, r * 1.25), 5, 3, bm=bm)


JAR_COUNT = [0]


def jar(wall, side, u, z, lid):
    JAR_COUNT[0] += 1
    if JAR_COUNT[0] % 2 == 0:
        lid = None
    c = wp(wall, side, u, 0.13, 0.0)
    m = Matrix.Translation((c.x, c.y, z))
    lathe_bm([(0.0, 0.0), (0.07, 0.0), (0.085, 0.03), (0.085, 0.17), (0.06, 0.2), (0.0, 0.2)], 8,
             bm=B("SH_Glass"), matrix=m)
    if lid:
        lathe_bm([(0.0, 0.195), (0.068, 0.195), (0.07, 0.23), (0.03, 0.245), (0.0, 0.25)], 8, bm=B(lid), matrix=m)
        ellipsoid_bm((c.x, c.y, z + 0.27), (0.025, 0.025, 0.025), 6, 4, bm=B(lid))
        lathe_bm([(0.0, 0.07), (0.098, 0.07), (0.098, 0.13), (0.0, 0.13)], 8, bm=B(lid), matrix=m)
    else:
        lathe_bm([(0.058, 0.2), (0.07, 0.215), (0.064, 0.225), (0.0, 0.18)], 8, bm=B("SH_Glass"), matrix=m)
        bone(wp(wall, side, u - 0.03, 0.12, z + 0.17), wp(wall, side, u - 0.07, 0.15, z + 0.31), 0.013,
             B("SH_Parchment"))
        bone(wp(wall, side, u + 0.02, 0.14, z + 0.17), wp(wall, side, u + 0.06, 0.11, z + 0.29), 0.013,
             B("SH_Parchment"))


def collar_rail(wall, side, u0, u1, z, mats):
    decor_zone(wall, side, u0, u1)
    wrbox("SH_Walnut", wall, side, u0, u1, -0.02, 0.05, z - 0.06, z + 0.06, 0.02)
    n = len(mats)
    for k, m in enumerate(mats):
        u = u0 + (u1 - u0) * (k + 0.5) / n
        a = wp(wall, side, u, 0.04, z)
        b = wp(wall, side, u, 0.15, z + 0.05)
        tube_bm([a, b], 0.018, 6, bm=B("SH_Timber"))
        ellipsoid_bm(b, (0.025, 0.025, 0.025), 6, 4, bm=B("SH_Timber"))
        R = 0.085 if k % 2 == 0 else 0.07
        cc = wp(wall, side, u, 0.1, z + 0.02 - R)
        rot = Matrix.Rotation(math.pi / 2, 4, "X") if wall["axis"] == "x" else Matrix.Rotation(math.pi / 2, 4, "Y")
        torus_bm(R, 0.02, 10, 4, bm=B(m), matrix=Matrix.Translation(cc) @ rot)
        ellipsoid_bm(wp(wall, side, u, 0.115, z + 0.02 - 2 * R - 0.02), R3(wall, 0.022, 0.012, 0.026), 5, 3,
                     bm=B("SH_Gold"))
        if k % 2 == 1:
            pts = [wp(wall, side, u + 0.02, 0.09, z + 0.03), wp(wall, side, u + 0.06, 0.08, z - 0.3),
                   wp(wall, side, u + 0.02, 0.07, z - 0.6), wp(wall, side, u + 0.05, 0.07, z - 0.78)]
            tube_bm(catmull(pts, 3), 0.014, 5, bm=B(m))
            cc2 = wp(wall, side, u + 0.05, 0.07, z - 0.86)
            torus_bm(0.06, 0.016, 8, 4, bm=B(m), matrix=Matrix.Translation(cc2) @ rot)


def sign(wall, side, u, z, w, h, motif, low=False):
    decor_zone(wall, side, u - w / 2 - 0.1, u + w / 2 + 0.1, low)
    wrbox("SH_Oak", wall, side, u - w / 2 + 0.03, u + w / 2 - 0.03, -0.02, 0.05, z - h / 2 + 0.03, z + h / 2 - 0.03,
          0.03)
    for a, b, p, q, f in ((u - w / 2, u + w / 2, z + h / 2 - 0.07, z + h / 2, 0.07),
                          (u - w / 2, u + w / 2, z - h / 2, z - h / 2 + 0.07, 0.07),
                          (u - w / 2 + 0.012, u - w / 2 + 0.07, z - h / 2 + 0.05, z + h / 2 - 0.05, 0.061),
                          (u + w / 2 - 0.07, u + w / 2 - 0.012, z - h / 2 + 0.05, z + h / 2 - 0.05, 0.061)):
        wrbox("SH_Walnut", wall, side, a, b, -0.02, f, p, q, 0.025)
    s = min(w, h) * 0.5
    bm = B("SH_Walnut")
    if motif == "paw":
        ellipsoid_bm(wp(wall, side, u, 0.05, z - 0.12 * s), R3(wall, 0.36 * s, 0.03, 0.3 * s), 10, 4, bm=bm)
        for du, dz, r in ((-0.38, 0.24, 0.13), (-0.14, 0.45, 0.14), (0.14, 0.45, 0.14), (0.38, 0.24, 0.13)):
            ellipsoid_bm(wp(wall, side, u + du * s, 0.05, z + dz * s), R3(wall, r * s, 0.028, r * 1.2 * s), 7, 3,
                         bm=bm)
    elif motif == "bone":
        bone(wp(wall, side, u - 0.5 * s, 0.06, z), wp(wall, side, u + 0.5 * s, 0.06, z), 0.13 * s, B("SH_Parchment"))
    elif motif == "fish":
        ellipsoid_bm(wp(wall, side, u - 0.08 * s, 0.05, z), R3(wall, 0.48 * s, 0.03, 0.27 * s), 12, 5, bm=B("SH_Teal"))
        tail = [(u + 0.32 * s, z), (u + 0.62 * s, z + 0.26 * s), (u + 0.62 * s, z - 0.26 * s)]
        face_prism("SH_Teal", wall, side, tail, 0.03, 0.07)
        ellipsoid_bm(wp(wall, side, u - 0.36 * s, 0.075, z + 0.06 * s), R3(wall, 0.05 * s, 0.015, 0.05 * s), 6, 4,
                     bm=B("SH_Parchment"))


def pecera(wall, side, u, z):
    W, H, D = 1.1, 0.72, 0.27
    decor_zone(wall, side, u - W / 2, u + W / 2)
    wrbox("SH_Walnut", wall, side, u - W / 2, u + W / 2, -0.02, D, z - 0.08, z, 0.025)
    wrbox("SH_Walnut", wall, side, u - W / 2, u + W / 2, -0.02, D, z + H, z + H + 0.08, 0.025)
    for a in (u - W / 2, u + W / 2 - 0.07):
        wrbox("SH_Walnut", wall, side, a, a + 0.07, -0.02, D, z, z + H, 0.02)
    wbox("SH_Water", wall, side, u - W / 2 + 0.07, u + W / 2 - 0.07, -0.02, D - 0.04, z, z + H - 0.12)
    wbox("SH_Glass", wall, side, u - W / 2 + 0.07, u + W / 2 - 0.07, -0.02, D - 0.05, z + H - 0.12, z + H)
    for du, dz, s in ((-0.2, 0.25, 1.0), (0.18, 0.42, 0.8)):
        c = wp(wall, side, u + du, D - 0.04, z + dz)
        ellipsoid_bm(c, R3(wall, 0.08 * s, 0.03, 0.05 * s), 8, 4, bm=B("SH_Gold"))
        f = 1 if du < 0 else -1
        tail = [(u + du + f * 0.07 * s, z + dz), (u + du + f * 0.13 * s, z + dz + 0.045 * s),
                (u + du + f * 0.13 * s, z + dz - 0.045 * s)]
        face_prism("SH_Gold", wall, side, tail, D - 0.06, D - 0.025)
    for du, hh in ((-0.4, 0.3), (-0.33, 0.22), (0.38, 0.34)):
        ellipsoid_bm(wp(wall, side, u + du, D - 0.045, z + hh / 2 + 0.02), R3(wall, 0.04, 0.02, hh / 2), 6, 4,
                     bm=B("SH_Leaf"))
    for du, dz in ((0.05, 0.3), (0.08, 0.42), (0.03, 0.5)):
        ellipsoid_bm(wp(wall, side, u + du, D - 0.04, z + dz), (0.018, 0.018, 0.018), 5, 3, bm=B("SH_Glass"))
    wrbox("SH_Stone", wall, side, u - W / 2 + 0.085, u + W / 2 - 0.085, -0.02, D - 0.025, z, z + 0.05, 0.015)


def mushrooms(x, y, dx, dy, s=1.0):
    group("mushrooms")
    for k, (ox, oy, sc) in enumerate(((0.3, 0.3, 1.0), (0.55, 0.12, 0.65), (0.12, 0.6, 0.55))):
        cx, cy = x + dx * ox * s, y + dy * oy * s
        sc *= s
        m = Matrix.Translation((cx, cy, GROUND))
        lathe_bm([(0.0, 0.0), (0.08 * sc, 0.0), (0.06 * sc, 0.2 * sc), (0.055 * sc, 0.36 * sc), (0.0, 0.38 * sc)], 6,
                 bm=B("SH_Parchment"), matrix=m)
        lathe_bm([(0.0, 0.3 * sc), (0.22 * sc, 0.3 * sc), (0.24 * sc, 0.34 * sc), (0.2 * sc, 0.44 * sc),
                  (0.1 * sc, 0.52 * sc), (0.0, 0.54 * sc)], 8, bm=B("SH_Plum" if k != 1 else "SH_Gold"), matrix=m)
        for a in range(2):
            ang = a * 3.1 + k
            r = 0.13 * sc
            ellipsoid_bm((cx + math.cos(ang) * r, cy + math.sin(ang) * r, GROUND + 0.47 * sc),
                         (0.035 * sc, 0.035 * sc, 0.018 * sc), 5, 3, bm=B("SH_Parchment"))
    for k in range(3):
        ang = math.atan2(dy, dx) + (k - 1) * 0.7
        p0 = Vector((x + dx * 0.04, y + dy * 0.04, GROUND + 0.35))
        pts = [p0, p0 + Vector((math.cos(ang) * 0.25, math.sin(ang) * 0.25, -0.2)),
               p0 + Vector((math.cos(ang) * 0.55, math.sin(ang) * 0.55, -0.33))]
        tube_bm(catmull(pts, 3), [0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.012], 5, bm=B("SH_Walnut"))


def dress():
    W = {w["name"]: w for w in WALLS}
    west_in = W["west"]["sides"][0]
    east_in = W["east"]["sides"][0]
    mid_shop = W["mid"]["sides"][1]
    mid_back = W["mid"]["sides"][0]
    back_in = W["back"]["sides"][0]
    group("west_in")
    shelf(W["west"], west_in, -16.9, -14.7, 1.95)
    shelf(W["west"], west_in, -16.9, -14.7, 2.65)
    for k, u in enumerate((-16.6, -16.3, -16.0)):
        food_bag(W["west"], west_in, u, 1.95, ["SH_Gold", "SH_Sage", "SH_Teal"][k])
    for k, u in enumerate((-15.55, -15.2, -14.95)):
        jar(W["west"], west_in, u, 1.95, ["SH_Plum", "SH_Teal", "SH_Gold"][k])
    for k, u in enumerate((-16.65, -16.35)):
        jar(W["west"], west_in, u, 2.65, ["SH_Sage", "SH_Gold"][k])
    for k, u in enumerate((-15.75, -15.45, -15.15)):
        food_bag(W["west"], west_in, u, 2.65, ["SH_Plum", "SH_Gold", "SH_Sage"][k], h=0.26)
    collar_rail(W["west"], west_in, -13.3, -11.3, 2.35, ["SH_Teal", "SH_Plum", "SH_Gold", "SH_Sage", "SH_Teal"])
    sign(W["west"], west_in, -12.3, 3.9, 0.9, 0.6, "bone")
    group("east_in")
    pecera(W["east"], east_in, -14.6, 1.95)
    sign(W["east"], east_in, -14.6, 3.9, 0.9, 0.6, "fish")
    shelf(W["east"], east_in, -11.8, -9.8, 2.2)
    for k, u in enumerate((-11.45, -11.1, -10.75, -10.4, -10.1)):
        jar(W["east"], east_in, u, 2.2, ["SH_Teal", "SH_Plum", "SH_Gold", "SH_Sage", "SH_Plum"][k])
    group("mid_in")
    sign(W["mid"], mid_shop, 29.2, 4.2, 1.3, 1.0, "paw")
    collar_rail(W["mid"], mid_shop, 25.4, 27.4, 2.35, ["SH_Plum", "SH_Sage", "SH_Gold", "SH_Teal"])
    shelf(W["mid"], mid_shop, 30.4, 32.4, 2.1)
    for k, u in enumerate((30.7, 31.05, 31.4, 31.75, 32.1)):
        if k % 2 == 0:
            food_bag(W["mid"], mid_shop, u, 2.1, ["SH_Sage", "SH_Gold", "SH_Teal"][k // 2])
        else:
            jar(W["mid"], mid_shop, u, 2.1, ["SH_Gold", "SH_Plum"][k // 2])
    group("east_in")
    shelf(W["east"], east_in, -22.4, -19.8, 1.7, depth=0.28)
    shelf(W["east"], east_in, -22.4, -19.8, 2.5, depth=0.28)
    for k, u in enumerate((-22.1, -21.75, -21.4, -21.05, -20.7, -20.35, -20.05)):
        food_bag(W["east"], east_in, u, 1.7 if k < 4 else 1.7, ["SH_Gold", "SH_Sage", "SH_Teal", "SH_Plum"][k % 4],
                 h=0.32)
    for k, u in enumerate((-22.1, -21.75, -21.4, -21.05, -20.7)):
        jar(W["east"], east_in, u, 2.5, ["SH_Sage", "SH_Plum", "SH_Gold", "SH_Teal", "SH_Sage"][k])
    group("back_in")
    collar_rail(W["back"], back_in, 30.0, 32.4, 2.35, ["SH_Gold", "SH_Teal", "SH_Plum", "SH_Sage", "SH_Gold"])
    group("mid_in")
    sign(W["mid"], mid_back, 29.2, 4.2, 1.1, 0.8, "bone")
    group("back_in")
    sign(W["back"], back_in, 27.3, 3.9, 0.9, 0.6, "paw")
    for x, y, dx, dy in ((23.5, -7.0, -1, 1), (36.5, -7.0, 1, 1), (23.5, -25.0, -1, -1), (36.5, -25.0, 1, -1)):
        mushrooms(x, y, dx, dy, 1.0 if y < -20 else 0.8)
    group("west_out")
    ws = W["west"]["sides"][1]
    sign(W["west"], ws, -15.42, 3.9, 0.8, 0.8, "paw")
    group("east_out")
    sign(W["east"], W["east"]["sides"][1], -15.42, 3.9, 0.8, 0.8, "paw")
    group("back_out")
    sign(W["back"], W["back"]["sides"][1], 30.0, 3.9, 0.8, 0.8, "paw")


def build():
    dress_pre()
    for w in WALLS:
        build_core(w)
        for side in w["sides"]:
            if side["kind"] == "in":
                build_interior_side(w, side)
            else:
                build_exterior_side(w, side)
    build_cap(WALLS[0], 23.45, 36.55, garland=False)
    build_cap(WALLS[1], 23.45, 36.55, garland=False)
    build_cap(WALLS[2], -24.45, -7.55)
    build_cap(WALLS[3], -24.45, -7.55)
    build_cap(WALLS[4], 24.05, 35.95, garland=False)
    corner_posts()
    build_floors()
    ramp("ramp_front", "y", -4.5, -7.0, 28.5, 31.5)
    ramp("ramp_west", "x", 21.5, 23.5, -24.0, -21.75)
    dress()


def dress_pre():
    dress()
    for g in list(GROUPS):
        for bm in GROUPS[g].values():
            bm.free()
    GROUPS.clear()


def materialize():
    objs = {}
    for g, mats in GROUPS.items():
        for m, bm in mats.items():
            if len(bm.faces) == 0:
                bm.free()
                continue
            objs.setdefault(g, []).append(finish("%s__%s" % (g, m), bm, m, angle=40))
    return objs


def parse_obj(match):
    V, F, cur = [], [], None
    for line in open(OBJ_PATH):
        p = line.split()
        if not p:
            continue
        if p[0] == "o":
            cur = p[1]
        elif p[0] == "v":
            V.append(Vector(tuple(map(float, p[1:4]))))
        elif p[0] == "f" and cur and match(cur):
            F.append([int(t.split("/")[0]) - 1 for t in p[1:]])
    return V, F


def import_obj_objects(match):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=OBJ_PATH, forward_axis='Y', up_axis='Z')
    new = [o for o in bpy.data.objects if o not in before]
    keep = []
    for o in new:
        if match(o.name):
            keep.append(o)
        else:
            bpy.data.objects.remove(o)
    return keep


def solid_at(p):
    for w in WALLS:
        t0, t1 = w["t"]
        a0, a1 = w["a"]
        x0, x1, y0, y1 = (a0, a1, t0, t1) if w["axis"] == "x" else (t0, t1, a0, a1)
        if x0 < p.x < x1 and y0 < p.y < y1 and 0 < p.z < TOP:
            inh = False
            for h in w["holes"]:
                u = p.x if w["axis"] == "x" else p.y
                if h[0] < u < h[1] and h[2] < p.z < h[3]:
                    inh = True
            if not inh:
                return True
    if 23.5 < p.x < 36.5 and -25 < p.y < -7 and 0 < p.z < FLOOR:
        return True
    return False


def solid_check(p):
    if solid_at(p):
        return True
    for w in WALLS:
        t0, t1 = w["t"]
        a0, a1 = w["a"]
        x0, x1, y0, y1 = (a0, a1, t0, t1) if w["axis"] == "x" else (t0, t1, a0, a1)
        if x0 < p.x < x1 and y0 < p.y < y1 and GROUND < p.z <= 0.0:
            return True
    return False


def bvh_of(objs):
    vs, ps = [], []
    for o in objs:
        base = len(vs)
        vs += [o.matrix_world @ v.co for v in o.data.vertices]
        ps += [[base + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(vs, ps)


def measure(objs):
    base_groups = lambda g: g.endswith("_core") or g.startswith(("floor_", "thresholds", "ramp_"))
    core = bvh_of([o for g, lst in objs.items() if base_groups(g) for o in lst])
    full = bvh_of([o for lst in objs.values() for o in lst])
    V, F = parse_obj(lambda n: "PetShop" in n)
    stats = {}
    miss = 0
    rnd = random.Random(3)
    for f in F:
        a, b, c = V[f[0]], V[f[1]], V[f[2]]
        n = (b - a).cross(c - a)
        area = n.length / 2
        if area < 1e-6:
            continue
        n.normalize()
        zs = [a.z, b.z, c.z]
        if abs(n.z) > 0.99 and (min(zs) > TOP - 0.01 or max(zs) < 0.01):
            continue
        k = max(3, int(area * 6))
        for _ in range(k):
            r1, r2 = rnd.random(), rnd.random()
            if r1 + r2 > 1:
                r1, r2 = 1 - r1, 1 - r2
            p = a + (b - a) * r1 + (c - a) * r2
            d = n.copy()
            if solid_at(p + d * 0.03):
                d = -d
            if solid_at(p + d * 0.03) or (abs(d.z) > 0.5 and d.z < 0):
                continue
            if abs(d.z) > 0.99:
                cat = "floor"
            elif abs(d.z) > 0.05:
                cat = "ramp"
            else:
                cat = "wall"
                for w in WALLS:
                    u = p.x if w["axis"] == "x" else p.y
                    tc = p.y if w["axis"] == "x" else p.x
                    for h in w["holes"]:
                        if w["t"][0] - 0.01 <= tc <= w["t"][1] + 0.01 and h[0] - 0.01 <= u <= h[1] + 0.01 and                                 h[2] - 0.01 <= p.z <= h[3] + 0.01:
                            cat = "reveal"
            if cat == "wall":
                q = p + d * 0.05
                cat = "wall_in" if (24 < q.x < 36 and -24.5 < q.y < -7.5) else "wall_out"
            o = p + d * 0.2
            hc = core.ray_cast(o, -d, 0.45)
            hf = full.ray_cast(o, -d, 0.45)
            if hc[0] is None:
                miss += 1
                continue
            st = stats.setdefault(cat, ([], []))
            st[0].append(0.2 - hc[3])
            near_corner = any(abs(p.x - c) < 0.06 for c in (24.0, 36.0)) and                 any(abs(p.y - c) < 0.06 for c in (-7.5, -18.0, -18.5, -24.5)) or                 (abs(d.x) > 0.9 and any(abs(p.y - c) < 0.06 for c in (-7.5, -18.0, -18.5, -24.5))) or                 (abs(d.y) > 0.9 and any(abs(p.x - c) < 0.06 for c in (24.0, 36.0)))
            if not (cat == "wall_in" and near_corner):
                st[1].append(0.2 - hf[3])
    print("MEASURE miss", miss)
    for k, (cv, fv) in stats.items():
        print("MEASURE %-7s n=%5d  base dev: min=%+.3f max=%+.3f max|d|=%.3f   deco protrusion max=%+.3f" % (
            k, len(cv), min(cv), max(cv), max(abs(x) for x in cv), max(fv) if fv else 0.0))


def make_wire_overlay():
    objs = import_obj_objects(lambda n: "PetShop" in n)
    red = bpy.data.materials.new("OverlayRed")
    red.diffuse_color = (0.95, 0.05, 0.05, 1)
    for o in objs:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1), verts=bm.verts, edges=bm.edges)
        bm.to_mesh(o.data)
        bm.free()
        o.data.materials.clear()
        o.data.materials.append(red)
        mod = o.modifiers.new("w", "WIREFRAME")
        mod.thickness = 0.05
        mod.use_replace = True
        o.show_in_front = True
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
    sh.shadow_intensity = 0.35
    sc.display.light_direction = (0.35, -0.45, 0.82)
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.35
    sc.world = sc.world or bpy.data.worlds.new("World")
    sc.world.color = (0.42, 0.45, 0.48)
    gm = bpy.data.materials.new("Ground")
    gm.diffuse_color = (0.33, 0.36, 0.38, 1)
    bpy.ops.mesh.primitive_plane_add(size=120, location=(30, -18, GROUND + 0.005))
    bpy.context.active_object.data.materials.append(gm)
    bpy.context.active_object.name = "GroundRef"


def cam_render(path, az, el, target, ortho, res=900, persp=None):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    if persp:
        cd.type = "PERSP"
        cd.lens = persp
    else:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    cd.clip_start = 0.1
    cd.clip_end = 300
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    a, e = math.radians(az), math.radians(el)
    t = Vector(target)
    dist = ortho if persp else 80
    cam.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def set_hidden(objs, prefixes):
    for g, lst in objs.items():
        hide = any(g.startswith(p) for p in prefixes)
        for o in lst:
            o.hide_render = hide


def previews(objs, out):
    os.makedirs(out, exist_ok=True)
    scene_setup()
    ctx = import_obj_objects(lambda n: "PetShop" not in n)
    cm = bpy.data.materials.new("Ctx")
    cm.diffuse_color = (0.62, 0.63, 0.66, 1)
    for o in ctx:
        o.data.materials.clear()
        o.data.materials.append(cm)
    load_dragon((30.0, -11.5, FLOOR), 160)
    load_dragon((27.6, -8.4, FLOOR), 200)
    load_dragon((28.5, -21.6, FLOOR), 20)
    load_dragon((27.3, -5.6, 0.0), 200)
    load_dragon((25.1, -13.6, FLOOR), 250)
    load_dragon((35.0, -13.3, FLOOR), 110)
    load_dragon((35.0, -22.6, FLOOR), 80)
    cells = []
    shots = [
        ("room_shop_a", 20, 52, (30, -12.5, 1.2), 15, ["back", "mid", "cap_back", "cap_mid"]),
        ("room_shop_b", 200, 52, (30, -13.0, 1.2), 15, ["front", "cap_front", "ramp_front"]),
        ("room_back", 200, 55, (30, -21.5, 1.0), 15, ["front", "cap_front", "ramp_front", "mid", "cap_mid"]),
        ("ext_front", 205, 22, (30, -7.0, 2.4), 18, []),
        ("ext_sw", 300, 28, (29, -17, 2.0), 26, []),
        ("detail_in", 25, 28, (29.5, -8.6, 1.4), 7.5, ["back", "mid", "cap_back", "cap_mid", "east", "cap_east"]),
    ]
    for tag, az, el, tgt, orth, hide in shots:
        set_hidden(objs, hide)
        f = "ShopBuilding_%s.png" % tag
        cam_render(os.path.join(out, f), az, el, tgt, orth)
        cells.append(f)
    set_hidden(objs, [])
    contact_sheet(out, cells, os.path.join(out, "ShopBuilding_sheet.png"), cell=900, cols=3)
    cells = []
    shots = [
        ("d_west_shop", 90, 14, (24.3, -13.9, 2.1), 5.4, ["east", "cap_east"]),
        ("d_east_shop", 270, 14, (35.7, -13.0, 2.4), 5.4, ["west", "cap_west"]),
        ("d_mid_shop", 180, 16, (29.0, -18.0, 2.9), 8.0, ["front", "cap_front", "ramp_front"]),
        ("d_facade", 200, 12, (27.4, -7.0, 2.2), 7.5, []),
        ("d_corner", 225, 25, (23.3, -6.8, 0.1), 2.6, []),
        ("d_back_east", 270, 14, (35.7, -22.3, 2.0), 5.4, ["west", "cap_west"]),
    ]
    for tag, az, el, tgt, orth, hide in shots:
        set_hidden(objs, hide)
        f = "ShopBuilding_%s.png" % tag
        cam_render(os.path.join(out, f), az, el, tgt, orth)
        cells.append(f)
    set_hidden(objs, [])
    contact_sheet(out, cells, os.path.join(out, "ShopBuilding_detail_sheet.png"), cell=900, cols=3)


def overlay(ob, out):
    for o in list(bpy.data.objects):
        if o.name.startswith("Dragon") or o.type == "ARMATURE":
            o.hide_render = True
    for o in bpy.data.objects:
        if o.type == "MESH" and o.parent is not None:
            o.hide_render = True
    wire = make_wire_overlay()
    cells = []
    for tag, az, el, tgt, orth in (("ov_top", 0, 90, (30, -16, 0), 20.5), ("ov_front", 180, 0, (30, -7, 2.5), 14),
                                    ("ov_west", 270, 0, (23.5, -16, 2.5), 20), ("ov_top_door", 0, 90, (30, -7.3, 0), 5),
                                    ("ov_west_door", 290, 20, (23.2, -22.9, 1.2), 6),
                                    ("ov_mid", 0, 90, (31.5, -18.25, 0), 5)):
        f = "ShopBuilding_%s.png" % tag
        cam_render(os.path.join(out, f), az, el, tgt, orth)
        cells.append(f)
    contact_sheet(out, cells, os.path.join(out, "ShopBuilding_overlay_sheet.png"), cell=900, cols=3)


out, flags = cli()
begin()
build()
objs = materialize()
if out and "nopreview" not in flags:
    previews(objs, out)
measure(objs)
ob = join_all("ShopBuilding", [o for lst in objs.values() for o in lst])
report(ob)
coplanar_check.check(ob, "ShopBuilding", os.path.join(out, "ShopBuilding_coplanar.txt") if out else None, solid=solid_check)
export(ob, flags)
if out and "nopreview" not in flags:
    overlay(ob, out)
