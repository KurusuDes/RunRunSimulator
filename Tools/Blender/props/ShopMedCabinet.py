import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

W, D = 0.90, 0.40
BW, BD = 0.80, 0.34
LOW_TOP = 0.65
LEDGE_Z0, LEDGE_Z1 = 0.63, 0.685
SHELF_Z = 1.0
TOP_Z0, TOP_Z1 = 1.295, 1.355
CREST_Y = 0.07
FY = -BD / 2


def face_m(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


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


def cross_badge(x, y, z, R):
    prof = [(0.0, 0.0), (R + 0.014, 0.0), (R + 0.018, 0.016), (R + 0.009, 0.03), (R, 0.028), (0.0, 0.028)]
    finish("BadgeRim", lathe_bm(prof, 28, matrix=face_m(x, y, z)), "SH_Oak", angle=55)
    prof = [(0.0, 0.0), (R - 0.004, 0.0), (R - 0.004, 0.032), (R - 0.018, 0.04), (0.0, 0.04)]
    finish("BadgeDisc", lathe_bm(prof, 28, matrix=face_m(x, y - 0.002, z)), "SH_White", angle=55)
    a, b = R * 1.25, R * 0.42
    bm = bmesh.new()
    rbox_bm((x, y - 0.05, z), (b, 0.034, a), 0.014, 2, bm=bm)
    rbox_bm((x, y - 0.05, z), (a, 0.034, b), 0.014, 2, bm=bm)
    finish("Cross", bm, "SH_Teal", angle=55)


def build_frame():
    finish("Plinth", loft(rbox_rings(W, D, 0.1, 0.07, 0.03, seg=2, Rb=0.012, z0=0.0), 3), "SH_Walnut", angle=50)
    finish("Lower", loft(rbox_rings(BW, BD, LOW_TOP - 0.08, 0.05, 0.012, seg=1, z0=0.08), 3), "SH_Oak", angle=50)
    finish("Ledge", loft(rbox_rings(W - 0.02, D, LEDGE_Z1 - LEDGE_Z0, 0.06, 0.022, seg=2, Rb=0.014, z0=LEDGE_Z0), 3),
           "SH_Walnut", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        rbox_bm((sx * (BW / 2 - 0.035), 0.0, (LEDGE_Z1 + TOP_Z0) / 2), (0.075, BD - 0.01, TOP_Z0 - LEDGE_Z1 + 0.02), 0.022, 2, bm=bm)
    rbox_bm((0, -0.012, SHELF_Z - 0.022), (BW - 0.1, BD - 0.06, 0.045), 0.016, 2, bm=bm)
    finish("UpperSides", bm, "SH_Oak", angle=50)
    finish("BackPanel", rbox_bm((0, BD / 2 - 0.05, (LEDGE_Z1 + TOP_Z0) / 2), (BW - 0.06, 0.04, TOP_Z0 - LEDGE_Z1 + 0.02), 0.015, 2),
           "SH_Sage", angle=50)
    finish("BackBoard", rbox_bm((0, BD / 2 - 0.02, (LEDGE_Z1 + TOP_Z0) / 2), (BW - 0.02, 0.035, TOP_Z0 - LEDGE_Z1 + 0.03), 0.012, 2),
           "SH_Oak", angle=50)
    bm = bmesh.new()
    loft(rbox_rings(W, D, TOP_Z1 - TOP_Z0, 0.07, 0.026, seg=2, Rb=0.016, segb=2, z0=TOP_Z0), 3, bm=bm)
    rbox_bm((0, FY - 0.006, SHELF_Z + 0.002), (BW - 0.09, 0.05, 0.05), 0.02, 2, bm=bm)
    prof = [(0.0, 0.08), (0.043, 0.08), (0.05, 0.11), (0.04, 0.16), (0.04, TOP_Z0 - 0.04), (0.05, TOP_Z0 - 0.01),
            (0.0, TOP_Z0 - 0.01)]
    for sx in (-1, 1):
        lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((sx * (BW / 2 + 0.005), FY + 0.01, 0)))
    finish("Trim", bm, "SH_Walnut", angle=55)


def build_doors():
    bm = bmesh.new()
    zc = (0.1 + LEDGE_Z0) / 2
    for sx in (-1, 1):
        loft(rbox_rings(0.335, 0.43, 0.026, 0.05, 0.012, seg=2), 3, cap0=False, bm=bm,
             matrix=face_m(sx * 0.18, FY + 0.008, zc))
    finish("Doors", bm, "SH_White", angle=55)
    bm = bmesh.new()
    prof = [(0.0, 0.0), (0.028, 0.0), (0.028, 0.016), (0.036, 0.03), (0.03, 0.046), (0.0, 0.05)]
    for sx in (-1, 1):
        lathe_bm(prof, 12, bm=bm, matrix=face_m(sx * 0.055, FY - 0.016, zc + 0.03))
    finish("Knobs", bm, "SH_Teal", angle=60)
    bm = bmesh.new()
    for sx in (-1, 1):
        for z in (zc - 0.15, zc + 0.15):
            rbox_bm((sx * (BW / 2 - 0.004), FY + 0.02, z), (0.02, 0.06, 0.07), 0.008, 1, bm=bm)
    finish("Hinges", bm, "SH_Walnut", angle=55)


def jar(x, y, z, r, h, bm_body, bm_lid, label=None):
    prof = [(0.0, 0.0), (r - 0.012, 0.0), (r, 0.014), (r, h - 0.03), (r - 0.012, h - 0.012), (r - 0.02, h), (0.0, h)]
    lathe_bm(prof, 14, bm=bm_body, matrix=Matrix.Translation((x, y, z)))
    prof = [(0.0, h - 0.016), (r - 0.006, h - 0.016), (r + 0.004, h - 0.004), (r + 0.004, h + 0.022), (r - 0.012, h + 0.034),
            (0.0, h + 0.036)]
    lathe_bm(prof, 14, bm=bm_lid, matrix=Matrix.Translation((x, y, z)))
    ellipsoid_bm((x, y, z + h + 0.045), (0.018, 0.018, 0.016), 8, 4, bm=bm_lid)
    if label is not None:
        prof = [(r + 0.004, h * 0.3), (r + 0.007, h * 0.34), (r + 0.007, h * 0.62), (r + 0.004, h * 0.66)]
        lathe_bm(prof, 14, bm=label, matrix=Matrix.Translation((x, y, z)))


def flask(x, y, z, r, bm_body, bm_cork):
    prof = [(0.0, 0.0), (r * 0.6, 0.0), (r * 0.95, r * 0.35), (r, r * 0.8), (r * 0.82, r * 1.4), (r * 0.42, r * 1.75),
            (r * 0.36, r * 2.1), (0.0, r * 2.1)]
    lathe_bm(prof, 14, bm=bm_body, matrix=Matrix.Translation((x, y, z)))
    prof = [(0.0, r * 2.0), (r * 0.42, r * 2.0), (r * 0.46, r * 2.35), (r * 0.36, r * 2.45), (0.0, r * 2.45)]
    lathe_bm(prof, 10, bm=bm_cork, matrix=Matrix.Translation((x, y, z)))


def build_items():
    white, teal, sage, walnut = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
    z0 = LEDGE_Z1 - 0.004
    jar(-0.25, 0.01, z0, 0.065, 0.17, white, teal, sage)
    jar(-0.1, 0.03, z0, 0.058, 0.13, white, teal, sage)
    prof = [(0.03, -0.055), (0.07, -0.055), (0.08, -0.045), (0.08, 0.045), (0.07, 0.055), (0.03, 0.055), (0.03, -0.055)]
    m = Matrix.Translation((0.06, 0.0, z0 + 0.078)) @ Matrix.Rotation(math.pi / 2, 4, "X")
    lathe_bm(prof, 16, bm=white, matrix=m)
    tube_bm([(0.13, -0.035, z0 + 0.006), (0.16, -0.06, z0 + 0.006), (0.2, -0.07, z0 + 0.008)], [0.012, 0.012, 0.012], 6,
            bm=white)
    rbox_bm((0.25, 0.02, z0 + 0.08), (0.12, 0.09, 0.16), 0.035, 2, bm=teal)
    rbox_bm((0.25, 0.02, z0 + 0.168), (0.05, 0.05, 0.03), 0.012, 1, bm=white)
    z1 = SHELF_Z + 0.0
    flask(-0.24, 0.02, z1, 0.068, teal, walnut)
    flask(-0.1, 0.04, z1, 0.052, sage, walnut)
    jar(0.06, 0.02, z1, 0.07, 0.19, white, teal, sage)
    jar(0.23, 0.03, z1, 0.06, 0.12, white, teal, None)
    finish("ItemsWhite", white, "SH_White", angle=60)
    finish("ItemsTeal", teal, "SH_Teal", angle=60)
    finish("ItemsSage", sage, "SH_Sage", angle=60)
    finish("Corks", walnut, "SH_Walnut", angle=60)


def build_crest():
    hw, hh = 0.31, 0.255
    ctrl = [(-hw - 0.07, 0.0), (-hw, 0.04), (-hw * 0.7, hh * 0.72), (-hw * 0.3, hh * 0.98), (0.0, hh),
            (hw * 0.3, hh * 0.98), (hw * 0.7, hh * 0.72), (hw, 0.04), (hw + 0.07, 0.0)]
    pts = [Vector((p.x, p.y)) for p in catmull([(x, y, 0) for x, y in ctrl], 3)]
    pts = [Vector((-hw - 0.07, -0.04))] + pts + [Vector((hw + 0.07, -0.04))]
    bm = slab(pts, 0.07, lambda u, v, w: (u, CREST_Y + w, TOP_Z1 - 0.015 + v), bev=0.022)
    finish("Crest", bm, "SH_Walnut", angle=45)
    cross_badge(0.0, CREST_Y - 0.035, TOP_Z1 + 0.105, 0.102)


out, flags = cli()
begin()
build_frame()
build_doors()
build_items()
build_crest()
ob = join_all("ShopMedCabinet")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.95, -0.35, 0), dragon_rot=25.0, target=(-0.3, 0.0, 0.75), ortho=2.6)
