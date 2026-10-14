import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

BWID = 0.52
BDEP = 0.46
LEG_H = 0.2
BODY_Z1 = 0.84
DOME_R = BWID / 2


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


def badge_bm(outline, t, bev, steps=2, bm=None, matrix=None, both=False):
    bm = bm or bmesh.new()
    rings = []
    if both:
        rings.append((bev + 0.012, 0.0))
        for j in range(steps, 0, -1):
            a = math.pi / 2 * j / steps
            rings.append((bev * (1 - math.cos(a)), bev - bev * math.sin(a)))
        rings.append((0.0, bev))
    else:
        rings.append((0.0, 0.0))
    rings.append((0.0, t - bev))
    for j in range(1, steps + 1):
        a = math.pi / 2 * j / steps
        rings.append((bev * (1 - math.cos(a)), t - bev + bev * math.sin(a)))
    rings.append((bev + 0.012, t))
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    vr = []
    for d, z in rings:
        vr.append([bm.verts.new((x, y, z)) for x, y in offset2d(outline, d)])
    n = len(outline)
    for A, B in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    c0 = bm.verts.new((cx, cy, rings[0][1]))
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


def silhouette(w, z0, z1, r_bot, grow=0.0):
    hw = w / 2 + grow
    R = w / 2 + grow
    pts = []
    for j in range(4):
        a = math.radians(270 + 90 * j / 3)
        pts.append((hw - r_bot + r_bot * math.cos(a), z0 - grow + r_bot + r_bot * math.sin(a)))
    for j in range(13):
        a = math.pi * j / 12
        pts.append((R * math.cos(a), z1 + R * math.sin(a)))
    for j in range(4):
        a = math.radians(180 + 90 * j / 3)
        pts.append((-hw + r_bot + r_bot * math.cos(a), z0 - grow + r_bot + r_bot * math.sin(a)))
    return pts


def depth_m(y_back):
    return Matrix(((1, 0, 0, 0), (0, 0, -1, y_back), (0, 1, 0, 0), (0, 0, 0, 1)))


def build_body():
    out = silhouette(BWID, LEG_H, BODY_Z1, 0.06)
    fin("Body", badge_bm(out, BDEP, 0.045, 2, matrix=depth_m(BDEP / 2), both=True), "SH_Teal", angle=50)
    bm = bmesh.new()
    for y in (-BDEP / 2 + 0.07, BDEP / 2 - 0.07):
        band = silhouette(BWID, LEG_H, BODY_Z1, 0.07, grow=0.018)
        badge_bm(band, 0.055, 0.02, 2, bm=bm, matrix=depth_m(y + 0.0275), both=True)
    fin("Bands", bm, "SH_Parchment", angle=55)


def build_front():
    yf = -BDEP / 2
    bm = bmesh.new()
    m = face_m(0, yf + 0.012, BODY_Z1 + 0.06) @ Matrix.Rotation(math.radians(-22), 4, "X")
    loft(rbox_rings(0.34, 0.12, 0.05, 0.05, 0.02, seg=2), 3, cap0=False, bm=bm, matrix=m)
    loft(rbox_rings(0.3, 0.2, 0.04, 0.05, 0.016, seg=2), 3, cap0=False, bm=bm, matrix=face_m(0, yf + 0.01, 0.52))
    fin("Plates", bm, "SH_Parchment", angle=55)
    bm = bmesh.new()
    loft(rbox_rings(0.2, 0.035, 0.03, 0.017, 0.012, seg=2), 2, cap0=False, bm=bm,
         matrix=face_m(0, yf - 0.03, BODY_Z1 + 0.03) @ Matrix.Rotation(math.radians(-22), 4, "X"))
    fin("Slot", bm, "SH_Dark", angle=60)
    m = face_m(0, yf - 0.02, 0.5)
    fin("Heart", badge_bm(heart_outline(0.15), 0.035, 0.012, 2, matrix=m), "SH_Gold", angle=60)


def build_legs():
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (BWID / 2 - 0.07), sy * (BDEP / 2 - 0.08)
            prof = [(0.0, 0.0), (0.075, 0.0), (0.08, 0.022), (0.062, 0.055), (0.056, LEG_H + 0.04), (0.0, LEG_H + 0.04)]
            lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((x, y, 0)))
    fin("Legs", bm, "SH_Teal", angle=50)


def build_flag():
    x = BWID / 2 + 0.015
    zc = 0.62
    bm = bmesh.new()
    prof = [(0.0, 0.0), (0.045, 0.0), (0.045, 0.03), (0.0, 0.035)]
    lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((x, 0.08, zc)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    fin("FlagHub", bm, "SH_Parchment", angle=60)
    outline = [(-0.03, -0.03), (0.03, -0.03), (0.03, 0.26), (0.15, 0.26), (0.15, 0.38), (-0.03, 0.38)]
    m = Matrix(((0, 0, 1, x + 0.02), (-1, 0, 0, 0.08), (0, 1, 0, zc), (0, 0, 0, 1)))
    m = m @ Matrix.Rotation(math.radians(-8), 4, "Z")
    fin("Flag", badge_bm(outline, 0.035, 0.012, 2, matrix=m), "SH_Gold", angle=60)


out, flags = cli()
begin()
build_body()
build_front()
build_legs()
build_flag()
ob = join_all("ShopMailbox")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.15, 0.55, 0), target=(-0.3, 0.0, 0.55), ortho=2.4)
