import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

W = 1.40
D = 0.48
POST = 0.1
BASE_H = 0.1
CAB_Z = 0.6
SHELF2_Z = 1.05
TOP_Z = 1.5
HX = W / 2 - POST / 2
FY = -D / 2 + POST / 2
BY = D / 2 - POST / 2


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
    bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


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


def star_bm(cx, y, cz, R, r, depth, bm=None):
    bm = bm or bmesh.new()
    prof = [(1.0, 0.0), (1.0, depth * 0.55), (0.86, depth * 0.9), (0.62, depth)]
    rings = []
    for s, d in prof:
        ring = []
        for k in range(10):
            a = math.pi / 2 + math.pi * k / 5
            rad = (R if k % 2 == 0 else r) * s
            ring.append(bm.verts.new((cx + rad * math.cos(a), y - d, cz + rad * math.sin(a))))
        rings.append(ring)
    faces = []
    for A, B in zip(rings, rings[1:]):
        for k in range(10):
            faces.append(bm.faces.new((A[k], A[(k + 1) % 10], B[(k + 1) % 10], B[k])))
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def build_carcass():
    bm = soft_box((0, 0, BASE_H / 2), (W, D, BASE_H), 0.06, 0.03, seg=2, Rb=0.01)
    soft_box((0, -0.005, TOP_Z + 0.045), (W + 0.04, D + 0.03, 0.09), 0.07, 0.035, seg=2, Rb=0.02, bm=bm)
    for sx in (-1, 1):
        x0, z0, L = sx * (W / 2 - POST + 0.01), TOP_Z + 0.01, 0.15
        pts = [Vector((x0, z0))] + [Vector((x0 - sx * L + sx * L * math.cos(math.radians(a)), z0 - L + L * math.sin(math.radians(a))))
                                    for a in ((0, 18, 36, 54, 72, 90) if sx > 0 else (90, 72, 54, 36, 18, 0))]
        slab(pts, 0.05, lambda u, v, w: (u, FY + w, v), bev=0.012, bm=bm)
    for x in (-HX, HX):
        for y in (FY, BY):
            rbox_bm((x, y, (BASE_H + TOP_Z) / 2), (POST, POST, TOP_Z - BASE_H + 0.02), 0.035, 2, bm=bm)
    for z in (CAB_Z, SHELF2_Z):
        rbox_bm((0, -0.005, z - 0.025), (W - 2 * POST + 0.02, D - 0.04, 0.05), 0.018, 2, bm=bm)
        rbox_bm((0, FY - 0.005, z - 0.015), (W - 2 * POST + 0.02, 0.06, 0.07), 0.026, 2, bm=bm)
    finish("Frame", bm, "SH_Walnut", angle=50)
    bm = bmesh.new()
    for x in (-HX, HX):
        ellipsoid_bm((x, FY, 0.045), (0.07, 0.07, 0.045), 8, 4, bm=bm)
    finish("Feet", bm, "SH_Walnut", angle=70)
    bm = bmesh.new()
    iw = W - 2 * POST + 0.02
    rbox_bm((0, 0.0, (BASE_H + CAB_Z) / 2), (iw, D - 0.06, CAB_Z - BASE_H), 0.02, 1, bm=bm)
    for x in (-HX, HX):
        rbox_bm((x, 0.0, (BASE_H + CAB_Z) / 2), (0.06, D - POST * 2 + 0.02, CAB_Z - BASE_H), 0.015, 1, bm=bm)
    finish("Cabinet", bm, "SH_Honey", angle=50)
    bm = bmesh.new()
    dw = (iw - 0.06) / 2
    for s in (-1, 1):
        rbox_bm((s * (dw / 2 + 0.015), FY - 0.012, (BASE_H + CAB_Z) / 2 - 0.005), (dw, 0.04, CAB_Z - BASE_H - 0.1), 0.03, 2, bm=bm)
    finish("Doors", bm, "SH_Honey", angle=50)
    bm = bmesh.new()
    for s in (-1, 1):
        rbox_bm((s * (dw / 2 + 0.015), FY - 0.028, (BASE_H + CAB_Z) / 2 - 0.005), (dw - 0.11, 0.02, CAB_Z - BASE_H - 0.2), 0.02, 1, bm=bm)
    finish("DoorInsets", bm, "SH_Plum", angle=50)
    bm = bmesh.new()
    for s in (-1, 1):
        ellipsoid_bm((s * 0.075, FY - 0.05, (BASE_H + CAB_Z) / 2 + 0.03), (0.045, 0.035, 0.045), 8, 5, bm=bm)
    finish("Knobs", bm, "SH_Gold", angle=80)
    bm = rbox_bm((0, BY - 0.01, (CAB_Z + TOP_Z) / 2), (iw, 0.03, TOP_Z - CAB_Z + 0.02), 0.012, 1)
    finish("Back", bm, "SH_Plum", angle=50)
    bm = rbox_bm((0, BY + 0.02, (BASE_H + TOP_Z) / 2), (iw + 0.02, 0.04, TOP_Z - BASE_H), 0.015, 1)
    finish("BackBoard", bm, "SH_Honey", angle=50)
    bm = bmesh.new()
    for x in (-HX, HX):
        rbox_bm((x, 0.0, (CAB_Z + TOP_Z) / 2), (0.04, D - 2 * POST + 0.02, TOP_Z - CAB_Z), 0.012, 1, bm=bm)
    finish("Glass", bm, "SH_Glass", angle=50)
    bm = bmesh.new()
    for x in (-HX, HX):
        rbox_bm((x, 0.0, SHELF2_Z), (0.07, D - 2 * POST + 0.02, 0.06), 0.02, 2, bm=bm)
    finish("Mullions", bm, "SH_Walnut", angle=50)


def build_crest():
    hw, hh = 0.42, 0.21
    ctrl = [(-hw - 0.1, 0.0), (-hw, 0.05), (-hw * 0.7, hh * 0.72), (-hw * 0.3, hh * 0.97), (0.0, hh),
            (hw * 0.3, hh * 0.97), (hw * 0.7, hh * 0.72), (hw, 0.05), (hw + 0.1, 0.0)]
    pts = [Vector((p.x, p.y)) for p in catmull([(x, y, 0) for x, y in ctrl], 3)]
    pts = [Vector((-hw - 0.1, -0.03))] + pts + [Vector((hw + 0.1, -0.03))]
    yc = 0.08
    z0 = TOP_Z + 0.09
    bm = slab(pts, 0.07, lambda u, v, w: (u, yc + w, z0 + v), bev=0.022)
    finish("Crest", bm, "SH_Walnut", angle=45)
    mz = z0 + 0.1
    my = yc - 0.05
    finish("CrestRing", oval_ring((0, my, mz), 0.09, 0.1, 0.028, 16, 5), "SH_Gold", angle=70)
    finish("CrestVelvet", ellipsoid_bm((0, my + 0.01, mz), (0.09, 0.028, 0.1), 10, 4), "SH_Plum", angle=None)
    finish("CrestStar", star_bm(0, my - 0.012, mz, 0.07, 0.033, 0.03), "SH_Gold", angle=70)


def cup(bm, x, y, z0, h, r):
    prof = [(0.0, z0), (r * 0.75, z0), (r * 0.78, z0 + 0.03), (r * 0.6, z0 + 0.05), (r * 0.25, z0 + 0.07),
            (r * 0.2, z0 + h * 0.35), (r * 0.35, z0 + h * 0.45), (r * 0.8, z0 + h * 0.6), (r, z0 + h * 0.85),
            (r * 1.06, z0 + h), (r * 0.9, z0 + h), (r * 0.82, z0 + h * 0.9), (0.0, z0 + h * 0.86)]
    lathe_bm(prof, 14, bm=bm, matrix=Matrix.Translation((x, y, 0)))
    for s in (-1, 1):
        pts = catmull([(x + s * r * 0.9, y, z0 + h * 0.85), (x + s * r * 1.45, y, z0 + h * 0.8),
                       (x + s * r * 1.4, y, z0 + h * 0.6), (x + s * r * 0.75, y, z0 + h * 0.55)], 2)
        tube_bm(pts, r * 0.16, 5, bm=bm)


def plinth(bm, x, y, z0, w, h):
    soft_box((x, y, z0 + h / 2), (w, w * 0.8, h), 0.03, 0.014, seg=2, bm=bm)


def medal(gold, plum, x, y, z, rot):
    M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rot), 4, "Y")
    rib = bmesh.new()
    for s in (-1, 1):
        rbox_bm((s * 0.035, 0, 0.11), (0.06, 0.024, 0.2), 0.01, 1, bm=rib,
                matrix=Matrix.Rotation(math.radians(-s * 18), 4, "Y"))
    xf(rib, M)
    me = bpy.data.meshes.new("tmp")
    rib.to_mesh(me)
    rib.free()
    plum.from_mesh(me)
    bpy.data.meshes.remove(me)
    prof = [(0.0, 0.0), (0.075, 0.0), (0.08, 0.012), (0.07, 0.024), (0.0, 0.026)]
    lathe_bm(prof, 14, bm=gold, matrix=M @ Matrix.Translation((0, -0.012, -0.02)) @ Matrix.Rotation(math.pi / 2, 4, "X"))


def build_trophies():
    gold, plum, wood = bmesh.new(), bmesh.new(), bmesh.new()
    z1 = CAB_Z
    plinth(wood, 0.0, 0.0, z1, 0.22, 0.07)
    cup(gold, 0.0, 0.0, z1 + 0.065, 0.34, 0.12)
    plinth(wood, -0.36, 0.02, z1, 0.17, 0.05)
    lathe_bm([(0.0, z1 + 0.045), (0.04, z1 + 0.045), (0.034, z1 + 0.17), (0.0, z1 + 0.17)], 8, bm=gold,
             matrix=Matrix.Translation((-0.36, 0.02, 0)))
    star_bm(-0.36, 0.045, z1 + 0.27, 0.12, 0.056, 0.055, bm=gold)
    medal(gold, plum, 0.36, 0.155, z1 + 0.18, 8)
    z2 = SHELF2_Z
    plinth(wood, -0.32, 0.0, z2, 0.17, 0.05)
    cup(gold, -0.32, 0.0, z2 + 0.045, 0.25, 0.085)
    plinth(wood, 0.32, 0.0, z2, 0.17, 0.05)
    cup(gold, 0.32, 0.0, z2 + 0.045, 0.28, 0.09)
    medal(gold, plum, 0.0, 0.155, z2 + 0.17, -6)
    finish("TrophyBases", wood, "SH_Walnut", angle=50)
    finish("Trophies", gold, "SH_Gold", angle=50)
    finish("Ribbons", plum, "SH_Plum", angle=50)


out, flags = cli()
begin()
build_carcass()
build_crest()
build_trophies()
for o in PARTS:
    print("PART %-11s tris=%d" % (o.name, sum(len(f.vertices) - 2 for f in o.data.polygons)))
ob = join_all("ShopTrophyCase")
report(ob)
export(ob, flags)
if out:
    preview(ob, out, dragon_loc=(1.5, -0.45, 0))
