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


def drop_outline(size, n=24):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 0.86 * math.sin(t) * math.sin(t / 2) ** 0.8
        y = math.cos(t)
        pts.append((x * size / 2.0, y * size / 2.0))
    return pts


def drape_path(yr, zr, R, front, back, n_side=7, n_arc=6):
    pts = []
    for j in range(n_side):
        u = j / n_side
        d = front * (1 - u)
        pts.append((yr - R - 0.04 * (d / max(front, 1e-3)) ** 2 * front, zr - d))
    for j in range(n_arc + 1):
        a = math.pi - math.pi * j / n_arc
        pts.append((yr + R * math.cos(a), zr + R * math.sin(a)))
    for j in range(1, n_side + 1):
        u = j / n_side
        d = back * u
        pts.append((yr + R + 0.04 * (d / max(back, 1e-3)) ** 2 * back, zr - d))
    return pts


def towel_bm(x0, x1, path, T, nx=8, fold=0.014, zr=0.0):
    bm = bmesh.new()
    P = [Vector(p) for p in path]
    m = len(P)
    N = []
    for j in range(m):
        t = (P[min(j + 1, m - 1)] - P[max(j - 1, 0)]).normalized()
        N.append(Vector((t.y, -t.x)))
    if N[m // 2].y < 0:
        N = [-n for n in N]
    outer, inner = [], []
    for i in range(nx + 1):
        u = i / nx
        x = x0 + (x1 - x0) * u
        ro, ri = [], []
        for j in range(m):
            depth = max(0.0, zr - P[j].y)
            w = fold * math.sin(u * math.pi * 2.5 + 0.4) * min(1.0, depth / 0.12)
            y = P[j].x + w * (1 if P[j].x < P[m // 2].x else -1)
            z = P[j].y
            no = N[j]
            ro.append(bm.verts.new((x, y + no.x * T / 2, z + no.y * T / 2)))
            ri.append(bm.verts.new((x, y - no.x * T / 2, z - no.y * T / 2)))
        outer.append(ro)
        inner.append(ri)
    faces = {}
    for i in range(nx):
        for j in range(m - 1):
            faces.setdefault(j, []).append(bm.faces.new((outer[i][j], outer[i + 1][j], outer[i + 1][j + 1], outer[i][j + 1])))
            faces.setdefault(j, []).append(bm.faces.new((inner[i][j + 1], inner[i + 1][j + 1], inner[i + 1][j], inner[i][j])))
    for i, sgn in ((0, 1), (nx, -1)):
        for j in range(m - 1):
            q = (outer[i][j], outer[i][j + 1], inner[i][j + 1], inner[i][j])
            faces.setdefault(j, []).append(bm.faces.new(q if sgn > 0 else tuple(reversed(q))))
    for j, sgn in ((0, 1), (m - 1, -1)):
        for i in range(nx):
            q = (outer[i][j], inner[i][j], inner[i + 1][j], outer[i + 1][j])
            faces.setdefault(min(j, m - 2), []).append(bm.faces.new(q if sgn > 0 else tuple(reversed(q))))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm, faces


def fin_two(name, bm, mat, mat2, sel_faces, angle=60.0):
    sel = set(sel_faces)
    idx = [k for k, f in enumerate(bm.faces) if f in sel]
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    ob = finish(name, bm, mat, angle=angle)
    ob.data.materials.append(MATS[mat2])
    for k in idx:
        ob.data.polygons[k].material_index = 1
    return ob


ACC = "SH_Teal"
PX = 0.355
TOP = 0.93
RAIL_R = 0.032
R1 = (-0.045, 0.79)
R2 = (0.045, 0.52)
SHELF_Z = 0.17


def build_frame():
    bm = bmesh.new()
    for sx in (-1, 1):
        rbox_bm((sx * PX, 0, TOP / 2 + 0.03), (0.075, 0.075, TOP - 0.02), 0.028, 2, bm=bm)
    fin("Posts", bm, "SH_Oak", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        soft_box((sx * PX, 0, 0.04), (0.1, 0.3, 0.08), 0.045, 0.03, bm=bm)
    fin("Feet", bm, "SH_Walnut", angle=50)
    fin("Crest", rbox_bm((0, 0, TOP), (2 * PX + 0.05, 0.065, 0.075), 0.03, 2), "SH_Walnut", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        lathe_bm([(0.0, TOP + 0.03), (0.05, TOP + 0.03), (0.06, TOP + 0.05), (0.0, TOP + 0.055)], 12, bm=bm,
                 matrix=Matrix.Translation((sx * PX, 0, 0)))
        ellipsoid_bm((sx * PX, 0, TOP + 0.085), (0.042, 0.042, 0.042), 10, 5, bm=bm)
    fin("Finials", bm, "SH_Gold", angle=70)
    bm = bmesh.new()
    for y, z in (R1, R2):
        tube_bm([(-PX, y, z), (PX, y, z)], [RAIL_R, RAIL_R], 10, bm=bm)
    fin("Rails", bm, "SH_Oak", angle=60)
    bm = bmesh.new()
    for sx in (-1, 1):
        for y, z in (R1, R2):
            lathe_bm([(0.0, 0.0), (0.045, 0.0), (0.05, 0.02), (0.035, 0.035), (0.0, 0.035)], 8, bm=bm,
                     matrix=Matrix.Translation((sx * (PX - 0.035), y, z)) @ Matrix.Rotation(math.radians(-90 * sx), 4, "Y"))
    fin("RailCaps", bm, "SH_Gold", angle=60)
    bm = bmesh.new()
    for k in range(4):
        y = -0.105 + 0.07 * k
        rbox_bm((0, y, SHELF_Z), (2 * PX, 0.058, 0.04), 0.016, 1, bm=bm)
    fin("Slats", bm, "SH_Oak", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        rbox_bm((sx * (PX - 0.02), 0, SHELF_Z - 0.04), (0.07, 0.29, 0.045), 0.018, 2, bm=bm)
    fin("ShelfBars", bm, "SH_Walnut", angle=50)
    m = front_matrix(0, -0.03, TOP + 0.002)
    fin("Drop", badge_bm(drop_outline(0.11), 0.03, 0.012, 2, matrix=m), "SH_White", angle=60)


def build_towels():
    yr, zr = R1
    path = drape_path(yr, zr, RAIL_R + 0.02, 0.36, 0.26)
    bm, faces = towel_bm(-0.27, 0.19, path, 0.04, 9, 0.03, zr)
    m = len(path)
    stripes = [f for j in (1, 3, m - 3) for f in faces.get(j, [])]
    fin_two("TowelA", bm, "SH_White", ACC, stripes)
    yr, zr = R2
    path = drape_path(yr, zr, RAIL_R + 0.02, 0.16, 0.24)
    bm, faces = towel_bm(0.03, 0.3, path, 0.04, 7, 0.026, zr)
    m = len(path)
    stripes = [f for j in (1, m - 3) for f in faces.get(j, [])]
    fin_two("TowelB", bm, ACC, "SH_White", stripes)


def build_stack():
    z = SHELF_Z + 0.02
    cols = (ACC, "SH_White", ACC)
    for k, mat in enumerate(cols):
        h = 0.075
        fin("Fold%d" % k, soft_box((-0.15 + 0.012 * (k % 2), 0.0, z + h / 2), (0.3, 0.24, h + 0.004), 0.06, 0.03),
            mat, angle=70)
        z += h
    bm = tube_bm([(0.08, 0.0, SHELF_Z + 0.075), (0.28, 0.0, SHELF_Z + 0.075)], [0.055, 0.055], 10)
    fin("Roll", bm, "SH_White", angle=70)
    bm = bmesh.new()
    for x in (0.08, 0.28):
        ellipsoid_bm((x, 0.0, SHELF_Z + 0.075), (0.012, 0.035, 0.035), 10, 5, bm=bm)
    fin("RollEnds", bm, ACC, angle=80)


out, flags = cli()
begin()
build_frame()
build_towels()
build_stack()
ob = join_all("ShopTowelRack")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.05, -0.3, 0), target=(-0.35, 0.0, 0.5), ortho=2.6)
