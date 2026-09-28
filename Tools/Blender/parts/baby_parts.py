import sys, os, importlib
import bpy, bmesh
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import part_common as pc
import transfer_skin as ts

a = pc.args()
names, work, out_dir = a[0].split(","), a[1], a[2]
SHELLS = {"Blobim": ("MonchiSlime_Skin.blend", "Slime_Body"), "Egg": ("MonchiEgg_Skin.blend", "Egg_Shell")}
SLIME_SCALE, SLIME_LIFT = 0.208, 0.6
LINK = {"Hoz": 0.45}
EGG_HORN = (0.55, 0.75, 25)
EGG_BACK = (1.0, 1.0, 0)


def append_shell(mode):
    path, name = SHELLS[mode]
    with bpy.data.libraries.load(os.path.join(work, path)) as (src, dst):
        dst.objects = [name]
    ob = dst.objects[0]
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update()
    return ob


def tagged(o, i):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.transform(o.matrix_world)
    layer = bm.faces.layers.int.new("src")
    for f in bm.faces:
        f[layer] = i
    me = bpy.data.meshes.new(o.name + "_tagged")
    bm.to_mesh(me)
    bm.free()
    return me


def joined(objs):
    bm = bmesh.new()
    for i, o in enumerate(objs):
        me = tagged(o, i)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new("joined")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("joined", me)
    bpy.context.collection.objects.link(ob)
    return ob


def split(ob, names):
    out = []
    for i, name in enumerate(names):
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.transform(ob.matrix_world)
        layer = bm.faces.layers.int.get("src")
        if layer is not None:
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[layer] != i], context="FACES")
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        for f in bm.faces:
            f.material_index = 0
            f.smooth = True
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        piece = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(piece)
        out.append(piece)
    bpy.data.objects.remove(ob, do_unlink=True)
    return out


def baby(mode, slot, objs, body, shell, link):
    names = [o.name for o in objs]
    for o in objs:
        o.name = o.name + "_adult"
    if mode == "Blobim":
        if slot != "Horn":
            return []
        src = joined(objs)
        placed = ts.place_rigid(src, body, shell, "placed", SLIME_SCALE, SLIME_LIFT, link)
        bpy.data.objects.remove(src, do_unlink=True)
        return split(placed, names)
    if slot == "Wing":
        return []
    k, lift, soft = EGG_HORN if slot == "Horn" else EGG_BACK
    out = []
    for o, name in zip(objs, names):
        mini = ts.conform(o, body, shell, name + "_mini", k, lift)
        mini.parent = None
        if soft and len(mini.data.vertices) >= 50:
            ts.soften(mini, soft)
        out += split(mini, [name])
    return out


def export(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_scale_options="FBX_SCALE_ALL",
                             bake_space_transform=True, object_types={"MESH"}, mesh_smooth_type="FACE", path_mode="STRIP")


os.makedirs(out_dir, exist_ok=True)
for name in names:
    mod = importlib.import_module("p_" + name)
    for mode in SHELLS:
        arm = pc.load_dragon("A")
        objs = mod.build(arm)
        shell = append_shell(mode)
        result = baby(mode, mod.SLOTS[0], objs, pc.mesh("Dragon_body"), shell, LINK.get(name, 0.25))
        if not result:
            print("BABY_SKIP", mode, name)
            continue
        export(result, os.path.join(out_dir, "%sPart_%s.fbx" % (mode, name)))
        print("BABY_DONE", mode, name, [(o.name, len(o.data.vertices), tuple(round(d, 3) for d in o.dimensions)) for o in result])
