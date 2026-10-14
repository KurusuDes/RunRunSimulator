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


STEM = [(0.0, 0.045), (0.094, 0.045), (0.1, 0.07), (0.092, 0.12), (0.08, 0.2), (0.071, 0.28), (0.068, 0.35),
        (0.0, 0.35)]
CAP = [(0.1, 0.333), (0.142, 0.336), (0.162, 0.354), (0.165, 0.385), (0.157, 0.43), (0.136, 0.485), (0.1, 0.535),
       (0.055, 0.568), (0.0, 0.578)]


def stem_r(z):
    for (r0, z0), (r1, z1) in zip(STEM[1:-1], STEM[2:-1]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return STEM[-2][0]


def build_base():
    prof = [(0.0, 0.0), (0.13, 0.0), (0.146, 0.016), (0.144, 0.04), (0.124, 0.06), (0.0, 0.06)]
    fin("Base", lathe_bm(prof, 20), "SH_Oak", angle=55)
    fin("Stem", lathe_bm(STEM, 16), "SH_Cream", angle=70)


def build_cap():
    gills = [(0.0, 0.375), (0.045, 0.322), (0.135, 0.335), (0.15, 0.348), (0.0, 0.37)]
    fin("Gills", lathe_bm(gills, 20), "SH_Lamp", angle=60)
    fin("Cap", lathe_bm(CAP, 20), ACC, angle=70)
    bm = bmesh.new()
    spots = ((-110, 3), (-35, 3), (40, 3), (115, 3), (185, 3), (-70, 5), (5, 5), (150, 5), (80, 6))
    for ang, idx in spots:
        a = math.radians(ang)
        r0, z0 = CAP[idx]
        r1, z1 = CAP[idx + 1]
        r, z = (r0 + r1) / 2, (z0 + z1) / 2
        t = Vector((r1 - r0, z1 - z0)).normalized()
        nrm2 = Vector((t.y, -t.x))
        n = Vector((math.cos(a) * nrm2.x, math.sin(a) * nrm2.x, nrm2.y)).normalized()
        p = Vector((math.cos(a) * r, math.sin(a) * r, z))
        size = {3: 0.04, 5: 0.034, 6: 0.03}[idx]
        sub = ellipsoid_bm((0, 0, 0), (size, size, 0.011), 10, 4)
        rot = n.to_track_quat("Z", "Y").to_matrix().to_4x4()
        xf(sub, Matrix.Translation(p - n * 0.003) @ rot)
        me = bpy.data.meshes.new("tmp")
        sub.to_mesh(me)
        sub.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    fin("Spots", bm, "SH_Cream", angle=None)


def build_door():
    z0 = 0.06
    w, h = 0.074, 0.13
    outline = fillet([(-w / 2, 0.0, 0.006), (w / 2, 0.0, 0.006), (w / 2, h, w / 2 - 0.001), (-w / 2, h, w / 2 - 0.001)], 4)
    pts = []
    for p in outline:
        if not pts or (p - pts[-1]).length > 1e-4:
            pts.append(p)
    if (pts[-1] - pts[0]).length < 1e-4:
        pts.pop()
    y0 = -stem_r(z0 + 0.05) + 0.012
    bm = badge_bm([(p.x, p.y) for p in pts], 0.028, 0.008, matrix=front_matrix(0, y0, z0))
    fin("Door", bm, "SH_Walnut", angle=60)
    bm = ellipsoid_bm((0.019, y0 - 0.03, z0 + 0.06), (0.012, 0.012, 0.012), 8, 4)
    zw = 0.255
    yw = -stem_r(zw) + 0.01
    lathe_bm([(0.0, 0.0), (0.028, 0.0), (0.028, 0.016), (0.0, 0.021)], 12, bm=bm, matrix=front_matrix(0, yw - 0.012, zw))
    fin("Window", bm, "SH_Lamp", angle=60)
    bm = torus_bm(0.033, 0.011, 14, 6, matrix=front_matrix(0, yw - 0.02, zw))
    fin("WindowFrame", bm, "SH_Walnut", angle=None)


out, flags = cli()
begin()
build_base()
build_cap()
build_door()
ob = join_all("ShopNightLamp")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.85, 0.45, 0), dragon_rot=30.0, target=(-0.3, 0.05, 0.42), ortho=1.7)
