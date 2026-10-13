import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FBX_DIR = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Models", "Shop")
FBX_PC = os.path.join(FBX_DIR, "ShopPC.fbx")
FBX_DESK = os.path.join(FBX_DIR, "ShopPC_Desk.fbx")
DRAGON_FBX = os.path.join(ROOT, "Assets", "Suriyun", "Dragons_SD", "FBX", "DragonSD_A.fbx")

PALETTE = {
    "PC_Beige": "E8D6AC",
    "PC_Cream": "F7EFDB",
    "PC_Keys": "A0968A",
    "PC_Coral": "F2786A",
    "PC_Mint": "7EE3BC",
    "PC_Dark": "3A322D",
    "PC_Screen": "1F5A3A",
    "PC_Wood": "BC7C4B",
    "PC_WoodDark": "8E5735",
}

DESK_H = 0.75
DESK_W = 0.92
DESK_D = 0.70
TOP_T = 0.085

BASE_W = 0.58
BASE_D = 0.38
BASE_H = 0.13
BASE_Y = 0.14

NECK_H = 0.03

MON_W = 0.54
MON_H = 0.48
MON_D = 0.40
MON_BW = 0.36
MON_BH = 0.32
SCR_W = 0.36
SCR_H = 0.27
SCR_R = 0.05
SCR_CY = 0.025
BULGE = 0.032

KB_W = 0.54
KB_D = 0.20
KB_H = 0.04
KB_WEDGE = 0.75
KB_Y = -0.225

UP = Vector((0, 0, 1))
MATS = {}
PC = []
DESK = []


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
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
        m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
        m.roughness = 0.85
        MATS[name] = m


def finish(name, bm, mat, smooth=True, angle=40.0, group=None):
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
    (PC if group is None else group).append(ob)
    return ob


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


def lathe_bm(prof, segs, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = []
    for r, z in prof:
        if r <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
            continue
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs), z))
                      for k in range(segs)])
    new = [v for ring in rings for v in ring]
    for A, B in zip(rings, rings[1:]):
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


def tube_bm(points, radius, sides=6, bm=None):
    bm = bm or bmesh.new()
    pts = [Vector(p) for p in points]
    n = len(pts)
    rings = []
    prev = None
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        h = prev if prev is not None else (UP if abs(t.z) < 0.9 else Vector((1, 0, 0)))
        side = (h - t * h.dot(t)).normalized()
        prev = side
        up = t.cross(side).normalized()
        rings.append([bm.verts.new(p + side * math.cos(2 * math.pi * k / sides) * radius +
                                   up * math.sin(2 * math.pi * k / sides) * radius) for k in range(sides)])
    faces = []
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            faces.append(bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k])))
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def front_matrix(x, y_back, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y_back), (0, 1, 0, z), (0, 0, 0, 1)))


def build_desk():
    top = rbox_rings(DESK_W, DESK_D, TOP_T, 0.07, 0.03, seg=3, Rb=0.018, segb=2, z0=DESK_H - TOP_T)
    finish("DeskTop", loft(top, 3), "PC_Wood", angle=50, group=DESK)
    apron = rbox_rings(DESK_W - 0.13, DESK_D - 0.13, 0.07, 0.05, 0.012, seg=1, z0=DESK_H - TOP_T - 0.065)
    finish("DeskApron", loft(apron, 2), "PC_WoodDark", angle=50, group=DESK)
    lz = DESK_H - TOP_T + 0.005
    prof = [(0.0, 0.0), (0.04, 0.0), (0.053, 0.012), (0.056, 0.034), (0.064, lz - 0.02), (0.064, lz), (0.0, lz)]
    bm = bmesh.new()
    for sx in (1, -1):
        for sy in (1, -1):
            lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((sx * (DESK_W / 2 - 0.1), sy * (DESK_D / 2 - 0.1), 0)))
    finish("DeskLegs", bm, "PC_WoodDark", angle=50, group=DESK)


def build_base_unit():
    y0 = BASE_Y
    rings = rbox_rings(BASE_W, BASE_D, BASE_H, 0.06, 0.032, seg=3, Rb=0.012, segb=1, z0=DESK_H, cy=y0)
    finish("BaseUnit", loft(rings, 3), "PC_Beige", angle=50)
    yf = y0 - BASE_D / 2
    zc = DESK_H + BASE_H * 0.5 + 0.004
    panel = rbox_rings(0.26, 0.085, 0.016, 0.022, 0.008, seg=2, z0=0.0)
    finish("DrivePanel", loft(panel, 2, cap0=False, matrix=front_matrix(0.125, yf + 0.006, zc)), "PC_Cream", angle=55)
    slot = rbox_rings(0.18, 0.02, 0.008, 0.01, 0.004, seg=1, z0=0.0)
    finish("DriveSlot", loft(slot, 2, cap0=False, matrix=front_matrix(0.11, yf - 0.006, zc + 0.012)), "PC_Dark", angle=60)
    bm = loft(rbox_rings(0.036, 0.022, 0.012, 0.008, 0.005, seg=1), 1, cap0=False,
              matrix=front_matrix(0.205, yf - 0.006, zc - 0.022))
    finish("DriveEject", bm, "PC_Coral", angle=60)
    prof = [(0.0, 0.0), (0.024, 0.0), (0.024, 0.012), (0.019, 0.02), (0.0, 0.022)]
    finish("PowerButton", lathe_bm(prof, 14, matrix=front_matrix(-0.17, yf + 0.004, zc)), "PC_Coral", angle=55)
    prof = [(0.0, 0.0), (0.013, 0.0), (0.013, 0.006), (0.009, 0.013), (0.0, 0.015)]
    finish("LED", lathe_bm(prof, 10, matrix=front_matrix(-0.24, yf + 0.004, zc)), "PC_Mint", angle=70)
    neck = rbox_rings(0.36, 0.26, NECK_H + 0.01, 0.05, 0.008, seg=1, z0=DESK_H + BASE_H - 0.01, cy=y0)
    finish("MonitorNeck", loft(neck, 2), "PC_Keys", angle=50)


def monitor_matrix():
    zc = DESK_H + BASE_H + NECK_H + MON_H / 2
    return front_matrix(0.0, BASE_Y + MON_D / 2, zc), zc


def build_monitor():
    M, zc = monitor_matrix()
    Rb, Rf = 0.045, 0.05
    back_cy = -(MON_H - MON_BH) / 2
    rings = []
    for j in range(4):
        t = math.pi / 2 * j / 3
        i = Rb * (1 - math.sin(t))
        rings.append((MON_BW - 2 * i, MON_BH - 2 * i, 0.08 - i, Rb * (1 - math.cos(t)), 0.0, back_cy))
    zf = MON_D - Rf
    for j in range(5):
        t = math.pi / 2 * j / 4
        i = Rf * (1 - math.cos(t))
        rings.append((MON_W - 2 * i, MON_H - 2 * i, 0.1 - i, zf + Rf * math.sin(t)))
    rings.append((SCR_W + 0.05, SCR_H + 0.05, SCR_R + 0.025, MON_D, 0.0, SCR_CY))
    rings.append((SCR_W + 0.026, SCR_H + 0.026, SCR_R + 0.013, MON_D - 0.01, 0.0, SCR_CY))
    rings.append((SCR_W + 0.012, SCR_H + 0.012, SCR_R + 0.006, MON_D - 0.032, 0.0, SCR_CY))
    finish("Monitor", loft(rings, 3, cap0=True, cap1=False, matrix=M), "PC_Beige", angle=50)
    rings = [(SCR_W + 0.02, SCR_H + 0.02, SCR_R + 0.01, MON_D - 0.036, 0.0, SCR_CY)]
    for t in (1.0, 0.84, 0.64, 0.42, 0.2):
        rings.append((SCR_W * t, SCR_H * t, SCR_R * t, MON_D - 0.026 + BULGE * (1 - t * t), 0.0, SCR_CY))
    finish("Screen", loft(rings, 3, cap0=False, matrix=M), "PC_Screen", angle=None)
    yf = BASE_Y - MON_D / 2
    prof = [(0.0, 0.0), (0.017, 0.0), (0.017, 0.012), (0.013, 0.019), (0.0, 0.02)]
    bm = bmesh.new()
    for x in (0.17, 0.215):
        lathe_bm(prof, 12, bm=bm, matrix=front_matrix(x, yf + 0.004, zc - 0.185))
    finish("Knobs", bm, "PC_Keys", angle=55)
    badge = rbox_rings(0.075, 0.028, 0.008, 0.012, 0.004, seg=1)
    finish("Badge", loft(badge, 2, cap0=False, matrix=front_matrix(-0.17, yf + 0.004, zc - 0.185)), "PC_Coral", angle=60)


def kb_surface(yl):
    return KB_H * (1 + KB_WEDGE * (yl + KB_D / 2) / KB_D)


def build_keyboard():
    rings = rbox_rings(KB_W, KB_D, KB_H, 0.045, 0.016, seg=2, Rb=0.006, segb=1)
    bm = loft(rings, 3)
    for v in bm.verts:
        v.co.z *= 1 + KB_WEDGE * (v.co.y + KB_D / 2) / KB_D
        v.co.y += KB_Y
        v.co.z += DESK_H
    finish("Keyboard", bm, "PC_Beige", angle=50)
    theta = math.atan(KB_H * KB_WEDGE / KB_D)
    rot = Matrix.Rotation(theta, 4, "X")
    pitch = 0.058
    size = 0.048
    rows = [(0.058, [1] * 8), (0.0, [1] * 6 + [2]), (-0.058, [1, 1, 4, 1, 1])]
    keys = bmesh.new()
    coral = bmesh.new()
    cream = bmesh.new()
    for yl, units in rows:
        x = -pitch * 4
        for idx, u in enumerate(units):
            w = size + (u - 1) * pitch
            cxk = x + u * pitch / 2
            x += u * pitch
            target = coral if u == 2 else (cream if u == 4 else keys)
            kr = rbox_rings(w, size, 0.03, 0.012, 0.011, seg=2, z0=-0.01)
            m = Matrix.Translation((cxk, KB_Y + yl, DESK_H + kb_surface(yl))) @ rot
            loft(kr, 2, cap0=False, bm=target, matrix=m)
    finish("Keys", keys, "PC_Keys", angle=55)
    finish("KeyEnter", coral, "PC_Coral", angle=55)
    finish("KeySpace", cream, "PC_Cream", angle=55)


def catmull(pts, n):
    P = [Vector(p) for p in pts]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(P[-2])
    return out


def build_cable():
    d = DESK_H
    path = catmull([(-0.2, KB_Y + KB_D / 2 - 0.01, d + 0.03), (-0.3, -0.1, d + 0.023), (-0.37, -0.02, d + 0.023),
                    (-0.36, 0.07, d + 0.025), (-BASE_W / 2 + 0.01, 0.1, d + 0.05)], 12)
    L = [0.0]
    for a, b in zip(path, path[1:]):
        L.append(L[-1] + (b - a).length)
    total = L[-1]
    coil_r = 0.014
    turns = 8
    n = turns * 8
    pts = []
    prev = None
    for k in range(n + 1):
        s = total * k / n
        j = max(i for i in range(len(L)) if L[i] <= s + 1e-9)
        j = min(j, len(path) - 2)
        f = (s - L[j]) / max(L[j + 1] - L[j], 1e-9)
        p = path[j].lerp(path[j + 1], f)
        t = (path[j + 1] - path[j]).normalized()
        h = prev if prev is not None else UP
        side = (h - t * h.dot(t)).normalized()
        prev = side
        up = t.cross(side).normalized()
        env = min(1.0, k / 6, (n - k) / 6)
        a = 2 * math.pi * turns * k / n
        pts.append(p + (side * math.cos(a) + up * math.sin(a)) * coil_r * env)
    finish("Cable", tube_bm(pts, 0.0075, 5), "PC_Keys", angle=80)


def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    return ob


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def export(ob, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"},
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                             apply_unit_scale=True, use_mesh_modifiers=True, bake_space_transform=True,
                             mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)


def report(ob):
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    print("%s tris=%d size x=%.3f y=%.3f z=%.3f zmin=%.3f" % (ob.name, tris(ob), max(xs) - min(xs), max(ys) - min(ys),
                                                             max(zs) - min(zs), min(zs)))
    print("%s mats" % ob.name, [m.name for m in ob.data.materials])


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
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, -0.001))
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
    cam.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * 10
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def load_dragon(x_offset):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=DRAGON_FBX)
    new = [o for o in bpy.data.objects if o not in before]
    body = bpy.data.materials.new("DragonRef")
    body.diffuse_color = (0.80, 0.78, 0.86, 1)
    for o in new:
        if o.parent is None:
            o.location.x += x_offset
        if o.type == "MESH":
            if o.name == "Face":
                o.hide_render = True
            o.data.materials.clear()
            o.data.materials.append(body)
    bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for o in new if o.type == "MESH" and not o.hide_render for c in o.bound_box]
    print("DRAGON_HEIGHT", round(max(zs) - min(zs), 3), "min", round(min(zs), 3))


def read_png(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    arr = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(arr)
    bpy.data.images.remove(img)
    return arr.reshape(h, w, 4)


def contact_sheet(out_dir, cells, path, cell=600, cols=3):
    pad = 8
    rows = (len(cells) + cols - 1) // cols
    W = cols * cell + (cols + 1) * pad
    H = rows * cell + (rows + 1) * pad
    canvas = np.ones((H, W, 4), dtype=np.float32)
    canvas[..., :3] = 0.16
    for idx, name in enumerate(cells):
        r, c = divmod(idx, cols)
        img = read_png(os.path.join(out_dir, name))
        h, w = img.shape[:2]
        left = pad + c * (cell + pad)
        top = pad + r * (cell + pad)
        canvas[H - top - h:H - top, left:left + w] = img
    img = bpy.data.images.new("sheet", W, H, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()


def main():
    out_dir, flags = cli()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    build_desk()
    build_base_unit()
    build_monitor()
    build_keyboard()
    build_cable()
    pc = join(PC, "ShopPC_Desk")
    solo = pc.copy()
    solo.data = pc.data.copy()
    bpy.context.scene.collection.objects.link(solo)
    solo.data.transform(Matrix.Translation((0, 0, -DESK_H)))
    solo.name = "ShopPC"
    solo.data.name = "ShopPC"
    report(solo)
    if "noexport" not in flags:
        export(solo, FBX_PC)
        print("EXPORTED", FBX_PC)
    bpy.data.objects.remove(solo)
    full = join([pc] + DESK, "ShopPC_Desk")
    report(full)
    if "noexport" not in flags:
        export(full, FBX_DESK)
        print("EXPORTED", FBX_DESK)
    if not out_dir:
        return
    os.makedirs(out_dir, exist_ok=True)
    setup_scene()
    tz = 0.7
    render(os.path.join(out_dir, "v_front.png"), 0, 4, (0, 0, tz), 1.65, (600, 600))
    render(os.path.join(out_dir, "v_34.png"), 35, 14, (0, 0, tz), 1.65, (600, 600))
    render(os.path.join(out_dir, "v_side.png"), 90, 4, (0, 0, tz), 1.65, (600, 600))
    render(os.path.join(out_dir, "v_close.png"), 30, 22, (0, -0.05, 1.0), 0.8, (600, 600))
    render(os.path.join(out_dir, "v_back.png"), 210, 25, (0, 0, tz), 1.65, (600, 600))
    load_dragon(0.85)
    render(os.path.join(out_dir, "v_dragon.png"), 18, 12, (0.4, 0, 0.7), 2.3, (600, 600))
    sheet = os.path.join(out_dir, "pc_sheet.png")
    contact_sheet(out_dir, ["v_front.png", "v_34.png", "v_side.png", "v_close.png", "v_back.png", "v_dragon.png"], sheet)
    print("SHEET", sheet)


main()
