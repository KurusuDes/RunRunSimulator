import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

W = 1.20
D = 0.35
SIDE_T = 0.075
FRONT = -D / 2
BACK = D / 2
UP_FRONT = -0.095
TOP = 1.44
S1 = 0.40
S2 = 0.80
S3 = 1.12
IW = W - 2 * SIDE_T + 0.02
DARK = "SH_Walnut"
WOOD = "SH_Oak"
PAINT = "SH_Sage"
ACC = "SH_Gold"
CERAMIC = "SH_Cream"


def fin(name, bm, mat, angle=50.0):
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def face_m(x, y, z, facing=-1):
    if facing < 0:
        return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
    return Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))


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
    big = [f for f in bm.faces if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


def bone_bm(length, r, flat=1.0, bm=None, matrix=None, useg=10):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    hx = length / 2 - r * 0.9
    tube_bm([(-hx, 0, 0), (hx, 0, 0)], r * 0.62, 8, bm=bm)
    for sx in (-1, 1):
        for sz in (-1, 1):
            ellipsoid_bm((sx * hx, 0, sz * r * 0.62), (r * 0.72, r * 0.72, r * 0.72), useg, max(4, useg // 2 + 1), bm=bm)
    new = [v for v in bm.verts if v not in before]
    m = Matrix.Diagonal((1.0, flat, 1.0, 1.0))
    if matrix is not None:
        m = matrix @ m
    xf(bm, m, new)
    return bm


def build_frame():
    prof = fillet([(FRONT, 0.04, 0.03), (BACK, 0.04, 0.03), (BACK, TOP, 0.1), (UP_FRONT, TOP, 0.06),
                   (UP_FRONT, 0.62, 0.07), (FRONT, 0.47, 0.08)], 3)
    bm = bmesh.new()
    for s in (-1, 1):
        x0 = s * (W / 2 - SIDE_T / 2)
        slab(prof, SIDE_T, lambda u, v, w, x0=x0: (x0 + w, u, v), bev=0.025, bm=bm)
    fin("Sides", bm, DARK, angle=45)
    bm = bmesh.new()
    for s in (-1, 1):
        for y in (FRONT + 0.07, BACK - 0.07):
            ellipsoid_bm((s * (W / 2 - 0.07), y, 0.05), (0.072, 0.066, 0.05), 8, 4, bm=bm)
    fin("Feet", bm, DARK, angle=70)
    bm = bmesh.new()
    for s in (-1, 1):
        ellipsoid_bm((s * (W / 2 - SIDE_T / 2), 0.07, TOP + 0.045), (0.066, 0.066, 0.062), 10, 5, bm=bm)
    fin("Finials", bm, ACC, angle=80)


def build_drawers():
    fin("Box", rbox_bm((0, 0.005, (0.07 + S1) / 2), (IW, D - 0.03, S1 - 0.07), 0.02, 2), WOOD, angle=50)
    bm = bmesh.new()
    dw = (IW - 0.08) / 2
    for s in (-1, 1):
        loft(rbox_rings(dw, 0.22, 0.03, 0.05, 0.013, seg=2), 3, cap0=False, bm=bm,
             matrix=face_m(s * (dw / 2 + 0.02), FRONT + 0.02, (0.07 + S1) / 2 - 0.005))
    fin("DrawerFronts", bm, PAINT, angle=55)
    bm = bmesh.new()
    for s in (-1, 1):
        x = s * (dw / 2 + 0.02)
        bone_bm(0.15, 0.027, 0.6, bm=bm, matrix=Matrix.Translation((x, FRONT - 0.032, (0.07 + S1) / 2)), useg=6)
        for xx in (x - 0.042, x + 0.042):
            tube_bm([(xx, FRONT - 0.005, (0.07 + S1) / 2), (xx, FRONT - 0.035, (0.07 + S1) / 2)], 0.012, 6, bm=bm)
    fin("Pulls", bm, ACC, angle=60)


def build_shelves():
    bm = bmesh.new()
    for z in (S2, S3):
        rbox_bm((0, (UP_FRONT + 0.16) / 2, z - 0.03), (IW, 0.16 - UP_FRONT + 0.01, 0.06), 0.022, 2, bm=bm)
    rbox_bm((0, (UP_FRONT + 0.16) / 2 + 0.01, TOP - 0.035), (IW, 0.16 - UP_FRONT + 0.03, 0.07), 0.025, 2, bm=bm)
    fin("Shelves", bm, WOOD, angle=50)
    bm = bmesh.new()
    rbox_bm((0, FRONT + 0.012, S1 + 0.012), (IW, 0.06, 0.07), 0.026, 2, bm=bm)
    for z in (S2, S3):
        rbox_bm((0, UP_FRONT - 0.008, z + 0.012), (IW, 0.06, 0.07), 0.026, 2, bm=bm)
    rbox_bm((0, UP_FRONT - 0.01, TOP - 0.03), (IW + 0.03, 0.07, 0.085), 0.03, 2, bm=bm)
    fin("Lips", bm, DARK, angle=50)
    bm = bmesh.new()
    z0, z1 = S1 - 0.02, TOP - 0.06
    n = 4
    h = (z1 - z0) / n
    for i in range(n):
        rbox_bm((0, 0.15, z0 + h * (i + 0.5)), (IW, 0.045, h + 0.004), 0.02, 1, bm=bm)
    fin("BackPlanks", bm, PAINT, angle=50)


def build_crest():
    hw, hh = 0.36, 0.17
    ctrl = [(-hw - 0.08, 0.0), (-hw, 0.04), (-hw * 0.72, hh * 0.7), (-hw * 0.32, hh * 0.97), (0.0, hh),
            (hw * 0.32, hh * 0.97), (hw * 0.72, hh * 0.7), (hw, 0.04), (hw + 0.08, 0.0)]
    pts = [Vector((p.x, p.y)) for p in catmull([(x, y, 0) for x, y in ctrl], 3)]
    pts = [Vector((-hw - 0.08, -0.03))] + pts + [Vector((hw + 0.08, -0.03))]
    yc = 0.11
    fin("Crest", slab(pts, 0.065, lambda u, v, w: (u, yc + w, TOP - 0.02 + v), bev=0.02), DARK, angle=45)
    bm = bone_bm(0.26, 0.05, 0.55, matrix=Matrix.Translation((0, yc - 0.045, TOP + 0.065)), useg=8)
    fin("CrestBone", bm, ACC, angle=60)


def jar(x, y, z, r, h, body, label, lid=ACC, bms=None, bone=False):
    segs = 10
    prof = [(0.0, 0.0), (r * 0.82, 0.0), (r, 0.03), (r, h * 0.72), (r * 0.86, h * 0.84), (r * 0.7, h * 0.86), (0.0, h * 0.86)]
    lathe_bm(prof, segs, bm=bms[body], matrix=Matrix.Translation((x, y, z)))
    lp = [(0.0, h * 0.82), (r * 0.8, h * 0.82), (r * 0.84, h * 0.9), (r * 0.7, h * 0.96), (0.0, h * 0.97)]
    lathe_bm(lp, segs, bm=bms[lid], matrix=Matrix.Translation((x, y, z)))
    if bone:
        bone_bm(r * 1.05, r * 0.25, 0.7, bm=bms[lid], matrix=Matrix.Translation((x, y, z + h * 0.97 + r * 0.12)), useg=6)
    else:
        ellipsoid_bm((x, y, z + h * 0.99), (r * 0.32, r * 0.32, r * 0.24), 6, 4, bm=bms[lid])
    bp = [(r - 0.004, h * 0.3), (r + 0.011, h * 0.34), (r + 0.011, h * 0.56), (r - 0.004, h * 0.6)]
    lathe_bm(bp, segs, bm=bms[label], matrix=Matrix.Translation((x, y, z)))


def book(x, y, z, w, d, t, cover, rz=0.0, bms=None):
    m = Matrix.Translation((x, y, z + t / 2)) @ Matrix.Rotation(math.radians(rz), 4, "Z")
    rbox_bm((0, 0, 0), (w, d, t), 0.012, 1, bm=bms[cover], matrix=m)
    rbox_bm((0.012, -0.008, 0), (w - 0.012, d - 0.012, t - 0.022), 0.006, 1, bm=bms[CERAMIC], matrix=m)


def build_contents():
    bms = {k: bmesh.new() for k in (CERAMIC, PAINT, ACC, DARK)}
    jar(-0.31, -0.01, S1, 0.13, 0.31, CERAMIC, PAINT, bms=bms, bone=True)
    jar(0.0, 0.0, S1, 0.115, 0.25, PAINT, CERAMIC, bms=bms, bone=True)
    book(0.31, -0.01, S1, 0.27, 0.2, 0.06, DARK, rz=-4, bms=bms)
    book(0.30, -0.02, S1 + 0.06, 0.24, 0.18, 0.055, PAINT, rz=7, bms=bms)
    yc = 0.035
    for x, r, h, body, lab in ((-0.39, 0.085, 0.24, CERAMIC, PAINT), (-0.15, 0.075, 0.2, CERAMIC, PAINT),
                               (0.1, 0.09, 0.26, PAINT, CERAMIC), (0.36, 0.08, 0.21, CERAMIC, PAINT)):
        jar(x, yc, S2, r, h, body, lab, bms=bms)
    for x, r, h, body, lab in ((-0.38, 0.08, 0.2, PAINT, CERAMIC), (-0.13, 0.085, 0.22, CERAMIC, PAINT)):
        jar(x, yc, S3, r, h, body, lab, bms=bms)
    bk = Matrix.Translation((0.2, yc + 0.01, S3)) @ Matrix.Rotation(math.radians(-12), 4, "Y")
    rbox_bm((0, 0, 0.12), (0.06, 0.19, 0.24), 0.012, 1, bm=bms[DARK], matrix=bk)
    rbox_bm((0.0, -0.008, 0.12), (0.04, 0.18, 0.218), 0.006, 1, bm=bms[CERAMIC], matrix=bk)
    bk = Matrix.Translation((0.28, yc + 0.01, S3)) @ Matrix.Rotation(math.radians(-12), 4, "Y")
    rbox_bm((0, 0, 0.11), (0.058, 0.18, 0.22), 0.012, 1, bm=bms[PAINT], matrix=bk)
    rbox_bm((0.0, -0.008, 0.11), (0.04, 0.17, 0.2), 0.006, 1, bm=bms[CERAMIC], matrix=bk)
    rbox_bm((0.385, yc, S3 + 0.12), (0.05, 0.16, 0.24), 0.012, 1, bm=bms[DARK])
    rbox_bm((0.385, yc - 0.008, S3 + 0.12), (0.032, 0.15, 0.22), 0.006, 1, bm=bms[CERAMIC])
    fin("Ceramics", bms[CERAMIC], CERAMIC, angle=55)
    fin("Painted", bms[PAINT], PAINT, angle=55)
    fin("Lids", bms[ACC], ACC, angle=60)
    fin("Covers", bms[DARK], DARK, angle=55)


out, flags = cli()
begin()
build_frame()
build_drawers()
build_shelves()
build_crest()
build_contents()
ob = join_all("ShopRecipeShelf")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.05, -0.35, 0), dragon_rot=20.0, target=(-0.25, 0, 0.8), ortho=2.6)
