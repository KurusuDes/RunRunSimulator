import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

ACC = "SH_Sky"


def front_matrix(x, y, z, rz=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ M


def fin(name, bm, mat, angle=50.0):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


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
    return bm


def tri_ngons(bm):
    big = [f for f in bm.faces if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


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


def star_outline(R, ri=0.46, tip=0.13, inner=0.05, segs=2):
    c = []
    for k in range(10):
        a = math.pi / 2 + math.pi * k / 5
        rr = R if k % 2 == 0 else R * ri
        c.append((rr * math.cos(a), rr * math.sin(a), R * (tip if k % 2 == 0 else inner)))
    return [(p.x, p.y) for p in fillet(c, segs)]


def cloud_top(w, bumps, n=28):
    pts = []
    for k in range(n + 1):
        x = w - 2 * w * k / n
        z = max(zc + math.sqrt(max(0.0, r * r - (x - c) ** 2)) for c, zc, r in bumps)
        pts.append(Vector((x, z)))
    return pts


BW = 0.64
BD = 0.4
Z0 = 0.055
BH = 0.36
TOP = Z0 + BH
LW = 0.68
LD = 0.44
LH = 0.055
OPEN = -28.0


def lid_matrix():
    return Matrix.Translation((0, BD / 2 + 0.01, TOP + 0.005)) @ Matrix.Rotation(math.radians(OPEN), 4, "X")


def merge_into(dst, src):
    me = bpy.data.meshes.new("tmp")
    src.to_mesh(me)
    src.free()
    dst.from_mesh(me)
    bpy.data.meshes.remove(me)


def build_body():
    bm = soft_box((0, 0, Z0 + BH / 2), (BW, BD, BH), 0.05, 0.02, seg=2, Rb=0.012)
    fin("Body", bm, "SH_Oak", angle=50)
    bm = bmesh.new()
    for z, h in ((Z0 + 0.03, 0.055), (TOP - 0.03, 0.055)):
        soft_box((0, 0, z), (BW + 0.024, BD + 0.024, h), 0.06, 0.018, seg=2, Rb=0.012, bm=bm)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tube_bm([(sx * (BW / 2 - 0.005), sy * (BD / 2 - 0.005), Z0 + 0.01), (sx * (BW / 2 - 0.005), sy * (BD / 2 - 0.005), TOP - 0.01)],
                    0.032, 6, bm=bm)
    inner = loft(rbox_rings(BW - 0.08, BD - 0.08, 0.012, 0.03, 0.005, seg=1, z0=TOP - 0.006), 2)
    merge_into(bm, inner)
    fin("Bands", bm, "SH_Walnut", angle=50)
    bm = bmesh.new()
    prof = [(0.0, 0.0), (0.04, 0.0), (0.05, 0.02), (0.045, 0.045), (0.03, Z0 + 0.02), (0.0, Z0 + 0.02)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            lathe_bm(prof, 8, bm=bm, matrix=Matrix.Translation((sx * (BW / 2 - 0.06), sy * (BD / 2 - 0.06), 0)))
    for sx in (-1, 1):
        x = sx * (BW / 2 + 0.008)
        pts = [(x, -0.08, TOP - 0.1), (x + sx * 0.035, -0.07, TOP - 0.1), (x + sx * 0.05, 0.0, TOP - 0.1),
               (x + sx * 0.035, 0.07, TOP - 0.1), (x, 0.08, TOP - 0.1)]
        tube_bm(catmull(pts, 2), 0.019, 6, bm=bm)
    fin("Feet", bm, "SH_Walnut", angle=60)


def build_front():
    w = 0.21
    bumps = ((-0.12, 0.05, 0.075), (0.0, 0.065, 0.085), (0.12, 0.05, 0.075))
    top = cloud_top(w, bumps, 16)
    bot = fillet([(-w + 0.0, 0.02, 0.0), (-w, -0.09, 0.045), (w, -0.09, 0.045), (w, 0.02, 0.0)], 3)
    outline = [Vector((p.x, p.y)) for p in bot[1:-1]] + top
    pts = []
    for p in outline:
        if not pts or (p - pts[-1]).length > 1e-4:
            pts.append(p)
    zc = 0.205
    m = front_matrix(0, -BD / 2 + 0.006, zc)
    bm = badge_bm([(p.x, p.y) for p in pts], 0.026, 0.01, matrix=m)
    fin("Cloud", bm, ACC, angle=60)
    m = front_matrix(0, -BD / 2 - 0.016, zc + 0.01)
    bm = badge_bm(star_outline(0.075), 0.028, 0.009, matrix=m)
    fin("Star", bm, "SH_Gold", angle=60)


def build_lid():
    bm = loft(rbox_rings(LW, LD, LH, 0.05, 0.026, seg=3, Rb=0.01, segb=1, cy=-LD / 2), 3)
    xf(bm, lid_matrix())
    fin("Lid", bm, "SH_Walnut", angle=50)
    bm = soft_box((0, -LD / 2, LH + 0.03), (LW - 0.07, LD - 0.07, 0.07), 0.07, 0.035, seg=2, Rb=0.01)
    for v in bm.verts:
        r = math.hypot(v.co.x / 0.2, (v.co.y + LD / 2) / 0.12)
        if v.co.z > LH + 0.05:
            v.co.z -= 0.014 * math.exp(-r * r * 3)
    xf(bm, lid_matrix())
    fin("LidPad", bm, ACC, angle=70)
    bm = ellipsoid_bm((0, -LD / 2, LH + 0.065), (0.022, 0.022, 0.014), 8, 4)
    xf(bm, lid_matrix())
    fin("LidButton", bm, "SH_Gold", angle=None)


def build_toys():
    c = Vector((0.14, -0.01, TOP + 0.05))
    r = 0.095
    bm = ellipsoid_bm(c, (r, r, r), 12, 7)
    ob = fin("Ball", bm, "SH_Gold", angle=None)
    ob.data.materials.append(MATS["SH_Cream"])
    for p in ob.data.polygons:
        q = p.center - c
        a = math.atan2(q.y, q.x)
        if int(((a + math.pi) / (2 * math.pi)) * 6) % 2 == 1 and abs(q.z) < r * 0.85:
            p.material_index = 1
    bm = rbox_bm((0, 0, 0), (0.11, 0.11, 0.11), 0.025, 2)
    xf(bm, Matrix.Translation((-0.14, -0.03, TOP + 0.02)) @ Matrix.Rotation(math.radians(24), 4, "Z")
       @ Matrix.Rotation(math.radians(14), 4, "X"))
    fin("Block", bm, "SH_Cream", angle=50)
    bm = torus_bm(0.065, 0.022, 14, 6, matrix=Matrix.Translation((-0.02, -BD / 2 + 0.005, TOP - 0.01))
                  @ Matrix.Rotation(math.radians(-14), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "Y")
                  @ Matrix.Rotation(math.radians(0), 4, "X"))
    fin("Ring", bm, ACC, angle=None)


out, flags = cli()
begin()
build_body()
build_front()
build_lid()
build_toys()
ob = join_all("ShopToyChest")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.0, 0.5, 0), dragon_rot=30.0, target=(-0.3, 0.05, 0.36), ortho=1.95)
