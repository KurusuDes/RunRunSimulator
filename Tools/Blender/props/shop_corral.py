import bpy, bmesh, math, os, sys, random
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FBX_OUT = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Models", "Shop", "ShopCorral.fbx")
DRAGON_FBX = os.path.join(ROOT, "Assets", "Suriyun", "Dragons_SD", "FBX", "DragonSD_A.fbx")

PALETTE = {
    "CR_Wood": "E8B070",
    "CR_WoodDark": "B87A47",
    "CR_Cream": "F8EDD6",
    "CR_Mint": "7DD6B5",
    "CR_Straw": "F9DA7E",
}

HALF = 1.40
BASE_H = 0.11
FENCE = 1.25
POST_R = 0.085
POST_TOP = 0.66
GATE_TOP = 0.82
GATE_HALF = 0.50
GATE_OPEN = 62.0
RAIL_ZS = (0.27, 0.50)
RAIL_H = 0.15
RAIL_T = 0.07

UP = Vector((0, 0, 1))
MATS = {}
PARTS = []


def cli():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = a[0] if a else ""
    return out, set(a[1:])


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def make_materials():
    for name, hx in PALETTE.items():
        rgb = [srgb_to_linear(int(hx[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF") or m.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
        m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
        m.roughness = 0.85
        MATS[name] = m


def finish(name, bm, mat, smooth=True, angle=40.0):
    for f in bm.faces:
        f.smooth = smooth
    if smooth and angle is not None:
        thr = math.radians(angle)
        for e in bm.edges:
            if e.is_manifold and e.calc_face_angle(0.0) > thr:
                e.smooth = False
    print("PART %-14s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(MATS[mat])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    PARTS.append(ob)
    return ob


def lathe_bm(prof, segs, sy=1.0, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = []
    for r, z in prof:
        if r <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
            continue
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs) * sy, z))
                      for k in range(segs)])
    new_verts = [v for ring in rings for v in ring]
    for A, B in zip(rings, rings[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(segs):
            k1 = (k + 1) % segs
            if len(A) == 1:
                bm.faces.new((A[0], B[k1], B[k]))
            elif len(B) == 1:
                bm.faces.new((A[k], A[k1], B[0]))
            else:
                bm.faces.new((A[k], A[k1], B[k1], B[k]))
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=new_verts)
    return bm


def ellipsoid_bm(center, radii, useg=12, vseg=7, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg, radius=1.0)
    for v in [v for v in bm.verts if v not in before]:
        v.co = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2])) + Vector(center)
    return bm


def tube_bm(points, radii, sides=6, bm=None):
    bm = bm or bmesh.new()
    pts = [Vector(p) for p in points]
    n = len(pts)
    rings = []
    prev_side = None
    for i, (p, r) in enumerate(zip(pts, radii)):
        if i == 0:
            t = (pts[1] - p).normalized()
        elif i == n - 1:
            t = (p - pts[i - 1]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        h = prev_side if prev_side is not None else (UP if abs(t.z) < 0.9 else Vector((1, 0, 0)))
        side = (h - t * h.dot(t)).normalized()
        prev_side = side
        up = t.cross(side).normalized()
        rings.append([bm.verts.new(p + side * math.cos(2 * math.pi * k / sides) * r + up * math.sin(2 * math.pi * k / sides) * r)
                      for k in range(sides)])
    faces = []
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            faces.append(bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k])))
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def torus_bm(R, r, segs=24, sides=6, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = []
    for k in range(segs):
        a = 2 * math.pi * k / segs
        out = Vector((math.cos(a), math.sin(a), 0))
        c = out * R
        rings.append([bm.verts.new(c + out * math.cos(2 * math.pi * j / sides) * r + UP * math.sin(2 * math.pi * j / sides) * r)
                      for j in range(sides)])
    faces = []
    for k in range(segs):
        A, B = rings[k], rings[(k + 1) % segs]
        for j in range(sides):
            faces.append(bm.faces.new((A[j], A[(j + 1) % sides], B[(j + 1) % sides], B[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=[v for ring in rings for v in ring])
    return bm


def rbox_bm(center, size, r, segs=2, bm=None, matrix=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    bmesh.ops.create_cube(bm, size=1.0)
    verts = [v for v in bm.verts if v not in before]
    for v in verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    edges = list({e for v in verts for e in v.link_edges})
    bmesh.ops.bevel(bm, geom=edges + verts, offset=r, offset_type="OFFSET", segments=segs, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    verts = [v for v in bm.verts if v not in before]
    m = Matrix.Translation(Vector(center))
    if matrix is not None:
        m = m @ matrix
    bmesh.ops.transform(bm, matrix=m, verts=verts)
    return bm


def rslab_bm(hx, hy, rc, prof, nc=4, bm=None):
    bm = bm or bmesh.new()
    rings = []
    for inset, z in prof:
        if inset is None:
            rings.append([bm.verts.new((0.0, 0.0, z))])
            continue
        ax, ay, r = hx - inset, hy - inset, max(rc - inset, 0.005)
        ring = []
        for cx, cy, a0 in ((ax - r, ay - r, 0), (-(ax - r), ay - r, 90), (-(ax - r), -(ay - r), 180), (ax - r, -(ay - r), 270)):
            for i in range(nc + 1):
                a = math.radians(a0 + 90.0 * i / nc)
                ring.append(bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z)))
        rings.append(ring)
    faces = []
    for A, B in zip(rings, rings[1:]):
        n = max(len(A), len(B))
        for k in range(n):
            k1 = (k + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new((A[0], B[k1], B[k])))
            elif len(B) == 1:
                faces.append(bm.faces.new((A[k], A[k1], B[0])))
            else:
                faces.append(bm.faces.new((A[k], A[k1], B[k1], B[k])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def build_base():
    h = BASE_H
    prof = [(None, 0.0), (0.0, 0.0), (0.0, h - 0.05), (0.014, h - 0.014), (0.05, h), (None, h)]
    finish("Base", rslab_bm(HALF, HALF, 0.17, prof, 4), "CR_WoodDark", angle=50)
    b = h - 0.01
    prof = [(None, b), (0.0, b), (0.0, b + 0.03), (0.018, b + 0.05), (0.05, b + 0.058), (None, b + 0.06)]
    finish("StrawBed", rslab_bm(FENCE - 0.2, FENCE - 0.2, 0.34, prof, 4), "CR_Straw", angle=60)


def post_bm(x, y, top, r, bm):
    z0 = BASE_H
    prof = [(0.0, z0), (r + 0.022, z0), (r + 0.024, z0 + 0.03), (r + 0.006, z0 + 0.06), (r, z0 + 0.09),
            (r, top - 0.035), (r * 0.82, top - 0.008), (r * 0.45, top + 0.004), (0.0, top + 0.006)]
    return lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((x, y, 0)))


def build_posts():
    F = FENCE
    posts = [(-F, -F), (F, -F), (F, F), (-F, F), (-0.62, -F), (0.62, -F), (0, F), (-F, 0)]
    gates = [(F, -GATE_HALF), (F, GATE_HALF)]
    bm = bmesh.new()
    balls = bmesh.new()
    gballs = bmesh.new()
    for x, y in posts:
        post_bm(x, y, POST_TOP, POST_R, bm)
        ellipsoid_bm((x, y, POST_TOP + 0.064), (0.08, 0.08, 0.072), 10, 6, bm=balls)
    for x, y in gates:
        post_bm(x, y, GATE_TOP, POST_R + 0.014, bm)
        ellipsoid_bm((x, y, GATE_TOP + 0.078), (0.098, 0.098, 0.088), 10, 6, bm=gballs)
    finish("Posts", bm, "CR_WoodDark", angle=40)
    finish("PostBalls", balls, "CR_Cream", angle=80)
    finish("GateBalls", gballs, "CR_Mint", angle=80)


def rail(bm, a, b, z, out):
    a, b = Vector(a), Vector(b)
    d = (b - a)
    L = d.length
    ang = math.atan2(d.y, d.x)
    c = (a + b) / 2 + Vector(out[:2]) * (POST_R + RAIL_T / 2 - 0.012)
    rot = Matrix.Rotation(ang, 4, "Z")
    rbox_bm((c.x, c.y, z), (L, RAIL_T, RAIL_H), 0.024, 2, bm=bm, matrix=rot)


def build_rails():
    bm = bmesh.new()
    ext = 0.09
    F = FENCE
    for z in RAIL_ZS:
        rail(bm, (-F - ext, -F), (F + ext, -F), z, (0, -1, 0))
        rail(bm, (-F - ext, F), (F + ext, F), z, (0, 1, 0))
        rail(bm, (-F, -F - ext), (-F, F + ext), z, (-1, 0, 0))
        rail(bm, (F, -F - ext), (F, -GATE_HALF - 0.02), z, (1, 0, 0))
        rail(bm, (F, GATE_HALF + 0.02), (F, F + ext), z, (1, 0, 0))
    finish("Rails", bm, "CR_Wood", angle=50)


def build_gate_leaf():
    hinge = Matrix.Translation((FENCE, -GATE_HALF, 0)) @ Matrix.Rotation(math.radians(-GATE_OPEN), 4, "Z")
    L = 2 * GATE_HALF - 0.16
    u0 = 0.11
    bm = bmesh.new()
    for z in RAIL_ZS:
        rbox_bm((0, 0, 0), (L, RAIL_T, RAIL_H * 0.9), 0.024, 2, bm=bm,
                matrix=hinge @ Matrix.Translation((0, u0 + L / 2, z)) @ Matrix.Rotation(math.pi / 2, 4, "Z"))
    zc = (RAIL_ZS[0] + RAIL_ZS[1]) / 2
    sh = RAIL_ZS[1] - RAIL_ZS[0] + RAIL_H + 0.08
    for u in (u0 + 0.05, u0 + L - 0.05):
        rbox_bm((0, 0, 0), (RAIL_T + 0.025, 0.1, sh), 0.03, 2, bm=bm, matrix=hinge @ Matrix.Translation((0, u, zc)))
    du = L - 0.2
    dz = RAIL_ZS[1] - RAIL_ZS[0]
    tilt = math.atan2(dz, du)
    rbox_bm((0, 0, 0), (math.hypot(du, dz) + 0.06, RAIL_T - 0.01, 0.09), 0.022, 2, bm=bm,
            matrix=hinge @ Matrix.Translation((0.012, u0 + L / 2, zc)) @ Matrix.Rotation(math.pi / 2, 4, "Z")
            @ Matrix.Rotation(-tilt, 4, "Y"))
    finish("GateLeaf", bm, "CR_Mint", angle=50)


def build_sign():
    y = -FENCE - POST_R - RAIL_T - 0.03
    zc = 0.30
    w, h = 0.76, 0.30
    bm = bmesh.new()
    rbox_bm((0, y, zc), (w, 0.045, h), 0.04, 2, bm=bm)
    finish("Sign", bm, "CR_Cream", angle=50)
    bm = bmesh.new()
    rbox_bm((0, y + 0.018, zc), (w + 0.07, 0.04, h + 0.07), 0.05, 2, bm=bm)
    finish("SignFrame", bm, "CR_Mint", angle=50)
    rope = bmesh.new()
    top_rail = RAIL_ZS[1]
    ry = -FENCE - POST_R - RAIL_T / 2 + 0.012
    for s in (-1, 1):
        x = s * (w / 2 - 0.08)
        tube_bm([(x, y + 0.01, zc + h / 2 - 0.02), (x, y - 0.005, top_rail + RAIL_H / 2 - 0.01),
                 (x, ry - RAIL_T / 2 - 0.012, top_rail + RAIL_H / 2 + 0.018)], [0.014, 0.014, 0.014], 6, bm=rope)
        m = Matrix.Translation((x, ry, top_rail + RAIL_H / 2 - 0.005)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
        torus_bm(0.06, 0.017, 10, 5, bm=rope, matrix=m @ Matrix.Diagonal((0.9, 1.0, 1.0, 1.0)))
    finish("SignRope", rope, "CR_WoodDark", angle=70)


def build_cushion():
    R = 0.64
    H = 0.2
    cx, cy = 0.05, 0.08
    z0 = BASE_H + 0.035
    prof = [(0.0, z0), (R - 0.08, z0), (R - 0.015, z0 + 0.03), (R + 0.012, z0 + H * 0.42), (R - 0.03, z0 + H * 0.8),
            (R - 0.14, z0 + H * 0.98), (R * 0.5, z0 + H * 1.0), (0.13, z0 + H * 0.84), (0.0, z0 + H * 0.76)]
    bm = lathe_bm(prof, 24, sy=0.88)
    bmesh.ops.translate(bm, vec=(cx, cy, 0), verts=bm.verts)
    finish("Cushion", bm, "CR_Mint", angle=70)
    m = Matrix.Translation((cx, cy, z0 + H * 0.42)) @ Matrix.Diagonal((1.0, 0.88, 1.0, 1.0))
    bm = torus_bm(R + 0.014, 0.03, 24, 5, matrix=m)
    finish("CushionPiping", bm, "CR_Cream", angle=70)
    bm = ellipsoid_bm((cx, cy, z0 + H * 0.78), (0.07, 0.062, 0.035), 10, 5)
    finish("CushionButton", bm, "CR_Cream", angle=80)


def build_straw():
    sx, sy, sz = 0.56, 0.36, 0.3
    place = Matrix.Translation((0.66, 0.76, BASE_H + 0.05 + sz / 2)) @ Matrix.Rotation(math.radians(28), 4, "Z")
    bm = rbox_bm((0, 0, 0), (sx, sy, sz), 0.07, 2, matrix=place)
    finish("HayBale", bm, "CR_Straw", angle=55)
    bm = bmesh.new()
    for u in (-0.15, 0.15):
        rbox_bm((0, 0, 0), (0.05, sy + 0.022, sz + 0.022), 0.08, 2, bm=bm, matrix=place @ Matrix.Translation((u, 0, 0)))
    finish("HayTwine", bm, "CR_WoodDark", angle=55)


def join_all():
    bpy.ops.object.select_all(action="DESELECT")
    for o in PARTS:
        o.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "ShopCorral"
    ob.data.name = "ShopCorral"
    return ob


def export(ob):
    os.makedirs(os.path.dirname(FBX_OUT), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=FBX_OUT, use_selection=True, object_types={"MESH"},
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                             apply_unit_scale=True, use_mesh_modifiers=True, bake_space_transform=True,
                             mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)


def setup_scene():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_object_outline = True
    sh.object_outline_color = (0.12, 0.1, 0.09)
    sh.show_backface_culling = True
    sh.show_shadows = True
    sh.shadow_intensity = 0.35
    sc.display.light_direction = (0.35, -0.45, 0.82)
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.35
    sc.render.film_transparent = False
    sc.world = sc.world or bpy.data.worlds.new("World")
    sc.world.color = (0.42, 0.45, 0.48)
    fl = bpy.data.materials.new("Floor")
    fl.diffuse_color = (0.33, 0.36, 0.38, 1)
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, -0.001))
    bpy.context.active_object.data.materials.append(fl)


def render(path, az, el, target, ortho, res):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ortho
    cd.clip_end = 100
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    a, e = math.radians(az), math.radians(el)
    t = Vector(target)
    cam.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * 12
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def load_dragon(loc, rot_z):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=DRAGON_FBX)
    new = [o for o in bpy.data.objects if o not in before]
    body = bpy.data.materials.get("DragonRef") or bpy.data.materials.new("DragonRef")
    body.diffuse_color = (0.80, 0.78, 0.86, 1)
    for o in new:
        if o.parent is None:
            o.rotation_euler.z += math.radians(rot_z)
            o.location += Vector(loc)
        if o.type == "MESH":
            if o.name.startswith("Face"):
                o.hide_render = True
            o.data.materials.clear()
            o.data.materials.append(body)
    bpy.context.view_layer.update()
    for o in new:
        if o.type == "MESH" and not o.hide_render:
            P = [o.matrix_world @ Vector(c) for c in o.bound_box]
            print("DRAGON", o.name, [round(min(p[i] for p in P), 2) for i in range(3)],
                  [round(max(p[i] for p in P), 2) for i in range(3)])


def read_png(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    arr = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(arr)
    bpy.data.images.remove(img)
    return arr.reshape(h, w, 4)


def contact_sheet(out_dir, cells, path, cell=640):
    pad = 8
    W = len(cells) * cell + (len(cells) + 1) * pad
    H = cell + 2 * pad
    canvas = np.ones((H, W, 4), dtype=np.float32)
    canvas[..., :3] = 0.16
    for idx, name in enumerate(cells):
        img = read_png(os.path.join(out_dir, name))
        left = pad + idx * (cell + pad)
        canvas[pad:pad + cell, left:left + cell] = img
    img = bpy.data.images.new("sheet", W, H, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()


def main():
    out_dir, flags = cli()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    build_base()
    build_cushion()
    build_straw()
    build_posts()
    build_rails()
    build_gate_leaf()
    build_sign()
    ob = join_all()
    bpy.context.view_layer.update()
    me = ob.data
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    print("CORRAL verts=%d tris=%d" % (len(me.vertices), tris))
    print("CORRAL size x=%.3f y=%.3f z=%.3f zmin=%.3f" % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), min(zs)))
    print("CORRAL mats", [m.name for m in me.materials])
    if "noexport" not in flags:
        export(ob)
        print("EXPORTED", FBX_OUT)
    if not out_dir:
        return
    os.makedirs(out_dir, exist_ok=True)
    setup_scene()
    load_dragon((0.05, -0.12, 0.26), -20)
    render(os.path.join(out_dir, "c_34.png"), 35, 28, (0, 0, 0.5), 4.0, (640, 640))
    render(os.path.join(out_dir, "c_iso.png"), 25, 55, (0, 0, 0.35), 3.8, (640, 640))
    load_dragon((2.75, -0.5, 0), 30)
    render(os.path.join(out_dir, "c_side.png"), 8, 6, (1.0, 0, 0.7), 5.6, (640, 640))
    contact_sheet(out_dir, ["c_34.png", "c_iso.png", "c_side.png"], os.path.join(out_dir, "corral_sheet.png"))
    print("SHEET", os.path.join(out_dir, "corral_sheet.png"))


main()
