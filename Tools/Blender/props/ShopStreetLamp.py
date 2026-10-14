import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

POLE_R = 0.075
POLE_Z0, POLE_Z1 = 0.4, 2.3
GLOBE_Z = 2.57
GLOBE_R = 0.26
ARM_Z = 2.06


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


def ellipse(rx, ry, n=14, cx=0.0, cy=0.0):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def build_post():
    prof = [(0.0, 0.0), (0.29, 0.0), (0.305, 0.03), (0.29, 0.08), (0.22, 0.105), (0.21, 0.2), (0.17, 0.27),
            (0.13, 0.33), (0.12, POLE_Z0 + 0.02), (0.0, POLE_Z0 + 0.02)]
    fin("Base", lathe_bm(prof, 16), "SH_Timber", angle=40)
    prof = [(0.0, POLE_Z0 - 0.01), (POLE_R + 0.02, POLE_Z0 - 0.01), (POLE_R, 1.2), (POLE_R - 0.008, POLE_Z1), (0.0, POLE_Z1)]
    fin("Pole", lathe_bm(prof, 12), "SH_Timber", angle=40)
    bm = bmesh.new()
    for z, R, r in ((0.13, 0.215, 0.037), (POLE_Z0 + 0.02, 0.12, 0.036), (1.2, POLE_R + 0.005, 0.032), (ARM_Z, POLE_R - 0.002, 0.034)):
        torus_bm(R, r, 16, 6, bm=bm, matrix=Matrix.Translation((0, 0, z)))
    fin("Rings", bm, "SH_Gold", angle=70)
    prof = [(0.0, POLE_Z1 - 0.02), (0.1, POLE_Z1 - 0.02), (0.15, POLE_Z1 + 0.04), (0.17, POLE_Z1 + 0.07),
            (0.13, POLE_Z1 + 0.1), (0.0, POLE_Z1 + 0.1)]
    fin("Cup", lathe_bm(prof, 16), "SH_Timber", angle=50)


def build_globe():
    prof = [(0.0, GLOBE_Z - GLOBE_R)]
    for k in range(1, 9):
        a = -math.pi / 2 + math.pi * k / 9
        prof.append((GLOBE_R * math.cos(a), GLOBE_Z + GLOBE_R * 1.05 * math.sin(a)))
    prof.append((0.0, GLOBE_Z + GLOBE_R * 1.05))
    fin("Globe", lathe_bm(prof, 16), "SH_Lamp", angle=80)
    zc = GLOBE_Z + GLOBE_R * 0.78
    prof = [(0.0, zc), (0.16, zc), (0.22, zc + 0.035), (0.215, zc + 0.065), (0.15, zc + 0.11), (0.06, zc + 0.15),
            (0.0, zc + 0.155)]
    fin("Cap", lathe_bm(prof, 16), "SH_Timber", angle=50)
    bm = ellipsoid_bm((0, 0, zc + 0.2), (0.06, 0.06, 0.065), 10, 6)
    fin("Finial", bm, "SH_Gold", angle=80)


def paw_bm(cx, y, cz, s, facing=-1, bm=None):
    bm = bm or bmesh.new()
    if facing < 0:
        m = face_m(cx, y, cz)
    else:
        m = Matrix(((-1, 0, 0, cx), (0, 0, 1, y), (0, 1, 0, cz), (0, 0, 0, 1)))
    badge_bm(ellipse(0.075 * s, 0.062 * s, 14, 0, -0.03 * s), 0.025, 0.01, 1, bm=bm, matrix=m)
    for dx, dy, r in ((-0.075, 0.045, 0.03), (-0.027, 0.075, 0.032), (0.027, 0.075, 0.032), (0.075, 0.045, 0.03)):
        badge_bm(ellipse(r * s, r * s * 1.15, 10, dx * s, dy * s), 0.025, 0.01, 1, bm=bm, matrix=m)
    return bm


def build_banner():
    x0, x1 = 0.11, 0.53
    bm = tube_bm([(0.0, 0, ARM_Z + 0.03), (x1 + 0.05, 0, ARM_Z + 0.03)], 0.026, 8)
    ellipsoid_bm((x1 + 0.07, 0, ARM_Z + 0.03), (0.045, 0.045, 0.045), 8, 5, bm=bm)
    tube_bm(catmull([(0.03, 0, ARM_Z - 0.22), (0.12, 0, ARM_Z - 0.12), (0.26, 0, ARM_Z + 0.0)], 3), 0.02, 6, bm=bm)
    fin("Arm", bm, "SH_Timber", angle=60)
    top = ARM_Z - 0.0
    bot = ARM_Z - 0.72
    xm = (x0 + x1) / 2
    outline = [(x0, top), (x0, bot), (xm, bot + 0.12), (x1, bot), (x1, top)]
    out = list(reversed([(x, z) for x, z in outline]))
    m = Matrix(((1, 0, 0, 0), (0, 0, -1, 0.025), (0, 1, 0, 0), (0, 0, 0, 1)))
    fin("Banner", badge_bm(out, 0.05, 0.015, 2, matrix=m), "SH_Teal", angle=55)
    bm = paw_bm(xm, -0.033, top - 0.3, 1.25, -1)
    paw_bm(xm, 0.033, top - 0.3, 1.25, 1, bm=bm)
    fin("Paw", bm, "SH_Parchment", angle=70)


out, flags = cli()
begin()
build_post()
build_globe()
build_banner()
ob = join_all("ShopStreetLamp")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.8, -0.3, 0), target=(0.0, 0.0, 1.5), ortho=3.6)
