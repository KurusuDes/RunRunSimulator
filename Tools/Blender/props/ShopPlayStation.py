import sys, random
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


def plinth(R, accent):
    prof = [(0.0, 0.0), (R - 0.025, 0.0), (R, 0.024), (R - 0.02, 0.05), (0.0, 0.05)]
    fin("PlinthFoot", lathe_bm(prof, 24), accent, angle=60)
    r2 = R - 0.022
    prof = [(r2, 0.04), (r2, 0.062), (r2 - 0.024, 0.08), (0.0, 0.08)]
    fin("PlinthTop", lathe_bm(prof, 24), "SH_Cream", angle=60)


def heart_outline(size, n=28):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * size / 32.0, (y + 2.0) * size / 32.0))
    return pts



def star_outline(ro, rin, n=5):
    pts = []
    for k in range(2 * n):
        a = math.pi / 2 + math.pi * k / n
        r = ro if k % 2 == 0 else rin
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


ACC = "SH_Mint"
PLINTH_R = 0.39
TX, TY = -0.1, 0.1
DECK = 0.36
DECK_Z = 0.44
POST_TOP = 0.77
PI = 0.15


def build_tower():
    rings = rbox_rings(DECK, DECK, 0.07, 0.06, 0.025, seg=2, Rb=0.015, segb=1, z0=DECK_Z - 0.07, cx=TX, cy=TY)
    fin("Deck", loft(rings, 3), "SH_Straw", angle=50)
    prof = [(0.06, 0.075), (0.05, 0.1), (0.043, 0.135), (0.043, POST_TOP), (0.0, POST_TOP)]
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((TX + sx * PI, TY + sy * PI, 0)))
    fin("Posts", bm, ACC, angle=50)
    bm = bmesh.new()
    z = DECK_Z + 0.13
    rbox_bm((TX, TY + PI, z), (2 * PI, 0.045, 0.06), 0.02, 2, bm=bm)
    rbox_bm((TX - PI, TY, z), (0.045, 2 * PI, 0.06), 0.02, 2, bm=bm)
    rbox_bm((TX, TY + PI, z - 0.075), (2 * PI, 0.04, 0.05), 0.018, 2, bm=bm)
    rbox_bm((TX - PI, TY, z - 0.075), (0.04, 2 * PI, 0.05), 0.018, 2, bm=bm)
    fin("Rails", bm, ACC, angle=50)
    rings = [(0.42, 0.42, 0.07, POST_TOP - 0.03, TX, TY), (0.46, 0.46, 0.09, POST_TOP - 0.005, TX, TY),
             (0.45, 0.45, 0.085, POST_TOP + 0.02, TX, TY), (0.3, 0.3, 0.07, POST_TOP + 0.09, TX, TY),
             (0.12, 0.12, 0.05, POST_TOP + 0.15, TX, TY), (0.04, 0.04, 0.018, POST_TOP + 0.165, TX, TY)]
    fin("Roof", loft(rings, 3), "SH_Coral", angle=45)
    ztop = POST_TOP + 0.165
    st = badge_bm(star_outline(0.1, 0.05), 0.06, 0.02, 2, matrix=front_matrix(TX, TY + 0.0275, ztop + 0.065))
    fin("StarTop", st, "SH_Cream", angle=60)


def sweep_u(path, w, h, t, tb):
    outline = [(-w, h), (-w, -tb), (w, -tb), (w, h), (w - t, h), (w - t, 0.0), (-w + t, 0.0), (-w + t, h)]
    bm = bmesh.new()
    P = [Vector(p) for p in path]
    n = len(P)
    rings = []
    frames = []
    for i in range(n):
        T = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        side = T.cross(UP).normalized()
        nor = side.cross(T).normalized()
        frames.append((side, nor))
        rings.append([bm.verts.new(P[i] + side * s + nor * q) for s, q in outline])
    m = len(outline)
    for A, B in zip(rings, rings[1:]):
        for k in range(m):
            bm.faces.new((A[k], A[(k + 1) % m], B[(k + 1) % m], B[k]))
    caps = [bm.faces.new(list(reversed(rings[0]))), bm.faces.new(rings[-1])]
    bmesh.ops.triangulate(bm, faces=caps)
    return bm, frames


def build_slide():
    path = catmull([(TX + PI + 0.02, TY - 0.06, DECK_Z - 0.005), (0.14, -0.02, DECK_Z - 0.06), (0.24, -0.12, 0.25),
                    (0.27, -0.24, 0.12), (0.27, -0.31, 0.095)], 4)
    w, h, t, tb = 0.105, 0.075, 0.03, 0.03
    bm, frames = sweep_u(path, w, h, t, tb)
    fin("Slide", bm, "SH_Coral", angle=50)
    lip = bmesh.new()
    for sgn in (-1, 1):
        pts = [p + fr[0] * sgn * (w - t / 2) + fr[1] * h for p, fr in zip(path, frames)]
        tube_bm(pts, 0.024, 6, bm=lip)
    fin("SlideLip", lip, ACC, angle=70)


def build_ladder():
    y0, y1 = TY - PI - 0.035, -0.28
    z0, z1 = DECK_Z - 0.01, 0.075
    bm = bmesh.new()
    for x in (TX - 0.085, TX + 0.085):
        tube_bm([(x, y0, z0 + 0.04), (x, y1, z1)], 0.032, 8, bm=bm)
    for f in (0.25, 0.5, 0.75):
        y = y0 + (y1 - y0) * f
        z = z0 + 0.04 + (z1 - z0 - 0.04) * f
        tube_bm([(TX - 0.09, y, z), (TX + 0.09, y, z)], 0.026, 8, bm=bm)
    fin("Ladder", bm, "SH_Straw", angle=60)


def build_ball():
    c = (0.2, 0.2, 0.08 + 0.085)
    r = 0.09
    for parity, mat in ((0, "SH_Coral"), (1, "SH_Cream")):
        bm = ellipsoid_bm(c, (r, r, r), 12, 8)
        dead = []
        for f in bm.faces:
            ce = f.calc_center_median() - Vector(c)
            sec = int(((math.atan2(ce.y, ce.x) + math.pi) / (2 * math.pi)) * 6) % 6
            if sec % 2 != parity:
                dead.append(f)
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        xf(bm, Matrix.Translation(c) @ Matrix.Rotation(0.5, 4, "X") @ Matrix.Translation(-Vector(c)))
        fin("Ball%d" % parity, bm, mat, angle=80)
    bm = ellipsoid_bm((0, 0, 0), (0.03, 0.03, 0.03), 8, 4)
    xf(bm, Matrix.Translation(c) @ Matrix.Rotation(0.5, 4, "X") @ Matrix.Translation((0, 0, r - 0.006)))
    fin("BallCap", bm, ACC, angle=80)


out, flags = cli()
begin()
plinth(PLINTH_R, ACC)
build_tower()
build_slide()
build_ladder()
build_ball()
ob = join_all("ShopPlayStation")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.95, 0.3, 0), target=(-0.4, 0.0, 0.5), ortho=2.6)
