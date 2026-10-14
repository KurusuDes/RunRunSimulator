import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


def fin(name, bm, mat, angle=50.0):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


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


def star_outline(ro, rin, n=5):
    pts = []
    for k in range(2 * n):
        a = math.pi / 2 + math.pi * k / n
        r = ro if k % 2 == 0 else rin
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


R_OUT = 1.5
VALLEY = 0.05
CREST = 0.068
LUMP = 0.006
R_CENTER = 0.21
SEQ = ["SH_Gold", "SH_Parchment", "SH_Parchment", "SH_Sage", "SH_Sage", "SH_Parchment", "SH_Plum", "SH_Parchment",
       "SH_Parchment", "SH_Gold", "SH_Gold", "SH_Parchment", "SH_Sage", "SH_Parchment", "SH_Plum", "SH_Plum"]
BW = (R_OUT - R_CENTER) / len(SEQ)
BANDS = [(0.0, R_CENTER, "SH_Gold")] + [(R_CENTER + i * BW, R_CENTER + (i + 1) * BW, m) for i, m in enumerate(SEQ)]


def band_bm(r0, r1, bm, phase, outer=False):
    rm = (r0 + r1) / 2
    segs = max(24, int(round(2 * math.pi * rm / 0.1 / 2.0)) * 2)
    if outer:
        prof = [(r0 - 0.01, VALLEY - 0.004, 0.0), (rm - 0.008, CREST, 1.0), (r1 - 0.016, 0.03, 0.3), (r1, 0.003, 0.0)]
    elif r0 <= 0.0:
        prof = [(0.0, CREST + 0.004, 0.0), (r1 * 0.6, CREST, 0.0), (r1 - 0.03, CREST - 0.006, 0.0),
                (r1 + 0.01, VALLEY - 0.004, 0.0)]
    else:
        prof = [(r0 - 0.01, VALLEY - 0.004, 0.0), (rm, CREST, 1.0), (r1 + 0.01, VALLEY - 0.004, 0.0)]
    rings = []
    for r, z, wgt in prof:
        if r <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
            continue
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            lump = LUMP * wgt * math.cos(segs / 2 * a + phase)
            rr = r + 0.006 * wgt * math.cos(segs / 2 * a + phase)
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z + lump)))
        rings.append(ring)
    for A, B in zip(rings, rings[1:]):
        for k in range(segs):
            k1 = (k + 1) % segs
            if len(A) == 1:
                bm.faces.new((A[0], B[k], B[k1]))
            else:
                bm.faces.new((A[k], A[k1], B[k1], B[k]))


def build_mat():
    bins = {}
    for i, (r0, r1, mat) in enumerate(BANDS):
        bm = bins.setdefault(mat, bmesh.new())
        band_bm(r0, r1, bm, phase=math.pi * (i % 2), outer=(r1 >= R_OUT - 1e-6))
    for mat, bm in bins.items():
        fin_up("Mat_" + mat, bm, mat, angle=70)
    st = badge_bm(star_outline(0.2, 0.1), 0.026, 0.012, 2,
                  matrix=Matrix.Translation((0, 0, CREST - 0.01)) @ Matrix.Rotation(0.0, 4, "Z"))
    fin("Star", st, "SH_Plum", angle=60)


def cushion(cx, cy, rz, half, hh, mat, z0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        rho = math.hypot(x, y)
        if rho > 1e-6:
            a = math.atan2(y, x)
            f = (abs(math.cos(a)) ** 6 + abs(math.sin(a)) ** 6) ** (-1.0 / 6.0)
        else:
            f = 1.0
        zz = z * hh * (1.0 - 0.5 * rho ** 2)
        if z > 0:
            zz -= 0.04 * math.exp(-(rho / 0.32) ** 2)
        v.co = Vector((x * f * half, y * f * half, zz + hh))
    m = Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(math.radians(rz), 4, "Z")
    xf(bm, m)
    fin("Cushion", bm, mat, angle=80)
    g = bmesh.new()
    ellipsoid_bm((0, 0, 2 * hh - 0.045), (0.05, 0.05, 0.03), 10, 5, bm=g)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = Vector((sx * half * 0.86, sy * half * 0.86, hh * 0.9))
            ellipsoid_bm(tuple(p), (0.04, 0.04, 0.05), 8, 5, bm=g)
            lathe_bm([(0.0, -0.035), (0.028, -0.03), (0.036, 0.0), (0.0, 0.006)], 8, bm=g,
                     matrix=Matrix.Translation(p + Vector((sx * 0.03, sy * 0.03, -0.045))))
    xf(g, m)
    fin("Tassels", g, "SH_Gold", angle=80)


out, flags = cli()
begin()
build_mat()
cushion(0.68, 0.66, 22, 0.36, 0.14, "SH_Sage", CREST - 0.035)
cushion(-0.78, 0.5, -14, 0.34, 0.14, "SH_Plum", CREST - 0.035)
ob = join_all("ShopPlayMat")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.95, -0.9, 0), target=(-0.3, 0.0, 0.3), ortho=4.4)
