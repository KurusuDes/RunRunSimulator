import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

H = 0.52
W = 0.60
D = 0.50
TOP_T = 0.08


def front(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


out, flags = cli()
begin()

finish("Top", loft(rbox_rings(W, D, TOP_T, 0.07, 0.03, seg=3, Rb=0.018, segb=2, z0=H - TOP_T), 3), "SH_Wood", angle=50)
apron_z = H - TOP_T - 0.075
finish("Apron", loft(rbox_rings(W - 0.12, D - 0.12, 0.08, 0.05, 0.012, seg=1, z0=apron_z), 2), "SH_WoodDark", angle=50)

yf = -(D - 0.12) / 2
drawer = bmesh.new()
loft(rbox_rings(0.3, 0.062, 0.016, 0.022, 0.007, seg=2), 2, cap0=False, bm=drawer, matrix=front(0, yf + 0.006, apron_z + 0.04))
finish("Drawer", drawer, "SH_Wood", angle=55)
knob = bmesh.new()
lathe_bm([(0.0, 0.0), (0.024, 0.0), (0.028, 0.014), (0.022, 0.026), (0.0, 0.03)], 12, bm=knob,
         matrix=front(0, yf - 0.008, apron_z + 0.04))
finish("Knob", knob, "SH_Straw", angle=55)

lz = H - TOP_T + 0.005
prof = [(0.0, 0.0), (0.05, 0.0), (0.068, 0.014), (0.072, 0.034), (0.064, 0.062), (0.066, 0.09), (0.078, lz - 0.03), (0.078, lz), (0.0, lz)]
legs = bmesh.new()
for sx in (1, -1):
    for sy in (1, -1):
        lathe_bm(prof, 12, bm=legs, matrix=Matrix.Translation((sx * (W / 2 - 0.1), sy * (D / 2 - 0.1), 0)))
finish("Legs", legs, "SH_WoodDark", angle=50)
finish("Shelf", loft(rbox_rings(W - 0.2, D - 0.2, 0.045, 0.03, 0.014, seg=2, z0=0.11), 3), "SH_Wood", angle=50)

ob = join_all("ShopSideTable")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.8, 0.5, 0), dragon_rot=20.0, target=(-0.15, 0, 0.4), ortho=1.7)
