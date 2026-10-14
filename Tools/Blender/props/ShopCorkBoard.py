import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

BC = 1.40
BW = 0.70
BH = 0.55
BAR = 0.068
FD = 0.075
POST_X = BW / 2 + 0.055
POST_R = 0.062
POST_TOP = 1.78
CORK_Y = 0.012
CARD_Y = -0.008


def fillet(corners, segs=3):
    pts = []
    n = len(corners)
    for i in range(n):
        p0 = Vector(corners[i - 1][:2])
        p1 = Vector(corners[i][:2])
        p2 = Vector(corners[(i + 1) % n][:2])
        r = corners[i][2]
        if r <= 0:
            pts.append(p1)
            continue
        d1 = (p0 - p1).normalized()
        d2 = (p2 - p1).normalized()
        th = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        t = r / math.tan(th / 2)
        a = p1 + d1 * t
        b = p1 + d2 * t
        c = p1 + (d1 + d2).normalized() * (r / math.sin(th / 2))
        a0 = math.atan2(a.y - c.y, a.x - c.x)
        a1 = math.atan2(b.y - c.y, b.x - c.x)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(segs + 1):
            ang = a0 + da * k / segs
            pts.append(c + Vector((math.cos(ang), math.sin(ang))) * r)
    return pts


def slab(pts, thick, to3d, bev=0.01, bsegs=2, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.faces)
    A = [bm.verts.new(to3d(p.x, p.y, -thick / 2)) for p in pts]
    B = [bm.verts.new(to3d(p.x, p.y, thick / 2)) for p in pts]
    n = len(pts)
    caps = [bm.faces.new(list(reversed(A))), bm.faces.new(B)]
    for k in range(n):
        bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in before])
    edges = list({e for f in caps for e in f.edges})
    bmesh.ops.bevel(bm, geom=edges, offset=bev, offset_type="OFFSET", segments=bsegs, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    big = [f for f in bm.faces if len(f.verts) > 4]
    bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


def egg_profile(h, r, n=8):
    zc = h * 0.42
    prof = [(0.0, 0.0)]
    for k in range(1, n):
        t = math.pi * k / n
        z = zc - zc * math.cos(t) if t <= math.pi / 2 else zc + (h - zc) * (-math.cos(t))
        prof.append((r * math.sin(t), z))
    prof.append((0.0, h))
    return prof


def on_board(x, z, rot_deg=0.0, y=CARD_Y):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Y")


def build_stand():
    bm = bmesh.new()
    for s in (-1, 1):
        rbox_bm((s * POST_X, 0.0, 0.05), (0.17, 0.58, 0.1), 0.048, 2, bm=bm)
    finish("Skis", bm, "SH_WoodDark", angle=50)
    bm = bmesh.new()
    r = POST_R
    for s in (-1, 1):
        z0 = 0.09
        prof = [(0.0, z0), (r + 0.03, z0), (r + 0.032, z0 + 0.035), (r + 0.008, z0 + 0.07), (r, z0 + 0.1),
                (r, POST_TOP - 0.035), (r * 0.82, POST_TOP - 0.008), (r * 0.45, POST_TOP + 0.004), (0.0, POST_TOP + 0.006)]
        lathe_bm(prof, 12, bm=bm, matrix=Matrix.Translation((s * POST_X, 0, 0)))
    finish("Posts", bm, "SH_WoodDark", angle=40)
    bm = bmesh.new()
    for s in (-1, 1):
        ellipsoid_bm((s * POST_X, 0, POST_TOP + 0.062), (0.08, 0.08, 0.072), 12, 6, bm=bm)
    finish("Finials", bm, "SH_Cream", angle=80)
    bm = rbox_bm((0, 0, 0.44), (2 * POST_X, 0.075, 0.09), 0.03, 2)
    rbox_bm((0, -0.035, BC - BH / 2 - 0.03), (2 * POST_X, 0.15, 0.05), 0.02, 2, bm=bm)
    rbox_bm((0, -0.098, BC - BH / 2 - 0.0), (2 * POST_X - 0.1, 0.04, 0.05), 0.018, 2, bm=bm)
    finish("CrossBar", bm, "SH_Wood", angle=50)


def build_board():
    bm = bmesh.new()
    rbox_bm((0, 0, BC + BH / 2 - BAR / 2), (BW, FD, BAR), 0.026, 2, bm=bm)
    rbox_bm((0, 0, BC - BH / 2 + BAR / 2), (BW, FD, BAR), 0.026, 2, bm=bm)
    for s in (-1, 1):
        rbox_bm((s * (BW / 2 - BAR / 2), 0, BC), (BAR, FD - 0.004, BH - 2 * BAR + 0.03), 0.026, 2, bm=bm)
    finish("Frame", bm, "SH_Wood", angle=50)
    bm = rbox_bm((0, CORK_Y, BC), (BW - 2 * BAR + 0.03, 0.03, BH - 2 * BAR + 0.03), 0.01, 1)
    finish("Cork", bm, "SH_StrawDark", angle=50)
    hw, hh = 0.25, 0.13
    ctrl = [(-hw - 0.05, 0.0), (-hw, 0.03), (-hw * 0.7, hh * 0.72), (-hw * 0.3, hh * 0.97), (0.0, hh),
            (hw * 0.3, hh * 0.97), (hw * 0.7, hh * 0.72), (hw, 0.03), (hw + 0.05, 0.0)]
    pts = [Vector((p.x, p.y)) for p in catmull([(x, y, 0) for x, y in ctrl], 3)]
    pts = [Vector((-hw - 0.05, -0.04))] + pts + [Vector((hw + 0.05, -0.04))]
    z0 = BC + BH / 2
    bm = slab(pts, 0.06, lambda u, v, w: (u, w, z0 + v), bev=0.02)
    finish("Crest", bm, "SH_WoodDark", angle=45)
    m = Matrix.Translation((0, -0.026, z0 + 0.012)) @ Matrix.Diagonal((1.0, 0.45, 1.0, 1.0))
    finish("CrestEgg", lathe_bm(egg_profile(0.115, 0.045), 12, matrix=m), "SH_Cream", angle=70)


def card(bm, x, z, w, h, rot):
    rbox_bm((0, 0, 0), (w, 0.014, h), 0.012, 1, bm=bm, matrix=on_board(x, z, rot))


def build_cards():
    cards = bmesh.new()
    parents = [(-0.14, BC + 0.095, -7.0), (0.14, BC + 0.1, 6.0)]
    child = (0.0, BC - 0.12, 2.0)
    note = (0.205, BC - 0.13, 14.0)
    for x, z, r in parents:
        card(cards, x, z, 0.15, 0.16, r)
    card(cards, child[0], child[1], 0.15, 0.15, child[2])
    card(cards, note[0], note[1], 0.1, 0.085, note[2])
    finish("Cards", cards, "SH_Cream", angle=50)
    ink = bmesh.new()
    for x, z, r in parents:
        sub = bmesh.new()
        ellipsoid_bm((0, 0, -0.012), (0.044, 0.01, 0.037), 10, 4, bm=sub)
        for s in (-1, 1):
            tube_bm([(s * 0.026, 0, 0.012), (s * 0.034, 0, 0.034), (s * 0.04, 0, 0.05)], [0.013, 0.01, 0.005], 5, bm=sub)
        xf(sub, on_board(x, z, r, CARD_Y - 0.009))
        me = bpy.data.meshes.new("tmp")
        sub.to_mesh(me)
        sub.free()
        ink.from_mesh(me)
        bpy.data.meshes.remove(me)
    m = on_board(child[0], child[1] - 0.045, child[2], CARD_Y - 0.009) @ Matrix.Diagonal((1.0, 0.25, 1.0, 1.0))
    lathe_bm(egg_profile(0.085, 0.033), 10, bm=ink, matrix=m)
    for k in range(2):
        rbox_bm((0, 0, 0), (0.065 - 0.02 * k, 0.01, 0.013), 0.005, 1, bm=ink,
                matrix=on_board(note[0], note[1] + 0.008 - 0.026 * k, note[2], CARD_Y - 0.009))
    finish("Ink", ink, "SH_WoodDark", angle=60)
    red = bmesh.new()
    pins = [(x, z + 0.058) for x, z, r in parents] + [(child[0], child[1] + 0.055), (note[0] - 0.01, note[1] + 0.03)]
    for x, z in pins:
        ellipsoid_bm((x, CARD_Y - 0.02, z), (0.026, 0.018, 0.026), 10, 5, bm=red)
    (pa, pb, pc) = pins[0], pins[1], pins[2]
    yb = CARD_Y - 0.017
    for p in (pa, pb):
        pts = catmull([(p[0], yb, p[1]), ((p[0] + pc[0]) / 2 + 0.01 * (1 if p[0] < 0 else -1), yb + 0.006,
                                           (p[1] + pc[1]) / 2 - 0.02), (pc[0], yb, pc[1])], 3)
        tube_bm(pts, [0.009] * len(pts), 5, bm=red)
    pts = catmull([(pa[0], yb, pa[1]), (0.0, yb + 0.004, (pa[1] + pb[1]) / 2 - 0.035), (pb[0], yb, pb[1])], 4)
    tube_bm(pts, [0.009] * len(pts), 5, bm=red)
    heart = []
    for k in range(24):
        t = 2 * math.pi * k / 24
        heart.append(Vector((16 * math.sin(t) ** 3, 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t)
                             - math.cos(4 * t))) * 0.0026)
    hz = (pa[1] + pb[1]) / 2 - 0.04
    slab(heart, 0.022, lambda u, v, w: (u, CARD_Y - 0.02 + w, hz + v), bev=0.007, bm=red)
    finish("Accents", red, "SH_Coral", angle=55)


out, flags = cli()
begin()
build_stand()
build_board()
build_cards()
for o in PARTS:
    print("PART %-9s tris=%d" % (o.name, sum(len(f.vertices) - 2 for f in o.data.polygons)))
ob = join_all("ShopCorkBoard")
report(ob)
print("BOARD_CENTER z=%.3f" % BC)
export(ob, flags)
if out:
    preview(ob, out, dragon_loc=(1.05, -0.3, 0))
    render(os.path.join(out, "ShopCorkBoard_cfront.png"), 0, 4, (0, 0, BC + 0.05), 1.0)
    render(os.path.join(out, "ShopCorkBoard_c34.png"), 30, 30, (0, 0, BC), 1.1)
    contact_sheet(out, ["ShopCorkBoard_cfront.png", "ShopCorkBoard_c34.png"], os.path.join(out, "ShopCorkBoard_close.png"), cols=2)
