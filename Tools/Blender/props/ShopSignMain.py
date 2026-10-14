import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

BW, BH, BT = 4.0, 1.1, 0.14
PW, PH, PT = 3.66, 0.8, 0.06
YB = BT / 2
YF = -BT / 2
PZ = BH / 2
HEAD_X = -1.42
TEXT_W = 3.4
ARCH = 0.07
FONT = os.path.join(ROOT, "Assets", "Feel", "MMTools", "Demos", "MMTween", "Fonts", "Lato", "TTF", "Lato-Black.ttf")


def face_m(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def fin(name, bm, mat, angle=50.0):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def arc_points(w, h, r, n):
    pts = [Vector((x, y)) for x, y in rrect(w, h, r, 6)]
    seg = [(pts[i] - pts[i - 1]).length for i in range(len(pts))]
    total = sum(seg)
    out = []
    for k in range(n):
        d = total * k / n
        i = 0
        acc = 0.0
        while acc + seg[(i + 1) % len(pts)] < d:
            acc += seg[(i + 1) % len(pts)]
            i += 1
        a, b = pts[i % len(pts)], pts[(i + 1) % len(pts)]
        t = (d - acc) / max(seg[(i + 1) % len(pts)], 1e-6)
        out.append(a.lerp(b, t))
    return out


def build_board():
    rings = rbox_rings(BW, BH, BT, 0.26, 0.05, seg=2, Rb=0.05, segb=2)
    fin("Back", loft(rings, 4, matrix=face_m(0, YB, PZ)), "SH_WoodDark", angle=50)
    rings = rbox_rings(PW, PH, PT + 0.01, 0.17, 0.03, seg=2)
    fin("Panel", loft(rings, 4, cap0=False, matrix=face_m(0, YF + 0.01, PZ)), "SH_Cream", angle=40)
    bm = bmesh.new()
    for p in arc_points(BW - 0.15, BH - 0.15, 0.2, 30):
        if p.x < HEAD_X + 0.42 and p.y > 0.3:
            continue
        ellipsoid_bm((p.x, YF - 0.005, PZ + p.y), (0.056, 0.045, 0.056), 8, 4, bm=bm)
    fin("Bulbs", bm, "SH_Lamp", angle=80)
    bm = bmesh.new()
    for sx in (-1, 1):
        x = sx * (BW / 2 - 0.55)
        rbox_bm((x, YB - 0.03, 0.12), (0.16, 0.1, 0.22), 0.03, bm=bm)
    fin("Brackets", bm, "SH_WoodDark", angle=50)


def build_text():
    cu = bpy.data.curves.new("SignText", type="FONT")
    cu.font = bpy.data.fonts.load(FONT)
    cu.body = "MoriMonchis"
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = 1.0
    cu.offset = 0.0
    cu.extrude = 0.05
    cu.bevel_depth = 0.03
    cu.bevel_resolution = 1
    cu.resolution_u = 1
    cu.space_character = 1.06
    ob = bpy.data.objects.new("SignText", cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    s = TEXT_W / (max(xs) - min(xs))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    zfront = max(v.co.z for v in bm.verts)
    hw = TEXT_W / 2
    for v in bm.verts:
        x = (v.co.x - cx) * s
        y = (v.co.y - cy) * s
        z = (v.co.z - zfront) * 1.0
        y += ARCH * (1 - (x / hw) ** 2)
        v.co = Vector((x, y, z))
    zthick = 0.05 * 2 + 0.03 * 2
    xf(bm, face_m(0.08, YF - PT - zthick + 0.015, PZ - 0.035))
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0005)
    ypanel = YF - PT - 0.004
    hidden = [f for f in bm.faces if all(v.co.y > ypanel for v in f.verts)]
    bmesh.ops.delete(bm, geom=hidden, context="FACES")
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(4), verts=list(bm.verts), edges=list(bm.edges))
    print("TEXT height", round((max(ys) - min(ys)) * s, 3), "scale", round(s, 3))
    fin("Letters", bm, "SH_Coral", angle=60)


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


def heart_outline(size, n=24):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * size / 32.0, (y + 2.0) * size / 32.0))
    return pts


def build_heart():
    m = face_m(BW / 2 - 0.32, YF + 0.02, BH - 0.02) @ Matrix.Rotation(math.radians(-14), 4, "Z")
    fin("Heart", badge_bm(heart_outline(0.5), 0.1, 0.035, 2, matrix=m), "SH_Coral", angle=60)


HS = 1.2


def build_head():
    hx, hz, hy = HEAD_X, BH + 0.2, 0.0
    first = len(PARTS)
    fin("Head", ellipsoid_bm((hx, hy, hz), (0.4, 0.33, 0.34), 16, 9), "SH_Mint", angle=80)
    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((hx + sx * 0.25, YF - 0.06, BH + 0.01), (0.1, 0.09, 0.075), 10, 5, bm=bm)
    fin("Paws", bm, "SH_Mint", angle=80)
    bm = bmesh.new()
    for sx in (-1, 1):
        p0 = Vector((hx + sx * 0.2, hy + 0.04, hz + 0.24))
        pts = [p0, p0 + Vector((sx * 0.08, 0.05, 0.13)), p0 + Vector((sx * 0.2, 0.12, 0.2)), p0 + Vector((sx * 0.31, 0.2, 0.2))]
        tube_bm(catmull(pts, 3), [0.085, 0.075, 0.066, 0.056, 0.046, 0.036, 0.026, 0.016, 0.006, 0.004], 8, bm=bm)
    for k, dx in enumerate((-0.12, 0.0, 0.12)):
        s = 1.0 - 0.15 * abs(k - 1)
        ellipsoid_bm((hx + dx * 0.35, hy + 0.3, hz + 0.18 - abs(dx) * 0.4), (0.05 * s, 0.07 * s, 0.09 * s), 8, 4, bm=bm)
    fin("Horns", bm, "SH_Cream", angle=80)
    bm = bmesh.new()
    ellipsoid_bm((hx, hy - 0.3, hz - 0.12), (0.2, 0.09, 0.11), 12, 6, bm=bm)
    fin("Muzzle", bm, "SH_Cream", angle=80)
    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((hx + sx * 0.15, hy - 0.285, hz + 0.05), (0.068, 0.04, 0.09), 10, 5, bm=bm)
    fin("Eyes", bm, "SH_WoodDark", angle=80)
    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((hx + sx * 0.15 + 0.02, hy - 0.32, hz + 0.09), (0.024, 0.012, 0.028), 6, 3, bm=bm)
    fin("EyeShine", bm, "SH_Cream", angle=80)
    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((hx + sx * 0.27, hy - 0.22, hz - 0.08), (0.06, 0.03, 0.035), 8, 4, bm=bm)
    fin("Cheeks", bm, "SH_Coral", angle=80)
    piv = Vector((hx, YF, BH))
    m = Matrix.Translation(piv) @ Matrix.Scale(HS, 4) @ Matrix.Translation(-piv)
    for ob in PARTS[first:]:
        ob.data.transform(m)


out, flags = cli()
begin()
build_board()
build_text()
build_head()
build_heart()
ob = join_all("ShopSignMain")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(2.6, -0.4, 0), target=(0.0, 0.0, 0.8), ortho=5.4)
if out and "close" in flags:
    render(os.path.join(out, "ShopSignMain_close.png"), 10, 12, (-0.4, 0.0, 0.75), 2.4, res=(900, 900))
