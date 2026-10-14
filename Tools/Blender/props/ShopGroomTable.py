import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


def front_matrix(x, y, z, rz=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ M


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


def badge_bm(outline, t, bev, steps=2, bm=None, matrix=None, inner=()):
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
    extra = []
    caps = []
    for ring, z, flip in ((vr[0], 0.0, True), (vr[-1], t, False)):
        prev = ring
        for s in inner:
            nr = [bm.verts.new((cx + (v.co.x - cx) * s, cy + (v.co.y - cy) * s, z)) for v in ring]
            extra += nr
            for k in range(n):
                q = (prev[k], prev[(k + 1) % n], nr[(k + 1) % n], nr[k])
                bm.faces.new(tuple(reversed(q)) if flip else q)
            prev = nr
        c = bm.verts.new((cx, cy, z))
        extra.append(c)
        for k in range(n):
            tri = (prev[k], prev[(k + 1) % n], c)
            bm.faces.new(tuple(reversed(tri)) if flip else tri)
    if matrix is not None:
        xf(bm, matrix, [v for r in vr for v in r] + extra)
    return bm


def loop_tube_bm(path, radius, sides=6, bm=None, matrix=None):
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
    if matrix is not None:
        xf(bm, matrix, [v for r in rings for v in r])
    return bm


def drop_outline(size, n=24):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 0.86 * math.sin(t) * math.sin(t / 2) ** 0.8
        y = math.cos(t)
        pts.append((x * size / 2.0, y * size / 2.0))
    return pts


def oval(a, b, n=32):
    return [(a * math.cos(2 * math.pi * k / n), b * math.sin(2 * math.pi * k / n)) for k in range(n)]


ACC = "SH_Teal"
TOP_Z = 0.62
LX, LY = 0.4, 0.21
MY = 0.215
MZ = 1.06
MA, MB = 0.29, 0.33
PX = 0.37


def build_table():
    fin("Top", soft_box((0, 0, TOP_Z - 0.035), (1.0, 0.6, 0.07), 0.07, 0.025), "SH_Oak", angle=50)
    bm = bmesh.new()
    prof = [(0.0, 0.0), (0.045, 0.0), (0.054, 0.025), (0.045, 0.07), (0.04, 0.12), (0.058, 0.24), (0.048, 0.33),
            (0.04, 0.4), (0.048, 0.5), (0.0, 0.56)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((sx * LX, sy * LY, 0)))
    fin("Legs", bm, "SH_Walnut", angle=50)
    fin("Apron", rbox_bm((0, 0, 0.49), (0.88, 0.48, 0.14), 0.03, 2), "SH_Walnut", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        rbox_bm((sx * 0.205, -0.245, 0.49), (0.36, 0.04, 0.1), 0.025, 2, bm=bm)
    fin("Drawers", bm, "SH_Oak", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((sx * 0.205, -0.275, 0.49), (0.036, 0.03, 0.036), 10, 5, bm=bm)
    fin("Knobs", bm, ACC, angle=80)
    fin("Shelf", rbox_bm((0, 0, 0.15), (0.84, 0.44, 0.045), 0.018, 2), "SH_Oak", angle=50)


def build_towels():
    bm = bmesh.new()
    soft_box((0.12, 0.0, 0.215), (0.36, 0.3, 0.085), 0.05, 0.035, bm=bm)
    soft_box((0.135, 0.01, 0.295), (0.34, 0.28, 0.08), 0.05, 0.034, bm=bm)
    fin("Towels", bm, "SH_White", angle=70)
    bm = bmesh.new()
    rbox_bm((0.03, 0.0, 0.215), (0.07, 0.31, 0.092), 0.032, 1, bm=bm)
    rbox_bm((0.045, 0.01, 0.295), (0.07, 0.29, 0.088), 0.032, 1, bm=bm)
    fin("TowelStripe", bm, ACC, angle=70)
    fin("Basket", soft_box((-0.24, 0.0, 0.25), (0.26, 0.26, 0.16), 0.08, 0.03), "SH_Walnut", angle=50)
    bm = bmesh.new()
    for x, y, r in ((-0.27, -0.03, 0.06), (-0.2, 0.04, 0.055), (-0.22, -0.06, 0.05)):
        ellipsoid_bm((x, y, 0.33), (r, r, r * 0.85), 10, 5, bm=bm)
    fin("BasketBalls", bm, "SH_White", angle=80)


def build_tabletop():
    fin("Mat", soft_box((-0.17, -0.02, TOP_Z + 0.012), (0.58, 0.44, 0.032), 0.08, 0.014), ACC, angle=60)
    bm = bmesh.new()
    px, py, pz = -0.17, -0.04, TOP_Z + 0.026
    ellipsoid_bm((px, py, pz), (0.075, 0.06, 0.016), 12, 4, bm=bm)
    for ang in (-62, -22, 22, 62):
        a = math.radians(90 + ang)
        ellipsoid_bm((px + 0.1 * math.cos(a), py + 0.03 + 0.085 * math.sin(a), pz), (0.03, 0.034, 0.014), 8, 4, bm=bm)
    fin("Paw", bm, "SH_White", angle=80)
    jx, jy = 0.33, -0.1
    prof = [(0.0, TOP_Z - 0.005), (0.075, TOP_Z - 0.005), (0.085, TOP_Z + 0.02), (0.085, TOP_Z + 0.15),
            (0.075, TOP_Z + 0.17), (0.0, TOP_Z + 0.17)]
    fin("Jar", lathe_bm(prof, 16, matrix=Matrix.Translation((jx, jy, 0))), "SH_Glass", angle=55)
    fin("JarLip", torus_bm(0.078, 0.02, 16, 5, matrix=Matrix.Translation((jx, jy, TOP_Z + 0.165))), ACC, angle=80)
    bm = bmesh.new()
    for k, (dx, ang) in enumerate(((-0.03, -14), (0.0, 4), (0.03, 18))):
        m = (Matrix.Translation((jx + dx, jy + 0.005 * k, TOP_Z + 0.2)) @ Matrix.Rotation(math.radians(ang), 4, "Y")
             @ Matrix.Rotation(math.radians(20 * k - 20), 4, "Z"))
        rbox_bm((0, 0, 0), (0.035, 0.03, 0.15), 0.012, 1, bm=bm, matrix=m)
    fin("Combs", bm, "SH_White", angle=60)
    bx, by = 0.27, 0.11
    m = Matrix.Translation((bx, by, TOP_Z)) @ Matrix.Rotation(math.radians(-25), 4, "Z")
    bm = tube_bm([(-0.15, 0, 0.03), (-0.04, 0, 0.032)], [0.026, 0.03], 8)
    ellipsoid_bm((-0.155, 0, 0.03), (0.03, 0.03, 0.03), 8, 4, bm=bm)
    rbox_bm((0.03, 0, 0.035), (0.15, 0.09, 0.05), 0.022, 2, bm=bm)
    fin("Brush", xf(bm, m), ACC, angle=60)
    bm = rbox_bm((0.03, 0, 0.068), (0.13, 0.075, 0.035), 0.014, 2)
    fin("Bristles", xf(bm, m), "SH_White", angle=60)


def build_mirror():
    bm = bmesh.new()
    for sx in (-1, 1):
        rbox_bm((sx * PX, MY, (TOP_Z + MZ + 0.04) / 2), (0.07, 0.07, MZ + 0.04 - TOP_Z + 0.01), 0.025, 2, bm=bm)
        ellipsoid_bm((sx * PX, MY, MZ + 0.065), (0.05, 0.05, 0.045), 10, 5, bm=bm)
        rbox_bm((sx * PX, MY, TOP_Z + 0.02), (0.11, 0.11, 0.04), 0.018, 2, bm=bm)
    fin("Posts", bm, "SH_Walnut", angle=50)
    back = badge_bm(oval(MA + 0.01, MB + 0.01), 0.04, 0.012, 2, matrix=front_matrix(0, MY + 0.03, MZ))
    fin("MirrorBack", back, "SH_Walnut", angle=50)
    glass = badge_bm(oval(MA - 0.01, MB - 0.01), 0.04, 0.015, 2, matrix=front_matrix(0, MY + 0.018, MZ))
    fin("Glass", glass, "SH_Glass", angle=60)
    path = [(x, y, 0.0) for x, y in oval(MA, MB, 30)]
    fr = loop_tube_bm(path, 0.038, 6, matrix=front_matrix(0, MY - 0.022, MZ))
    fin("Frame", fr, "SH_Oak", angle=70)
    bm = bmesh.new()
    for sx in (-1, 1):
        m = Matrix.Translation((sx * (MA + 0.03), MY, MZ)) @ Matrix.Rotation(math.radians(90 * sx), 4, "Y")
        lathe_bm([(0.0, -0.01), (0.04, -0.01), (0.045, 0.02), (0.03, 0.04), (0.0, 0.045)], 12, bm=bm, matrix=m)
    fin("Pivots", bm, ACC, angle=60)
    bm = bmesh.new()
    rbox_bm((0, MY, MZ + MB + 0.02), (0.14, 0.06, 0.06), 0.025, 2, bm=bm)
    fin("CrestBase", bm, "SH_Oak", angle=50)
    m = front_matrix(0, MY - 0.03, MZ + MB + 0.085)
    fin("Drop", badge_bm(drop_outline(0.13), 0.05, 0.016, 2, matrix=m), "SH_White", angle=60)
    bm = bmesh.new()
    for dx, dz, L in ((-0.13, 0.13, 0.16), (-0.06, 0.16, 0.08)):
        m = Matrix.Translation((dx, MY - 0.028, MZ + dz)) @ Matrix.Rotation(math.radians(-45), 4, "Y")
        rbox_bm((0, 0, 0), (0.035, 0.016, L), 0.007, 1, bm=bm, matrix=m)
    fin("Shine", bm, "SH_White", angle=60)


out, flags = cli()
begin()
build_table()
build_towels()
build_tabletop()
build_mirror()
ob = join_all("ShopGroomTable")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.25, -0.3, 0), target=(-0.35, 0.0, 0.75), ortho=2.9)
