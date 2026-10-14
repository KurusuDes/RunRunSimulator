import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

MED_Y = -0.175
CHILD = (0.0, 1.0, 0.16, 0.2)
PARENTS = [(-0.6, 1.5, 0.145, 0.175), (0.6, 1.5, 0.145, 0.175)]
GRANDS = [(-0.88, 2.02, 0.125, 0.152), (-0.32, 2.27, 0.125, 0.152), (0.32, 2.27, 0.125, 0.152),
          (0.88, 2.02, 0.125, 0.152)]


def add(dst, src):
    me = bpy.data.meshes.new("tmp")
    src.to_mesh(me)
    src.free()
    dst.from_mesh(me)
    bpy.data.meshes.remove(me)
    return dst


def oval_ring(c, a, b, r, segs=16, sides=5, bm=None):
    bm = bm or bmesh.new()
    c = Vector(c)
    Y = Vector((0, 1, 0))
    rings = []
    for k in range(segs):
        t = 2 * math.pi * k / segs
        p = c + Vector((a * math.cos(t), 0, b * math.sin(t)))
        n = Vector((b * math.cos(t), 0, a * math.sin(t))).normalized()
        rings.append([bm.verts.new(p + n * math.cos(2 * math.pi * j / sides) * r + Y * math.sin(2 * math.pi * j / sides) * r)
                      for j in range(sides)])
    faces = []
    for k in range(segs):
        A, B = rings[k], rings[(k + 1) % segs]
        for j in range(sides):
            faces.append(bm.faces.new((A[j], A[(j + 1) % sides], B[(j + 1) % sides], B[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def monchi_badge(cx, cy, cz, s, gold, plum, shoulders=True):
    hz = cz - 0.05 * s
    ellipsoid_bm((cx, cy, hz), (s, 0.022, s * 0.86), 8, 5, bm=gold)
    if shoulders:
        ellipsoid_bm((cx, cy + 0.006, hz - 1.05 * s), (s * 0.95, 0.02, s * 0.42), 8, 4, bm=gold)
    for sx in (-1, 1):
        tube_bm([(cx + sx * 0.5 * s, cy, hz + 0.6 * s), (cx + sx * 0.82 * s, cy, hz + 0.9 * s),
                 (cx + sx * 0.88 * s, cy, hz + 1.25 * s)], [0.2 * s, 0.13 * s, 0.04 * s], 5, bm=gold)
        if shoulders:
            ellipsoid_bm((cx + sx * 0.36 * s, cy - 0.02, hz + 0.02 * s), (0.15 * s, 0.012, 0.19 * s), 5, 3, bm=plum)


def medallion(m, gold, plum, frame, my=MED_Y):
    x, z, a, b = m
    oval_ring((x, my, z), a, b, 0.034, 14, 5, bm=frame)
    ellipsoid_bm((x, my + 0.012, z), (a, 0.034, b), 10, 4, bm=plum)
    big = a > 0.14
    s = a * (0.5 if big else 0.56)
    monchi_badge(x, my - 0.02, z - (0.1 if big else 0.2) * b, s, gold, plum, big)


def clump(cx, cy, cz, rx, ry, rz, seed, leaf, moss, puffs=3):
    ellipsoid_bm((cx, cy, cz), (rx, ry, rz), 12 if puffs > 2 else 10, 6 if puffs > 2 else 5, bm=leaf)
    for k in range(puffs):
        a = math.radians(-60 + 360 / puffs * k + 25 * math.sin(seed * 2.1 + k))
        px = cx + math.cos(a) * rx * 0.86
        pz = cz + math.sin(a) * rz * 0.8
        rr = 0.48 + 0.08 * math.sin(seed + k * 1.7)
        tgt = moss if math.sin(a) < -0.2 else leaf
        ellipsoid_bm((px, cy + 0.03, pz), (rx * rr, ry * 0.8, rz * rr), 7, 4, bm=tgt)


def build_base():
    bm = soft_box((0, 0, 0.075), (1.32, 0.48, 0.15), 0.14, 0.045, seg=2, Rb=0.015)
    finish("Plinth", bm, "SH_Walnut", angle=50)
    bm = ellipsoid_bm((0, 0.0, 0.14), (0.5, 0.2, 0.075), 12, 5)
    finish("Mound", bm, "SH_Moss", angle=80)
    bm = rbox_bm((0, -0.235, 0.075), (0.42, 0.03, 0.08), 0.014, 1)
    finish("Plaque", bm, "SH_Gold", angle=50)


def build_wood():
    bm = bmesh.new()
    trunk = catmull([(0, 0, 0.1), (0.03, 0.0, 0.6), (-0.03, 0.01, 1.15), (0.01, 0.03, 1.6), (0, 0.06, 2.0)], 3)
    n = len(trunk)
    tube_bm(trunk, [0.17 - 0.04 * (i / (n - 1)) for i in range(n)], 8, bm=bm)
    for ph in (0.0, math.pi):
        pts = []
        N = 12
        for i in range(N + 1):
            t = i / N
            z = 0.1 + 1.45 * t
            a = ph + 2 * math.pi * 0.9 * t
            off = 0.085 * (1 - t ** 2)
            base = Vector((0.03 * math.sin(t * 3.0), 0.01 * t, z))
            pts.append(base + Vector((math.cos(a) * off, math.sin(a) * off * 0.7, 0)))
        tube_bm(pts, [0.135 - 0.03 * (i / N) for i in range(N + 1)], 7, bm=bm)
    for ang, L in ((-150, 0.45), (-110, 0.36), (-35, 0.42), (25, 0.38), (160, 0.44), (95, 0.3)):
        a = math.radians(ang)
        d = Vector((math.cos(a), math.sin(a) * 0.45, 0))
        p0 = Vector((0, 0, 0.32))
        pts = [p0, p0 + d * 0.16 + Vector((0, 0, -0.1)), p0 + d * L * 0.8 + Vector((0, 0, -0.165)),
               p0 + d * L + Vector((0, 0, -0.18))]
        tube_bm(pts, [0.11, 0.085, 0.055, 0.032], 6, bm=bm)
    branches = [
        [(0.0, 0.02, 1.2), (-0.3, 0.04, 1.32), (-0.5, 0.06, 1.45), (-0.6, 0.08, 1.5)],
        [(0.0, 0.02, 1.2), (0.3, 0.04, 1.32), (0.5, 0.06, 1.45), (0.6, 0.08, 1.5)],
        [(-0.42, 0.05, 1.4), (-0.66, 0.06, 1.62), (-0.82, 0.08, 1.88), (-0.88, 0.1, 2.02)],
        [(0.42, 0.05, 1.4), (0.66, 0.06, 1.62), (0.82, 0.08, 1.88), (0.88, 0.1, 2.02)],
        [(0.0, 0.04, 1.82), (-0.16, 0.06, 2.0), (-0.27, 0.08, 2.18), (-0.32, 0.1, 2.27)],
        [(0.0, 0.04, 1.82), (0.16, 0.06, 2.0), (0.27, 0.08, 2.18), (0.32, 0.1, 2.27)],
    ]
    for br in branches:
        pts = catmull(br, 2)
        n = len(pts)
        tube_bm(pts, [0.1 - 0.035 * (i / (n - 1)) for i in range(n)], 6, bm=bm)
    finish("Wood", bm, "SH_Walnut", angle=50)


def build_crown(leaf, moss):
    for i, (x, z, a, b) in enumerate(PARENTS + GRANDS):
        clump(x, 0.03, z + 0.02, a + 0.15, 0.21, b + 0.11, i, leaf, moss)
    clump(-0.6, 0.08, 1.98, 0.24, 0.17, 0.22, 7, leaf, moss, 0)
    clump(0.6, 0.08, 1.98, 0.24, 0.17, 0.22, 8, leaf, moss, 0)
    clump(0.0, 0.08, 2.08, 0.24, 0.17, 0.24, 9, leaf, moss, 0)


def heart_pts(sc):
    pts = []
    for k in range(20):
        t = 2 * math.pi * k / 20
        pts.append(Vector((16 * math.sin(t) ** 3, 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t)
                           - math.cos(4 * t))) * sc)
    return pts


def heart(cx, cy, cz, sc, bm):
    pts = heart_pts(sc)
    A = [bm.verts.new((cx + p.x, cy + 0.015, cz + p.y)) for p in pts]
    B = [bm.verts.new((cx + p.x * 0.85, cy - 0.015, cz + p.y * 0.85 + sc)) for p in pts]
    n = len(pts)
    fs = [bm.faces.new(list(reversed(A))), bm.faces.new(B)]
    for k in range(n):
        fs.append(bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bmesh.ops.triangulate(bm, faces=[f for f in fs if len(f.verts) > 4], quad_method="BEAUTY", ngon_method="BEAUTY")


out, flags = cli()
begin()
build_base()
build_wood()
leaf, moss = bmesh.new(), bmesh.new()
build_crown(leaf, moss)
finish("Leaves", leaf, "SH_Leaf", angle=None)
finish("Moss", moss, "SH_Moss", angle=None)
gold, plum, frame = bmesh.new(), bmesh.new(), bmesh.new()
medallion(CHILD, gold, plum, frame, -0.215)
for m in PARENTS + GRANDS:
    medallion(m, gold, plum, frame)
heart(0.0, -0.19, 0.6, 0.0045, frame)
finish("Frames", frame, "SH_Gold", angle=70)
finish("Badges", gold, "SH_Gold", angle=None)
finish("Velvet", plum, "SH_Plum", angle=None)
for o in PARTS:
    print("PART %-8s tris=%d" % (o.name, sum(len(f.vertices) - 2 for f in o.data.polygons)))
ob = join_all("ShopFamilyTree")
report(ob)
export(ob, flags)
if out:
    preview(ob, out, dragon_loc=(1.55, -0.45, 0))
    render(os.path.join(out, "ShopFamilyTree_cfront.png"), 0, 6, (0, 0, 1.75), 1.7)
    render(os.path.join(out, "ShopFamilyTree_c34.png"), 30, 35, (0, 0, 1.6), 2.0)
    contact_sheet(out, ["ShopFamilyTree_cfront.png", "ShopFamilyTree_c34.png"], os.path.join(out, "ShopFamilyTree_close.png"), cols=2)
