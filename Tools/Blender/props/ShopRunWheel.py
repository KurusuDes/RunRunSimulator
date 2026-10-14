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



def lathe_closed(prof, segs, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = [[bm.verts.new((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs), z))
              for k in range(segs)] for r, z in prof]
    n = len(rings)
    for i in range(n):
        A, B = rings[i], rings[(i + 1) % n]
        for k in range(segs):
            k1 = (k + 1) % segs
            bm.faces.new((A[k], A[k1], B[k1], B[k]))
    if matrix is not None:
        xf(bm, matrix, [v for r in rings for v in r])
    return bm


ZC = 0.83
RI = 0.58
RO = 0.70
RIM_Y = 0.33
RIM_T = 0.04
SLATS = 22
RS = 0.63
LEG_Y = 0.43
AXIS_Y = Matrix.Rotation(math.radians(-90), 4, "X")


def wheel_m(y):
    return Matrix.Translation((0.0, y, ZC)) @ AXIS_Y


def build_rims():
    sec = fillet_poly([(RI, -RIM_T), (RO, -RIM_T), (RO, RIM_T), (RI, RIM_T)], 0.03, 2)
    bm = bmesh.new()
    for sy in (-1, 1):
        lathe_closed(sec, 40, bm=bm, matrix=wheel_m(sy * RIM_Y))
    fin("Rims", bm, "SH_Teal", angle=40)
    bm = bmesh.new()
    rp = [(0.0, 0.0), (0.024, 0.0), (0.024, 0.007), (0.016, 0.018), (0.0, 0.021)]
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        r = (RI + RO) / 2
        m = Matrix.Translation((r * math.sin(a), -RIM_Y - RIM_T + 0.006, ZC + r * math.cos(a))) @ \
            Matrix.Rotation(math.radians(90), 4, "X")
        lathe_bm(rp, 8, bm=bm, matrix=m)
    fin("Rivets", bm, "SH_Gold", angle=60)


def build_slats():
    for parity, mat in ((0, "SH_Oak"), (1, "SH_Honey")):
        bm = bmesh.new()
        for i in range(SLATS):
            if i % 2 != parity:
                continue
            a = 2 * math.pi * i / SLATS
            m = Matrix.Translation((0.0, 0.0, ZC)) @ Matrix.Rotation(a, 4, "Y") @ Matrix.Translation((0.0, 0.0, -RS))
            rbox_bm((0.0, 0.0, 0.0), (0.125, 2 * RIM_Y - 0.01, 0.05), 0.018, 1, bm=bm, matrix=m)
        fin("Slats%d" % parity, bm, mat, angle=50)


def build_spokes_stand():
    bm = bmesh.new()
    yb = RIM_Y + 0.03
    for k in range(6):
        a = 2 * math.pi * k / 6
        d = Vector((math.sin(a), 0.0, math.cos(a)))
        p0 = Vector((0.0, yb, ZC)) + d * 0.08
        p1 = Vector((0.0, yb, ZC)) + d * (RI + 0.03)
        tube_bm([p0, p1], 0.032, 8, bm=bm)
    for sx in (-1, 1):
        tube_bm([(sx * 0.56, LEG_Y, 0.07), (sx * 0.3, LEG_Y, 0.46), (sx * 0.05, LEG_Y, ZC - 0.03)], [0.05, 0.046, 0.042], 8,
                bm=bm)
    tube_bm([(-0.36, LEG_Y, 0.36), (0.36, LEG_Y, 0.36)], 0.038, 8, bm=bm)
    tube_bm([(0.0, yb - 0.02, ZC), (0.0, LEG_Y + 0.05, ZC)], 0.045, 10, bm=bm)
    fin("Spokes", bm, "SH_Walnut", angle=60)
    bm = bmesh.new()
    soft_box((0.0, 0.02, 0.06 / 2 + 0.0), (1.4, 0.88, 0.06), 0.14, 0.025, seg=2, Rb=0.01, bm=bm)
    fin("Base", bm, "SH_Walnut", angle=50)
    bm = bmesh.new()
    soft_box((0.0, 0.02, 0.075), (1.3, 0.78, 0.05), 0.11, 0.022, seg=2, bm=bm)
    fin("BaseTop", bm, "SH_Honey", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        rbox_bm((sx * 0.56, LEG_Y, 0.1), (0.14, 0.12, 0.05), 0.02, 1, bm=bm)
    fin("LegShoes", bm, "SH_Walnut", angle=50)


def build_hub():
    prof = [(0.0, -0.03), (0.1, -0.03), (0.125, -0.015), (0.125, 0.015), (0.1, 0.03), (0.0, 0.03)]
    m = Matrix.Translation((0.0, RIM_Y + 0.03, ZC)) @ AXIS_Y
    fin("Hub", lathe_bm(prof, 24, matrix=m), "SH_Gold", angle=50)
    cap = ellipsoid_bm((0.0, LEG_Y + 0.05, ZC), (0.06, 0.04, 0.06), 12, 6)
    fin("AxleCap", cap, "SH_Gold", angle=None)
    st = badge_bm(star_outline(0.085, 0.04), 0.03, 0.012, 2, matrix=front_matrix(0.0, RIM_Y + 0.004, ZC + 0.004))
    fin("Star", st, "SH_Teal", angle=60)


out, flags = cli()
begin()
build_rims()
build_slats()
build_spokes_stand()
build_hub()
ob = join_all("ShopRunWheel")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.25, -0.35, 0), target=(-0.4, 0.0, 0.7), ortho=3.2)
