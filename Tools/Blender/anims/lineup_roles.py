import bpy
import json
import math
import os
import sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RECIPES = ARGS[0]
OUT = ARGS[1]
MESHES = "E:/GitHub/RunRunSimulator/Assets/Synty/SidekickCharacters/Resources/Meshes"

index = {}
for root, _, files in os.walk(MESHES):
    for f in files:
        if f.endswith(".fbx"):
            index[f[:-4]] = os.path.join(root, f)

SKIN = (0.85, 0.66, 0.54, 1)
PALETTE = {"TORS": (0.42, 0.55, 0.36, 1), "AUPL": (0.42, 0.55, 0.36, 1), "AUPR": (0.42, 0.55, 0.36, 1),
           "ALWL": (0.62, 0.48, 0.32, 1), "ALWR": (0.62, 0.48, 0.32, 1), "HIPS": (0.36, 0.42, 0.62, 1),
           "LEGL": (0.36, 0.42, 0.62, 1), "LEGR": (0.36, 0.42, 0.62, 1), "FOTL": (0.35, 0.25, 0.18, 1),
           "FOTR": (0.35, 0.25, 0.18, 1), "HAIR": (0.45, 0.30, 0.18, 1), "FCHR": (0.45, 0.30, 0.18, 1),
           "AHED": (0.80, 0.55, 0.25, 1), "AFAC": (0.85, 0.80, 0.40, 1), "ABAC": (0.70, 0.40, 0.35, 1)}

data = json.load(open(RECIPES, encoding="utf-8"))
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'OBJECT'
scene.display.shading.show_cavity = True
scene.world = bpy.data.worlds.new("w")
scene.world.color = (0.18, 0.18, 0.2)

spacing = 1.75
missing = []
for i, role in enumerate(data):
    x = i * spacing
    before = set(bpy.data.objects)
    for part in role["parts"]:
        if part not in index:
            missing.append((role["name"], part))
            continue
        bpy.ops.import_scene.fbx(filepath=index[part])
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.type == 'ARMATURE':
            o.location.x += x
        elif o.type == 'MESH':
            code = o.name.split("_")[-2][2:] if len(o.name.split("_")) >= 2 else ""
            code = code[-4:]
            o.color = SKIN if "HUMN" in o.name else PALETTE.get(code, (0.6, 0.6, 0.6, 1))
            if o.parent is None:
                o.location.x += x
            if o.data.shape_keys:
                kb = o.data.shape_keys.key_blocks
                bt = role.get("bodyType", 0)
                bs = role.get("bodySize", 0)
                mu = role.get("muscle", 0)
                if "masculineFeminine" in kb:
                    kb["masculineFeminine"].value = (bt + 100) / 200
                if "defaultHeavy" in kb:
                    kb["defaultHeavy"].value = max(0, bs) / 100
                if "defaultSkinny" in kb:
                    kb["defaultSkinny"].value = max(0, -bs) / 100
                if "defaultBuff" in kb:
                    kb["defaultBuff"].value = max(0, mu) / 100
    curve = bpy.data.curves.new("lbl%d" % i, 'FONT')
    curve.body = role["name"]
    curve.size = 0.09
    curve.align_x = 'CENTER'
    t = bpy.data.objects.new("lbl%d" % i, curve)
    scene.collection.objects.link(t)
    t.location = (x, -0.3, 0.02)
    t.rotation_euler = (math.radians(90), 0, 0)
    t.color = (1, 1, 1, 1)

n = len(data)
cd = bpy.data.cameras.new("cam")
cd.type = 'ORTHO'
cd.ortho_scale = max(2.2, n * spacing)
cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cam.location = ((n - 1) * spacing / 2, -8, 0.95)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam
scene.render.resolution_x = int(420 * n)
scene.render.resolution_y = int(420 * n * 2.1 / cd.ortho_scale)
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("LINEUP", OUT, "missing", missing)
