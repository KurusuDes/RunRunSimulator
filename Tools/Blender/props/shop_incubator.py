import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FBX_OUT = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Models", "Shop", "ShopIncubator.fbx")
DRAGON_FBX = os.path.join(ROOT, "Assets", "Suriyun", "Dragons_SD", "FBX", "DragonSD_A.fbx")

PALETTE = {
    "INC_Mint": "9FD8C4",
    "INC_Cream": "F5EAD2",
    "INC_Chrome": "D9CBB4",
    "INC_Straw": "EDC25E",
    "INC_StrawDark": "C99341",
    "INC_Coral": "EF7E68",
    "INC_Cloth": "F7AE9C",
    "INC_Face": "FFF8EA",
    "INC_Dark": "4A3A3C",
    "INC_Glass": "CDEFF2",
    "INC_Lamp": "FFD47A",
}
GLASS_ALPHA = 0.28

BODY_R = 0.449
TOP_Z = 0.456
RIM_R = 0.405
RIM_Z = 0.455
DOME_R = 0.392
DOME_Z0 = 0.478
DOME_Z1 = 0.56
DOME_H = 0.33
NEST_Z = 0.525
NEST_R = 0.268
NEST_T = 0.085
FLOOR_Z = 0.47
PANEL_CV = 0.272
HOOD_Y = 0.0
ARM_YAW = -50.0

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
        alpha = 1.0
        if name == "INC_Chrome":
            bsdf.inputs["Metallic"].default_value = 1.0
            bsdf.inputs["Roughness"].default_value = 0.3
            m.metallic = 1.0
        if name == "INC_Glass":
            alpha = GLASS_ALPHA
            bsdf.inputs["Alpha"].default_value = alpha
            bsdf.inputs["Roughness"].default_value = 0.05
            for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
                try:
                    setattr(m, attr, val)
                except Exception:
                    pass
        if name == "INC_Lamp":
            bsdf.inputs["Emission Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
            bsdf.inputs["Emission Strength"].default_value = 2.0
        m.diffuse_color = (rgb[0], rgb[1], rgb[2], alpha)
        m.roughness = 0.85
        MATS[name] = m


def finish(name, bm, mat, smooth=True, angle=50.0, alt=None):
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
    if alt:
        me.materials.append(MATS[alt[0]])
        for i in alt[1]:
            me.polygons[i].material_index = 1
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    PARTS.append(ob)
    return ob


def xf(bm, m):
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts[:])
    return bm


def lathe_bm(prof, segs, sy=1.0, tweak=None, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = []
    for i, (r, z) in enumerate(prof):
        if r <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
            continue
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            x, y, zz = r * math.cos(a), r * math.sin(a) * sy, z
            if tweak:
                x, y, zz = tweak(i, a, x, y, zz)
            ring.append(bm.verts.new((x, y, zz)))
        rings.append(ring)
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


def ellipsoid_bm(center, radii, useg=16, vseg=8, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg, radius=1.0)
    for v in [v for v in bm.verts if v not in before]:
        v.co = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2])) + Vector(center)
    return bm


def tube_bm(points, radii, sides=8, bm=None, side_hint=None, caps=True):
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
        if prev_side is None:
            h = Vector(side_hint) if side_hint is not None else (UP if abs(t.z) < 0.9 else Vector((1, 0, 0)))
            side = (h - t * h.dot(t)).normalized()
        else:
            side = (prev_side - t * prev_side.dot(t)).normalized()
        prev_side = side
        up = t.cross(side).normalized()
        ring = [bm.verts.new(p + side * math.cos(2 * math.pi * k / sides) * r + up * math.sin(2 * math.pi * k / sides) * r)
                for k in range(sides)]
        rings.append(ring)
    faces = []
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            faces.append(bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k])))
    if caps:
        faces.append(bm.faces.new(list(reversed(rings[0]))))
        faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def torus_bm(R, r, z, segs=32, sides=8, bm=None, wobble=None, twist=0):
    bm = bm or bmesh.new()
    rings = []
    for k in range(segs):
        a = 2 * math.pi * k / segs
        out = Vector((math.cos(a), math.sin(a), 0))
        ring = []
        for j in range(sides):
            b = 2 * math.pi * (j + twist * k / segs) / sides
            rr = r * (wobble(a, b) if wobble else 1.0)
            ring.append(bm.verts.new(out * R + Vector((0, 0, z)) + out * math.cos(b) * rr + UP * math.sin(b) * rr))
        rings.append(ring)
    faces = []
    for k in range(segs):
        A, B = rings[k], rings[(k + 1) % segs]
        for j in range(sides):
            faces.append(bm.faces.new((A[j], A[(j + 1) % sides], B[(j + 1) % sides], B[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def frame(p, n, up=UP):
    z = Vector(n).normalized()
    x = up.cross(z)
    if x.length < 1e-4:
        x = Vector((1, 0, 0))
    x.normalize()
    y = z.cross(x).normalized()
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(p)
    return m


def cyl_point(u, v, h, R=BODY_R):
    phi = u / R
    rr = R + h
    return Vector((rr * math.sin(phi), -rr * math.cos(phi), v)), Vector((math.sin(phi), -math.cos(phi), 0))


def rrect(a, b, rc, m, nh=6, nv=1):
    groups = []
    for cx, cy, a0 in ((a - rc, b - rc, 0), (-(a - rc), b - rc, 90), (-(a - rc), -(b - rc), 180), (a - rc, -(b - rc), 270)):
        groups.append([(cx + rc * math.cos(math.radians(a0 + 90.0 * i / m)), cy + rc * math.sin(math.radians(a0 + 90.0 * i / m)))
                       for i in range(m + 1)])
    pts = []
    for gi, g in enumerate(groups):
        pts.extend(g)
        nxt = groups[(gi + 1) % 4][0]
        n = nh if gi % 2 == 0 else nv
        for s in range(1, n + 1):
            t = s / (n + 1)
            pts.append((g[-1][0] + (nxt[0] - g[-1][0]) * t, g[-1][1] + (nxt[1] - g[-1][1]) * t))
    return pts


def cyl_plate(cu, cv, a, b, rc, rings, m=4, bm=None):
    bm = bm or bmesh.new()
    vrings = []
    for mode, val, h in rings:
        if mode == "off":
            rcc = max(rc + val, 0.002)
            outline = rrect(a + val, b + val, rcc, m)
        else:
            outline = [(x * val, y * val) for x, y in rrect(a, b, rc, m)]
        vrings.append([bm.verts.new(cyl_point(cu + x, cv + y, h)[0]) for x, y in outline])
    centre = bm.verts.new(cyl_point(cu, cv, rings[-1][2])[0])
    faces = []
    n = len(vrings[0])
    for A, B in zip(vrings, vrings[1:]):
        for k in range(n):
            faces.append(bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k])))
    last = vrings[-1]
    for k in range(n):
        faces.append(bm.faces.new((last[k], last[(k + 1) % n], centre)))
    ref = faces[-1]
    ref.normal_update()
    if ref.normal.dot(cyl_point(cu, cv, 0)[1]) < 0:
        for f in faces:
            f.normal_flip()
    return bm


def catmull(ctrl, per=4):
    pts = [Vector(p) for p in ctrl]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for s in range(per):
            t = s / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


def build_base():
    prof = [(0.0, 0.04), (0.34, 0.04), (0.39, 0.048), (0.42, 0.066), (0.437, 0.095), (0.445, 0.14),
            (BODY_R, 0.27), (0.447, 0.37), (0.44, 0.408), (0.425, 0.434), (0.40, 0.45), (0.37, TOP_Z), (0.0, TOP_Z)]
    finish("Body", lathe_bm(prof, 28), "INC_Mint", angle=50)
    prof = [(0.43, 0.058), (0.456, 0.066), (0.47, 0.09), (0.472, 0.115), (0.463, 0.138), (0.44, 0.148)]
    finish("Bumper", lathe_bm(prof, 28), "INC_Cream", angle=50)
    finish("Rim", torus_bm(RIM_R, 0.038, RIM_Z, 28, 6), "INC_Chrome", angle=60)
    bm = bmesh.new()
    for k in range(4):
        a = math.radians(45 + 90 * k)
        ellipsoid_bm((0.32 * math.cos(a), 0.32 * math.sin(a), 0.042), (0.075, 0.075, 0.042), 8, 4, bm=bm)
    finish("Feet", bm, "INC_Chrome", angle=70)


def build_panel():
    rings = [("off", 0.022, -0.012), ("off", 0.022, 0.006), ("off", 0.014, 0.019), ("off", 0.0, 0.024),
             ("s", 0.66, 0.024), ("s", 0.33, 0.024)]
    finish("Panel", cyl_plate(0.0, PANEL_CV, 0.27, 0.105, 0.055, rings, m=4), "INC_Cream", angle=50)


def build_dial():
    h = 0.024
    p, n = cyl_point(0.0, PANEL_CV + 0.004, h)
    m = frame(p, n)
    finish("DialBezel", xf(torus_bm(0.08, 0.017, 0.006, 24, 6), m), "INC_Chrome", angle=60)
    finish("DialFace", lathe_bm([(0.0, -0.004), (0.078, -0.004), (0.078, 0.004), (0.0, 0.006)], 24, matrix=m),
           "INC_Face", angle=60)
    dark = bmesh.new()
    for deg in (-60, -30, 0, 30, 60):
        t = math.radians(90 + deg)
        d = Vector((math.cos(t), math.sin(t), 0))
        a0 = d * 0.046 + Vector((0, 0, 0.007))
        a1 = d * 0.064 + Vector((0, 0, 0.007))
        tube_bm([m @ a0, m @ a1], [0.006, 0.006], 6, bm=dark, side_hint=n)
    finish("DialTicks", dark, "INC_Dark", angle=70)
    hot = bmesh.new()
    t =math.radians(90 + 32)
    d = Vector((math.cos(t), math.sin(t), 0))
    tube_bm([m @ (Vector((0, 0, 0.011)) - d * 0.012), m @ (d * 0.058 + Vector((0, 0, 0.011)))], [0.0085, 0.006], 6,
            bm=hot, side_hint=n)
    finish("DialNeedle", hot, "INC_Coral", angle=70)
    cap = lathe_bm([(0.0, 0.004), (0.016, 0.004), (0.018, 0.012), (0.012, 0.019), (0.0, 0.021)], 12, matrix=m)
    finish("DialCap", cap, "INC_Chrome", angle=70)


def build_knobs():
    for s in (-1, 1):
        p, n = cyl_point(s * 0.18, PANEL_CV - 0.005, 0.024)
        m = frame(p, n)
        skirt = [(0.0, -0.004), (0.054, -0.004), (0.058, 0.004), (0.054, 0.012), (0.0, 0.012)]
        finish("KnobSkirt", lathe_bm(skirt, 16, matrix=m), "INC_Chrome", angle=60)
        knob = [(0.0, 0.008), (0.042, 0.008), (0.045, 0.03), (0.043, 0.05), (0.034, 0.062), (0.0, 0.066)]
        finish("Knob", lathe_bm(knob, 16, matrix=m), "INC_Coral", angle=55)
        t = math.radians(90 + (-40 if s < 0 else 25))
        d = Vector((math.cos(t), math.sin(t), 0))
        mk = tube_bm([m @ (d * 0.004 + Vector((0, 0, 0.066))), m @ (d * 0.03 + Vector((0, 0, 0.062)))], [0.0065, 0.0065], 6,
                     side_hint=n)
        finish("KnobMark", mk, "INC_Face", angle=70)


def build_nest():
    prof = [(0.30, NEST_Z + 0.03), (0.24, NEST_Z - 0.005), (0.17, FLOOR_Z + 0.012), (0.09, FLOOR_Z + 0.002), (0.0, FLOOR_Z)]

    def tw(i, a, x, y, z):
        if i <= 1:
            f = 1.0 + 0.03 * math.cos(7 * a)
            return x * f, y * f, z + 0.008 * math.sin(7 * a)
        return x, y, z

    finish("Cloth", lathe_bm(prof, 28, tweak=tw), "INC_Cloth", angle=60)

    def wob(a, b):
        return 1.0 + 0.07 * math.sin(6 * a + 1.3 * math.sin(b)) + 0.03 * math.sin(11 * a + 2 * b)

    segs, sides = 28, 8
    stripes = [k * sides + j for k in range(segs) for j in range(sides) if j % 2]
    finish("Nest", torus_bm(NEST_R, NEST_T, NEST_Z, segs, sides, wobble=wob, twist=3 * sides), "INC_Straw", angle=70,
           alt=("INC_StrawDark", stripes))
    light, dark = bmesh.new(), bmesh.new()
    n = 7
    for k in range(n):
        a = 2 * math.pi * (k + 0.2) / n + 0.18 * math.sin(k * 2.7)
        out = Vector((math.cos(a), math.sin(a), 0))
        tang = Vector((-math.sin(a), math.cos(a), 0)) * (1 if k % 2 else -1)
        base = out * (NEST_R + 0.015) + Vector((0, 0, NEST_Z + NEST_T * 0.82))
        d = (tang * 0.8 + out * 0.45 + UP * 0.25).normalized()
        L = 0.13 + 0.02 * ((k * 7) % 3)
        pts = [base, base + d * L * 0.4, base + d * L * 0.75 - UP * 0.012, base + d * L - UP * 0.035]
        tube_bm(pts, [0.022, 0.019, 0.014, 0.007], 5, bm=dark if k % 3 == 0 else light)
    finish("NestStraws", light, "INC_Straw", angle=70)
    finish("NestStrawsDark", dark, "INC_StrawDark", angle=70)


def build_dome():
    prof = [(DOME_R, DOME_Z0), (DOME_R, DOME_Z1)]
    for deg in range(12, 91, 13):
        t = math.radians(min(deg, 90))
        prof.append((max(0.0, DOME_R * math.cos(t)), DOME_Z1 + DOME_H * math.sin(t)))
    if prof[-1][0] > 1e-6:
        prof.append((0.0, DOME_Z1 + DOME_H))
    finish("Dome", lathe_bm(prof, 28), "INC_Glass", angle=60)
    top = DOME_Z1 + DOME_H
    finish("DomeCollar", torus_bm(0.058, 0.014, top - 0.008, 18, 6), "INC_Chrome", angle=70)
    finish("DomeHandle", ellipsoid_bm((0, 0, top + 0.026), (0.05, 0.05, 0.036), 14, 7), "INC_Coral", angle=70)


def build_lamp():
    hz = 1.07
    ctrl = [(0, 0.40, 0.30), (0, 0.50, 0.33), (0, 0.53, 0.52), (0, 0.515, 0.80), (0, 0.46, 1.02), (0, 0.34, 1.17),
            (0, 0.18, 1.235), (0, 0.06, 1.22), (0, HOOD_Y + 0.005, hz + 0.11)]
    pts = catmull(ctrl, 2)
    rot = Matrix.Rotation(math.radians(ARM_YAW), 4, "Z")
    finish("Arm", tube_bm(pts, [0.03] * len(pts), 8, side_hint=(1, 0, 0)), "INC_Chrome", angle=60)
    PARTS[-1].data.transform(rot)
    finish("ArmMount", ellipsoid_bm((0, 0.452, 0.31), (0.085, 0.05, 0.085), 12, 6), "INC_Coral", angle=70)
    PARTS[-1].data.transform(rot)
    finish("ArmCollar", torus_bm(0.034, 0.012, 0.0, 12, 6), "INC_Chrome", angle=70)
    PARTS[-1].data.transform(rot @ frame((0, 0.52, 0.43), (0, 0.04, 1)))
    prof = [(0.0, hz + 0.065), (0.07, hz + 0.05), (0.112, hz + 0.008), (0.15, hz - 0.002), (0.168, hz + 0.012),
            (0.163, hz + 0.055), (0.135, hz + 0.1), (0.085, hz + 0.125), (0.0, hz + 0.13)]
    hood = lathe_bm(prof, 24)
    bmesh.ops.translate(hood, vec=(0, HOOD_Y, 0), verts=hood.verts[:])
    finish("Hood", hood, "INC_Coral", angle=55)
    finish("HoodRing", torus_bm(0.158, 0.014, hz + 0.004, 24, 6), "INC_Chrome", angle=70)
    PARTS[-1].data.transform(Matrix.Translation((0, HOOD_Y, 0)))
    finish("Bulb", ellipsoid_bm((0, HOOD_Y, hz + 0.008), (0.064, 0.064, 0.064), 12, 6), "INC_Lamp", angle=80)


def join_all():
    objs = PARTS
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "ShopIncubator"
    ob.data.name = "ShopIncubator"
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
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.data.materials.append(fl)


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


def load_dragon():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=DRAGON_FBX)
    new = [o for o in bpy.data.objects if o not in before]
    body = bpy.data.materials.new("DragonRef")
    body.diffuse_color = (0.80, 0.78, 0.86, 1)
    roots = []
    for o in new:
        if o.parent is None:
            roots.append(o)
        if o.type == "MESH":
            if o.name == "Face":
                o.hide_render = True
            o.data.materials.clear()
            o.data.materials.append(body)
    bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for o in new if o.type == "MESH" and not o.hide_render for c in o.bound_box]
    print("DRAGON_HEIGHT", round(max(zs) - min(zs), 3), "min", round(min(zs), 3))
    return roots


def place(roots, x, y):
    for o in roots:
        o.location.x = x
        o.location.y = y
    bpy.context.view_layer.update()


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
    build_base()
    build_panel()
    build_dial()
    build_knobs()
    build_nest()
    build_dome()
    build_lamp()
    ob = join_all()
    bpy.context.view_layer.update()
    me = ob.data
    me.calc_loop_triangles()
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    print("INCUBATOR verts=%d tris=%d" % (len(me.vertices), len(me.loop_triangles)))
    print("INCUBATOR size x=%.3f y=%.3f z=%.3f zmin=%.3f" % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), min(zs)))
    print("INCUBATOR mats", [m.name for m in me.materials])
    if "noexport" not in flags:
        export(ob)
        print("EXPORTED", FBX_OUT)
    if not out_dir:
        return
    os.makedirs(out_dir, exist_ok=True)
    setup_scene()
    tz = 0.62
    render(os.path.join(out_dir, "inc_34.png"), 32, 16, (0, 0, tz), 1.55, (640, 640))
    render(os.path.join(out_dir, "inc_front.png"), 0, 6, (0, 0, tz), 1.55, (640, 640))
    render(os.path.join(out_dir, "inc_side.png"), 90, 6, (0, 0, tz), 1.55, (640, 640))
    render(os.path.join(out_dir, "inc_iso.png"), 20, 55, (0, 0, 0.5), 1.45, (640, 640))
    roots = load_dragon()
    place(roots, 1.05, -0.1)
    render(os.path.join(out_dir, "inc_dragon34.png"), 24, 14, (0.52, 0, 0.7), 2.5, (640, 640))
    place(roots, 0.0, -1.15)
    render(os.path.join(out_dir, "inc_dragonside.png"), 90, 8, (0, -0.55, 0.7), 2.6, (640, 640))
    sheet = os.path.join(out_dir, "incubator_sheet.png")
    contact_sheet(out_dir, ["inc_34.png", "inc_front.png", "inc_side.png", "inc_iso.png", "inc_dragon34.png",
                            "inc_dragonside.png"], sheet)
    print("SHEET", sheet)


main()
