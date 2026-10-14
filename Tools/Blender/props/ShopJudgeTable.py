import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

W, D = 1.6, 0.54
TOP = 0.8
TOP_T = 0.07
LEG_X, LEG_Y = 0.68, 0.17
YF = -D / 2


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


def heart_outline(size, cx=0.0, cy=0.0, n=20):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * size / 32.0, cy + (y + 2.0) * size / 32.0))
    return pts


def scallop_outline(w, h0, hs, nsw, per=6):
    hw = w / 2
    pts = [(hw, 0.0), (-hw, 0.0)]
    sw = w / nsw
    for k in range(nsw):
        x0 = -hw + k * sw
        for j in range(per + 1):
            if k > 0 and j == 0:
                continue
            t = j / per
            pts.append((x0 + sw * t, -h0 - hs * math.sin(math.pi * t)))
    return pts


def build_table():
    rings = rbox_rings(W, D, TOP_T, 0.1, 0.03, seg=2, Rb=0.02, segb=1, z0=TOP - TOP_T)
    fin("Top", loft(rings, 4), "SH_Oak", angle=50)
    bm = bmesh.new()
    rbox_bm((0, 0, TOP - TOP_T - 0.05), (W - 0.14, D - 0.12, 0.11), 0.03, 2, bm=bm)
    rbox_bm((0, YF + 0.075, 0.43), (2 * LEG_X, 0.05, 0.5), 0.02, 1, bm=bm)
    prof = [(0.0, 0.04), (0.05, 0.04), (0.06, 0.1), (0.05, 0.16), (0.044, 0.3), (0.056, 0.42), (0.05, 0.52),
            (0.05, TOP - TOP_T), (0.0, TOP - TOP_T)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((sx * LEG_X, sy * LEG_Y, 0)))
    fin("Frame", bm, "SH_Walnut", angle=45)
    gold = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            ellipsoid_bm((sx * LEG_X, sy * LEG_Y, 0.04), (0.06, 0.06, 0.045), 8, 5, bm=gold)
    fin("Feet", gold, "SH_Gold", angle=60)


def build_cloth():
    w = 1.5
    y = YF - 0.004
    fin("Cloth", slab_bm(scallop_outline(w, 0.2, 0.1, 3, 7), 0.03, 0.012, 2, matrix=face_m(0, y, TOP - 0.01)), "SH_Plum", angle=30)
    gold = bmesh.new()
    tube_bm([(-w / 2 - 0.02, y - 0.03, TOP - 0.025), (w / 2 + 0.02, y - 0.03, TOP - 0.025)], 0.026, 8, bm=gold)
    for k in range(4):
        x = -w / 2 + k * w / 3
        x = max(-w / 2 + 0.03, min(w / 2 - 0.03, x))
        z = TOP - 0.01 - 0.2
        ellipsoid_bm((x, y - 0.035, z - 0.01), (0.035, 0.035, 0.035), 6, 4, bm=gold)
        prof = [(0.0, z - 0.14), (0.03, z - 0.135), (0.045, z - 0.095), (0.03, z - 0.055), (0.0, z - 0.04)]
        lathe_bm(prof, 6, bm=gold, matrix=Matrix.Translation((x, y - 0.035, 0)))
    fin("ClothGold", gold, "SH_Gold", angle=60)
    bm = bmesh.new()
    for k, x in enumerate((-0.5, 0.0, 0.5)):
        slab_bm(star_outline(0.085, 0.04, 0, 0), 0.03, 0.01, 1, bm=bm, matrix=face_m(x, y - 0.02, TOP - 0.16))
    fin("ClothStars", bm, "SH_Gold", angle=30)


def tent_card(x, y, mark, bms):
    h, w, lean = 0.17, 0.2, math.radians(17)
    apex = Matrix.Translation((x, y, TOP - 0.004 + h * math.cos(lean)))
    for side in (-1, 1):
        m = apex @ Matrix.Rotation(side * lean, 4, "X") @ Matrix.Translation((0, side * 0.012, -h / 2))
        rbox_bm((0, 0, 0), (w, 0.028, h), 0.011, 1, bm=bms["card"], matrix=m)
    m = apex @ Matrix.Rotation(-lean, 4, "X") @ Matrix.Translation((0, -0.024, -h / 2)) @ face_m(0, 0, 0)
    if mark == "star":
        slab_bm(star_outline(0.055, 0.026), 0.016, 0.006, 1, bm=bms["gold"], matrix=m)
    else:
        slab_bm(heart_outline(0.1, 0, -0.05), 0.016, 0.006, 1, bm=bms["plum"], matrix=m)


def build_desk_items():
    bms = {"card": bmesh.new(), "gold": bmesh.new(), "plum": bmesh.new()}
    for x, mark in ((-0.5, "star"), (0.0, "heart"), (0.5, "star")):
        tent_card(x, -0.13, mark, bms)
    fin("Cards", bms["card"], "SH_Parchment", angle=50)
    fin("CardStars", bms["gold"], "SH_Gold", angle=30)
    fin("CardHeart", bms["plum"], "SH_Plum", angle=30)
    bx, by = 0.27, 0.08
    prof = [(0.0, TOP - 0.005), (0.085, TOP - 0.005), (0.09, TOP + 0.015), (0.08, TOP + 0.035), (0.0, TOP + 0.035)]
    fin("BellBase", lathe_bm(prof, 14, matrix=Matrix.Translation((bx, by, 0))), "SH_Walnut", angle=50)
    z0 = TOP + 0.03
    prof = [(0.0, z0), (0.072, z0), (0.074, z0 + 0.012), (0.066, z0 + 0.04), (0.05, z0 + 0.068), (0.026, z0 + 0.085),
            (0.0, z0 + 0.09)]
    bm = lathe_bm(prof, 14, matrix=Matrix.Translation((bx, by, 0)))
    prof = [(0.0, z0 + 0.08), (0.012, z0 + 0.08), (0.012, z0 + 0.105), (0.024, z0 + 0.11), (0.026, z0 + 0.125),
            (0.016, z0 + 0.135), (0.0, z0 + 0.137)]
    lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((bx, by, 0)))
    fin("Bell", bm, "SH_Gold", angle=60)
    bm = bmesh.new()
    for sx, x in ((-1, -0.25), (1, -0.62)):
        rbox_bm((x, 0.1, TOP + 0.014), (0.24, 0.17, 0.032), 0.012, 1, bm=bm,
                matrix=Matrix.Rotation(math.radians(8 * sx), 4, "Z"))
    fin("Papers", bm, "SH_Parchment", angle=50)


out, flags = cli()
begin()
build_table()
build_cloth()
build_desk_items()
ob = join_all("ShopJudgeTable")
ys = [v.co.y for v in ob.data.vertices]
ob.data.transform(Matrix.Translation((0, -(max(ys) + min(ys)) / 2, 0)))
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(1.45, -0.55, 0), target=(0.35, 0.0, 0.5), ortho=3.2)
