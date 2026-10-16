import bpy
import sys

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

bpy.ops.wm.read_factory_settings(use_empty=True)
for path in ARGS:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False)
    new = [o for o in bpy.data.objects if o not in before]
    print("=== FILE", path)
    for o in new:
        print("OBJ", o.name, o.type, "loc", tuple(round(v, 4) for v in o.location),
              "rot", tuple(round(v, 4) for v in o.rotation_euler), "scale", tuple(round(v, 4) for v in o.scale),
              "parent", o.parent.name if o.parent else None)
        if o.type == 'ARMATURE':
            arm = o.data
            print("BONES", len(arm.bones))
            for b in arm.bones:
                hl = o.matrix_world @ b.head_local
                print("  B", b.name, "parent", b.parent.name if b.parent else None,
                      "head", tuple(round(v, 3) for v in hl))
            ad = o.animation_data
            if ad and ad.action:
                a = ad.action
                print("ACTION", a.name, "range", tuple(a.frame_range))
    for a in bpy.data.actions:
        print("ACT", a.name, tuple(a.frame_range))
    print("FPS", bpy.context.scene.render.fps, bpy.context.scene.render.fps_base)
    print("UNIT", bpy.context.scene.unit_settings.scale_length)
