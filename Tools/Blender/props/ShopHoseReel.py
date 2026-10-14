import sys, random
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *


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


def flower_outline(R, lobes=4, n=32, depth=0.32):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = R * (1 - depth + depth * abs(math.cos(lobes * a / 2)) ** 0.7)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


AX_X = Matrix.Rotation(math.radians(90), 4, "Y")
BASE_H = 0.06
PX, PY, PW = -0.225, 0.04, 0.125
POST_TOP = 0.8
CY, CZ = 0.0, 0.3
D0, D1 = -0.065, 0.175
DISC_R = 0.19
DISC_T = 0.036
BR0, BR1 = D0 - 0.04, D1 + 0.04
HOSE_R = 0.026
COIL_R = 0.146
FAU_Z = 0.64


def build_base():
    bm = soft_box((0.0, 0.0, BASE_H / 2), (0.6, 0.4, BASE_H), 0.1, 0.028, seg=2, Rb=0.008)
    fin("Base", bm, "SH_Stone", angle=50)


def build_post():
    w = PW
    rings = [(w + 0.03, w + 0.03, 0.04, BASE_H - 0.01), (w + 0.03, w + 0.03, 0.04, BASE_H + 0.03),
             (w, w, 0.03, BASE_H + 0.07), (w, w, 0.03, POST_TOP - 0.1), (w - 0.012, w - 0.012, 0.025, POST_TOP - 0.08)]
    rings = [r + (PX, PY) for r in rings]
    fin("Post", loft(rings, 3), "SH_Timber", angle=50)
    cap = [(w + 0.01, w + 0.01, 0.03, POST_TOP - 0.1), (w + 0.05, w + 0.05, 0.035, POST_TOP - 0.085),
           (w + 0.05, w + 0.05, 0.035, POST_TOP - 0.062), (w - 0.02, w - 0.02, 0.03, POST_TOP - 0.025),
           (0.035, 0.035, 0.015, POST_TOP)]
    cap = [r + (PX, PY) for r in cap]
    fin("PostCap", loft(cap, 3), "SH_Honey", angle=45)


def build_faucet():
    g = bmesh.new()
    yf = PY - PW / 2
    lathe_bm([(0.0, 0.0), (0.06, 0.0), (0.06, 0.012), (0.045, 0.025), (0.0, 0.026)], 14, bm=g,
             matrix=Matrix.Translation((PX, yf + 0.004, FAU_Z)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    pts = catmull([(PX, yf - 0.01, FAU_Z), (PX, yf - 0.08, FAU_Z), (PX, yf - 0.115, FAU_Z - 0.035),
                   (PX, yf - 0.12, FAU_Z - 0.075)], 4)
    tube_bm(pts, 0.03, 10, bm=g)
    tube_bm([(PX, yf - 0.065, FAU_Z), (PX, yf - 0.065, FAU_Z + 0.07)], 0.018, 8, bm=g)
    badge_bm(flower_outline(0.07, 4), 0.026, 0.01, 2, bm=g,
             matrix=Matrix.Translation((PX, yf - 0.065, FAU_Z + 0.06)) @ Matrix.Rotation(0.3, 4, "Z"))
    ellipsoid_bm((PX, yf - 0.065, FAU_Z + 0.09), (0.024, 0.024, 0.018), 8, 4, bm=g)
    fin("Faucet", g, "SH_Gold", angle=55)
    return Vector((PX, yf - 0.12, FAU_Z - 0.075))


def build_reel():
    wood = bmesh.new()
    for x in (D0, D1):
        prof = [(0.0, -DISC_T / 2), (DISC_R - 0.015, -DISC_T / 2), (DISC_R, -DISC_T / 2 + 0.012),
                (DISC_R, DISC_T / 2 - 0.012), (DISC_R - 0.015, DISC_T / 2), (0.0, DISC_T / 2)]
        lathe_bm(prof, 24, bm=wood, matrix=Matrix.Translation((x, CY, CZ)) @ AX_X)
    fin("Discs", wood, "SH_Honey", angle=50)
    core = lathe_bm([(0.0, D0), (COIL_R - 0.02, D0), (COIL_R - 0.02, D1), (0.0, D1)], 18,
                    matrix=Matrix.Translation((0, CY, CZ)) @ AX_X)
    fin("CoilCore", core, "SH_Moss", angle=60)
    br = bmesh.new()
    for x in (BR0, BR1):
        rings = [(0.04, 0.16, 0.02, BASE_H - 0.01), (0.04, 0.12, 0.02, BASE_H + 0.06), (0.04, 0.1, 0.02, CZ - 0.02)]
        rings = [r + (x, CY) for r in rings]
        loft(rings, 2, bm=br)
        lathe_bm([(0.05, -0.02), (0.05, 0.02)], 12, bm=br, matrix=Matrix.Translation((x, CY, CZ - 0.02)) @ AX_X)
        lathe_bm([(0.0, -0.02), (0.05, -0.02)], 12, bm=br, matrix=Matrix.Translation((x, CY, CZ - 0.02)) @ AX_X)
        lathe_bm([(0.05, 0.02), (0.0, 0.02)], 12, bm=br, matrix=Matrix.Translation((x, CY, CZ - 0.02)) @ AX_X)
    lathe_bm([(0.0, BR0 - 0.03), (0.028, BR0 - 0.03), (0.028, BR1 + 0.03), (0.0, BR1 + 0.03)], 10, bm=br,
             matrix=Matrix.Translation((0, CY, CZ)) @ AX_X)
    fin("Brackets", br, "SH_Timber", angle=50)
    g = bmesh.new()
    for x, s in ((BR0 - 0.02, -1), (BR1 + 0.02, 1)):
        prof = [(0.0, 0.0), (0.04, 0.0), (0.042, 0.012), (0.03, 0.026), (0.0, 0.03)]
        m = Matrix.Translation((x, CY, CZ)) @ Matrix.Rotation(math.radians(90 * s), 4, "Y")
        lathe_bm(prof, 12, bm=g, matrix=m)
    xc = BR1 + 0.045
    a = math.radians(40)
    ex, ez = CY + math.cos(a) * 0.1, CZ + math.sin(a) * 0.1
    tube_bm([(xc, CY, CZ), (xc, ex, ez)], 0.02, 8, bm=g)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.25
        for x, s in ((D1 + DISC_T / 2, 1), (D0 - DISC_T / 2, -1)):
            ellipsoid_bm((x, CY + math.cos(a) * 0.125, CZ + math.sin(a) * 0.125), (0.014, 0.022, 0.022), 6, 3, bm=g)
    fin("Hubs", g, "SH_Gold", angle=60)
    kn = lathe_bm([(0.0, 0.0), (0.026, 0.0), (0.03, 0.03), (0.026, 0.06), (0.0, 0.066)], 10,
                  matrix=Matrix.Translation((xc - 0.01, ex, ez)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
    fin("Knob", kn, "SH_Honey", angle=60)


def coil_pt(theta, x, r):
    return Vector((x, CY - r * math.sin(theta), CZ + r * math.cos(theta)))


def build_hose(spout):
    turns = 4.25
    x0, x1 = D0 + DISC_T / 2 + HOSE_R + 0.002, D1 - DISC_T / 2 - HOSE_R - 0.002
    n = int(turns * 18)
    pts = []
    th_end = turns * 2 * math.pi
    th0 = th_end - turns * 2 * math.pi
    for i in range(n + 1):
        t = i / n
        pts.append(coil_pt(th0 + (th_end - th0) * t, x0 + (x1 - x0) * t, COIL_R))
    end = pts[-1]
    tail = catmull([end, end + Vector((0.0, -0.02, -0.06)), Vector((x1 - 0.01, -0.172, 0.14)),
                    Vector((0.11, -0.165, BASE_H + HOSE_R + 0.002)), Vector((0.03, -0.12, BASE_H + HOSE_R + 0.002)),
                    Vector((-0.02, -0.11, BASE_H + HOSE_R + 0.002))], 4)
    hose = tube_bm(pts + tail[1:], HOSE_R, 8)
    sup = catmull([spout + Vector((0, 0, 0.01)), spout + Vector((0.0, -0.01, -0.08)), Vector((PX + 0.04, -0.13, 0.4)),
                   Vector((BR0 - 0.07, -0.06, CZ + 0.01)), Vector((BR0 - 0.04, CY, CZ))], 4)
    tube_bm(sup, HOSE_R, 8, bm=hose)
    fin("Hose", hose, "SH_Moss", angle=70)
    g = bmesh.new()
    lathe_bm([(0.0, 0.0), (HOSE_R + 0.008, 0.0), (HOSE_R + 0.01, 0.03), (HOSE_R + 0.004, 0.034), (0.0, 0.034)], 10, bm=g,
             matrix=Matrix.Translation(spout + Vector((0, 0, 0.012))) @ Matrix.Rotation(math.pi, 4, "X"))
    nz = Vector((-0.02, -0.11, BASE_H + HOSE_R + 0.002))
    prof = [(0.0, 0.0), (HOSE_R + 0.006, 0.0), (HOSE_R + 0.01, 0.03), (0.028, 0.04), (0.026, 0.1), (0.04, 0.135),
            (0.042, 0.15), (0.03, 0.155), (0.0, 0.155)]
    lathe_bm(prof, 12, bm=g, matrix=Matrix.Translation(nz + Vector((0.01, 0, 0))) @ Matrix.Rotation(math.radians(-90), 4, "Y")
             @ Matrix.Rotation(math.radians(0), 4, "Z"))
    fin("Brass", g, "SH_Gold", angle=60)


out, flags = cli()
begin()
build_base()
build_post()
spout = build_faucet()
build_reel()
build_hose(spout)
ob = join_all("ShopHoseReel")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.05, 0.45, 0), target=(-0.4, 0.0, 0.45), ortho=2.1)
