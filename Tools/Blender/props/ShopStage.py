import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

DECK_Y0, DECK_Y1 = -0.7, 1.0
DECK_TOP = 0.40
PIL_X, PIL_Y, PIL_TOP = 1.36, 0.82, 2.85
BEAM_Z = 2.9
VAL_Y = 0.69
CUR_Y = 0.8
CUR_X0 = 1.27
CUR_TOP = 2.7
TIE_Z = 1.25
BACK_Y = 0.9


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


def smooth_interp(keys, z):
    keys = sorted(keys)
    if z <= keys[0][0]:
        return keys[0][1]
    for (z0, v0), (z1, v1) in zip(keys, keys[1:]):
        if z <= z1:
            t = (z - z0) / (z1 - z0)
            t = t * t * (3 - 2 * t)
            return v0 + (v1 - v0) * t
    return keys[-1][1]


def build_deck():
    cy = (DECK_Y0 + DECK_Y1) / 2
    d = DECK_Y1 - DECK_Y0
    rings = rbox_rings(3.0, d, DECK_TOP - 0.03, 0.12, 0.04, seg=2, Rb=0.02, segb=1, cy=cy)
    fin("DeckBody", loft(rings, 4), "SH_Walnut", angle=50)
    bm = bmesh.new()
    n = 6
    bw = (d - 0.08) / n
    for k in range(n):
        y = DECK_Y0 + 0.04 + bw * (k + 0.5)
        rbox_bm((0, y, DECK_TOP - 0.022), (2.92, bw - 0.014, 0.044), 0.016, 1, bm=bm)
    rbox_bm((0, -0.85, 0.185), (0.94, 0.27, 0.04), 0.016, 1, bm=bm)
    fin("Boards", bm, "SH_Oak", angle=50)
    rings = rbox_rings(1.0, 0.3, 0.17, 0.06, 0.03, seg=2, Rb=0.015, segb=1, cy=-0.85)
    fin("Step", loft(rings, 4), "SH_Walnut", angle=50)


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


def scallop_curve(w, h0, hs, nsw, per=6):
    hw = w / 2
    sw = w / nsw
    pts = []
    for k in range(nsw):
        x0 = -hw + k * sw
        for j in range(per + 1):
            if k > 0 and j == 0:
                continue
            t = j / per
            pts.append((x0 + sw * t, -h0 - hs * math.sin(math.pi * t)))
    return pts


def build_apron():
    plum = bmesh.new()
    gold = bmesh.new()
    y = DECK_Y0 - 0.004
    for sx in (-1, 1):
        cx = sx * 0.99
        w = 0.86
        slab_bm(scallop_outline(w, 0.1, 0.07, 3, 5), 0.03, 0.012, 1, bm=plum, matrix=face_m(cx, y, DECK_TOP - 0.05))
        tube_bm([(cx - w / 2 - 0.01, y - 0.03, DECK_TOP - 0.045), (cx + w / 2 + 0.01, y - 0.03, DECK_TOP - 0.045)], 0.024, 8, bm=gold)
    fin("Apron", plum, "SH_Plum", angle=30)
    fin("StepStar", slab_bm(star_outline(0.075, 0.036), 0.03, 0.01, 1, matrix=face_m(0, -1.0 + 0.012, 0.085)), "SH_Gold", angle=30)
    for x in (-1.22, -0.78, 0.78, 1.22):
        ellipsoid_bm((x, DECK_Y0 + 0.1, DECK_TOP), (0.08, 0.06, 0.055), 8, 5, bm=gold)
    fin("ApronGold", gold, "SH_Gold", angle=70)


def build_frame():
    bm = bmesh.new()
    prof = [(0.0, DECK_TOP - 0.01), (0.13, DECK_TOP - 0.01), (0.135, DECK_TOP + 0.04), (0.12, DECK_TOP + 0.1),
            (0.095, DECK_TOP + 0.16), (0.088, 1.6), (0.084, PIL_TOP - 0.18), (0.1, PIL_TOP - 0.12),
            (0.13, PIL_TOP - 0.06), (0.13, PIL_TOP + 0.01), (0.0, PIL_TOP + 0.01)]
    for sx in (-1, 1):
        lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((sx * PIL_X, PIL_Y, 0)))
    rbox_bm((0, PIL_Y, BEAM_Z), (3.0, 0.26, 0.17), 0.055, 2, bm=bm)
    rbox_bm((0, BACK_Y + 0.045, 1.63), (2.76, 0.05, 2.5), 0.02, 1, bm=bm)
    fin("Frame", bm, "SH_Walnut", angle=45)
    gold = bmesh.new()
    for sx in (-1, 1):
        for z, R in ((DECK_TOP + 0.17, 0.092), (PIL_TOP - 0.19, 0.088)):
            torus_bm(R, 0.028, 10, 4, bm=gold, matrix=Matrix.Translation((sx * PIL_X, PIL_Y, z)))
        ellipsoid_bm((sx * 1.44, PIL_Y, BEAM_Z + 0.12), (0.085, 0.085, 0.08), 8, 5, bm=gold)
    crest = [(0.6 * math.cos(math.pi * k / 12), 0.25 * math.sin(math.pi * k / 12)) for k in range(13)]
    slab_bm(crest, 0.07, 0.025, 2, bm=gold, matrix=face_m(0, PIL_Y + 0.05, BEAM_Z + 0.05))
    fin("FrameGold", gold, "SH_Gold", angle=60)
    fin("CrestStar", slab_bm(star_outline(0.13, 0.06, 0, 0.1), 0.035, 0.012, 1, matrix=face_m(0, PIL_Y - 0.06, BEAM_Z + 0.05)), "SH_Gold", angle=30)
    bm = bmesh.new()
    for x in (-1.05, -0.35, 0.35, 1.05):
        rbox_bm((x, BACK_Y + 0.085, 1.62), (0.16, 0.04, 2.3), 0.015, 1, bm=bm)
    rbox_bm((0, BACK_Y + 0.09, 1.0), (2.5, 0.035, 0.14), 0.015, 1, bm=bm)
    rbox_bm((0, BACK_Y + 0.09, 2.3), (2.5, 0.035, 0.14), 0.015, 1, bm=bm)
    fin("BackBattens", bm, "SH_Oak", angle=50)
    inner = [(0.5 * math.cos(math.pi * k / 12), 0.185 * math.sin(math.pi * k / 12)) for k in range(13)]
    slab_bm_ = slab_bm(inner, 0.03, 0.01, 1, matrix=face_m(0, PIL_Y - 0.015, BEAM_Z + 0.06))
    fin("Crest", slab_bm_, "SH_Parchment", angle=30)


def build_backdrop():
    fin("Backdrop", rbox_bm((0, BACK_Y, 1.63), (2.64, 0.05, 2.44), 0.02, 1), "SH_Parchment", angle=50)
    bm = bmesh.new()
    y = BACK_Y - 0.02
    slab_bm(star_outline(0.3, 0.14), 0.04, 0.014, 1, bm=bm, matrix=face_m(0, y, 1.75))
    for x, z, R in ((-0.5, 2.3, 0.09), (0.55, 2.25, 0.1), (-0.62, 1.25, 0.08), (0.6, 1.15, 0.075), (0.0, 2.45, 0.07)):
        slab_bm(star_outline(R, R * 0.46), 0.03, 0.01, 1, bm=bm, matrix=face_m(x, y, z))
    fin("BackStars", bm, "SH_Gold", angle=30)


def build_valance():
    w = 2.84
    fin("Valance", slab_bm(scallop_outline(w, 0.2, 0.17, 5, 7), 0.05, 0.018, 2, matrix=face_m(0, VAL_Y, BEAM_Z - 0.02)), "SH_Plum", angle=30)
    gold = bmesh.new()
    curve = [(x, VAL_Y - 0.035, BEAM_Z - 0.02 + z) for x, z in scallop_curve(w - 0.04, 0.2, 0.17, 5, 6)]
    tube_bm(curve, 0.024, 5, bm=gold)
    sw = w / 5
    for k in range(6):
        x = -w / 2 + k * sw
        x = max(-w / 2 + 0.05, min(w / 2 - 0.05, x))
        z = BEAM_Z - 0.02 - 0.2
        ellipsoid_bm((x, VAL_Y - 0.04, z - 0.04), (0.037, 0.037, 0.037), 6, 4, bm=gold)
        prof = [(0.0, z - 0.17), (0.03, z - 0.165), (0.045, z - 0.12), (0.03, z - 0.075), (0.012, z - 0.06), (0.0, z - 0.06)]
        lathe_bm(prof, 6, bm=gold, matrix=Matrix.Translation((x, VAL_Y - 0.04, 0)))
    fin("ValanceGold", gold, "SH_Gold", angle=60)


def curtain_bm(sx, bm):
    nz, nx = 12, 8
    widths = [(CUR_TOP, 0.62), (2.15, 0.5), (1.6, 0.3), (TIE_Z, 0.19), (0.95, 0.27), (DECK_TOP, 0.44)]
    rows = []
    for i in range(nz + 1):
        z = CUR_TOP + (DECK_TOP + 0.005 - CUR_TOP) * i / nz
        w = smooth_interp(widths, z)
        gather = 1.0 - w / 0.62
        A = 0.03 + 0.07 * gather
        pull = 0.05 * math.exp(-((z - TIE_Z) / 0.35) ** 2)
        flare = 0.04 * max(0.0, (0.9 - z) / 0.5)
        row = []
        for j in range(nx + 1):
            u = j / nx
            x = sx * (CUR_X0 - w * u)
            y = CUR_Y - A * (0.5 - 0.5 * math.cos(2 * math.pi * 2.5 * u)) - pull - flare * u
            row.append(Vector((x, y, z)))
        rows.append(row)
    th = 0.035
    F = [[bm.verts.new(p) for p in r] for r in rows]
    B = [[bm.verts.new(p + Vector((0, th, 0))) for p in r] for r in rows]
    for i in range(nz):
        for j in range(nx):
            bm.faces.new((F[i][j], F[i][j + 1], F[i + 1][j + 1], F[i + 1][j]))
            bm.faces.new((B[i][j], B[i + 1][j], B[i + 1][j + 1], B[i][j + 1]))
    for i in range(nz):
        for j in (0, nx):
            bm.faces.new((F[i][j], F[i + 1][j], B[i + 1][j], B[i][j]))
    for j in range(nx):
        for i in (0, nz):
            bm.faces.new((F[i][j], B[i][j], B[i][j + 1], F[i][j + 1]))
    zt = TIE_Z
    w = smooth_interp(widths, zt)
    cx = sx * (CUR_X0 - w / 2)
    return cx, w


def build_curtains():
    bm = bmesh.new()
    ties = []
    for sx in (-1, 1):
        ties.append((sx,) + curtain_bm(sx, bm))
    fin("Curtains", bm, "SH_Plum", angle=85)
    gold = bmesh.new()
    for sx, cx, w in ties:
        yc = CUR_Y - 0.045
        m = Matrix.Translation((cx, yc, TIE_Z)) @ Matrix.Diagonal((1.0, 0.62, 1.0, 1.0))
        torus_bm(w / 2 + 0.05, 0.032, 10, 4, bm=gold, matrix=m)
        tx = cx - sx * 0.02
        tube_bm(catmull([(tx, yc - 0.08, TIE_Z - 0.02), (tx + 0.01, yc - 0.1, TIE_Z - 0.14), (tx, yc - 0.1, TIE_Z - 0.24)], 3), 0.018, 6, bm=gold)
        prof = [(0.0, TIE_Z - 0.42), (0.045, TIE_Z - 0.41), (0.065, TIE_Z - 0.34), (0.04, TIE_Z - 0.27), (0.025, TIE_Z - 0.24), (0.0, TIE_Z - 0.235)]
        lathe_bm(prof, 8, bm=gold, matrix=Matrix.Translation((tx, yc - 0.1, 0)))
    fin("TieBacks", gold, "SH_Gold", angle=60)


def build_bunting():
    rope = bmesh.new()
    flags = {"SH_Gold": bmesh.new(), "SH_Parchment": bmesh.new()}
    x0, x1, z0, sag, y = -1.25, 1.25, 2.5, 0.2, 0.62
    n = 12
    pts = [Vector((x0 + (x1 - x0) * k / n, y, z0 - sag * (1 - (2 * k / n - 1) ** 2))) for k in range(n + 1)]
    tube_bm(pts, 0.017, 5, bm=rope)
    fin("BuntingRope", rope, "SH_Walnut", angle=70)
    nf = 9
    tri = [(-0.085, 0.0), (0.085, 0.0), (0.012, -0.19), (-0.012, -0.19)]
    for k in range(nf):
        t = (k + 0.5) / nf
        x = x0 + (x1 - x0) * t
        u = 2 * t - 1
        z = z0 - sag * (1 - u * u)
        ang = math.atan2(2 * sag * u * 2 / (x1 - x0), 1.0)
        m = Matrix.Translation((x, y + 0.012, z + 0.01)) @ Matrix.Rotation(ang, 4, "Y") @ face_m(0, 0, 0)
        mat = "SH_Gold" if k % 2 == 0 else "SH_Parchment"
        slab_bm(tri, 0.025, 0.009, 1, bm=flags[mat], matrix=m)
    fin("FlagsGold", flags["SH_Gold"], "SH_Gold", angle=30)
    fin("FlagsCream", flags["SH_Parchment"], "SH_Parchment", angle=30)


out, flags = cli()
begin()
build_deck()
build_apron()
build_frame()
build_backdrop()
build_valance()
build_curtains()
build_bunting()
ob = join_all("ShopStage")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(0.35, 0.0, DECK_TOP), target=(0.0, 0.0, 1.5), ortho=5.4)
if out and "close" in flags:
    render(os.path.join(out, "ShopStage_close.png"), 20, 15, (0.0, 0.5, 2.0), 2.2, res=(800, 800))
