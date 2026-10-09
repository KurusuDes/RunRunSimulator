import sys, os, types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ICON_LIB = os.path.join(ROOT, "Tools", "Blender", "parts", "icon_part.py")
FBX = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Models", "Brawl", "BrawlScarecrow.fbx")
OUT_PNG = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Sprites", "Brawl", "Icon_Scarecrow.png")
PART_ICONS = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Sprites", "PartIcons")
COMPARE = ("Alforja", "Unicornio", "Cristales")

VIEW = (0.35, -1.0, 0.3)
HEAD_PX = 20.5
TOP_PAD = 2.2
HEAD_MIN_Z = 0.76
T_STITCH = 0.45
JUMP = (0.07, 0.25)
T_CROSS = 0.35
T_SHINE = 0.22
CLASSES = ("SC_Stitch", "SC_Cross", "SC_Cheek", "SC_Helmet", "SC_Burlap", "SC_Straw", "SC_Cloth", "SC_Patch", "SC_Wood")
SHIFT = (0, 0, 0, 1, 0, 1, 0, 1, 1, 1)
MOUTH = (0.8, 0.025)
FACE_MIN_Z = 0.82


def load_lib():
    src = open(ICON_LIB, encoding="utf-8").read()
    cut = src.rfind("\ntry:\n    import bpy\nexcept ImportError:")
    if cut < 0:
        raise RuntimeError("icon_part.py: no se encontro el bloque de arranque")
    mod = types.ModuleType("icon_part_lib")
    mod.__file__ = ICON_LIB
    exec(compile(src[:cut], ICON_LIB, "exec"), mod.__dict__)
    return mod


def class_of(name):
    base = name.split(".")[0]
    return CLASSES.index(base) + 1 if base in CLASSES else 0


def linear_to_srgb(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def albedos(objs):
    import numpy as np
    out = np.full((len(CLASSES) + 1, 3), 0.5)
    for o in objs:
        for m in o.data.materials:
            k = class_of(m.name)
            if not k:
                continue
            col = m.diffuse_color
            if m.use_nodes:
                b = m.node_tree.nodes.get("Principled BSDF")
                if b:
                    col = b.inputs["Base Color"].default_value
            out[k] = [linear_to_srgb(col[i]) for i in range(3)]
    return out


def add_material_attr(objs):
    import numpy as np
    for o in objs:
        me = o.data
        mi = np.empty(len(me.polygons), dtype=np.int32)
        lt = np.empty(len(me.polygons), dtype=np.int32)
        me.polygons.foreach_get("material_index", mi)
        me.polygons.foreach_get("loop_total", lt)
        cls = np.array([class_of(m.name) for m in me.materials] or [0], dtype=np.int32)
        vi = np.empty(len(me.loops), dtype=np.int32)
        me.loops.foreach_get("vertex_index", vi)
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        mw = np.array(o.matrix_world)
        wp = (co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3])[vi]
        k = cls[np.repeat(mi, lt)]
        k = np.where((k == class_of("SC_Stitch")) & (wp[:, 2] < FACE_MIN_Z), class_of("SC_Cloth"), k)
        side = (k == class_of("SC_Cross")) & ((wp[:, 1] > 0) | (np.abs(wp[:, 0]) > 0.2))
        k = np.where(side, class_of("SC_Helmet"), k)
        col = np.zeros((len(me.loops), 4))
        col[:, 0] = k
        col[:, 3] = 1
        a = me.color_attributes.new("icon_mat", "FLOAT_COLOR", "CORNER")
        a.data.foreach_set("color", col.ravel())


def prune(objs):
    import bmesh
    for o in objs:
        mw = o.matrix_world
        names = [m.name.split(".")[0] for m in o.data.materials]
        bm = bmesh.new()
        bm.from_mesh(o.data)
        dead = []
        for f in bm.faces:
            c = mw @ f.calc_center_median()
            n = names[f.material_index]
            if n in ("SC_Straw", "SC_Wood") and abs(c.x) > 0.36:
                dead.append(f)
            elif n == "SC_Cross" and (c.y > 0 or abs(c.x) > 0.2):
                dead.append(f)
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        face = set(f for f in bm.faces if names[f.material_index] == "SC_Stitch"
                   and (mw @ f.calc_center_median()).y < 0 and (mw @ f.calc_center_median()).z > 0.9)
        seen, gone, inv = set(), [], mw.inverted()
        for f0 in face:
            if f0 in seen:
                continue
            isl, st = [], [f0]
            seen.add(f0)
            while st:
                g = st.pop()
                isl.append(g)
                for e in g.edges:
                    for h in e.link_faces:
                        if h in face and h not in seen:
                            seen.add(h)
                            st.append(h)
            vs = set(v for g in isl for v in g.verts)
            xs = [(mw @ v.co).x for v in vs]
            ext = max(xs) - min(xs)
            if ext < 0.1:
                gone += isl
            elif ext > 0.2:
                for v in vs:
                    w = mw @ v.co
                    w.x *= MOUTH[0]
                    w.z -= MOUTH[1]
                    v.co = inv @ w
        bmesh.ops.delete(bm, geom=gone, context="FACES")
        bm.to_mesh(o.data)
        bm.free()
        o.data.update()


def use_attr(objs, name):
    for o in objs:
        ca = o.data.color_attributes
        ca.active_color = ca[name]
        ca.render_color_index = ca.find(name)


def render(ip, objs, tmp):
    import bpy, numpy as np
    from mathutils import Vector, Matrix
    f, r, u = ip.view_basis(VIEW)
    data = ip.gather(objs)
    P = ip.bake_attrs(data, f, r, u, "Scarecrow")
    W = np.concatenate([d[1] for d in data])
    head = (W[:, 2] > HEAD_MIN_Z) & (np.abs(W[:, 0]) < 0.36)
    x0, x1 = P[head, 0].min(), P[head, 0].max()
    ps = (x1 - x0) / HEAD_PX
    cx = (x0 + x1) / 2
    cy = P[:, 1].max() + TOP_PAD * ps - ip.N / 2 * ps
    add_material_attr(objs)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "FLAT"
    sh.color_type = "VERTEX"
    sh.show_cavity = False
    sh.show_object_outline = False
    sh.show_shadows = False
    sh.show_specular_highlight = False
    sh.show_xray = False
    sc.display.render_aa = "OFF"
    sc.render.dither_intensity = 0
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = ip.N * ip.SS
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    cd = bpy.data.cameras.new("icon_cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ps * ip.N
    cd.clip_start = 0.01
    cd.clip_end = 100
    cam = bpy.data.objects.new("icon_cam", cd)
    sc.collection.objects.link(cam)
    m = Matrix((r, u, -f)).transposed().to_4x4()
    m.translation = Vector(r) * cx + Vector(u) * cy - Vector(f) * (P[:, 2].max() + 10)
    cam.matrix_world = m
    sc.camera = cam
    paths = []
    for attr in ("icon", "icon_mat"):
        use_attr(objs, attr)
        paths.append(os.path.join(tmp, "raw_scarecrow_%s.exr" % attr))
        sc.render.filepath = paths[-1]
        bpy.ops.render.render(write_still=True)
    return paths


def compose(ip, raw, mat, alb):
    import numpy as np
    N, SS = ip.N, ip.SS
    grey = ip.process(raw, {})
    A = raw[..., 3] > 0.5
    C = np.rint(mat[..., 0]).astype(np.int32) * A
    B = lambda a: a.reshape(N, SS, N, SS)
    frac = np.stack([B((C == k).astype(np.float64)).sum((1, 3)) / (SS * SS) for k in range(len(CLASSES) + 1)])
    frac[0] = 0
    lab = frac.argmax(0)
    has = frac.max(0) > 0
    body = grey[..., 3] > 0
    for _ in range(4):
        miss = body & ~has
        if not miss.any():
            break
        for dy, dx in ip.N8:
            src = ip.shift(lab, dy, dx)
            ok = ip.shift(has.astype(np.int32), dy, dx) > 0
            take = miss & ok & ~has
            lab[take] = src[take]
            has = has | take
    g = grey[..., 0]
    lines = body & (g < 0.35)
    toned = body & ~lines
    tf = np.where(toned, g / ip.TONES[0], 1.0)
    stitch = toned & (frac[1] >= T_STITCH)
    cross = toned & (frac[2] >= T_CROSS) & ~stitch
    shine = stitch & (frac[4] >= T_SHINE)
    t = np.where(g > 0.83, 0, np.where(g > 0.6, 1, 2))
    tones = np.array(ip.TONES)
    final = grey.copy()
    final[toned, :3] = tones[np.minimum(2, t + np.array(SHIFT)[lab])][toned][:, None]
    final[stitch, :3] = ip.INNER
    final[shine, :3] = ip.TONES[0]
    final[cross, :3] = alb[2][None] * tf[cross][:, None]
    color = grey.copy()
    color[toned, :3] = alb[lab[toned]] * tf[toned][:, None]
    color[stitch, :3] = alb[1]
    color[shine, :3] = alb[4]
    color[cross, :3] = alb[2][None] * tf[cross][:, None]
    return final, color, grey


def blender_main(tmp):
    import bpy
    ip = load_lib()
    ip.DEPTH_JUMP = JUMP
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=FBX)
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    prune(objs)
    bpy.context.view_layer.update()
    alb = albedos(objs)
    p_icon, p_mat = render(ip, objs, tmp)
    final, color, grey = compose(ip, ip.load_exr(p_icon), ip.load_exr(p_mat), alb)
    ip.save_png(final, OUT_PNG)
    ip.save_png(final, os.path.join(tmp, "scarecrow_final.png"))
    ip.save_png(color, os.path.join(tmp, "scarecrow_color.png"))
    ip.save_png(grey, os.path.join(tmp, "scarecrow_grey.png"))
    print("ICON_DONE", OUT_PNG)


def contact_main(tmp):
    from PIL import Image, ImageDraw
    items = [("Scarecrow (final)", os.path.join(tmp, "scarecrow_final.png")),
             ("Scarecrow color", os.path.join(tmp, "scarecrow_color.png")),
             ("Scarecrow gris", os.path.join(tmp, "scarecrow_grey.png"))]
    items += [(n, os.path.join(PART_ICONS, "PartIcon_%s.png" % n)) for n in COMPARE]
    bgs = ((251, 240, 220), (51, 38, 36), (96, 104, 112))
    Z, pad, lab = 5, 10, 18
    S = 32 * Z
    cw = S + pad
    small_h = 48 + 8
    H = pad + lab + len(bgs) * (S + 4) + small_h * len(bgs) + pad
    sheet = Image.new("RGB", (pad + cw * len(items), H), (70, 66, 64))
    d = ImageDraw.Draw(sheet)
    for j, (name, path) in enumerate(items):
        ic = Image.open(path).convert("RGBA")
        x = pad + j * cw
        d.text((x, pad), name, fill=(255, 255, 255))
        y = pad + lab
        big = ic.resize((S, S), Image.NEAREST)
        for bg in bgs:
            d.rectangle((x, y, x + S - 1, y + S - 1), fill=bg)
            sheet.paste(big, (x, y), big)
            y += S + 4
        for bg in bgs:
            d.rectangle((x, y, x + S - 1, y + small_h - 8), fill=bg)
            xx = x + 4
            for size in (48, 32, 28, 16):
                im = ic if size == 32 else ic.resize((size, size), Image.NEAREST if size == 48 else Image.BILINEAR)
                sheet.paste(im, (xx, y + 2), im)
                xx += size + 6
            y += small_h
    out = os.path.join(tmp, "icon_scarecrow_sheet.png")
    sheet.save(out)
    print("CONTACT", out, sheet.size)


try:
    import bpy
except ImportError:
    bpy = None

if bpy is not None:
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    blender_main(args[0] if args else os.path.join(os.environ.get("TEMP", "."), "scarecrow_icon"))
elif __name__ == "__main__":
    contact_main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("TEMP", "."), "scarecrow_icon"))
