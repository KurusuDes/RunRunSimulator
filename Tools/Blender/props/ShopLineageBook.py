import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

TILT = 22.0
DESK_Z = 0.92
DESK_W, DESK_D, DESK_T = 0.6, 0.42, 0.05
PAGE_X = [0.005, 0.03, 0.07, 0.14, 0.21, 0.245]
PAGE_Z = [0.052, 0.082, 0.096, 0.094, 0.084, 0.068]
PAGE_D = 0.33


def desk_m():
    return Matrix.Translation((0, 0.0, DESK_Z)) @ Matrix.Rotation(math.radians(TILT), 4, "X")


def ph(ax):
    return float(np.interp(ax, PAGE_X, PAGE_Z))


def slab(pts, thick, to3d, bev=0.01, bsegs=2, bm=None):
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
    bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


def build_stand():
    prof = [(0.0, 0.0), (0.22, 0.0), (0.235, 0.015), (0.238, 0.04), (0.225, 0.06), (0.19, 0.072), (0.12, 0.08),
            (0.0, 0.08)]
    finish("Base", lathe_bm(prof, 18), "SH_Walnut", angle=55)
    prof = [(0.0, 0.07), (0.125, 0.07), (0.125, 0.1), (0.1, 0.14), (0.085, 0.2), (0.08, 0.38), (0.105, 0.44),
            (0.112, 0.49), (0.105, 0.54), (0.08, 0.6), (0.08, 0.74), (0.095, 0.79), (0.1, 0.85), (0.0, 0.85)]
    finish("Column", lathe_bm(prof, 12), "SH_Honey", angle=45)
    bm = bmesh.new()
    for z, r in ((0.13, 0.1), (0.76, 0.09)):
        torus_bm(r, 0.024, 12, 5, bm=bm, matrix=Matrix.Translation((0, 0, z)))
    finish("Rings", bm, "SH_Walnut", angle=70)
    M = desk_m()
    bm = soft_box((0, 0, 0), (DESK_W, DESK_D, DESK_T), 0.05, 0.02, seg=2, Rb=0.012)
    xf(bm, M @ Matrix.Translation((0, 0, -DESK_T / 2)))
    rbox_bm((0, 0, 0), (DESK_W - 0.02, 0.045, 0.07), 0.02, 2, bm=bm,
            matrix=M @ Matrix.Translation((0, -DESK_D / 2 + 0.005, 0.012)))
    soft_box((0, 0.0, DESK_Z - 0.09), (0.2, 0.2, 0.13), 0.05, 0.02, seg=2, bm=bm)
    finish("Desk", bm, "SH_Walnut", angle=50)


def build_book():
    M = desk_m()
    cov = bmesh.new()
    for s in (-1, 1):
        rbox_bm((0, 0, 0), (0.265, PAGE_D + 0.04, 0.024), 0.01, 1, bm=cov,
                matrix=Matrix.Translation((s * 0.14, 0, 0.022)) @ Matrix.Identity(4))
    tube_bm([(0, -PAGE_D / 2 - 0.015, 0.03), (0, PAGE_D / 2 + 0.015, 0.03)], 0.026, 8, bm=cov)
    xf(cov, M)
    finish("Covers", cov, "SH_Plum", angle=50)
    pages = bmesh.new()
    for s in (-1, 1):
        top = catmull([(s * x, z, 0) for x, z in zip(PAGE_X, PAGE_Z)], 2)
        pts = [Vector((s * 0.245, 0.03)), Vector((s * 0.005, 0.03))] + [Vector((p.x, p.y)) for p in top]
        if s < 0:
            pts = list(reversed(pts))
        slab(pts, PAGE_D, lambda u, v, w: (u, w, v), bev=0.008, bm=pages)
    xf(pages, M)
    finish("Pages", pages, "SH_Parchment", angle=45)
    ink, dots, gold = bmesh.new(), bmesh.new(), bmesh.new()
    tx = -0.14
    tube_bm([(tx, -0.1, ph(0.14) + 0.002), (tx, 0.0, ph(0.14) + 0.002)], 0.011, 5, bm=ink)
    for bx in (-0.2, -0.08):
        tube_bm([(tx, 0.0, ph(0.14) + 0.002), ((tx + bx) / 2, 0.04, ph(abs((tx + bx) / 2)) + 0.002),
                 (bx, 0.075, ph(abs(bx)) + 0.002)], 0.011, 5, bm=ink)
    for x, y in ((-0.2, 0.085), (-0.08, 0.085), (tx, -0.11)):
        ellipsoid_bm((x, y, ph(abs(x)) + 0.002), (0.03, 0.03, 0.01), 12, 4, bm=dots)
    for i, (L, y) in enumerate(((0.11, 0.1), (0.13, 0.05), (0.09, 0.0), (0.12, -0.05), (0.07, -0.1))):
        x = 0.07 + L / 2
        rbox_bm((x, y, (ph(0.07) + ph(0.07 + L)) / 2), (L, 0.02, 0.012), 0.006, 1, bm=ink,
                matrix=Matrix.Rotation(math.atan2(ph(0.07 + L) - ph(0.07), L), 4, "Y").inverted())
    for s in (-1, 1):
        for t in (-1, 1):
            rbox_bm((s * 0.255, t * (PAGE_D / 2 + 0.005), 0.024), (0.055, 0.055, 0.032), 0.012, 1, bm=gold,
                    matrix=Matrix.Identity(4))
    xf(ink, M)
    xf(dots, M)
    xf(gold, M)
    p0 = M @ Vector((0.015, PAGE_D / 2 - 0.02, 0.06))
    p1 = M @ Vector((0.03, 0.0, 0.07))
    p2 = M @ Vector((0.04, -PAGE_D / 2 - 0.01, 0.055))
    p3 = M @ Vector((0.045, -DESK_D / 2 - 0.03, 0.02))
    p4 = p3 + Vector((0.005, -0.008, -0.12))
    p5 = p3 + Vector((0.01, -0.012, -0.2))
    tube_bm(catmull([p0, p1, p2, p3, p4, p5], 2), 0.016, 5, bm=gold)
    ellipsoid_bm(p5 + Vector((0, 0, -0.02)), (0.03, 0.03, 0.035), 8, 5, bm=gold)
    finish("Ink", ink, "SH_Walnut", angle=60)
    finish("Dots", dots, "SH_Plum", angle=None)
    finish("Gold", gold, "SH_Gold", angle=55)


out, flags = cli()
begin()
build_stand()
build_book()
for o in PARTS:
    print("PART %-8s tris=%d" % (o.name, sum(len(f.vertices) - 2 for f in o.data.polygons)))
ob = join_all("ShopLineageBook")
report(ob)
export(ob, flags)
if out:
    preview(ob, out, dragon_loc=(1.1, -0.3, 0), ortho=2.6, target=(0.45, 0, 0.6))
    render(os.path.join(out, "ShopLineageBook_c34.png"), 25, 50, (0, 0, DESK_Z), 0.9)
    render(os.path.join(out, "ShopLineageBook_cfront.png"), 0, 20, (0, 0, DESK_Z - 0.1), 0.9)
    contact_sheet(out, ["ShopLineageBook_c34.png", "ShopLineageBook_cfront.png"],
                  os.path.join(out, "ShopLineageBook_close.png"), cols=2)
