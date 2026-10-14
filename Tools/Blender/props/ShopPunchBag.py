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



BY = -0.065
POST_Y = 0.27
POST_TOP = 1.7
ARM_Z = 1.64
BAG_R = 0.21
BAG_Z0 = 0.38
BAG_Z1 = 1.18


def build_base():
    prof = [(0.0, 0.0), (0.37, 0.0), (0.395, 0.022), (0.385, 0.06), (0.36, 0.075), (0.0, 0.075)]
    fin("Base", lathe_bm(prof, 32), "SH_Walnut", angle=50)
    prof = [(0.3, 0.06), (0.3, 0.085), (0.28, 0.105), (0.0, 0.105)]
    fin("BaseTop", lathe_bm(prof, 32), "SH_Honey", angle=50)


def build_post():
    prof = [(0.0, 0.1), (0.1, 0.1), (0.1, 0.13), (0.075, 0.17), (0.08, 0.21), (0.075, POST_TOP - 0.1), (0.0, POST_TOP - 0.1)]
    fin("Post", lathe_bm(prof, 14, matrix=Matrix.Translation((0.0, POST_Y, 0.0))), "SH_Honey", angle=50)
    prof = [(0.0, 0.085), (0.125, 0.085), (0.135, 0.11), (0.115, 0.15), (0.0, 0.15)]
    fin("PostFoot", lathe_bm(prof, 14, matrix=Matrix.Translation((0.0, POST_Y, 0.0))), "SH_Walnut", angle=50)
    bm = bmesh.new()
    rbox_bm((0.0, POST_Y - 0.2, ARM_Z), (0.11, 0.66, 0.12), 0.045, 2, bm=bm)
    rbox_bm((0.0, POST_Y, POST_TOP - 0.06), (0.17, 0.17, 0.11), 0.045, 2, bm=bm)
    fin("Arm", bm, "SH_Walnut", angle=50)
    bm = bmesh.new()
    tube_bm([(0.0, POST_Y - 0.02, 1.3), (0.0, POST_Y - 0.18, ARM_Z - 0.03)], 0.036, 8, bm=bm)
    fin("Brace", bm, "SH_Honey", angle=60)
    bm = ellipsoid_bm((0.0, POST_Y, POST_TOP + 0.03), (0.065, 0.065, 0.06), 12, 6)
    ellipsoid_bm((0.0, POST_Y - 0.53, ARM_Z), (0.045, 0.07, 0.07), 10, 6, bm=bm)
    fin("Finials", bm, "SH_Gold", angle=None)


def build_bag():
    prof = [(0.0, BAG_Z0), (0.09, BAG_Z0 + 0.008), (0.15, BAG_Z0 + 0.035), (BAG_R, BAG_Z0 + 0.1), (BAG_R + 0.006, 0.8),
            (BAG_R, BAG_Z1 - 0.08), (0.16, BAG_Z1 - 0.02), (0.1, BAG_Z1), (0.0, BAG_Z1 + 0.004)]
    fin("Bag", lathe_bm(prof, 20, matrix=Matrix.Translation((0.0, BY, 0.0))), "SH_Teal", angle=50)
    bm = bmesh.new()
    for zc in (BAG_Z0 + 0.14, BAG_Z1 - 0.1):
        r = BAG_R + 0.004
        prof = [(r - 0.01, zc - 0.035), (r + 0.012, zc - 0.028), (r + 0.016, zc), (r + 0.012, zc + 0.028), (r - 0.01, zc + 0.035)]
        lathe_bm(prof, 20, bm=bm, matrix=Matrix.Translation((0.0, BY, 0.0)))
    fin("Bands", bm, "SH_Walnut", angle=50)
    bm = bmesh.new()
    prof = [(0.0, BAG_Z1 - 0.01), (0.075, BAG_Z1 - 0.01), (0.075, BAG_Z1 + 0.025), (0.055, BAG_Z1 + 0.04), (0.0, BAG_Z1 + 0.04)]
    lathe_bm(prof, 14, bm=bm, matrix=Matrix.Translation((0.0, BY, 0.0)))
    torus_bm(0.045, 0.014, 14, 6, bm=bm, matrix=Matrix.Translation((0.0, BY, ARM_Z - 0.1)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
    st = badge_bm(star_outline(0.095, 0.045), 0.035, 0.012, 2, matrix=front_matrix(0.0, BY - BAG_R + 0.024, 0.8))
    fin("Star", st, "SH_Gold", angle=60)
    fin("Hardware", bm, "SH_Gold", angle=50)


def build_ropes():
    bm = bmesh.new()
    top = Vector((0.0, BY, ARM_Z - 0.14))
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 2
        p1 = Vector((0.055 * math.cos(a), BY + 0.055 * math.sin(a), BAG_Z1 + 0.03))
        tube_bm([top, top.lerp(p1, 0.5), p1], 0.017, 6, bm=bm)
    tube_bm([(0.0, BY, ARM_Z - 0.04), (0.0, BY, ARM_Z - 0.07)], 0.02, 6, bm=bm)
    fin("Ropes", bm, "SH_Parchment", angle=70)


out, flags = cli()
begin()
build_base()
build_post()
build_bag()
build_ropes()
ob = join_all("ShopPunchBag")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.85, -0.25, 0), dragon_rot=-20.0, target=(-0.3, 0.0, 0.9), ortho=2.6)
