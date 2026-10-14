import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


def fin_up(name, bm, mat, angle=60.0):
    for f in bm.faces:
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
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


def blob(cx, cy, ax, ay, waves, n):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        f = 1.0 + sum(amp * math.sin(m * a + ph) for amp, m, ph in waves)
        pts.append((cx + ax * f * math.cos(a), cy + ay * f * math.sin(a)))
    return pts


RIM = [(0.0, 0.001), (0.022, 0.011), (0.042, 0.0165), (0.062, 0.0145), (0.078, 0.0115)]
WATER_Z = 0.0115


def puddle(outline, rim_bm, water_bm, scale=1.0):
    rings = []
    for d, z in RIM:
        rings.append([rim_bm.verts.new((x, y, z)) for x, y in offset2d(outline, d * scale)])
    n = len(outline)
    for A, B in zip(rings, rings[1:]):
        for k in range(n):
            rim_bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    inner = offset2d(outline, RIM[-1][0] * scale - 0.004)
    cx = sum(p[0] for p in inner) / n
    cy = sum(p[1] for p in inner) / n
    mid = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55) for x, y in inner]
    w0 = [water_bm.verts.new((x, y, WATER_Z)) for x, y in inner]
    w1 = [water_bm.verts.new((x, y, WATER_Z - 0.0015)) for x, y in mid]
    c = water_bm.verts.new((cx, cy, WATER_Z - 0.002))
    for k in range(n):
        k1 = (k + 1) % n
        water_bm.faces.new((w0[k], w0[k1], w1[k1], w1[k]))
        water_bm.faces.new((w1[k], w1[k1], c))


def build():
    rim, water = bmesh.new(), bmesh.new()
    main = blob(-0.07, 0.02, 0.5, 0.36, [(0.08, 2, 0.6), (0.07, 3, 1.9), (0.035, 5, 0.4)], 48)
    puddle(main, rim, water)
    puddle(blob(0.5, -0.27, 0.09, 0.07, [(0.06, 2, 1.0)], 18), rim, water, scale=0.55)
    puddle(blob(0.56, 0.05, 0.06, 0.05, [(0.05, 3, 0.2)], 16), rim, water, scale=0.45)
    fin_up("Rim", rim, "SH_Glass", angle=70)
    fin_up("Water", water, "SH_Water", angle=80)
    rip = bmesh.new()
    for R, rr in ((0.075, 0.013), (0.14, 0.012)):
        torus_bm(R, rr, 28, 4, bm=rip, matrix=Matrix.Translation((0.13, -0.02, WATER_Z - 0.002)) @
                 Matrix.Diagonal((1.0, 0.8, 0.35, 1.0)))
    torus_bm(0.06, 0.011, 22, 4, bm=rip, matrix=Matrix.Translation((-0.3, 0.13, WATER_Z - 0.002)) @
             Matrix.Diagonal((1.0, 0.8, 0.35, 1.0)))
    ellipsoid_bm((0.13, -0.02, WATER_Z), (0.022, 0.018, 0.006), 10, 4, bm=rip)
    fin_up("Ripples", rip, "SH_White", angle=80)
    leaf = []
    L = 0.1
    for k in range(13):
        t = k / 12
        leaf.append((-L + 2 * L * t, 0.045 * math.sin(math.pi * t) ** 0.8))
    for k in range(1, 12):
        t = 1 - k / 12
        leaf.append((-L + 2 * L * t, -0.045 * math.sin(math.pi * t) ** 0.8))
    lf = bmesh.new()
    m = Matrix.Translation((-0.24, -0.12, WATER_Z - 0.001)) @ Matrix.Rotation(0.6, 4, "Z")
    top = [lf.verts.new(m @ Vector((x, y, 0.006 + 0.004 * (1 - abs(x) / L)))) for x, y in leaf]
    bot = [lf.verts.new(m @ Vector((x, y, 0.0))) for x, y in leaf]
    c = lf.verts.new(m @ Vector((0, 0, 0.011)))
    n = len(leaf)
    for k in range(n):
        k1 = (k + 1) % n
        lf.faces.new((top[k], top[k1], c))
        lf.faces.new((bot[k], bot[k1], top[k1], top[k]))
    bmesh.ops.recalc_face_normals(lf, faces=list(lf.faces))
    print("PART Leaf tris=%d" % sum(len(f.verts) - 2 for f in lf.faces))
    finish("Leaf", lf, "SH_Leaf", angle=60)


out, flags = cli()
begin()
build()
ob = join_all("ShopPuddle")
xs = [v.co.x for v in ob.data.vertices]
ys = [v.co.y for v in ob.data.vertices]
sh = Vector((-(max(xs) + min(xs)) / 2, -(max(ys) + min(ys)) / 2, 0))
for v in ob.data.vertices:
    v.co += sh
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.2, 0.5, 0), target=(-0.3, 0.0, 0.3), ortho=2.3)
