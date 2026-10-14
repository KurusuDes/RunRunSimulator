import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

BW, BH = 1.0, 0.7
BAR = 0.075
YBACK = 0.04
FD = 0.06
FY = YBACK - FD / 2
FRONT = FY - FD / 2
SLATE_Y = 0.022
SLATE_F = SLATE_Y - 0.012
RAIL_Z = 0.205
RAIL_Y = SLATE_F - 0.014
HOOK_XS = (-0.34, -0.17, 0.0, 0.17, 0.34)
CARD_W, CARD_H = 0.13, 0.17
CARD_Y = RAIL_Y - 0.03
SPECIAL = 2
LIFT_Z = 1.35


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


def merge(dst, src, m):
    xf(src, m)
    me = bpy.data.meshes.new("tmp")
    src.to_mesh(me)
    src.free()
    dst.from_mesh(me)
    bpy.data.meshes.remove(me)


def star_pts(r_out, r_in, n=5):
    pts = []
    for k in range(2 * n):
        r = r_out if k % 2 == 0 else r_in
        a = math.pi / 2 + math.pi * k / n
        pts.append(Vector((r * math.cos(a), r * math.sin(a))))
    return pts


def paw_bm():
    bm = bmesh.new()
    ellipsoid_bm((0, 0, -0.004), (0.015, 0.006, 0.012), 6, 3, bm=bm)
    for dx in (-0.016, 0.0, 0.016):
        ellipsoid_bm((dx, 0, 0.014 - abs(dx) * 0.25), (0.006, 0.005, 0.007), 5, 2, bm=bm)
    return bm


def chalk_paw_bm():
    bm = bmesh.new()
    ellipsoid_bm((0, 0, 0), (0.034, 0.006, 0.028), 10, 3, bm=bm)
    for dx, dz in ((-0.034, 0.034), (-0.012, 0.05), (0.012, 0.05), (0.034, 0.034)):
        ellipsoid_bm((dx, 0, dz), (0.011, 0.005, 0.013), 6, 3, bm=bm)
    return bm


def bar(bm, a, b, r):
    tube_bm([a, b], r, 5, bm=bm)


def build_frame():
    bm = bmesh.new()
    rbox_bm((0, FY, BH / 2 - BAR / 2), (BW, FD, BAR), 0.028, 2, bm=bm)
    rbox_bm((0, FY, -BH / 2 + BAR / 2), (BW, FD, BAR), 0.028, 2, bm=bm)
    for s in (-1, 1):
        rbox_bm((s * (BW / 2 - BAR / 2), FY, 0), (BAR, FD - 0.004, BH - 2 * BAR + 0.03), 0.028, 2, bm=bm)
    finish("Frame", bm, "SH_Honey", angle=50)
    bm = rbox_bm((0, SLATE_Y, 0), (BW - 2 * BAR + 0.03, 0.024, BH - 2 * BAR + 0.03), 0.01, 1)
    finish("Slate", bm, "SH_Teal", angle=50)


def build_walnut():
    bm = bmesh.new()
    rbox_bm((0, RAIL_Y + 0.004, RAIL_Z), (BW - 2 * BAR + 0.02, 0.036, 0.055), 0.016, 1, bm=bm)
    prof = [(0.0, 0.0), (0.031, 0.0), (0.032, 0.014), (0.02, 0.026), (0.0, 0.028)]
    for s in (-1, 1):
        for sz in (-1, 1):
            m = Matrix.Translation((s * (BW / 2 - BAR / 2), FRONT + 0.004, sz * (BH / 2 - BAR / 2))) @ \
                Matrix.Rotation(math.pi / 2, 4, "X")
            lathe_bm(prof, 8, bm=bm, matrix=m)
    ty = FRONT - 0.018
    tz = -BH / 2 + BAR + 0.004
    rbox_bm((0, ty + 0.006, tz - 0.016), (0.64, 0.056, 0.034), 0.014, 1, bm=bm)
    rbox_bm((0, ty - 0.02, tz + 0.006), (0.64, 0.018, 0.03), 0.008, 1, bm=bm)
    hw, hh = 0.21, 0.1
    ctrl = [(-hw - 0.05, 0.0), (-hw, 0.025), (-hw * 0.7, hh * 0.72), (-hw * 0.3, hh * 0.97), (0.0, hh),
            (hw * 0.3, hh * 0.97), (hw * 0.7, hh * 0.72), (hw, 0.025), (hw + 0.05, 0.0)]
    pts = [Vector((p.x, p.y)) for p in catmull([(x, y, 0) for x, y in ctrl], 2)]
    pts = [Vector((-hw - 0.05, -0.04))] + pts + [Vector((hw + 0.05, -0.04))]
    slab(pts, 0.05, lambda u, v, w: (u, FY + 0.004 + w, BH / 2 + v), bev=0.016, bsegs=1, bm=bm)
    finish("Walnut", bm, "SH_Walnut", angle=45)
    return ty, tz


def build_gold():
    bm = bmesh.new()
    for x in HOOK_XS:
        y0 = RAIL_Y - 0.012
        pts = [(x, y0, RAIL_Z), (x, y0 - 0.022, RAIL_Z - 0.004), (x, y0 - 0.038, RAIL_Z - 0.022),
               (x, y0 - 0.036, RAIL_Z - 0.044), (x, y0 - 0.02, RAIL_Z - 0.05)]
        tube_bm([(x, y0 + 0.01, RAIL_Z)] + pts, [0.012, 0.011, 0.01, 0.01, 0.009, 0.008], 5, bm=bm)
    s = 1.2
    bx, by, bz = 0.0, FRONT - 0.03, BH / 2 + 0.05
    prof = [(0.0, 0.0), (0.052, 0.0), (0.056, 0.008), (0.05, 0.016), (0.044, 0.03), (0.036, 0.05),
            (0.026, 0.064), (0.012, 0.072), (0.0, 0.074)]
    prof = [(r * s, z * s) for r, z in prof]
    lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((bx, by, bz - 0.074 * s)))
    ellipsoid_bm((bx, by, bz + 0.012), (0.017, 0.017, 0.017), 6, 3, bm=bm)
    ellipsoid_bm((bx, by, bz - 0.074 * s - 0.008), (0.022, 0.022, 0.02), 6, 3, bm=bm)
    tube_bm([(bx, FY - 0.02, bz + 0.012), (bx, by, bz + 0.012)], 0.011, 5, bm=bm)
    sx, sz = CARD_W * 0.18, RAIL_Z - 0.06 - CARD_H * 0.62
    slab(star_pts(0.038, 0.017), 0.014, lambda u, v, w: (HOOK_XS[SPECIAL] + sx + u, CARD_Y - 0.012 + w, sz + v),
         bev=0.005, bsegs=1, bm=bm)
    finish("Gold", bm, "SH_Gold", angle=55)


def build_cards():
    cards = bmesh.new()
    ink = bmesh.new()
    rots = (-6.0, 4.0, 0.0, -3.0, 7.0)
    for k, x in enumerate(HOOK_XS):
        top = RAIL_Z - 0.052
        h = CARD_H + (0.02 if k == SPECIAL else 0.0)
        m = Matrix.Translation((x, CARD_Y, top)) @ Matrix.Rotation(math.radians(rots[k]), 4, "Y")
        rbox_bm((0, 0, -h / 2), (CARD_W, 0.014, h), 0.014, 1, bm=cards, matrix=m)
        yi = -0.009
        bar(ink, m @ Vector((-0.012, yi, -0.012)), m @ Vector((0.012, yi, -0.012)), 0.006)
        lines = 1 if k == SPECIAL else 3
        for j in range(lines):
            w = (0.085, 0.07, 0.05)[j]
            x0 = -0.045
            bar(ink, m @ Vector((x0, yi, -0.04 - 0.028 * j)), m @ Vector((x0 + w, yi, -0.04 - 0.028 * j)), 0.0065)
        if k != SPECIAL:
            merge(ink, paw_bm(), m @ Matrix.Translation((0.03, yi, -h + 0.033)))
    finish("Cards", cards, "SH_Parchment", angle=50)
    finish("Ink", ink, "SH_Walnut", angle=60)


def build_chalk(ty, tz):
    bm = bmesh.new()
    zc = tz + 0.026
    tube_bm([(0.1, ty - 0.004, zc), (0.23, ty - 0.004, zc)], 0.016, 6, bm=bm)
    tube_bm([(0.26, ty - 0.002, zc), (0.31, ty - 0.002, zc)], 0.016, 6, bm=bm)
    yc = SLATE_F - 0.004
    merge(bm, chalk_paw_bm(), Matrix.Translation((-0.3, yc, -0.19)) @ Matrix.Rotation(math.radians(12), 4, "Y"))
    for k in range(4):
        x = 0.2 + k * 0.03
        bar(bm, (x, yc, -0.21), (x, yc, -0.135), 0.006)
    bar(bm, (0.18, yc, -0.2), (0.31, yc, -0.145), 0.006)
    finish("Chalk", bm, "SH_Parchment", angle=60)


out, flags = cli()
begin()
build_frame()
ty, tz = build_walnut()
build_gold()
build_cards()
build_chalk(ty, tz)
for o in PARTS:
    print("PART %-8s tris=%d" % (o.name, sum(len(f.vertices) - 2 for f in o.data.polygons)))
ob = join_all("ShopOrderBoard")
report(ob)
export(ob, flags)
if out:
    ob.data.transform(Matrix.Translation((0, 0, LIFT_Z)))
    preview(ob, out, dragon_loc=(1.0, -0.55, 0), target=(0.35, 0.0, 0.85), ortho=2.6)
    render(os.path.join(out, "ShopOrderBoard_cfront.png"), 0, 4, (0, 0, LIFT_Z + 0.04), 1.15)
    render(os.path.join(out, "ShopOrderBoard_c34.png"), 30, 30, (0, 0, LIFT_Z), 1.2)
    contact_sheet(out, ["ShopOrderBoard_cfront.png", "ShopOrderBoard_c34.png"],
                  os.path.join(out, "ShopOrderBoard_close.png"), cols=2)
