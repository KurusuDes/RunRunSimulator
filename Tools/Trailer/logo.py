import bpy, math, sys, os

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]
FONT = argv[1]
TAG = argv[2] if len(argv) > 2 else 'CRÍA  ·  EXPLORA  ·  VENDE'
FRAMES = int(argv[3]) if len(argv) > 3 else 60

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        scn.render.engine = eng
        break
    except TypeError:
        pass
scn.render.resolution_x = 1920
scn.render.resolution_y = 1080
scn.render.fps = 30
scn.frame_start = 1
scn.frame_end = FRAMES
scn.render.film_transparent = True
scn.render.image_settings.file_format = 'PNG'
scn.render.image_settings.color_mode = 'RGBA'
scn.render.filepath = os.path.join(OUT, 'logo_')
scn.view_settings.view_transform = 'Standard'
try:
    scn.eevee.taa_render_samples = 32
except Exception:
    pass

world = bpy.data.worlds.new('W')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.05, 0.035, 0.03, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.6
scn.world = world


def srgb(c):
    def f(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (f(c[0]), f(c[1]), f(c[2]), 1.0)


def mat(name, color, metallic=0.0, rough=0.4, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = srgb(color)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    if emit > 0:
        b.inputs['Emission Color'].default_value = srgb(color)
        b.inputs['Emission Strength'].default_value = emit
    return m


gold = mat('Gold', (245, 185, 72), 0.55, 0.28, 0.15)
side = mat('Side', (194, 68, 40), 0.1, 0.5)
cream = mat('Cream', (244, 227, 206), 0.0, 0.6, 0.6)
coral = mat('Coral', (255, 126, 88), 0.0, 0.5, 0.8)

font = bpy.data.fonts.load(FONT)


def text(body, size, extrude, bevel, mats):
    cu = bpy.data.curves.new(body, 'FONT')
    cu.body = body
    cu.font = font
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    ob = bpy.data.objects.new(body, cu)
    scn.collection.objects.link(ob)
    for m in mats:
        ob.data.materials.append(m)
    return ob


logo = text('MoriMonchis', 1.0, 0.11, 0.028, [gold, side])
logo.data.materials[0] = gold
tag = text(TAG, 0.34, 0.02, 0.004, [cream])
tag.location = (0, -0.85, 0)

bar = bpy.data.objects.new('Bar', bpy.data.meshes.new('Bar'))
bm = bar.data
bm.from_pydata([(-1, -0.02, 0), (1, -0.02, 0), (1, 0.02, 0), (-1, 0.02, 0)], [], [(0, 1, 2, 3)])
bar.data.materials.append(coral)
scn.collection.objects.link(bar)
bar.location = (0, -0.58, 0.05)

cam_data = bpy.data.cameras.new('Cam')
cam_data.lens = 50
cam = bpy.data.objects.new('Cam', cam_data)
scn.collection.objects.link(cam)
cam.location = (0, 0, 9.5)
scn.camera = cam


def light(name, kind, loc, energy, color=(1, 1, 1), size=3.0):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == 'AREA':
        ld.size = size
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    scn.collection.objects.link(lo)
    c = lo.constraints.new('TRACK_TO')
    c.target = logo
    return lo


light('Key', 'AREA', (-4, 3, 6), 900, (1.0, 0.92, 0.8), 4)
light('Rim', 'AREA', (5, 2, -3), 1500, (1.0, 0.55, 0.35), 3)
light('Fill', 'AREA', (3, -4, 5), 250, (0.6, 0.75, 1.0), 5)


def key(ob, path, frame, value, interp='BEZIER'):
    setattr(ob, path, value)
    ob.keyframe_insert(path, frame=frame)
    for fc in ob.animation_data.action.fcurves if hasattr(ob.animation_data.action, 'fcurves') else []:
        for kp in fc.keyframe_points:
            kp.interpolation = interp


logo.scale = (0.0, 0.0, 0.0)
logo.keyframe_insert('scale', frame=1)
logo.scale = (1.12, 1.12, 1.12)
logo.keyframe_insert('scale', frame=8)
logo.scale = (0.94, 0.94, 0.94)
logo.keyframe_insert('scale', frame=12)
logo.scale = (1.0, 1.0, 1.0)
logo.keyframe_insert('scale', frame=16)
logo.scale = (1.04, 1.04, 1.04)
logo.keyframe_insert('scale', frame=FRAMES)

logo.rotation_euler = (math.radians(-55), math.radians(-12), 0)
logo.keyframe_insert('rotation_euler', frame=1)
logo.rotation_euler = (math.radians(8), math.radians(4), 0)
logo.keyframe_insert('rotation_euler', frame=10)
logo.rotation_euler = (0, 0, 0)
logo.keyframe_insert('rotation_euler', frame=16)
logo.rotation_euler = (math.radians(-4), math.radians(7), 0)
logo.keyframe_insert('rotation_euler', frame=FRAMES)

bar.scale = (0.0, 1.0, 1.0)
bar.keyframe_insert('scale', frame=10)
bar.scale = (2.0, 1.0, 1.0)
bar.keyframe_insert('scale', frame=20)

tag.location = (0, -1.2, 0)
tag.scale = (1, 1, 1)
tag.keyframe_insert('location', frame=14)
tag.location = (0, -0.85, 0)
tag.keyframe_insert('location', frame=24)
tag.scale = (0.0, 0.0, 0.0)
tag.keyframe_insert('scale', frame=13)
tag.scale = (1.0, 1.0, 1.0)
tag.keyframe_insert('scale', frame=20)

bpy.ops.render.render(animation=True)
print('LOGO_DONE')
