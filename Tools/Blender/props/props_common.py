import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MODELS_DIR = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Models", "Shop")
DRAGON_FBX = os.path.join(ROOT, "Assets", "Suriyun", "Dragons_SD", "FBX", "DragonSD_A.fbx")
GAME_MONCHI_SCALE = 0.7

PALETTE = {
    "SH_Wood": "E8B070",
    "SH_WoodDark": "B87A47",
    "SH_WoodDeep": "8E5735",
    "SH_Cream": "F8EDD6",
    "SH_Beige": "E8D6AC",
    "SH_Mint": "7DD6B5",
    "SH_MintSoft": "9FD8C4",
    "SH_Coral": "F2786A",
    "SH_Peach": "F7AE9C",
    "SH_Straw": "F9DA7E",
    "SH_StrawDark": "C99341",
    "SH_Sky": "8CC8EE",
    "SH_Lilac": "B9A4E0",
    "SH_Water": "6FC3E8",
    "SH_Glass": "CDEFF2",
    "SH_Chrome": "D9CBB4",
    "SH_Lamp": "FFD47A",
    "SH_Dark": "3A322D",
    "SH_Screen": "1F5A3A",
    "SH_White": "FFF8EA",
    "SH_Honey": "C98A4B",
    "SH_Oak": "D9A86A",
    "SH_Walnut": "7A4E2D",
    "SH_Timber": "5E3B22",
    "SH_Parchment": "EFE0BF",
    "SH_Stone": "B9AFA2",
    "SH_StoneDark": "8D8376",
    "SH_Sage": "9CB38A",
    "SH_Moss": "6E8F5A",
    "SH_Teal": "5E9C94",
    "SH_Plum": "8E6A8F",
    "SH_Gold": "E2B04A",
    "SH_Leaf": "7FAF5E",
}

UP = Vector((0, 0, 1))
MATS = {}
PARTS = []


def cli():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = a[0] if a else ""
    return out, set(a[1:])


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def begin():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MATS.clear()
    PARTS.clear()
    for name, hx in PALETTE.items():
        rgb = [srgb_to_linear(int(hx[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if m.node_tree else None
        if bsdf is not None:
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
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(MATS[mat])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    PARTS.append(ob)
    return ob


def xf(bm, m, verts=None):
    bmesh.ops.transform(bm, matrix=m, verts=list(bm.verts) if verts is None else verts)
    return bm


def lathe_bm(prof, segs, sy=1.0, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = []
    for r, z in prof:
        if r <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
            continue
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs) * sy, z))
                      for k in range(segs)])
    new = [v for ring in rings for v in ring]
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
        bmesh.ops.transform(bm, matrix=matrix, verts=new)
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
    if not isinstance(radii, (list, tuple)):
        radii = [radii] * n
    rings = []
    prev_side = None
    for i, (p, r) in enumerate(zip(pts, radii)):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
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


def rrect(w, h, r, m, cx=0.0, cy=0.0):
    r = max(0.004, min(r, w / 2 - 0.002, h / 2 - 0.002))
    hw, hh = w / 2 - r, h / 2 - r
    pts = []
    for qx, qy, a0 in ((hw, hh, 0), (-hw, hh, 90), (-hw, -hh, 180), (hw, -hh, 270)):
        for j in range(m + 1):
            a = math.radians(a0 + 90 * j / m)
            pts.append((cx + qx + r * math.cos(a), cy + qy + r * math.sin(a)))
    return pts


def loft(rings, m, cap0=True, cap1=True, bm=None, matrix=None):
    bm = bm or bmesh.new()
    vrings = []
    new = []
    for ring in rings:
        w, h, r, z = ring[:4]
        cx = ring[4] if len(ring) > 4 else 0.0
        cy = ring[5] if len(ring) > 5 else 0.0
        vr = [bm.verts.new((x, y, z)) for x, y in rrect(w, h, r, m, cx, cy)]
        vrings.append(vr)
        new += vr
    n = len(vrings[0])
    for A, B in zip(vrings, vrings[1:]):
        for k in range(n):
            k1 = (k + 1) % n
            bm.faces.new((A[k], A[k1], B[k1], B[k]))
    if cap0:
        bm.faces.new(list(reversed(vrings[0])))
    if cap1:
        bm.faces.new(vrings[-1])
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=new)
    return bm


def rbox_rings(w, d, h, rc, R, seg=3, Rb=0.0, segb=1, z0=0.0, cx=0.0, cy=0.0):
    prof = []
    if Rb > 0:
        for j in range(segb + 1):
            t = math.pi / 2 * j / segb
            prof.append((Rb * (1 - math.sin(t)), Rb * (1 - math.cos(t))))
    else:
        prof.append((0.0, 0.0))
    for j in range(seg + 1):
        t = math.pi / 2 * j / seg
        prof.append((R * (1 - math.cos(t)), h - R + R * math.sin(t)))
    return [(w - 2 * i, d - 2 * i, rc - i, z0 + z, cx, cy) for i, z in prof]


def soft_box(center, size, rc, R, seg=3, Rb=0.0, bm=None):
    w, d, h = size
    rings = rbox_rings(w, d, h, rc, R, seg=seg, Rb=Rb, z0=center[2] - h / 2, cx=center[0], cy=center[1])
    return loft(rings, 4, bm=bm)


def catmull(pts, n):
    P = [Vector(p) for p in pts]
    P = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(P[-2])
    return out


def join_all(name, objs=None):
    objs = objs or PARTS
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    return ob


def report(ob):
    me = ob.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    print("%s verts=%d tris=%d size x=%.3f y=%.3f z=%.3f zmin=%.3f" % (
        ob.name, len(me.vertices), tris, max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), min(zs)))
    print("%s mats" % ob.name, [m.name for m in me.materials])


def export(ob, flags=()):
    if "noexport" in flags:
        return
    path = os.path.join(MODELS_DIR, ob.name + ".fbx")
    os.makedirs(MODELS_DIR, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"},
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                             apply_unit_scale=True, use_mesh_modifiers=True, bake_space_transform=True,
                             mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)
    print("EXPORTED", path)


def setup_scene(floor=14):
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
    bpy.ops.mesh.primitive_plane_add(size=floor, location=(0, 0, -0.001))
    bpy.context.active_object.data.materials.append(fl)


def render(path, az, el, target, ortho, res=(640, 640)):
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


def load_dragon(loc, rot_z=0.0, scale=GAME_MONCHI_SCALE):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=DRAGON_FBX)
    new = [o for o in bpy.data.objects if o not in before]
    body = bpy.data.materials.get("DragonRef") or bpy.data.materials.new("DragonRef")
    body.diffuse_color = (0.80, 0.78, 0.86, 1)
    for o in new:
        if o.parent is None:
            o.scale = o.scale * scale
            o.rotation_euler.z += math.radians(rot_z)
            o.location = Vector(loc)
        if o.type == "MESH":
            if o.name.startswith("Face"):
                o.hide_render = True
            o.data.materials.clear()
            o.data.materials.append(body)
    bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for o in new if o.type == "MESH" and not o.hide_render for c in o.bound_box]
    print("DRAGON_HEIGHT", round(max(zs) - min(zs), 3))
    return new


def read_png(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    arr = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(arr)
    bpy.data.images.remove(img)
    return arr.reshape(h, w, 4)


def contact_sheet(out_dir, cells, path, cell=640, cols=3):
    pad = 8
    rows = (len(cells) + cols - 1) // cols
    W = cols * cell + (cols + 1) * pad
    H = rows * cell + (rows + 1) * pad
    canvas = np.ones((H, W, 4), dtype=np.float32)
    canvas[..., :3] = 0.16
    for idx, name in enumerate(cells):
        img = read_png(os.path.join(out_dir, name))
        r, c = idx // cols, idx % cols
        top = H - pad - (r + 1) * cell - r * pad
        left = pad + c * (cell + pad)
        canvas[top:top + cell, left:left + cell] = img
    img = bpy.data.images.new("sheet", W, H, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    print("SHEET", path)


def preview(ob, out_dir, dragon_loc, dragon_rot=-20.0, target=None, ortho=None):
    if not out_dir:
        return
    os.makedirs(out_dir, exist_ok=True)
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1.0)
    ortho = ortho or span * 1.7 + 0.6
    target = target or (0.0, 0.0, (max(zs) + min(zs)) * 0.5)
    setup_scene()
    load_dragon(dragon_loc, dragon_rot)
    n = ob.name
    cells = []
    for tag, az, el in (("34", 35, 28), ("front", 0, 8), ("iso", 25, 55), ("back", 200, 25), ("side", 90, 8), ("top", 0, 89)):
        f = "%s_%s.png" % (n, tag)
        render(os.path.join(out_dir, f), az, el, target, ortho)
        cells.append(f)
    contact_sheet(out_dir, cells, os.path.join(out_dir, n + "_sheet.png"))
