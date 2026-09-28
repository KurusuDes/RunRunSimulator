import math
import bmesh
from mathutils import Vector
import part_common as pc

SLOTS = ("Back",)

Y0, Y1 = -0.40, 0.98
N = 6
R0, R1 = 0.20, 0.085
THICK = 0.36
SINK = 0.20
CORNER = 0.62
CORNER_SEGS = 4
ROT = (22, 44, 28, 42, 20, 36)
PROFILE = ((-0.5, 0.80), (-0.38, 0.95), (-0.18, 1.0), (0.18, 1.0), (0.38, 0.95), (0.5, 0.80))
TWIST = (-6, 4, -3, 5, -4, 2)


def outline(R, corners_deg, jitter):
    pts = []
    n = len(corners_deg)
    cs = []
    for i, a in enumerate(corners_deg):
        ang = math.radians(a + 90)
        rr = R * (1 + jitter[i % len(jitter)])
        cs.append(Vector((math.cos(ang) * rr, math.sin(ang) * rr)))
    for i in range(n):
        p, a, b = cs[i], cs[i - 1], cs[(i + 1) % n]
        pa = p.lerp(a, CORNER * 0.5)
        pb = p.lerp(b, CORNER * 0.5)
        for k in range(CORNER_SEGS + 1):
            t = k / CORNER_SEGS
            q = pa * (1 - t) ** 2 + p * 2 * (1 - t) * t + pb * t * t
            pts.append(q)
    return pts


def gem(name, center, fwd, up, R, i):
    side = fwd.cross(up).normalized()
    rot = ROT[i % len(ROT)]
    shape = tuple(rot - 45 + 90 * j for j in range(4))
    jitter = (0.03, -0.02, 0.02, -0.03)
    ol = outline(R, shape, jitter[i % 4:] + jitter[:i % 4])
    tw = math.radians(TWIST[i % len(TWIST)])
    f2 = fwd * math.cos(tw) + up * math.sin(tw)
    u2 = up * math.cos(tw) - fwd * math.sin(tw)
    bm = bmesh.new()
    rings = []
    for off, sc in PROFILE:
        ring = [bm.verts.new(center + side * (off * R * THICK * 2) + f2 * (q.x * sc) + u2 * (q.y * sc)) for q in ol]
        rings.append(ring)
    m = len(ol)
    for a, b in zip(rings, rings[1:]):
        for k in range(m):
            bm.faces.new((a[k], a[(k + 1) % m], b[(k + 1) % m], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = pc.new_object(name, bm)
    pc.shade_smooth(obj, 35)
    return obj


def bottom_depth(R, i):
    rot = ROT[i % len(ROT)]
    tw = TWIST[i % len(TWIST)]
    return max(-math.sin(math.radians(rot - 45 + 90 * j + 90 + tw)) for j in range(4)) * R


def spine(samples=120):
    pts = []
    for i in range(samples + 1):
        y = Y0 + (Y1 - Y0) * i / samples
        p, n = pc.surface_point((0, y, 3.0), (0, 0, -1))
        pts.append((p, n))
    arc = [0.0]
    for a, b in zip(pts, pts[1:]):
        arc.append(arc[-1] + (b[0] - a[0]).length)
    return pts, arc


def at(pts, arc, s):
    for i in range(1, len(arc)):
        if arc[i] >= s:
            f = (s - arc[i - 1]) / max(1e-6, arc[i] - arc[i - 1])
            p = pts[i - 1][0].lerp(pts[i][0], f)
            n = pts[i - 1][1].lerp(pts[i][1], f)
            t = (pts[i][0] - pts[i - 1][0]).normalized()
            return p, n, t
    return pts[-1][0], pts[-1][1], (pts[-1][0] - pts[-2][0]).normalized()


def build(arm):
    pts, arc = spine()
    radii = [R0 + (R1 - R0) * (i / (N - 1)) ** 0.85 for i in range(N)]
    s0 = radii[0] * 0.75
    s1 = arc[-1] - radii[-1] * 0.9
    steps = [radii[i] + radii[i + 1] for i in range(N - 1)]
    k = (s1 - s0) / sum(steps)
    pos = [s0]
    for st in steps:
        pos.append(pos[-1] + st * k)
    plates = []
    for i, R in enumerate(radii):
        p, nrm, tan = at(pts, arc, pos[i])
        nrm = Vector((0, nrm.y, nrm.z)).normalized()
        up = (nrm * 0.75 + Vector((0, 0, 1)) * 0.25).normalized()
        fwd = Vector((0, -tan.y, -tan.z))
        fwd = (fwd - up * fwd.dot(up)).normalized()
        c = p + up * (bottom_depth(R, i) * 0.85 - R * SINK)
        plates.append(gem("plate%d" % i, c, fwd, up, R, i))
    obj = pc.join(plates, "Back_Placas")
    pc.skin_like(obj, arm, "Back")
    return [obj]
