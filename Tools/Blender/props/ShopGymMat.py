import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


def front_matrix(x, y, z, rz=0.0, tilt=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ \
        Matrix.Rotation(math.radians(tilt), 4, "X") @ M


def fin(name, bm, mat, angle=50.0):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def offset2d(pts, d):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        t = (p2 - p0).normalized()
        nin = Vector((-t.y, t.x)) * s
        out.append((p1.x + nin.x * d, p1.y + nin.y * d))
    return out


def badge_bm(outline, t, bev, steps=2, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = [(0.0, 0.0), (0.0, t - bev)]
    for j in range(1, steps + 1):
        a = math.pi / 2 * j / steps
        rings.append((bev * (1 - math.cos(a)), t - bev + bev * math.sin(a)))
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    vr = []
    for d, z in rings:
        vr.append([bm.verts.new((x, y, z)) for x, y in offset2d(outline, d)])
    n = len(outline)
    for A, B in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    c0 = bm.verts.new((cx, cy, 0.0))
    c1 = bm.verts.new((cx, cy, t))
    for k in range(n):
        bm.faces.new((vr[0][(k + 1) % n], vr[0][k], c0))
        bm.faces.new((vr[-1][k], vr[-1][(k + 1) % n], c1))
    if matrix is not None:
        xf(bm, matrix, [v for r in vr for v in r] + [c0, c1])
    return bm


def fillet_poly(pts, r, m=4):
    out = []
    n = len(pts)
    for i in range(n):
        P, A, B = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[(i + 1) % n])
        d1, d2 = (A - P).normalized(), (B - P).normalized()
        th = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        rr = r[i] if isinstance(r, (list, tuple)) else r
        t = min(rr / math.tan(th / 2), (A - P).length * 0.49, (B - P).length * 0.49)
        rr = t * math.tan(th / 2)
        s, e = P + d1 * t, P + d2 * t
        c = P + (d1 + d2).normalized() * (rr / math.sin(th / 2))
        a0 = math.atan2(s.y - c.y, s.x - c.x)
        a1 = math.atan2(e.y - c.y, e.x - c.x)
        da = a1 - a0
        while da > math.pi:
            da -= 2 * math.pi
        while da < -math.pi:
            da += 2 * math.pi
        for j in range(m + 1):
            a = a0 + da * j / m
            out.append((c.x + rr * math.cos(a), c.y + rr * math.sin(a)))
    return out


def star_outline(ro, rin, n=5):
    pts = []
    for k in range(2 * n):
        a = math.pi / 2 + math.pi * k / n
        r = ro if k % 2 == 0 else rin
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts



def loop_tube_bm(path, radius, sides=6, bm=None):
    bm = bm or bmesh.new()
    P = [Vector(p) for p in path]
    n = len(P)
    rings = []
    for i in range(n):
        t = (P[(i + 1) % n] - P[i - 1]).normalized()
        side = (UP - t * UP.dot(t))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = t.cross(side).normalized()
        rings.append([bm.verts.new(P[i] + side * math.cos(2 * math.pi * k / sides) * radius +
                                   up * math.sin(2 * math.pi * k / sides) * radius) for k in range(sides)])
    for i in range(n):
        A, B = rings[i], rings[(i + 1) % n]
        for k in range(sides):
            bm.faces.new((A[k], A[(k + 1) % sides], B[(k + 1) % sides], B[k]))
    return bm


MW = 1.9
MD = 1.2
PW = 0.6
PD = 1.12
PRC = 0.1
PX = (-0.635, 0.0, 0.635)
TOP = 0.12


def build_base():
    bm = soft_box((0.0, 0.0, 0.025), (MW, MD, 0.05), 0.12, 0.02, seg=2, Rb=0.008)
    fin("Base", bm, "SH_Parchment", angle=50)


def build_panels():
    bm = bmesh.new()
    pipe = bmesh.new()
    for cx in PX:
        rings = [(PW - 0.03, PD - 0.03, PRC - 0.015, 0.035, cx, 0.0),
                 (PW, PD, PRC, 0.058, cx, 0.0),
                 (PW, PD, PRC, 0.074, cx, 0.0),
                 (PW - 0.03, PD - 0.03, PRC - 0.015, 0.098, cx, 0.0),
                 (PW - 0.1, PD - 0.1, PRC - 0.05, 0.113, cx, 0.0),
                 (PW - 0.24, PD - 0.26, PRC - 0.08, TOP, cx, 0.0)]
        loft(rings, 3, bm=bm)
        path = [(x, y, 0.066) for x, y in rrect(PW + 0.006, PD + 0.006, PRC + 0.003, 4, cx, 0.0)]
        loop_tube_bm(path, 0.017, 6, bm=pipe)
    fin("Panels", bm, "SH_Teal", angle=40)
    fin("Piping", pipe, "SH_Parchment", angle=70)


def build_tufts():
    bm = bmesh.new()
    for cx in (PX[0], PX[2]):
        for sy in (-1, 1):
            ellipsoid_bm((cx, sy * 0.24, TOP - 0.004), (0.035, 0.035, 0.018), 10, 4, bm=bm)
    fin("Tufts", bm, "SH_Gold", angle=None)


def build_star():
    st = badge_bm(star_outline(0.2, 0.095), 0.025, 0.012, 2, matrix=Matrix.Translation((0.0, 0.0, TOP - 0.012)))
    fin("Star", st, "SH_Gold", angle=60)


def build_handles():
    bm = bmesh.new()
    for sx in (-1, 1):
        x0 = sx * (MW / 2 - 0.02)
        pts = []
        for j in range(9):
            a = math.pi * j / 8
            pts.append((x0 + sx * 0.085 * math.sin(a), 0.14 * math.cos(a), 0.06))
        tube_bm(pts, 0.026, 8, bm=bm)
        for sy in (-1, 1):
            rbox_bm((x0 - sx * 0.005, sy * 0.14, 0.06), (0.07, 0.07, 0.06), 0.02, 1, bm=bm)
    fin("Handles", bm, "SH_Walnut", angle=60)


out, flags = cli()
begin()
build_base()
build_panels()
build_tufts()
build_star()
build_handles()
ob = join_all("ShopGymMat")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.45, 0.55, 0), dragon_rot=-20.0, target=(-0.35, 0.0, 0.35), ortho=3.3)
