import sys, random
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


def front_matrix(x, y, z, rz=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ M


def fin(name, bm, mat, angle=50.0, recalc=True):
    if recalc:
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


def loop_tube_bm(path, radius, sides=6, bm=None, matrix=None):
    bm = bm or bmesh.new()
    P = [Vector(p) for p in path]
    n = len(P)
    rings = []
    for i in range(n):
        t = (P[(i + 1) % n] - P[i - 1]).normalized()
        side = (UP - t * UP.dot(t))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = t.cross(side).normalized()
        rings.append([bm.verts.new(P[i] + side * math.cos(2 * math.pi * k / sides) * radius +
                                   up * math.sin(2 * math.pi * k / sides) * radius) for k in range(sides)])
    for i in range(n):
        A, B = rings[i], rings[(i + 1) % n]
        for k in range(sides):
            bm.faces.new((A[k], A[(k + 1) % sides], B[(k + 1) % sides], B[k]))
    if matrix is not None:
        xf(bm, matrix, [v for r in rings for v in r])
    return bm


def drop_outline(size, n=24):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 0.86 * math.sin(t) * math.sin(t / 2) ** 0.8
        y = math.cos(t)
        pts.append((x * size / 2.0, y * size / 2.0))
    return pts


def orient_inward(bm, cz):
    for f in bm.faces:
        f.normal_update()
    side = [f for f in bm.faces if abs(f.normal.z) < 0.7]
    score = sum(f.normal.dot(Vector((f.calc_center_median().x, f.calc_center_median().y, 0))) for f in side)
    if score > 0:
        for f in bm.faces:
            f.normal_flip()
    return bm


ACC = "SH_Teal"
RIM_Z = 0.625
RIM_W, RIM_D = 1.30, 0.72
SHELL = [(0.84, 0.34, 0.12), (0.98, 0.48, 0.135), (1.11, 0.59, 0.18), (1.21, 0.665, 0.27), (1.27, 0.705, 0.40),
         (1.305, 0.73, 0.53), (1.315, 0.74, RIM_Z)]
INNER = [(1.12, 0.55, 0.49), (1.19, 0.615, 0.57), (1.255, 0.675, 0.635), (1.275, 0.695, 0.65)]
WATER_Z = 0.545


def ring(w, d, z):
    return (w, d, d / 2 - 0.01, z)


def build_shell():
    rings = [ring(*r) for r in SHELL]
    fin("Shell", loft(rings, 6, cap0=True, cap1=False), ACC, angle=55, recalc=False)
    path = [(x, y, RIM_Z + 0.012) for x, y in rrect(RIM_W, RIM_D, RIM_D / 2 - 0.01, 6)]
    fin("Rim", loop_tube_bm(path, 0.046, 6), "SH_White", angle=80)
    inner = loft([ring(*r) for r in INNER], 6, cap0=True, cap1=False)
    fin("Inner", orient_inward(inner, 0.5), "SH_White", angle=55, recalc=False)
    w = 1.172
    d = 0.6
    fin("Water", loft([ring(w, d, WATER_Z - 0.02), ring(w, d, WATER_Z)], 6), "SH_Water", angle=70)


def build_feet():
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            a = Vector((sx * 0.38, sy * 0.15, 0.2))
            b = Vector((sx * 0.5, sy * 0.235, 0.075))
            mid = (a + b) / 2 + Vector((sx * 0.03, sy * 0.01, 0.0))
            tube_bm([a, mid, b], [0.06, 0.05, 0.045], 8, bm=bm)
            ellipsoid_bm((b.x, b.y, 0.062), (0.078, 0.078, 0.064), 10, 5, bm=bm)
            out = Vector((sx * 0.8, sy * 0.6, 0)).normalized()
            tang = Vector((-out.y, out.x, 0))
            for k in (-1, 0, 1):
                d = (out + tang * 0.75 * k).normalized()
                p = Vector((b.x, b.y, 0.03)) + d * 0.07
                ellipsoid_bm(p, (0.036, 0.036, 0.03), 8, 4, bm=bm)
    fin("Feet", bm, "SH_Gold", angle=70)


def build_faucet():
    x0 = RIM_W / 2
    ctrl = [(x0, 0, 0.65), (x0, 0, 0.72), (x0 - 0.02, 0, 0.775), (x0 - 0.085, 0, 0.8), (x0 - 0.15, 0, 0.78),
            (x0 - 0.175, 0, 0.735)]
    pts = catmull(ctrl, 3)
    fin("Pipe", tube_bm(pts, [0.032] * len(pts), 8), "SH_Gold", angle=60)
    bm = lathe_bm([(0.0, 0.645), (0.07, 0.645), (0.075, 0.665), (0.055, 0.69), (0.03, 0.70), (0.0, 0.70)], 12,
                  matrix=Matrix.Translation((x0, 0, 0.0)))
    lathe_bm([(0.0, -0.04), (0.042, -0.04), (0.046, -0.005), (0.04, 0.012), (0.0, 0.016)], 10, bm=bm,
             matrix=Matrix.Translation(pts[-1]))
    fin("Flange", bm, "SH_Gold", angle=60)
    bm = tube_bm([(x0, -0.13, 0.715), (x0, 0.13, 0.715)], [0.024, 0.024], 8)
    fin("Bar", bm, "SH_Gold", angle=60)
    bm = bmesh.new()
    for s in (-1, 1):
        ellipsoid_bm((x0, s * 0.145, 0.715), (0.045, 0.045, 0.045), 10, 5, bm=bm)
    fin("Knobs", bm, "SH_White", angle=80)


def build_caddy():
    xc = 0.2
    fin("Caddy", rbox_bm((xc, 0.0, RIM_Z + 0.078), (0.21, 0.8, 0.045), 0.018, 2), "SH_Oak", angle=50)
    zt = RIM_Z + 0.1
    fin("Soap", soft_box((xc, -0.2, zt + 0.028), (0.15, 0.1, 0.06), 0.035, 0.022), ACC, angle=60)
    fin("Sponge", soft_box((xc + 0.005, 0.15, zt + 0.035), (0.13, 0.16, 0.075), 0.03, 0.025), "SH_Gold", angle=60)


def build_foam():
    rnd = random.Random(11)
    bm = bmesh.new()
    spots = [(-0.46, 0.1, 0.13, 0.0), (-0.44, -0.14, 0.13, 0.0), (-0.24, -0.18, 0.13, 0.0), (-0.24, 0.17, 0.13, 0.0),
             (-0.05, -0.12, 0.12, 0.0), (-0.06, 0.13, 0.12, 0.0), (-0.34, 0.0, 0.15, 0.07), (-0.15, 0.0, 0.13, 0.06),
             (-0.26, 0.04, 0.1, 0.15), (0.45, 0.13, 0.1, 0.0), (0.42, -0.13, 0.09, 0.0), (0.36, 0.0, 0.08, 0.03)]
    for x, y, r, lift in spots:
        z = WATER_Z + r * 0.35 + lift + rnd.uniform(0.0, 0.015)
        ellipsoid_bm((x, y, z), (r, r, r * 0.9), 12, 6, bm=bm)
    for x, y, r in ((-0.36, -0.36, 0.06), (-0.22, -0.375, 0.045), (-0.47, 0.35, 0.05)):
        ellipsoid_bm((x, y, RIM_Z + 0.045 + r * 0.7), (r, r, r), 10, 5, bm=bm)
    fin("Foam", bm, "SH_White", angle=80)


def build_badge():
    yb = -0.354
    m = front_matrix(0, yb + 0.012, 0.36)
    fin("Drop", badge_bm(drop_outline(0.2), 0.04, 0.016, 2, matrix=m), "SH_White", angle=60)


out, flags = cli()
begin()
build_shell()
build_feet()
build_faucet()
build_caddy()
build_foam()
build_badge()
ob = join_all("ShopBathtub")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.45, -0.25, 0), target=(-0.4, 0.0, 0.42), ortho=3.1)
