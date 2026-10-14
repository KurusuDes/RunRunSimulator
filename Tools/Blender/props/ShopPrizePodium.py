import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

BLOCK_W = 0.85
DEPTH = 0.86
BODY_D = 0.8
PLINTH_H = 0.05
CAP_H = 0.04
BLOCKS = (("1", 0.0, 0.45, 0.14), ("2", -0.85, 0.31, 0.115), ("3", 0.85, 0.19, 0.08))
FONT = os.path.join(ROOT, "Assets", "Feel", "MMTools", "Demos", "MMTween", "Fonts", "Lato", "TTF", "Lato-Black.ttf")


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


def slab_bm(outline, t, bev, steps=2, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = [(0.0, 0.0), (0.0, t - bev)]
    for j in range(1, steps + 1):
        a = math.pi / 2 * j / steps
        rings.append((bev * (1 - math.cos(a)), t - bev + bev * math.sin(a)))
    vr = [[bm.verts.new((x, y, z)) for x, y in offset2d(outline, d)] for d, z in rings]
    n = len(outline)
    for A, B in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    caps = [bm.faces.new(list(reversed(vr[0]))), bm.faces.new(vr[-1])]
    bmesh.ops.triangulate(bm, faces=caps, quad_method="BEAUTY", ngon_method="BEAUTY")
    if matrix is not None:
        xf(bm, matrix, [v for r in vr for v in r])
    return bm


def star_outline(R, r, cx=0.0, cy=0.0):
    return [(cx + (R if k % 2 == 0 else r) * math.cos(math.pi / 2 + math.pi * k / 5),
             cy + (R if k % 2 == 0 else r) * math.sin(math.pi / 2 + math.pi * k / 5)) for k in range(10)]


def rosette_outline(R, n=32, lobes=8, amp=0.09):
    return [(R * (1 + amp * math.cos(lobes * 2 * math.pi * k / n)) * math.cos(2 * math.pi * k / n),
             R * (1 + amp * math.cos(lobes * 2 * math.pi * k / n)) * math.sin(2 * math.pi * k / n)) for k in range(n)]


def circle(R, n=20):
    return [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n)) for k in range(n)]


def text_bm(body, height, depth):
    cu = bpy.data.curves.new("Num", type="FONT")
    cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    cu.body = body
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = 1.0
    cu.extrude = 0.06
    cu.bevel_depth = 0.035
    cu.bevel_resolution = 0
    cu.resolution_u = 1
    ob = bpy.data.objects.new("Num", cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    s = height / (max(ys) - min(ys))
    sz = depth / (max(zs) - min(zs))
    cx, cy, z0 = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, min(zs)
    for v in bm.verts:
        v.co = Vector(((v.co.x - cx) * s, (v.co.y - cy) * s, (v.co.z - z0) * sz))
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0003)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(3), verts=list(bm.verts), edges=list(bm.edges))
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


def build_blocks():
    oak = bmesh.new()
    wal = bmesh.new()
    plum = bmesh.new()
    for _, x, h, _r in BLOCKS:
        rings = rbox_rings(BLOCK_W, DEPTH, PLINTH_H, 0.07, 0.022, seg=2, Rb=0.015, segb=1, cx=x)
        loft(rings, 3, bm=wal)
        rings = rbox_rings(BLOCK_W - 0.04, BODY_D, h - PLINTH_H - 0.01, 0.06, 0.045, seg=2, z0=PLINTH_H - 0.01, cx=x)
        loft(rings, 3, bm=oak)
        rings = rbox_rings(BLOCK_W - 0.01, BODY_D + 0.02, CAP_H, 0.07, 0.018, seg=2, Rb=0.01, segb=1, z0=h - CAP_H, cx=x)
        loft(rings, 3, bm=wal)
        rings = rbox_rings(BLOCK_W - 0.1, BODY_D - 0.08, 0.03, 0.06, 0.014, seg=2, z0=h - 0.018, cx=x)
        loft(rings, 3, bm=plum)
    fin("Bodies", oak, "SH_Oak", angle=50)
    fin("Trim", wal, "SH_Walnut", angle=50)
    fin("Carpets", plum, "SH_Plum", angle=50)


def build_medals():
    plum = bmesh.new()
    gold = bmesh.new()
    nums = bmesh.new()
    yf = -BODY_D / 2 + 0.002
    for label, x, h, R in BLOCKS:
        zc = PLINTH_H + (h - CAP_H - PLINTH_H) * 0.5
        slab_bm(rosette_outline(R), 0.026, 0.01, 1, bm=plum, matrix=face_m(x, yf, zc))
        slab_bm(circle(R * 0.74, 20), 0.032, 0.012, 2, bm=gold, matrix=face_m(x, yf - 0.022, zc))
        t = text_bm(label, R * 0.95, 0.03)
        xf(t, face_m(x, yf - 0.05, zc))
        me = bpy.data.meshes.new("tmp")
        t.to_mesh(me)
        t.free()
        nums.from_mesh(me)
        bpy.data.meshes.remove(me)
    fin("Rosettes", plum, "SH_Plum", angle=30)
    fin("Medals", gold, "SH_Gold", angle=40)
    fin("Numbers", nums, "SH_Walnut", angle=40)
    bm = bmesh.new()
    _, x, h, R = BLOCKS[0]
    zc = PLINTH_H + (h - CAP_H - PLINTH_H) * 0.5
    for sx in (-1, 1):
        slab_bm(star_outline(0.07, 0.033), 0.03, 0.01, 1, bm=bm, matrix=face_m(x + sx * 0.27, -BODY_D / 2 + 0.002, zc + 0.03))
    fin("Stars", bm, "SH_Gold", angle=30)


out, flags = cli()
begin()
build_blocks()
build_medals()
ob = join_all("ShopPrizePodium")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(0.0, 0.05, 0.45), target=(0.0, 0.0, 0.55), ortho=3.4)
