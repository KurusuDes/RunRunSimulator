import bpy
import math
import os
import sys
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = ARGS[0]
FILES = ARGS[1:]
BASE = "E:/GitHub/RunRunSimulator/Assets/Synty/SidekickCharacters/Resources/Meshes/SK_BaseModel.fbx"
W, H = 420, 520

GRAB = {"A_MM_Receive": ("after", 0.45), "A_MM_PickUp_Floor": ("after", 0.45),
        "A_MM_HandOver": ("before", 0.50), "A_MM_Carry_Loop": ("after", -1.0)}
PROPS = {"A_MM_Receive": "counter", "A_MM_HandOver": "counter", "A_MM_Pay": "counter",
         "A_MM_Sit_Enter": "bench", "A_MM_Sit_Loop": "bench", "A_MM_Sit_Exit": "bench"}
SAMPLES = {"A_MM_Carry_Loop": [0.0, 0.25, 0.5, 0.75], "A_MM_Sit_Loop": [0.0, 0.5]}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'OBJECT'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.render.resolution_x = W
scene.render.resolution_y = H
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("w")
scene.render.image_settings.file_format = 'PNG'

bpy.ops.import_scene.fbx(filepath=BASE, automatic_bone_orientation=False)
mesh_rig = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh_rig.name = "MeshRig"
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for o in meshes:
    o.color = (0.86, 0.68, 0.55, 1)
    if o.data.shape_keys:
        for kb in o.data.shape_keys.key_blocks:
            if kb.name != "Basis":
                kb.value = 0.0


def set_body(gender):
    for o in meshes:
        if not o.data.shape_keys:
            continue
        for kb in o.data.shape_keys.key_blocks:
            low = kb.name.lower()
            if "feminine" in low and "masculine" in low:
                kb.value = 1.0 if gender == "Femn" else 0.0


def box(name, loc, size, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    o.color = color
    return o


floor = box("Floor", (0, 0, -0.01), (4, 4, 0.02), (0.55, 0.62, 0.5, 1))
counter = box("Counter", (0, -0.52, 0.44), (1.2, 0.46, 0.88), (0.55, 0.38, 0.22, 1))
bench = box("Bench", (0, 0.32, 0.195), (1.0, 0.40, 0.39), (0.55, 0.38, 0.22, 1))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0, -0.40, 1.0))
mochi = bpy.context.active_object
mochi.name = "Mochi"
mochi.scale = (1.0, 1.0, 1.15)
mochi.color = (0.95, 0.55, 0.7, 1)
bpy.ops.object.shade_smooth()

cams = []
for name, loc in (("Front34", (1.7, -2.4, 1.25)), ("Side", (2.9, 0.0, 1.0))):
    cd = bpy.data.cameras.new(name)
    cd.lens = 50
    cam = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(cam)
    cam.location = loc
    d = Vector((0, -0.05, 0.85)) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cams.append(cam)


def hand_mid(rig):
    pl = rig.matrix_world @ rig.pose.bones["hand_l"].head
    pr = rig.matrix_world @ rig.pose.bones["hand_r"].head
    ml = rig.matrix_world @ rig.pose.bones["middle_01_l"].head
    mr = rig.matrix_world @ rig.pose.bones["middle_01_r"].head
    return (pl + pr + ml + mr) / 4


def compose(paths, rows, cols, out):
    tiles = []
    for p in paths:
        img = bpy.data.images.load(p)
        a = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
        tiles.append(a)
        bpy.data.images.remove(img)
    h, w = tiles[0].shape[:2]
    sheet = np.ones((h * rows, w * cols, 4), dtype=np.float32)
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = t
    img = bpy.data.images.new("sheet", w * cols, h * rows, alpha=True)
    img.pixels = sheet.ravel()
    img.filepath_raw = out
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


for path in FILES:
    base = os.path.splitext(os.path.basename(path))[0]
    clip, gender = base.rsplit("_", 1)
    set_body(gender)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False)
    new = [o for o in bpy.data.objects if o not in before]
    anim = [o for o in new if o.type == 'ARMATURE'][0]
    anim.hide_render = True
    for pb in mesh_rig.pose.bones:
        for c in list(pb.constraints):
            pb.constraints.remove(c)
        if pb.name in anim.pose.bones:
            c = pb.constraints.new('COPY_TRANSFORMS')
            c.target = anim
            c.subtarget = pb.name
    act = anim.animation_data.action
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    prop = PROPS.get(clip)
    counter.hide_render = prop != "counter"
    bench.hide_render = prop != "bench"
    grab = GRAB.get(clip)
    mochi.hide_render = grab is None
    samples = SAMPLES.get(clip, [0.0, 0.35, 0.6, 1.0])
    rest_spot = Vector((0, -0.40, 0.88 + 0.15)) if clip != "A_MM_PickUp_Floor" else Vector((0, -0.36, 0.15))
    paths = []
    for cam in cams:
        scene.camera = cam
        for s in samples:
            f = round(f0 + s * (f1 - f0))
            scene.frame_set(f)
            bpy.context.view_layer.update()
            if grab:
                mode, tg = grab
                t = (f - f0) / max(1, (f1 - f0))
                held = (t >= tg) if mode == "after" else (t <= tg)
                mochi.location = (hand_mid(mesh_rig) + Vector((0, -0.02, 0.06))) if held else rest_spot
            p = os.path.join(OUT_DIR, f"{base}_f{f:02d}_{cam.name}.png")
            scene.render.filepath = p
            bpy.ops.render.render(write_still=True)
            paths.append(p)
    out = os.path.join(OUT_DIR, f"{base}_check.png")
    compose(paths, 2, len(samples), out)
    for p in paths:
        os.remove(p)
    print("SHEET", out, "frames", f0, f1)
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
