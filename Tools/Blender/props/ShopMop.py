import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

LEN = 1.2
COLLAR_Z = 0.2
STICK_R = 0.037


def strand(bm, ang, reach, r0, r1, curl, droop):
    prof = [(0.035, COLLAR_Z - 0.02), (0.08 + 0.04 * reach, COLLAR_Z - 0.08), (0.12 + 0.07 * reach, 0.07 + droop),
            (0.15 + 0.1 * reach, r1 + 0.004), (0.17 + 0.12 * reach, r1 + 0.008)]
    pts = catmull(prof, 2)
    n = len(pts)
    out = []
    for i, p in enumerate(pts):
        a = math.radians(ang + curl * i / (n - 1))
        out.append((p.x * math.cos(a), p.x * math.sin(a), p.y))
    radii = [r0 + (r1 - r0) * (i / (n - 1)) for i in range(n)]
    tube_bm(out, radii, 8, bm=bm)
    e = Vector(out[-1])
    ellipsoid_bm(e, (r1 * 1.08, r1 * 1.08, r1 * 1.0), useg=8, vseg=5, bm=bm)


out, flags = cli()
begin()

stick = bmesh.new()
lathe_bm([(0.0, COLLAR_Z), (STICK_R, COLLAR_Z), (STICK_R, LEN - 0.07), (0.0, LEN - 0.07)], 10, bm=stick)
finish("Stick", stick, "SH_Wood", angle=50)

cap = bmesh.new()
lathe_bm([(0.0, LEN - 0.085), (0.04, LEN - 0.085), (0.046, LEN - 0.07), (0.046, LEN - 0.03), (0.036, LEN - 0.006), (0.0, LEN)], 12, bm=cap)
finish("Cap", cap, "SH_Coral", angle=50)

collar = bmesh.new()
lathe_bm([(0.0, COLLAR_Z - 0.06), (0.066, COLLAR_Z - 0.06), (0.078, COLLAR_Z - 0.045), (0.078, COLLAR_Z + 0.03),
          (0.066, COLLAR_Z + 0.045), (0.05, COLLAR_Z + 0.06), (0.034, COLLAR_Z + 0.075), (0.0, COLLAR_Z + 0.075)], 14, bm=collar)
finish("Collar", collar, "SH_Sky", angle=50)

bolt = bmesh.new()
lathe_bm([(0.0, 0.0), (0.024, 0.0), (0.024, 0.014), (0.017, 0.022), (0.0, 0.024)], 10, bm=bolt,
         matrix=Matrix(((1, 0, 0, 0), (0, 0, -1, -0.074), (0, 1, 0, COLLAR_Z), (0, 0, 0, 1))))
finish("Bolt", bolt, "SH_Coral", angle=55)

mop = bmesh.new()
ellipsoid_bm((0, 0, 0.112), (0.15, 0.15, 0.11), useg=12, vseg=7, bm=mop)
N = 11
for k in range(N):
    ang = 360.0 * k / N + 6 * math.sin(k * 2.3)
    strand(mop, ang, 0.5 + 0.5 * (0.5 + 0.5 * math.sin(k * 1.7)), 0.046, 0.054, 16 * math.sin(k * 1.3), 0.015 * math.cos(k * 2.1))
finish("Strands", mop, "SH_Cream", angle=None)

ob = join_all("ShopMop")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.75, 0.45, 0), dragon_rot=20.0, target=(-0.15, 0, 0.6), ortho=1.6)
