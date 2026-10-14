import sys, random
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

POT_H = 0.4
RIM_R = 0.3


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


def heart_outline(size, n=22):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * size / 32.0, (y + 2.0) * size / 32.0))
    return pts


def pot_r(z):
    return 0.22 + (RIM_R - 0.03 - 0.22) * (z / POT_H) ** 0.8


def build_pot():
    prof = [(0.0, 0.0), (0.2, 0.0), (0.225, 0.02), (0.235, 0.05), (0.226, 0.07)]
    for k in range(1, 6):
        z = 0.07 + (POT_H - 0.07) * k / 5
        prof.append((pot_r(z), z))
    prof += [(0.22, POT_H), (0.0, POT_H)]
    fin("Pot", lathe_bm(prof, 20), "SH_Honey", angle=45)
    bm = torus_bm(RIM_R - 0.02, 0.05, 20, 7, matrix=Matrix.Translation((0, 0, POT_H)))
    torus_bm(0.235, 0.028, 20, 5, bm=bm, matrix=Matrix.Translation((0, 0, 0.06)))
    fin("Rim", bm, "SH_Walnut", angle=80)
    zc = 0.22
    rf = pot_r(zc)
    m = face_m(0, -rf + 0.012, zc - 0.07) @ Matrix.Rotation(0.0, 4, "Z")
    fin("Heart", badge_bm(heart_outline(0.16), 0.035, 0.013, 2, matrix=m), "SH_Plum", angle=60)


def build_bush():
    rnd = random.Random(11)
    bm = bmesh.new()
    ellipsoid_bm((0, 0, POT_H + 0.06), (0.26, 0.26, 0.12), 14, 7, bm=bm)
    blobs = []
    for k in range(7):
        a = 2 * math.pi * k / 7 + 0.3
        r = 0.17
        c = (r * math.cos(a), r * math.sin(a), POT_H + 0.1 + rnd.uniform(0.0, 0.04))
        s = rnd.uniform(0.11, 0.13)
        ellipsoid_bm(c, (s, s, s * 0.9), 9, 5, bm=bm)
        blobs.append(c)
    ellipsoid_bm((0, 0, POT_H + 0.2), (0.15, 0.15, 0.13), 12, 7, bm=bm)
    fin("Bush", bm, "SH_Leaf", angle=80)
    return blobs


def flower(c, n_up, s, petals, centers, rnd):
    n = Vector(n_up).normalized()
    rot = n.to_track_quat("Z", "Y").to_matrix().to_4x4()
    m = Matrix.Translation(c) @ rot @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Z")
    for k in range(5):
        a = 2 * math.pi * k / 5
        before = set(petals.verts)
        ellipsoid_bm((0.062 * s * math.cos(a), 0.062 * s * math.sin(a), 0.0), (0.05 * s, 0.05 * s, 0.022 * s), 8, 3, bm=petals)
        xf(petals, m, [v for v in petals.verts if v not in before])
    before = set(centers.verts)
    ellipsoid_bm((0, 0, 0.018 * s), (0.042 * s, 0.042 * s, 0.03 * s), 8, 3, bm=centers)
    xf(centers, m, [v for v in centers.verts if v not in before])


def build_flowers(blobs):
    rnd = random.Random(5)
    petals, centers = bmesh.new(), bmesh.new()
    spots = [((0, 0, POT_H + 0.345), (0, 0, 1), 1.55)]
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.55
        r = 0.2
        z = POT_H + 0.2 + rnd.uniform(-0.01, 0.03)
        spots.append(((r * math.cos(a), r * math.sin(a), z), (math.cos(a) * 0.6, math.sin(a) * 0.6, 1), rnd.uniform(1.3, 1.45)))
    for c, n, s in spots:
        flower(Vector(c), n, s, petals, centers, rnd)
    fin("Petals", petals, "SH_Plum", angle=80)
    fin("Centers", centers, "SH_Gold", angle=80)


out, flags = cli()
begin()
build_pot()
blobs = build_bush()
build_flowers(blobs)
ob = join_all("ShopPlanter")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.25, 0.4, 0), target=(-0.25, 0.0, 0.42), ortho=2.2)
