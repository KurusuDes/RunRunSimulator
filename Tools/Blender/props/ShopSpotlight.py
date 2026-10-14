import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

HUB_Z = 0.5
POLE_TOP = 1.06
PIV_Z = 1.3
HS = 1.3
HEAD_R = 0.17 * HS
TILT = math.radians(22)
YOKE_X = 0.3


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


def slab_bm(outline, t, bev, steps=2, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = [(0.0, 0.0), (0.0, t - bev)]
    for j in range(1, steps + 1):
        a = math.pi / 2 * j / steps
        rings.append((bev * (1 - math.cos(a)), t - bev + bev * math.sin(a)))
    vr = [[bm.verts.new((x, y, z)) for x, y in offset2d(outline, d)] for d, z in rings]
    n = len(outline)
    for A, B in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    caps = [bm.faces.new(list(reversed(vr[0]))), bm.faces.new(vr[-1])]
    bmesh.ops.triangulate(bm, faces=caps, quad_method="BEAUTY", ngon_method="BEAUTY")
    if matrix is not None:
        xf(bm, matrix, [v for r in vr for v in r])
    return bm


def star_outline(R, r, cx=0.0, cy=0.0):
    return [(cx + (R if k % 2 == 0 else r) * math.cos(math.pi / 2 + math.pi * k / 5),
             cy + (R if k % 2 == 0 else r) * math.sin(math.pi / 2 + math.pi * k / 5)) for k in range(10)]


HEAD_M = Matrix.Translation((0, 0, PIV_Z)) @ Matrix.Rotation(math.pi / 2 + TILT, 4, "X")


def build_stand():
    bm = bmesh.new()
    feet = []
    for a in (-90, 30, 150):
        r = math.radians(a)
        foot = Vector((0.23 * math.cos(r), 0.23 * math.sin(r), 0.045))
        mid = Vector((0.135 * math.cos(r), 0.135 * math.sin(r), 0.27))
        top = Vector((0.04 * math.cos(r), 0.04 * math.sin(r), HUB_Z - 0.03))
        tube_bm(catmull([top, mid, foot], 2), [0.052, 0.054, 0.056, 0.058, 0.06], 8, bm=bm)
        feet.append(foot)
    prof = [(0.0, HUB_Z - 0.1), (0.08, HUB_Z - 0.11), (0.115, HUB_Z - 0.07), (0.115, HUB_Z + 0.04), (0.085, HUB_Z + 0.08),
            (0.0, HUB_Z + 0.08)]
    lathe_bm(prof, 12, bm=bm)
    prof = [(0.0, HUB_Z), (0.075, HUB_Z), (0.068, POLE_TOP - 0.02), (0.0, POLE_TOP - 0.02)]
    lathe_bm(prof, 12, bm=bm)
    rbox_bm((0, 0, POLE_TOP), (2 * YOKE_X + 0.07, 0.1, 0.09), 0.035, 2, bm=bm)
    for sx in (-1, 1):
        rbox_bm((sx * YOKE_X, 0, (POLE_TOP + PIV_Z) / 2 + 0.01), (0.07, 0.1, PIV_Z - POLE_TOP + 0.1), 0.03, 2, bm=bm)
    fin("Stand", bm, "SH_Walnut", angle=45)
    gold = bmesh.new()
    for f in feet:
        ellipsoid_bm((f.x, f.y, 0.045), (0.075, 0.075, 0.05), 10, 5, bm=gold)
    torus_bm(0.1, 0.032, 12, 5, bm=gold, matrix=Matrix.Translation((0, 0, HUB_Z + 0.075)))
    torus_bm(0.08, 0.034, 12, 5, bm=gold, matrix=Matrix.Translation((0, 0, 0.82)))
    tube_bm([(0, -0.07, 0.82), (0, -0.15, 0.82)], 0.026, 6, bm=gold)
    ellipsoid_bm((0, -0.17, 0.82), (0.055, 0.045, 0.045), 8, 5, bm=gold)
    fin("StandGold", gold, "SH_Gold", angle=60)
    bm = bmesh.new()
    for sx in (-1, 1):
        m = Matrix.Translation((sx * (YOKE_X + 0.03), 0, PIV_Z)) @ Matrix.Rotation(sx * math.pi / 2, 4, "Y")
        slab_bm(star_outline(0.08, 0.04), 0.04, 0.014, 1, bm=bm, matrix=m)
    fin("PivotStars", bm, "SH_Gold", angle=30)


def build_head():
    S = Matrix.Scale(HS, 4)
    M = HEAD_M @ S
    prof = [(0.0, -0.21), (0.08, -0.21), (0.13, -0.195), (0.16, -0.16), (0.17, -0.11), (0.17, 0.15),
            (0.15, 0.16), (0.0, 0.16)]
    fin("Head", lathe_bm(prof, 18, matrix=M), "SH_Plum", angle=45)
    gold = bmesh.new()
    torus_bm(0.175, 0.03, 18, 6, bm=gold, matrix=M @ Matrix.Translation((0, 0, 0.165)))
    torus_bm(0.172, 0.02, 18, 4, bm=gold, matrix=M @ Matrix.Translation((0, 0, -0.07)))
    for sx in (-1, 1):
        tube_bm([(sx * (HEAD_R - 0.01), 0, PIV_Z), (sx * (YOKE_X - 0.01), 0, PIV_Z)], 0.045, 8, bm=gold)
    pts = [M @ Vector(p) for p in ((0, 0.16, -0.12), (0, 0.23, -0.08), (0, 0.245, 0.0), (0, 0.23, 0.08), (0, 0.16, 0.11))]
    tube_bm(catmull(pts, 2), 0.03, 6, bm=gold)
    fin("HeadGold", gold, "SH_Gold", angle=60)
    prof = [(0.0, 0.225), (0.08, 0.214), (0.13, 0.192), (0.15, 0.168), (0.14, 0.15), (0.0, 0.15)]
    fin("Lens", lathe_bm(prof, 18, matrix=M), "SH_Lamp", angle=70)
    bm = bmesh.new()
    for sx in (-1, 1):
        m = M @ Matrix.Translation((sx * 0.19, 0, 0.17)) @ Matrix.Rotation(sx * math.radians(-28), 4, "Y") \
            @ Matrix.Translation((0, 0, 0.07))
        rbox_bm((0, 0, 0), (0.034, 0.25, 0.17), 0.014, 2, bm=bm, matrix=m)
    fin("BarnDoors", bm, "SH_Plum", angle=45)

out, flags = cli()
begin()
build_stand()
build_head()
ob = join_all("ShopSpotlight")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.95, -0.1, 0), target=(-0.35, 0.0, 0.8), ortho=2.6)
