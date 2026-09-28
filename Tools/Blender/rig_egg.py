import bpy
import math
import os
import sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = ARGS[0] if ARGS else bpy.path.abspath("//")
FPS = 30
HEIGHT = 0.32
BASE_R = 0.12


def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def wave(t, cycles=1.0, phase=0.0):
    return math.sin(2 * math.pi * (t * cycles + phase))


def bump(t, a, b):
    if t <= a or t >= b:
        return 0.0
    return math.sin(math.pi * (t - a) / (b - a))


def deg(x):
    return math.radians(x)


def vol(h):
    return 1.0 / math.sqrt(max(h, 0.05))


def pose(root_loc=(0, 0, 0), root_rot=(0, 0, 0), h=1.0):
    return {"root_loc": root_loc, "root_rot": root_rot, "h": h, "w": vol(h)}


def idle(t):
    breath = 0.5 - 0.5 * math.cos(2 * math.pi * t)
    return pose(h=1 - 0.012 * breath, root_rot=(0, 0, deg(1.2) * wave(t)))


def wobble(t):
    env = smooth(0.0, 0.06, t) * (1 - smooth(0.45, 1.0, t))
    return pose(root_rot=(deg(3) * wave(t, 2.5, 0.25) * env, 0, deg(13) * wave(t, 2.5) * env),
                h=1 - 0.015 * abs(wave(t, 5)) * env)


def hop_once(t):
    ant = bump(t, 0.0, 0.3)
    air = bump(t, 0.25, 0.75)
    land = bump(t, 0.72, 0.95)
    stretch = bump(t, 0.25, 0.45) - 0.5 * bump(t, 0.45, 0.62)
    return 0.035 * air, 1 - 0.08 * ant + 0.05 * stretch - 0.07 * land, air


def hop(t):
    first = t < 0.5
    k = t * 2 if first else t * 2 - 1
    up, h, air = hop_once(k)
    side = 1 if first else -1
    return pose(root_loc=(0, up, 0), h=h, root_rot=(deg(-3) * air, 0, deg(4) * side * air))


def jingle(t):
    env = bump(t, 0.0, 1.0)
    return pose(root_loc=(0, 0.003 * abs(wave(t, 9)) * env, 0),
                root_rot=(deg(2) * wave(t, 7, 0.3) * env, 0, deg(4.5) * wave(t, 9) * env),
                h=1 + 0.01 * wave(t, 9, 0.25) * env)


CLIPS = [("Idle", idle, 72), ("Wobble", wobble, 60), ("Hop", hop, 40), ("Jingle", jingle, 36)]


def build_rig():
    arm_data = bpy.data.armatures.new("Egg_Rig")
    rig = bpy.data.objects.new("Egg_Rig", arm_data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    root = arm_data.edit_bones.new("Root")
    root.head, root.tail = (0, 0, 0), (0, 0, 0.05)
    body = arm_data.edit_bones.new("Body")
    body.head, body.tail, body.parent = (0, 0, 0), (0, 0, HEIGHT), root
    bpy.ops.object.mode_set(mode="OBJECT")
    return rig


def skin(rig, meshes):
    for ob in meshes:
        wm = ob.matrix_world.copy()
        ob.parent = None
        ob.matrix_world = wm
    for ob in meshes:
        ob.vertex_groups.clear()
        g = ob.vertex_groups.new(name="Body")
        g.add([v.index for v in ob.data.vertices], 1.0, "REPLACE")
        mod = ob.modifiers.new("Rig", "ARMATURE")
        mod.object = rig
        wm = ob.matrix_world.copy()
        ob.parent = rig
        ob.matrix_world = wm


def apply_pose(rig, p):
    pb = rig.pose.bones
    rx, _, rz = p["root_rot"]
    r = BASE_R * p["h"]
    roll = Vector((r * math.sin(rz), r * (1 - math.cos(rz)) + r * (1 - math.cos(rx)), -r * math.sin(rx)))
    pb["Root"].location = Vector(p["root_loc"]) + roll
    pb["Root"].rotation_euler = p["root_rot"]
    pb["Body"].scale = (p["w"], p["h"], p["w"])


def bake(rig):
    for b in rig.pose.bones:
        b.rotation_mode = "XYZ"
    rig.animation_data_create()
    for name, fn, frames in CLIPS:
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        rig.animation_data.action = act
        for f in range(frames + 1):
            apply_pose(rig, fn(f / frames))
            for b in rig.pose.bones:
                b.keyframe_insert("location", frame=f)
                b.keyframe_insert("rotation_euler", frame=f)
                b.keyframe_insert("scale", frame=f)
        act.frame_range = (0, frames)
    apply_pose(rig, pose())
    rig.animation_data.action = bpy.data.actions["Idle"]


def main():
    bpy.context.scene.render.fps = FPS
    shell = bpy.data.objects["Egg_Shell"]
    meshes = [shell] + [o for o in bpy.data.objects if o.parent is shell]
    rig = build_rig()
    skin(rig, meshes)
    bake(rig)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "MonchiEgg_Rig.blend"))
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, "MonchiEgg.fbx"), use_selection=False,
                             apply_scale_options="FBX_SCALE_ALL", bake_space_transform=True,
                             object_types={"MESH", "ARMATURE"}, mesh_smooth_type="FACE", path_mode="STRIP",
                             add_leaf_bones=False, use_armature_deform_only=True,
                             bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
                             bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0)
    print("RIG_DONE", [c[0] for c in CLIPS])


main()
