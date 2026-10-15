import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from zone_annex import *

T = 0.3
ZT = 2.7
CAP = ZT + 0.09
X_HI, X_WALL = 23.5, 15.85
YN_IN, YN_OUT = -16.65, -16.95
YS_IN, YS_OUT = -7.15, -6.85
FX1 = 22.6

out, flags = cli()
begin_env()
rng = random.Random(1591)
S = Shed(X_HI, X_WALL, 0.4, CAP + 0.165, 4.72, YN_OUT, YS_OUT, 0.25)
n = 9
rafters = [YN_IN + (YS_IN - YN_IN) * k / n for k in range(1, n)]
B = build_shed_roof(S, rafters, (YN_IN, YS_IN), (YN_OUT + 0.03, YS_OUT - 0.03), T,
                    [(YN_IN, YN_OUT, X_WALL, CAP, [17.78, 19.4, 20.92], [19.4]), (YS_IN, YS_OUT, X_WALL, CAP, [17.3, 21.3], [18.34, 20.16])],
                    CAP, rng, lanterns=[(19.3, rafters[4]), (21.3, rafters[1])],
                    lintel=(FX1 - 0.02, X_HI, [(YN_IN, YN_OUT), (YS_IN, YS_OUT)]))
B.done("Roof", angle=50)
parts_report()
ob = join_all("ShopRoofSalaJuegos")
report(ob)
zs = [v.co.z for v in ob.data.vertices]
print("ROOF_ZMAX %.3f ZMIN %.3f slope_deg %.1f" % (max(zs), min(zs), math.degrees(S.th)))
coplanar_report([ob], "ShopRoofSalaJuegos", show=30)
export(ob, flags)
