import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

BW = 0.42
BD = 0.34
BH = 0.19
LW = 0.44
LD = 0.36
LH = 0.075
OPEN = -24.0
SX = 0.125


def front(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


ARCH = 0.045


def arch(bm, verts=None):
    for v in (verts if verts is not None else bm.verts):
        u = (v.co.y + LD / 2) / (LD / 2 + 0.02)
        v.co.z += ARCH * max(0.0, 1 - u * u) * max(0.0, v.co.z) / LH


def lid_matrix():
    return Matrix.Translation((0, LD / 2, BH)) @ Matrix.Rotation(math.radians(OPEN), 4, "X")


out, flags = cli()
begin()

body = bmesh.new()
soft_box((0, 0, BH * 0.25), (BW, BD, BH * 0.5), 0.045, 0.02, seg=2, Rb=0.012, bm=body)
soft_box((0, 0, BH * 0.75), (BW, BD, BH * 0.5 + 0.004), 0.045, 0.02, seg=2, Rb=0.012, bm=body)
finish("Body", body, "SH_WoodDark", angle=50)

inner = bmesh.new()
loft(rbox_rings(BW - 0.07, BD - 0.07, 0.012, 0.03, 0.005, seg=1, z0=BH - 0.008), 2, bm=inner)
finish("Inside", inner, "SH_Dark", angle=50)

coins = bmesh.new()
for x, y, z, r in ((-0.07, -0.02, BH + 0.006, 0.045), (-0.02, 0.03, BH + 0.012, 0.05), (0.05, -0.03, BH + 0.004, 0.044),
                   (0.11, 0.04, BH + 0.006, 0.042)):
    ellipsoid_bm((x, y, z), (r, r, 0.022), useg=10, vseg=5, bm=coins)
finish("Treasure", coins, "SH_Straw", angle=None)

straps = bmesh.new()
for sx in (1, -1):
    soft_box((sx * SX, 0, BH * 0.5 - 0.001), (0.055, BD + 0.022, BH - 0.012), 0.012, 0.01, seg=1, Rb=0.006, bm=straps)
feet = bmesh.new()
for sx in (1, -1):
    for sy in (1, -1):
        rbox_bm((sx * (BW / 2 - 0.03), sy * (BD / 2 - 0.03), 0.035), (0.08, 0.08, 0.07), 0.022, segs=1, bm=feet)
finish("Feet", feet, "SH_Dark", angle=50)

lid = bmesh.new()
loft(rbox_rings(LW, LD, LH, 0.05, 0.035, seg=3, Rb=0.01, segb=1, cy=-LD / 2), 3, bm=lid)
arch(lid)
xf(lid, lid_matrix())
finish("Lid", lid, "SH_WoodDark", angle=50)
for sx in (1, -1):
    sb = loft(rbox_rings(0.055, LD + 0.02, LH + 0.012, 0.012, 0.034, seg=3, z0=-0.002, cx=sx * SX, cy=-LD / 2), 2)
    arch(sb)
    xf(sb, lid_matrix())
    tmp = bpy.data.meshes.new("tmp")
    sb.to_mesh(tmp)
    sb.free()
    straps.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)
finish("Straps", straps, "SH_Dark", angle=50)

gold = bmesh.new()
loft(rbox_rings(0.09, 0.085, 0.014, 0.022, 0.007, seg=2), 2, cap0=False, bm=gold, matrix=front(0, -BD / 2 + 0.004, BH - 0.055))
hasp = bmesh.new()
rbox_bm((0, -LD - 0.004, 0.005), (0.06, 0.024, 0.085), 0.016, segs=2, bm=hasp)
xf(hasp, lid_matrix())
rprof = [(0.0, 0.0), (0.017, 0.0), (0.017, 0.006), (0.011, 0.015), (0.0, 0.017)]
for sx in (1, -1):
    for z in (0.055, BH - 0.055):
        lathe_bm(rprof, 8, bm=gold, matrix=front(sx * SX, -BD / 2 - 0.009, z))
    lathe_bm(rprof, 8, bm=gold, matrix=front(sx * SX, BD / 2 + 0.009, BH * 0.5) @ Matrix.Rotation(math.pi, 4, "Y"))
finish("Lock", gold, "SH_Straw", angle=55)
finish("Hasp", hasp, "SH_Straw", angle=55)
key = bmesh.new()
loft(rbox_rings(0.018, 0.034, 0.008, 0.008, 0.003, seg=1), 2, cap0=False, bm=key, matrix=front(0, -BD / 2 - 0.008, BH - 0.06))
finish("Keyhole", key, "SH_Dark", angle=60)

ob = join_all("ShopCrate")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.72, 0.42, 0), dragon_rot=20.0, target=(-0.1, 0, 0.3), ortho=1.25)
