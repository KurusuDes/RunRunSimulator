import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

W = 1.60
D = 0.45
SIDE_T = 0.08
FRONT = -D / 2
UP_FRONT = -0.115
TOP = 1.30
LOW_Z = 0.385
UPP_Z = 0.92
NEST_X = (-0.47, 0.0, 0.47)
LOW_Y = -0.035
UPP_Y = 0.045
NEST_R = 0.128
NEST_T = 0.05
EGG_H = 0.28
EGG_SEAT = 0.03


def fillet(corners, segs=4):
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


def slab(pts, thick, to3d, bev=0.02, bsegs=2, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.faces)
    A = [bm.verts.new(to3d(p.x, p.y, -thick / 2)) for p in pts]
    B = [bm.verts.new(to3d(p.x, p.y, thick / 2)) for p in pts]
    n = len(pts)
    caps = [bm.faces.new(list(reversed(A))), bm.faces.new(B)]
    for k in range(n):
        bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    new_faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=new_faces)
    edges = list({e for f in caps for e in f.edges})
    bmesh.ops.bevel(bm, geom=edges, offset=bev, offset_type="OFFSET", segments=bsegs, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    return bm


def tri_ngons(bm):
    big = [f for f in bm.faces if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


def rope_torus(R, r, z, segs, sides, wobble, twist, cx=0.0, cy=0.0, bm=None):
    bm = bm or bmesh.new()
    rings = []
    for k in range(segs):
        a = 2 * math.pi * k / segs
        out = Vector((math.cos(a), math.sin(a), 0))
        ring = []
        for j in range(sides):
            b = 2 * math.pi * (j + twist * k / segs) / sides
            rr = r * wobble(a, b)
            ring.append(bm.verts.new(out * R + Vector((cx, cy, z)) + out * math.cos(b) * rr + UP * math.sin(b) * rr))
        rings.append(ring)
    faces = []
    for k in range(segs):
        A, B = rings[k], rings[(k + 1) % segs]
        for j in range(sides):
            faces.append(bm.faces.new((A[j], A[(j + 1) % sides], B[(j + 1) % sides], B[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def build_sides():
    prof = fillet([(FRONT, 0.05, 0.03), (-FRONT, 0.05, 0.03), (-FRONT, TOP, 0.11), (UP_FRONT, TOP, 0.06),
                   (UP_FRONT, 0.90, 0.07), (FRONT, 0.66, 0.09)], 4)
    bm = bmesh.new()
    for s in (-1, 1):
        x0 = s * (W / 2 - SIDE_T / 2)
        slab(prof, SIDE_T, lambda u, v, w, x0=x0: (x0 + w, u, v), bev=0.025, bm=bm)
    finish("Sides", tri_ngons(bm), "SH_WoodDark", angle=45)
    bm = bmesh.new()
    for s in (-1, 1):
        for y in (FRONT + 0.075, -FRONT - 0.075):
            ellipsoid_bm((s * (W / 2 - 0.075), y, 0.05), (0.075, 0.07, 0.05), 8, 4, bm=bm)
    finish("Feet", bm, "SH_WoodDark", angle=70)
    bm = bmesh.new()
    for s in (-1, 1):
        ellipsoid_bm((s * (W / 2 - SIDE_T / 2), 0.055, TOP + 0.045), (0.07, 0.07, 0.065), 10, 5, bm=bm)
    finish("Finials", bm, "SH_Mint", angle=80)


def build_cabinet():
    iw = W - 2 * SIDE_T + 0.02
    bm = rbox_bm((0, 0.005, 0.21), (iw, D - 0.03, 0.32), 0.02, 2)
    finish("Cabinet", bm, "SH_Wood", angle=50)
    bm = bmesh.new()
    dw = (iw - 0.1) / 2
    for s in (-1, 1):
        rbox_bm((s * (dw / 2 + 0.025), FRONT + 0.012, 0.215), (dw, 0.04, 0.22), 0.03, 2, bm=bm)
    finish("Drawers", bm, "SH_Wood", angle=50)
    bm = bmesh.new()
    for s in (-1, 1):
        ellipsoid_bm((s * (dw / 2 + 0.025), FRONT - 0.018, 0.225), (0.045, 0.035, 0.04), 8, 5, bm=bm)
    finish("Knobs", bm, "SH_Mint", angle=80)


def build_shelves():
    iw = W - 2 * SIDE_T + 0.02
    bm = bmesh.new()
    rbox_bm((0, 0.0, LOW_Z - 0.03), (iw, D + 0.01, 0.06), 0.022, 2, bm=bm)
    rbox_bm((0, (UP_FRONT + 0.2) / 2, UPP_Z - 0.03), (iw, 0.2 - UP_FRONT + 0.01, 0.06), 0.022, 2, bm=bm)
    finish("Shelves", bm, "SH_Wood", angle=50)
    bm = bmesh.new()
    rbox_bm((0, FRONT + 0.012, LOW_Z + 0.01), (iw, 0.06, 0.075), 0.028, 2, bm=bm)
    rbox_bm((0, UP_FRONT - 0.01, UPP_Z + 0.01), (iw, 0.06, 0.075), 0.028, 2, bm=bm)
    finish("Lips", bm, "SH_WoodDark", angle=50)


def build_back():
    iw = W - 2 * SIDE_T + 0.02
    bm = bmesh.new()
    z0, z1 = LOW_Z - 0.02, TOP
    n = 4
    h = (z1 - z0) / n
    for i in range(n):
        rbox_bm((0, 0.195, z0 + h * (i + 0.5)), (iw, 0.05, h + 0.004), 0.02, 2, bm=bm)
    finish("BackPlanks", bm, "SH_Mint", angle=50)


def build_crest():
    hw, hh = 0.42, 0.25
    ctrl = [(-hw - 0.08, 0.0), (-hw, 0.05), (-hw * 0.72, hh * 0.7), (-hw * 0.32, hh * 0.97), (0.0, hh),
            (hw * 0.32, hh * 0.97), (hw * 0.72, hh * 0.7), (hw, 0.05), (hw + 0.08, 0.0)]
    pts = [Vector((p.x, p.y)) for p in catmull([(x, y, 0) for x, y in ctrl], 3)]
    pts = [Vector((-hw - 0.08, -0.03))] + pts + [Vector((hw + 0.08, -0.03))]
    yc = 0.195
    bm = slab(pts, 0.07, lambda u, v, w: (u, yc + w, TOP - 0.02 + v), bev=0.022)
    finish("Crest", tri_ngons(bm), "SH_WoodDark", angle=45)
    eh = 0.2
    prof = egg_profile(eh, 0.074)
    m = Matrix.Translation((0, yc - 0.03, TOP + 0.02)) @ Matrix.Diagonal((1.0, 0.45, 1.0, 1.0))
    bm = lathe_bm(prof, 12, matrix=m)
    finish("CrestEgg", bm, "SH_Mint", angle=70)
    bm = bmesh.new()
    zz = [(-0.072, 0.0), (-0.036, 0.03), (0.0, -0.005), (0.036, 0.03), (0.072, 0.0)]
    pts = [(x, yc - 0.03 - 0.034, TOP + 0.02 + eh * 0.5 + z) for x, z in zz]
    tube_bm(pts, [0.011] * len(pts), 5, bm=bm)
    finish("CrestCrack", bm, "SH_WoodDark", angle=70)


def egg_profile(h, r, n=9):
    zc = h * 0.42
    prof = [(0.0, 0.0)]
    for k in range(1, n):
        t = math.pi * k / n
        z = zc - zc * math.cos(t) if t <= math.pi / 2 else zc + (h - zc) * (-math.cos(t))
        prof.append((r * math.sin(t), z))
    prof.append((0.0, h))
    return prof


def build_nests():
    def wob(a, b):
        return 1.0 + 0.08 * math.sin(5 * a + 1.3 * math.sin(b)) + 0.04 * math.sin(9 * a + 2 * b)

    segs, sides = 20, 6
    stripes = [k * sides + j for k in range(segs) for j in range(sides) if j % 2]
    rope = bmesh.new()
    dish = bmesh.new()
    light, dark = bmesh.new(), bmesh.new()
    count = 0
    for level, (zb, yc) in enumerate(((LOW_Z, LOW_Y), (UPP_Z, UPP_Y))):
        for i, xc in enumerate(NEST_X):
            seed = level * 3 + i
            rope_torus(NEST_R, NEST_T, zb + NEST_T * 0.78, segs, sides, wob, 3 * sides, xc, yc, bm=rope)
            count += 1
            prof = [(0.0, zb + 0.024), (0.12, zb + 0.028), (0.155, zb - 0.005)]
            lathe_bm(prof, 12, bm=dish, matrix=Matrix.Translation((xc, yc, 0)))
            for k in range(3):
                a = -math.pi / 2 + (k - 1) * 1.05 + 0.25 * math.sin(seed * 1.7 + k)
                out = Vector((math.cos(a), math.sin(a), 0))
                tang = Vector((-math.sin(a), math.cos(a), 0)) * (1 if (k + seed) % 2 else -1)
                base = Vector((xc, yc, 0)) + out * (NEST_R + 0.02) + Vector((0, 0, zb + NEST_T * 1.45))
                d = (tang * 0.8 + out * 0.5 + UP * 0.2).normalized()
                L = 0.1 + 0.02 * ((k + seed) % 3)
                pts = [base, base + d * L * 0.45, base + d * L * 0.8 - UP * 0.015, base + d * L - UP * 0.04]
                tube_bm(pts, [0.02, 0.017, 0.013, 0.007], 5, bm=dark if (k + seed) % 3 == 0 else light)
    ob = finish("Nests", rope, "SH_Straw", angle=70)
    ob.data.materials.append(MATS["SH_StrawDark"])
    per = segs * sides
    for n in range(count):
        for i in stripes:
            ob.data.polygons[n * per + i].material_index = 1
    finish("NestDish", dish, "SH_StrawDark", angle=60)
    finish("Straws", light, "SH_Straw", angle=70)
    finish("StrawsDark", dark, "SH_StrawDark", angle=70)


def egg_anchors():
    out = []
    for zb, yc in ((LOW_Z, LOW_Y), (UPP_Z, UPP_Y)):
        for xc in NEST_X:
            out.append((xc, yc, zb + EGG_SEAT + EGG_H / 2))
    return out


def test_eggs():
    cols = ["F7AE9C", "B9A4E0", "8CC8EE", "F8EDD6", "9FD8C4", "F2786A"]
    for i, (x, y, z) in enumerate(egg_anchors()):
        hx = cols[i]
        m = bpy.data.materials.new("TestEgg%d" % i)
        m.diffuse_color = tuple(srgb_to_linear(int(hx[j:j + 2], 16) / 255.0) for j in (0, 2, 4)) + (1.0,)
        bm = lathe_bm(egg_profile(EGG_H, 0.1, 10), 16, matrix=Matrix.Translation((x, y, z - EGG_H / 2)))
        for f in bm.faces:
            f.smooth = True
        me = bpy.data.meshes.new("TestEgg%d" % i)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(m)
        o = bpy.data.objects.new("TestEgg%d" % i, me)
        bpy.context.scene.collection.objects.link(o)


def import_ref(path, loc):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    for o in [o for o in bpy.data.objects if o not in before]:
        if o.parent is None:
            o.location = Vector(loc)
        if o.type == "MESH":
            for m in o.data.materials:
                if m and m.node_tree:
                    b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
                    if b:
                        c = b.inputs["Base Color"].default_value
                        m.diffuse_color = (c[0], c[1], c[2], 1.0)


out, flags = cli()
begin()
build_sides()
build_cabinet()
build_shelves()
build_back()
build_crest()
build_nests()
for o in PARTS:
    print("PART %-12s tris=%d" % (o.name, sum(len(f.vertices) - 2 for f in o.data.polygons)))
ob = join_all("ShopEggShelf")
report(ob)
for a in egg_anchors():
    print("EGG_ANCHOR (%.3f, %.3f, %.3f)" % a)
export(ob, flags)
if out:
    test_eggs()
    preview(ob, out, dragon_loc=(1.45, -0.45, 0))
    import_ref(os.path.join(MODELS_DIR, "ShopIncubator.fbx"), (0.0, -0.78, 0.0))
    render(os.path.join(out, "ShopEggShelf_ctx34.png"), 30, 32, (0.3, -0.3, 0.7), 3.0)
    render(os.path.join(out, "ShopEggShelf_ctxhigh.png"), 15, 50, (0.3, -0.3, 0.6), 3.0)
    contact_sheet(out, ["ShopEggShelf_ctx34.png", "ShopEggShelf_ctxhigh.png"],
                  os.path.join(out, "ShopEggShelf_context.png"), cols=2)
