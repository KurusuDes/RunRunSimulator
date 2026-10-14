import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

R = 0.30
TOP = 0.30
SEG = 24


def fillet(corners, segs=3):
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


def build():
    base = [(0.0, 0.0), (R - 0.03, 0.0), (R - 0.008, 0.012), (R, 0.04), (R - 0.008, 0.066), (R - 0.03, 0.08),
            (0.24, 0.085), (0.0, 0.085)]
    finish("Base", lathe_bm(base, SEG), "SH_WoodDark", angle=55)
    body = [(0.0, 0.07), (0.236, 0.07), (0.246, 0.11), (0.25, 0.155), (0.246, 0.2), (0.236, 0.24), (0.0, 0.24)]
    finish("Body", lathe_bm(body, SEG), "SH_Wood", angle=55)
    finish("Rim", torus_bm(0.262, 0.038, SEG, 6, matrix=Matrix.Translation((0, 0, 0.258))), "SH_WoodDark", angle=70)
    felt = [(0.236, 0.235), (0.24, TOP - 0.04), (0.228, TOP - 0.018), (0.2, TOP - 0.005), (0.16, TOP), (0.0, TOP)]
    finish("Felt", lathe_bm(felt, SEG), "SH_Mint", angle=70)
    bm = bmesh.new()
    for k in range(SEG // 2):
        a = 2 * math.pi * (k + 0.5) / (SEG // 2)
        if abs(math.atan2(math.sin(a + math.pi / 2), math.cos(a + math.pi / 2))) < 0.6:
            continue
        p0 = Vector((math.cos(a) * 0.236, math.sin(a) * 0.236, 0.095))
        p1 = Vector((math.cos(a) * 0.236, math.sin(a) * 0.236, 0.215))
        mid = Vector((math.cos(a) * 0.247, math.sin(a) * 0.247, 0.155))
        tube_bm([p0, mid, p1], [0.014, 0.016, 0.014], 5, bm=bm)
    finish("Ribs", bm, "SH_WoodDark", angle=70)
    ro, ri = 0.088, 0.042
    corners = []
    for k in range(10):
        a = math.pi / 2 + math.pi * k / 5
        rr = ro if k % 2 == 0 else ri
        corners.append((rr * math.cos(a), rr * math.sin(a), 0.014 if k % 2 == 0 else 0.008))
    pts = fillet(corners, 2)
    yc = -0.238
    zc = 0.155
    bm = slab(pts, 0.036, lambda u, v, w: (u, yc + w, zc + v), bev=0.01)
    finish("Star", bm, "SH_Straw", angle=50)


out, flags = cli()
begin()
build()
for o in PARTS:
    print("PART %-8s tris=%d" % (o.name, sum(len(f.vertices) - 2 for f in o.data.polygons)))
ob = join_all("ShopDecorPedestal")
report(ob)
print("DECO_TOP z=%.3f" % TOP)
export(ob, flags)
if out:
    if "deco" in flags:
        bm = ellipsoid_bm((0, 0, TOP + 0.12), (0.12, 0.12, 0.12), 12, 7)
        me = bpy.data.meshes.new("TestDeco")
        bm.to_mesh(me)
        bm.free()
        m = bpy.data.materials.new("TestDeco")
        m.diffuse_color = (0.75, 0.6, 0.9, 1)
        me.materials.append(m)
        bpy.context.scene.collection.objects.link(bpy.data.objects.new("TestDeco", me))
    preview(ob, out, dragon_loc=(1.05, -0.25, 0), ortho=2.3, target=(0.45, 0, 0.4))
