import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

L = 1.6
SX = 0.66
SEAT_Z = 0.44
SLAT_T = 0.07
BACK_TILT = math.radians(14)


def face_m(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


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


def heart_outline(size, n=22):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * size / 32.0, (y + 2.0) * size / 32.0))
    return pts


def back_point(d, h):
    y0, z0 = 0.2, SEAT_Z + 0.02
    return (y0 + d * math.cos(BACK_TILT) + h * math.sin(BACK_TILT), z0 - d * math.sin(BACK_TILT) + h * math.cos(BACK_TILT))


def build_frames():
    bm = bmesh.new()
    feet = bmesh.new()
    for sx in (-1, 1):
        x = sx * SX
        front = [(x, -0.2, 0.03), (x, -0.21, 0.3), (x, -0.23, SEAT_Z), (x, -0.27, 0.56), (x, -0.22, 0.65),
                 (x, -0.1, 0.66), (x, 0.08, 0.65), (x, 0.2, 0.62)]
        tube_bm(catmull(front, 3), 0.052, 8, bm=bm)
        by, bz = back_point(0.0, 0.48)
        back = [(x, 0.22, 0.03), (x, 0.21, 0.25), (x, 0.2, SEAT_Z), (x, (0.2 + by) / 2, (SEAT_Z + bz) / 2 + 0.01), (x, by, bz)]
        tube_bm(catmull(back, 3), 0.052, 8, bm=bm)
        tube_bm([(x, -0.22, SEAT_Z - 0.035), (x, 0.21, SEAT_Z - 0.035)], 0.045, 8, bm=bm)
        ellipsoid_bm((x, -0.21, 0.66), (0.072, 0.085, 0.072), 10, 6, bm=bm)
        ellipsoid_bm((x, by, bz + 0.02), (0.07, 0.07, 0.07), 10, 6, bm=bm)
        for y in (-0.2, 0.22):
            ellipsoid_bm((x, y, 0.04), (0.08, 0.09, 0.04), 10, 5, bm=feet)
    fin("Frames", bm, "SH_Timber", angle=60)
    fin("Feet", feet, "SH_Walnut", angle=70)


def build_slats():
    bm = bmesh.new()
    for y in (-0.165, 0.0, 0.165):
        rings = rbox_rings(L, 0.145, SLAT_T, 0.05, 0.026, seg=2, Rb=0.016, segb=1, z0=SEAT_Z - 0.01, cy=y)
        loft(rings, 2, bm=bm)
    for h in (0.2, 0.38):
        rings = rbox_rings(L, SLAT_T, 0.16, 0.03, 0.028, seg=2, Rb=0.028, segb=2, z0=-0.08)
        y, z = back_point(0.0, h)
        m = Matrix.Translation((0, y + 0.05, z)) @ Matrix.Rotation(-BACK_TILT, 4, "X")
        loft(rings, 2, bm=bm, matrix=m)
    fin("Slats", bm, "SH_Oak", angle=50)


def build_heart():
    y, z = back_point(0.0, 0.38)
    m = Matrix.Translation((0, y + 0.05 - SLAT_T / 2 - 0.012, z)) @ Matrix.Rotation(-BACK_TILT, 4, "X") @ face_m(0, 0, 0)
    m = m @ Matrix.Translation((0, -0.07, 0))
    fin("Heart", badge_bm(heart_outline(0.22), 0.04, 0.014, 2, matrix=m), "SH_Plum", angle=60)


out, flags = cli()
begin()
build_frames()
build_slats()
build_heart()
ob = join_all("ShopBench")
ys = [v.co.y for v in ob.data.vertices]
ob.data.transform(Matrix.Translation((0, -(max(ys) + min(ys)) / 2, 0)))
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.55, -0.3, 0), target=(-0.25, 0.0, 0.45), ortho=3.0)
