import bpy
import sys
from mathutils import Quaternion, Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=ARGS[0], automatic_bone_orientation=False)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
sc = bpy.context.scene
sc.frame_set(2)
W = arm.matrix_world


def wp(name, tail=False):
    pb = arm.pose.bones[name]
    return W @ (pb.tail if tail else pb.head)


for n in ["pelvis", "spine_01", "spine_03", "neck_01", "head", "upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r", "thigh_l", "calf_l", "foot_l", "ball_l", "thigh_r", "calf_r", "foot_r", "index_01_l", "pinky_01_l", "middle_03_l"]:
    print("POS", n, tuple(round(v, 3) for v in wp(n)), "tail", tuple(round(v, 3) for v in wp(n, True)), "mode", arm.pose.bones[n].rotation_mode)

pb = arm.pose.bones["hand_l"]
for ax in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
    print("HANDL_AXIS_WORLD", ax, tuple(round(v, 3) for v in (W.to_3x3().normalized() @ (pb.matrix.to_3x3().normalized() @ Vector(ax)))))
pb = arm.pose.bones["hand_r"]
for ax in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
    print("HANDR_AXIS_WORLD", ax, tuple(round(v, 3) for v in (W.to_3x3().normalized() @ (pb.matrix.to_3x3().normalized() @ Vector(ax)))))

for side, palm in (("l", Vector((-1, 0, 0))), ("r", Vector((1, 0, 0)))):
    for f in ["index_02_" + side, "middle_01_" + side, "thumb_02_" + side]:
        pbf = arm.pose.bones[f]
        child = pbf.children[0] if pbf.children else pbf
        base = wp(child.name, tail=(child == pbf))
        orig = pbf.rotation_quaternion.copy()
        for name, ax in (("X", (1, 0, 0)), ("Z", (0, 0, 1)), ("Y", (0, 1, 0))):
            pbf.rotation_quaternion = orig @ Quaternion(ax, 0.6)
            bpy.context.view_layer.update()
            tip = wp(child.name, tail=(child == pbf))
            d = tip - base
            print("FINGER", f, "+" + name, "dpalm", round(d.dot(palm), 4), "dz", round(d.z, 4), "dy", round(d.y, 4))
        pbf.rotation_quaternion = orig
        bpy.context.view_layer.update()

act = arm.animation_data.action
print("ACTION", act.name, act.frame_range)
