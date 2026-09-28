import os
import sys
import glob
import bpy
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "parts"))
import part_common as pc

ARGS = pc.args()
SRC, OUT = ARGS[0], ARGS[1]
VIEWS = ARGS[2].split(",") if len(ARGS) > 2 else ["side"]
SIZE = 360


def textured(img):
    mat = bpy.data.materials.new("pat")
    mat.use_nodes = True
    nt = mat.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    nt.nodes.active = tex
    return mat


def read(path):
    img = bpy.data.images.load(path)
    a = np.empty(len(img.pixels), dtype=np.float32)
    img.pixels.foreach_get(a)
    arr = a.reshape(img.size[1], img.size[0], 4)
    bpy.data.images.remove(img)
    return arr


files = sorted(glob.glob(os.path.join(SRC, "*.png")))
tiles = []
for f in files:
    for v in VIEWS:
        pc.load_dragon("A")
        body = pc.mesh("Dragon_body")
        img = bpy.data.images.load(f)
        body.data.materials.clear()
        body.data.materials.append(textured(img))
        sc = bpy.context.scene
        tmp = os.path.join(OUT, "_tile.png")
        pc.setup_render(tmp, res=(SIZE, SIZE), view=v)
        body.data.materials.clear()
        body.data.materials.append(textured(img))
        sc.display.shading.color_type = "TEXTURE"
        bpy.ops.render.render(write_still=True)
        tiles.append(read(tmp))
cols = 5 * len(VIEWS)
rows = (len(tiles) + cols - 1) // cols
sheet = np.zeros((rows * SIZE, cols * SIZE, 4), dtype=np.float32)
sheet[..., 3] = 1
for k, t in enumerate(tiles):
    r, c = k // cols, k % cols
    sheet[(rows - 1 - r) * SIZE:(rows - r) * SIZE, c * SIZE:(c + 1) * SIZE] = t
out = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=True)
out.pixels.foreach_set(sheet.ravel())
out.filepath_raw = os.path.join(OUT, "patterns_sheet.png")
out.file_format = "PNG"
out.save()
print("PREVIEW_DONE", len(tiles), [os.path.basename(f) for f in files])
