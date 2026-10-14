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


def side_matrix(cx, sgn):
    return Matrix(((0, 0, sgn, cx), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


W = 1.2
PX = 0.55
PT = 0.09
CB_Y = 0.215
CB_Z = 0.70
TRAY_LO = (-0.08, 0.22, 0.26)
TRAY_HI = (0.09, 0.5, 0.24)
BIG = (0.115, 0.08, 0.47)
SMALL = (0.085, 0.06, 0.3)


def build_frame():
    outline = fillet_poly([(-0.26, 0.03), (0.25, 0.03), (0.25, 0.74), (-0.03, 0.74)], [0.03, 0.03, 0.07, 0.12], 4)
    bm = bmesh.new()
    for sx in (-1, 1):
        for sgn in (-1, 1):
            badge_bm(outline, PT / 2, 0.028, 2, bm=bm, matrix=side_matrix(sx * PX, sgn))
    fin("Panels", bm, "SH_Walnut", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        soft_box((sx * PX, -0.005, 0.04), (0.15, 0.57, 0.08), 0.06, 0.03, seg=2, Rb=0.01, bm=bm)
    rbox_bm((0.0, CB_Y, CB_Z), (2 * PX, 0.07, 0.085), 0.03, 2, bm=bm)
    rbox_bm((0.0, 0.2, 0.13), (2 * PX, 0.06, 0.07), 0.025, 2, bm=bm)
    fin("FeetBars", bm, "SH_Walnut", angle=50)
    bm = bmesh.new()
    ellipsoid_bm((PX, 0.11, 0.765), (0.052, 0.052, 0.046), 12, 6, bm=bm)
    fin("Knobs", bm, "SH_Gold", angle=None)


def build_trays():
    bm = bmesh.new()
    lips = bmesh.new()
    for yc, zt, d in (TRAY_LO, TRAY_HI):
        rbox_bm((0.0, yc, zt - 0.02), (2 * PX - 0.02, d + 0.02, 0.04), 0.015, 1, bm=bm)
        for sy in (-1, 1):
            tube_bm([(-PX + 0.02, yc + sy * d / 2, zt + 0.014), (PX - 0.02, yc + sy * d / 2, zt + 0.014)],
                    0.03, 8, bm=lips)
    fin("Trays", bm, "SH_Oak", angle=50)
    fin("TrayLips", lips, "SH_Oak", angle=60)


def head_prof(R, hw, n=8):
    out = []
    for i in range(n + 1):
        a = -math.pi / 2 + math.pi * i / n
        c = max(0.0, math.cos(a))
        out.append((R * c ** 0.4, hw * math.sin(a)))
    return out


def dumbbell(bm_head, bm_handle, bm_gold, x, y, z, spec):
    R, hw, L = spec
    rot = Matrix.Rotation(math.radians(90), 4, "Y")
    for s in (-1, 1):
        hx = x + s * (L / 2 - hw)
        lathe_bm(head_prof(R, hw), 14, bm=bm_head, matrix=Matrix.Translation((hx, y, z)) @ rot)
        cx = x + s * (L / 2 - 2 * hw - 0.01)
        cp = [(0.0, -0.014), (R * 0.42, -0.014), (R * 0.5, -0.004), (R * 0.5, 0.004), (R * 0.42, 0.014), (0.0, 0.014)]
        lathe_bm(cp, 12, bm=bm_gold, matrix=Matrix.Translation((cx, y, z)) @ rot)
    tube_bm([(x - L / 2 + hw, y, z), (x + L / 2 - hw, y, z)], R * 0.3, 8, bm=bm_handle)


def build_dumbbells():
    heads, handles, gold = bmesh.new(), bmesh.new(), bmesh.new()
    yc, zt, _ = TRAY_LO
    for x in (-0.255, 0.255):
        dumbbell(heads, handles, gold, x, yc, zt + BIG[0] - 0.006, BIG)
    yc, zt, _ = TRAY_HI
    for x in (-0.325, 0.0, 0.325):
        dumbbell(heads, handles, gold, x, yc, zt + SMALL[0] - 0.006, SMALL)
    fin("Heads", heads, "SH_Teal", angle=40)
    fin("Handles", handles, "SH_Oak", angle=70)
    fin("Collars", gold, "SH_Gold", angle=50)


def sweep_strip(path, w, t, rc, m=2):
    bm = bmesh.new()
    P = [Vector(p) for p in path]
    n = len(P)
    Y = Vector((0, 1, 0))
    rings = []
    for i in range(n):
        T = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        N = T.cross(Y).normalized()
        rings.append([bm.verts.new(P[i] + Y * a + N * b) for a, b in rrect(w, t, rc, m)])
    k = len(rings[0])
    for A, B in zip(rings, rings[1:]):
        for j in range(k):
            bm.faces.new((A[j], A[(j + 1) % k], B[(j + 1) % k], B[j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return bm


def build_towel():
    x0, yc, top = -PX, 0.13, 0.745
    ctrl = [(x0 - 0.068, top - 0.25), (x0 - 0.063, top - 0.12), (x0 - 0.05, top - 0.012), (x0, top + 0.014),
            (x0 + 0.05, top - 0.012), (x0 + 0.06, top - 0.05), (x0 + 0.062, top - 0.08)]
    pts = [(p.x, yc, p.y) for p in catmull([Vector(c) for c in ctrl], 3)]
    bm = sweep_strip(pts, 0.17, 0.035, 0.015)
    fin("Towel", bm, "SH_Parchment", angle=60)
    bm = bmesh.new()
    for z in (top - 0.2, top - 0.17):
        rbox_bm((x0 - 0.08, yc, z), (0.014, 0.174, 0.02), 0.005, 1, bm=bm)
    fin("TowelStripes", bm, "SH_Teal", angle=60)


def build_medallion():
    z = 0.735
    prof = [(0.0, 0.0), (0.072, 0.0), (0.086, 0.012), (0.086, 0.03), (0.072, 0.045), (0.0, 0.045)]
    m = front_matrix(0.0, CB_Y - 0.035 + 0.01, z)
    fin("Medallion", lathe_bm(prof, 24, matrix=m), "SH_Teal", angle=50)
    st = badge_bm(star_outline(0.06, 0.028), 0.03, 0.012, 2, matrix=front_matrix(0.0, CB_Y - 0.035 - 0.03, z + 0.004))
    fin("Star", st, "SH_Gold", angle=60)


out, flags = cli()
begin()
build_frame()
build_trays()
build_dumbbells()
build_medallion()
build_towel()
ob = join_all("ShopDumbbellRack")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.3, 0.35, 0), target=(-0.5, 0.0, 0.42), ortho=2.9)
