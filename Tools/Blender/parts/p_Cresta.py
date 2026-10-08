import math
import bmesh
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
import part_common as pc

SLOTS = ("Back",)

X = Vector((1, 0, 0))
FLAMES = ((-0.26, 0.40), (0.14, 0.37), (0.52, 0.31))
FLAME = ((-0.30, -0.24), (-0.44, -0.02), (-0.48, 0.22), (-0.44, 0.42), (-0.40, 0.56), (-0.46, 0.70),
         (-0.50, 0.86), (-0.45, 1.00), (-0.34, 1.07), (-0.31, 0.96), (-0.28, 0.84), (-0.21, 0.72),
         (-0.11, 0.62), (-0.09, 0.78), (-0.03, 0.94), (0.07, 1.10), (0.21, 1.24), (0.39, 1.34),
         (0.58, 1.37), (0.66, 1.29), (0.56, 1.23), (0.45, 1.15), (0.40, 1.03), (0.42, 0.89),
         (0.48, 0.72), (0.52, 0.50), (0.50, 0.26), (0.44, 0.04), (0.32, -0.24))
CORE = ((-0.20, -0.10), (-0.26, 0.10), (-0.25, 0.30), (-0.18, 0.48), (-0.10, 0.62), (0.0, 0.76),
        (0.10, 0.86), (0.08, 0.70), (0.12, 0.54), (0.20, 0.36), (0.24, 0.16), (0.20, -0.04), (0.10, -0.14), (-0.06, -0.16))
WIDE = 1.0
THICK = 0.32
CORE_THICK = 0.50
GRID = 0.085
RIM = 0.004
POW = 0.32


def closed_catmull(pts, n=3):
    k = [Vector(p) for p in pts]
    m = len(k)
    out = []
    for i in range(m):
        p0, p1, p2, p3 = k[(i - 1) % m], k[i], k[(i + 1) % m], k[(i + 2) % m]
        for s in range(n):
            t = s / n
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    return out


def inside(p, poly):
    c = False
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if (a.y > p.y) != (b.y > p.y) and p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x:
            c = not c
    return c


def edge_dist(p, poly):
    best = 1e9
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
        best = min(best, (a + ab * t - p).length)
    return best


def inflate(name, outline, to3, side, thick):
    poly = [Vector((p.x, p.y)) for p in outline]
    lo = Vector((min(p.x for p in poly), min(p.y for p in poly)))
    hi = Vector((max(p.x for p in poly), max(p.y for p in poly)))
    pts = list(poly)
    y = lo.y + GRID * 0.5
    row = 0
    while y < hi.y:
        x = lo.x + GRID * (0.5 + 0.5 * (row % 2))
        while x < hi.x:
            q = Vector((x, y))
            if inside(q, poly) and edge_dist(q, poly) > GRID * 0.45:
                pts.append(q)
            x += GRID
        y += GRID * 0.87
        row += 1
    n = len(poly)
    cdt = delaunay_2d_cdt(pts, [], [list(range(n))], 1, 1e-6)
    verts2, faces, orig = cdt[0], cdt[2], cdt[3]
    where = {}
    for k, src in enumerate(orig):
        for j in src:
            where[j] = k
    d = [edge_dist(Vector(v), poly) for v in verts2]
    dmax = max(d)
    bm = bmesh.new()
    top, bot = [], []
    for v, dist in zip(verts2, d):
        h = max(RIM, thick * min(1.0, dist / dmax) ** POW)
        base = to3(Vector(v))
        top.append(bm.verts.new(base + side * h))
        bot.append(bm.verts.new(base - side * h))
    for f in faces:
        bm.faces.new([top[i] for i in f])
        bm.faces.new([bot[i] for i in reversed(f)])
    for i in range(n):
        a, b = where[i], where[(i + 1) % n]
        bm.faces.new((top[b], top[a], bot[a], bot[b]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def frame(y):
    p, _ = pc.surface_point((0, y, 3.0), (0, 0, -1))
    q, _ = pc.surface_point((0, y + 0.02, 3.0), (0, 0, -1))
    t = (q - p).normalized()
    n = X.cross(t).normalized()
    if n.z < 0:
        n = -n
    up = (n * 0.5 + Vector((0, 0, 1)) * 0.5).normalized()
    back = up.cross(X).normalized()
    if back.y < 0:
        back = -back
    return p, up, back


def build(arm):
    outline = closed_catmull(FLAME)
    core = closed_catmull(CORE)
    outer, inner = [], []
    for i, (y, H) in enumerate(FLAMES):
        p, up, back = frame(y)

        def to3(q, p=p, up=up, back=back, H=H):
            return p + back * (q.x * H * WIDE) + up * (q.y * H)
        outer.append(inflate("f%d" % i, outline, to3, X, THICK * H * 0.5))
        inner.append(inflate("c%d" % i, core, to3, X, CORE_THICK * H * 0.5))
    objs = [pc.join(outer, "Back_Cresta"), pc.join(inner, "Back_Cresta_core")]
    for o in objs:
        o.modifiers.clear()
        pc.shade_smooth(o, angle=85)
        pc.skin_like(o, arm, "Back")
    return objs
