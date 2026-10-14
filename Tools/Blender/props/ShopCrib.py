import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

ACC = "SH_Sky"
PX = 0.45
PY = 0.29
POST_R = 0.042
POST_TOP = 0.6
BASE_Z0 = 0.15
BASE_Z1 = 0.25
RAIL_Z = 0.5
HUB = (0.0, 0.02, 0.84)


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


def build_posts():
    prof = [(0.0, 0.0), (0.048, 0.0), (0.054, 0.025), (0.046, 0.06), (POST_R, 0.09), (POST_R, POST_TOP - 0.06),
            (0.05, POST_TOP - 0.035), (0.046, POST_TOP - 0.01), (0.0, POST_TOP)]
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = POST_TOP + (0.05 if sx < 0 else 0.0)
            p = [(r, z if z < POST_TOP - 0.07 else z + (top - POST_TOP)) for r, z in prof]
            lathe_bm(p, 10, bm=bm, matrix=Matrix.Translation((sx * PX, sy * PY, 0)))
    fin("Posts", bm, "SH_Oak", angle=60)
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = POST_TOP + (0.05 if sx < 0 else 0.0)
            ellipsoid_bm((sx * PX, sy * PY, top + 0.035), (0.055, 0.055, 0.05), 10, 6, bm=bm)
    fin("Finials", bm, "SH_Gold", angle=None)


def build_base():
    bm = rbox_bm((0, 0, (BASE_Z0 + BASE_Z1) / 2), (2 * PX, 2 * PY + 0.02, BASE_Z1 - BASE_Z0), 0.03, 2)
    fin("Base", bm, "SH_Walnut", angle=50)
    bm = soft_box((0, 0, BASE_Z1 + 0.045), (2 * PX - 0.05, 2 * PY - 0.03, 0.1), 0.06, 0.04, seg=3, Rb=0.01)
    fin("Mattress", bm, "SH_Cream", angle=60)
    bm = ellipsoid_bm((-PX + 0.15, 0, BASE_Z1 + 0.12), (0.1, 0.17, 0.05), 12, 6)
    fin("Pillow", bm, "SH_Cream", angle=None)


def build_blanket():
    x0, x1 = -0.13, PX - 0.02
    nu, nv = 10, 9
    top_z = BASE_Z1 + 0.095
    bm = bmesh.new()
    top, bot = [], []
    for j in range(nv):
        rt, rb = [], []
        v = j / (nv - 1)
        y = (v - 0.5) * (2 * PY - 0.05)
        for i in range(nu):
            u = i / (nu - 1)
            x = x0 + (x1 - x0) * u
            edge_y = abs(v - 0.5) * 2
            z = top_z - 0.07 * max(0.0, edge_y - 0.72) / 0.28 + 0.01 * math.sin(u * 9.0 + v * 3)
            rb.append(bm.verts.new((x, y, z)))
            rt.append(bm.verts.new((x, y, z + 0.038)))
        top.append(rt)
        bot.append(rb)
    for j in range(nv - 1):
        for i in range(nu - 1):
            bm.faces.new((top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]))
            bm.faces.new((bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]))
    ring = [(0, i) for i in range(nu)] + [(j, nu - 1) for j in range(1, nv)] + \
           [(nv - 1, i) for i in range(nu - 2, -1, -1)] + [(j, 0) for j in range(nv - 2, 0, -1)]
    for k in range(len(ring)):
        a, b = ring[k], ring[(k + 1) % len(ring)]
        bm.faces.new((bot[a[0]][a[1]], bot[b[0]][b[1]], top[b[0]][b[1]], top[a[0]][a[1]]))
    fin("Blanket", bm, ACC, angle=70)
    bm = bmesh.new()
    pts = [(x0 - 0.01, (v - 0.5) * (2 * PY - 0.05), top_z + 0.035 - 0.07 * max(0.0, abs(v - 0.5) * 2 - 0.72) / 0.28)
           for v in [k / 8 for k in range(9)]]
    tube_bm(pts, 0.032, 8, bm=bm)
    fin("BlanketFold", bm, "SH_Cream", angle=70)


def cloud_top(w, bumps, n=28):
    pts = []
    for k in range(n + 1):
        x = w - 2 * w * k / n
        z = max(zc + math.sqrt(max(0.0, r * r - (x - c) ** 2)) for c, zc, r in bumps)
        pts.append(Vector((x, z)))
    return pts


def build_panels():
    bm = bmesh.new()
    w = PY
    heads = ((-1, ((-0.17, 0.53, 0.12), (0.0, 0.55, 0.15), (0.17, 0.53, 0.12))),
             (1, ((-0.165, 0.47, 0.125), (0.0, 0.49, 0.13), (0.165, 0.47, 0.125))))
    for sx, bumps in heads:
        pts = [Vector((-w, BASE_Z0 + 0.02)), Vector((w, BASE_Z0 + 0.02))] + cloud_top(w, bumps)
        clean = [pts[0]]
        for p in pts[1:]:
            if (p - clean[-1]).length > 1e-4:
                clean.append(p)
        if (clean[-1] - clean[0]).length < 1e-4:
            clean.pop()
        slab(clean, 0.05, lambda u, v, w_, sx=sx: (sx * PX + w_, u, v), bev=0.018, bm=bm)
    fin("Panels", tri_ngons(bm), ACC, angle=45)
    bm = bmesh.new()
    badge_bm(star_outline(0.095), 0.03, 0.009, bm=bm,
             matrix=Matrix.Translation((-PX + 0.02, 0, 0.56)) @ Matrix.Rotation(math.radians(90), 4, "Y")
             @ Matrix.Rotation(math.radians(90), 4, "Z"))
    badge_bm(star_outline(0.095), 0.03, 0.009, bm=bm,
             matrix=Matrix.Translation((PX + 0.02, 0, 0.36)) @ Matrix.Rotation(math.radians(90), 4, "Y")
             @ Matrix.Rotation(math.radians(90), 4, "Z"))
    fin("PanelStars", bm, "SH_Gold", angle=60)


def build_rails():
    bm = bmesh.new()
    for sy in (-1, 1):
        rbox_bm((0, sy * PY, RAIL_Z), (2 * PX, 0.065, 0.055), 0.024, 2, bm=bm)
    fin("TopRails", bm, "SH_Walnut", angle=50)
    bm = bmesh.new()
    n = 6
    for sy in (-1, 1):
        for i in range(n):
            x = -PX + 2 * PX * (i + 1) / (n + 1)
            prof = [(0.018, BASE_Z1 - 0.01), (0.022, BASE_Z1 + 0.04), (0.017, RAIL_Z - 0.08), (0.021, RAIL_Z - 0.01)]
            pts = [(x, sy * PY, z) for r, z in prof]
            tube_bm(pts, [r for r, z in prof], 7, bm=bm)
    fin("Spindles", bm, "SH_Oak", angle=60)


def build_mobile():
    bm = bmesh.new()
    clamp_x = -0.1
    pts = catmull([(clamp_x, PY, RAIL_Z), (clamp_x, PY + 0.01, 0.7), (clamp_x * 0.6, PY - 0.06, 0.86),
                   (clamp_x * 0.2, HUB[1] + 0.12, HUB[2] + 0.04), (HUB[0], HUB[1], HUB[2] + 0.02)], 4)
    tube_bm(pts, 0.022, 8, bm=bm)
    rbox_bm((clamp_x, PY, RAIL_Z + 0.01), (0.08, 0.09, 0.08), 0.025, 2, bm=bm)
    arms = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        d = Vector((math.cos(a), math.sin(a), 0))
        h = Vector(HUB)
        p = [h, h + d * 0.08 + UP * 0.01, h + d * 0.15 - UP * 0.005, h + d * 0.17 - UP * 0.03]
        tube_bm(p, [0.015, 0.014, 0.013, 0.012], 6, bm=bm)
        arms.append((h + d * 0.17 - UP * 0.03, a))
    fin("MobileArm", bm, "SH_Walnut", angle=60)
    hub = ellipsoid_bm((HUB[0], HUB[1], HUB[2] + 0.015), (0.06, 0.06, 0.045), 12, 6)
    fin("MobileHub", hub, ACC, angle=None)
    strings = bmesh.new()
    stars = bmesh.new()
    moon = bmesh.new()
    drops = (0.07, 0.11, 0.08, 0.12)
    for k, (end, a) in enumerate(arms):
        bot = end - UP * drops[k]
        tube_bm([end, bot], 0.007, 5, bm=strings)
        if k == 1:
            build_moon_bm(moon, bot - UP * 0.06, a)
        else:
            m = front_matrix(bot.x, bot.y, bot.z - 0.085, 12 * (k - 1.5)) @ Matrix.Translation((0, 0, -0.016))
            badge_bm(star_outline(0.095), 0.032, 0.009, bm=stars, matrix=m)
    fin("Strings", strings, "SH_Cream", angle=None)
    fin("MobileStars", stars, "SH_Gold", angle=60)
    fin("MobileMoon", moon, "SH_Gold", angle=80)


def build_moon_bm(bm, c, a):
    R = 0.085
    rin = R * 0.74
    off = R * 0.42
    n = 13
    lim = math.acos((R * R + off * off - rin * rin) / (2 * R * off))
    pts, rad = [], []
    for k in range(n):
        u = k / (n - 1)
        phi = lim + (2 * math.pi - 2 * lim) * u
        dx, dy = math.cos(phi), math.sin(phi)
        b = dx * off
        disc = b * b - (off * off - rin * rin)
        tin = min(b + math.sqrt(disc) if disc > 0 else 0.0, R)
        w = max(R - tin, 0.03)
        mid = (R + tin) / 2 if tin < R else R - 0.004
        pts.append((-dx * mid, 0.0, dy * mid))
        rad.append(w / 2)
    sub = tube_bm(pts, rad, 8)
    xf(sub, Matrix.Diagonal((1, 0.7, 1, 1)))
    xf(sub, Matrix.Translation(c) @ Matrix.Rotation(0.25, 4, "Z"))
    me = bpy.data.meshes.new("tmpmoon")
    sub.to_mesh(me)
    sub.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


out, flags = cli()
begin()
build_posts()
build_base()
build_blanket()
build_panels()
build_rails()
build_mobile()
ob = join_all("ShopCrib")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.25, 0.35, 0), dragon_rot=30.0, target=(-0.35, 0.0, 0.45), ortho=2.7)
