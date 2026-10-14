import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

ACC = "SH_Sky"


def front_matrix(x, y, z, rz=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ M


def fin(name, bm, mat, angle=50.0):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def fillet(corners, segs=4):
    pts = []
    n = len(corners)
    for i in range(n):
        p0 = Vector(corners[i - 1][:2])
        p1 = Vector(corners[i][:2])
        p2 = Vector(corners[(i + 1) % n][:2])
        r = corners[i][2]
        if r <= 0:
            pts.append(p1)
            continue
        d1 = (p0 - p1).normalized()
        d2 = (p2 - p1).normalized()
        th = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        t = r / math.tan(th / 2)
        a = p1 + d1 * t
        b = p1 + d2 * t
        c = p1 + (d1 + d2).normalized() * (r / math.sin(th / 2))
        a0 = math.atan2(a.y - c.y, a.x - c.x)
        a1 = math.atan2(b.y - c.y, b.x - c.x)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(segs + 1):
            ang = a0 + da * k / segs
            pts.append(c + Vector((math.cos(ang), math.sin(ang))) * r)
    return pts


def slab(pts, thick, to3d, bev=0.02, bsegs=2, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.faces)
    A = [bm.verts.new(to3d(p.x, p.y, -thick / 2)) for p in pts]
    B = [bm.verts.new(to3d(p.x, p.y, thick / 2)) for p in pts]
    n = len(pts)
    caps = [bm.faces.new(list(reversed(A))), bm.faces.new(B)]
    for k in range(n):
        bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in before])
    edges = list({e for f in caps for e in f.edges})
    bmesh.ops.bevel(bm, geom=edges, offset=bev, offset_type="OFFSET", segments=bsegs, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    return bm


def tri_ngons(bm):
    big = [f for f in bm.faces if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


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


def star_outline(R, ri=0.46, tip=0.13, inner=0.05, segs=2):
    c = []
    for k in range(10):
        a = math.pi / 2 + math.pi * k / 5
        rr = R if k % 2 == 0 else R * ri
        c.append((rr * math.cos(a), rr * math.sin(a), R * (tip if k % 2 == 0 else inner)))
    return [(p.x, p.y) for p in fillet(c, segs)]


def cloud_top(w, bumps, n=28):
    pts = []
    for k in range(n + 1):
        x = w - 2 * w * k / n
        z = max(zc + math.sqrt(max(0.0, r * r - (x - c) ** 2)) for c, zc, r in bumps)
        pts.append(Vector((x, z)))
    return pts


LEAN = math.radians(13)
RX = 0.27
FY = -0.2
BY = 0.19
SEAT_Z = 0.42
ARM_Z = 0.63
RR = 1.25
RL = 0.4


def back_y(z):
    return BY + max(0.0, z - SEAT_Z) * math.tan(LEAN)


def rocker_z(y):
    return RR - math.sqrt(RR * RR - y * y)


def build_rockers():
    n = 12
    bm = bmesh.new()
    for sx in (-1, 1):
        bot = [Vector((-RL + 2 * RL * k / n, rocker_z(-RL + 2 * RL * k / n))) for k in range(n + 1)]
        top = [Vector((p.x, p.y + 0.075)) for p in reversed(bot)]
        slab(bot + top, 0.06, lambda u, v, w, sx=sx: (sx * RX + w, u, v), bev=0.022, bm=bm)
        for y in (-RL, RL):
            ellipsoid_bm((sx * RX, y + (0.01 if y > 0 else -0.01), rocker_z(y) + 0.06), (0.042, 0.05, 0.05), 10, 6, bm=bm)
    fin("Rockers", tri_ngons(bm), "SH_Walnut", angle=45)


def build_legs():
    bm = bmesh.new()
    for sx in (-1, 1):
        z0 = rocker_z(FY) + 0.06
        prof = [(0.0, z0), (0.04, z0), (0.044, z0 + 0.03), (0.032, z0 + 0.08), (0.03, SEAT_Z - 0.12),
                (0.04, SEAT_Z - 0.08), (0.032, SEAT_Z - 0.03), (0.034, ARM_Z - 0.06), (0.04, ARM_Z - 0.03),
                (0.0, ARM_Z - 0.01)]
        lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((sx * (RX + 0.01), FY, 0)))
        z0 = rocker_z(BY) + 0.06
        pts = catmull([(sx * RX, BY, z0), (sx * RX, BY, SEAT_Z - 0.1), (sx * (RX + 0.005), back_y(SEAT_Z + 0.15), SEAT_Z + 0.15),
                       (sx * (RX + 0.01), back_y(0.9), 0.9)], 3)
        tube_bm(pts, [0.042] + [0.035] * (len(pts) - 2) + [0.03], 10, bm=bm)
    fin("Legs", bm, "SH_Oak", angle=60)
    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((sx * (RX + 0.01), back_y(0.93), 0.935), (0.05, 0.05, 0.048), 10, 6, bm=bm)
    fin("Finials", bm, "SH_Gold", angle=None)


def build_seat():
    bm = rbox_bm((0, -0.005, SEAT_Z - 0.03), (2 * RX + 0.04, BY - FY + 0.13, 0.06), 0.026, 2)
    fin("Seat", bm, "SH_Oak", angle=50)
    bm = bmesh.new()
    rbox_bm((0, FY + 0.005, SEAT_Z - 0.09), (2 * RX - 0.04, 0.05, 0.07), 0.022, 2, bm=bm)
    for sx in (-1, 1):
        rbox_bm((sx * RX, (FY + BY) / 2, rocker_z(0.0) + 0.16), (0.045, BY - FY, 0.045), 0.018, 1, bm=bm)
    fin("Apron", bm, "SH_Walnut", angle=50)
    bm = soft_box((0, -0.015, SEAT_Z + 0.045), (2 * RX - 0.06, BY - FY + 0.06, 0.1), 0.08, 0.045, seg=3, Rb=0.012)
    for v in bm.verts:
        r = math.hypot(v.co.x / 0.25, (v.co.y + 0.015) / 0.22)
        if v.co.z > SEAT_Z + 0.07:
            v.co.z -= 0.022 * math.exp(-r * r * 6)
    fin("Cushion", bm, ACC, angle=70)


def build_back():
    l = LEAN

    def to3d(u, v, w):
        return (u, back_y(v) + w, v)

    bumps = ((-0.17, 0.81, 0.115), (0.0, 0.84, 0.14), (0.17, 0.81, 0.115))
    pts = [Vector((-RX, 0.72)), Vector((RX, 0.72))] + cloud_top(RX, bumps)
    clean = [pts[0]]
    for p in pts[1:]:
        if (p - clean[-1]).length > 1e-4:
            clean.append(p)
    if (clean[-1] - clean[0]).length < 1e-4:
        clean.pop()
    bm = slab(clean, 0.05, to3d, bev=0.018)
    fin("Crest", tri_ngons(bm), ACC, angle=45)
    zc = 0.83
    m = Matrix.Translation((0, back_y(zc) - 0.02, zc)) @ Matrix.Rotation(-l, 4, "X") @ \
        Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    bm = badge_bm(star_outline(0.085), 0.03, 0.009, matrix=m)
    fin("CrestStar", bm, "SH_Gold", angle=60)
    bm = bmesh.new()
    for x in (-0.15, 0.0, 0.15):
        z0, z1 = SEAT_Z - 0.01, 0.74
        prof = [(z0, 0.022), (z0 + 0.06, 0.026), ((z0 + z1) / 2, 0.02), (z1 - 0.04, 0.025), (z1, 0.022)]
        tube_bm([(x, back_y(z), z) for z, r in prof], [r for z, r in prof], 7, bm=bm)
    rbox_bm((0, back_y(0.72), 0.7), (2 * RX, 0.05, 0.05), 0.02, 1, bm=bm,
            matrix=Matrix.Rotation(-l, 4, "X"))
    fin("Spindles", bm, "SH_Oak", angle=60)


def build_arms():
    bm = bmesh.new()
    y0, y1 = FY - 0.075, back_y(ARM_Z) + 0.02
    for sx in (-1, 1):
        x = sx * (RX + 0.035)
        rbox_bm((x, (y0 + y1) / 2, ARM_Z), (0.095, y1 - y0, 0.045), 0.02, 2, bm=bm)
        ellipsoid_bm((x, y0 + 0.01, ARM_Z + 0.008), (0.06, 0.055, 0.042), 10, 6, bm=bm)
    fin("Arms", bm, "SH_Walnut", angle=50)


def build_pillow():
    zc = 0.6
    bm = ellipsoid_bm((0, 0, 0), (1.0, 1.0, 1.0), 16, 10)
    for v in bm.verts:
        a, b, c = v.co.x, v.co.y, v.co.z
        x = math.copysign(abs(a) ** 0.6, a) * 0.165
        z = math.copysign(abs(c) ** 0.6, c) * 0.125
        edge = min(1.0, (abs(a) ** 2 + abs(c) ** 2))
        y = b * 0.07 * (1.0 - 0.6 * edge ** 2)
        v.co = Vector((x, y, z))
    xf(bm, Matrix.Translation((0.02, back_y(zc) - 0.07, zc)) @ Matrix.Rotation(math.radians(-7), 4, "Y")
       @ Matrix.Rotation(-LEAN, 4, "X"))
    fin("Pillow", bm, "SH_Cream", angle=None)


out, flags = cli()
begin()
build_rockers()
build_legs()
build_seat()
build_back()
build_arms()
build_pillow()
ob = join_all("ShopRockingChair")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.95, 0.35, 0), dragon_rot=30.0, target=(-0.25, 0.0, 0.5), ortho=2.4)
