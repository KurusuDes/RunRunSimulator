import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from zone_annex import *

T = 0.3
ZT = 2.7
CAP = ZT + 0.09
X_HI, X_WALL = 36.5, 46.15
YN_IN, YN_OUT = -21.85, -22.15
YS_IN, YS_OUT = -7.15, -6.85
FX0 = 36.8

out, flags = cli()
begin_env()
rng = random.Random(1590)
S = Shed(X_HI, X_WALL, 0.4, CAP + 0.165, 4.72, YN_OUT, YS_OUT, 0.25)
n = 13
rafters = [YN_IN + (YS_IN - YN_IN) * k / n for k in range(1, n)]
B = build_shed_roof(S, rafters, (YN_IN, YS_IN), (YN_OUT + 0.03, YS_OUT - 0.03), T,
                    [(YN_IN, YN_OUT, X_WALL, CAP, [39.3, 41.8, 44.3], [41.8]), (YS_IN, YS_OUT, X_WALL, CAP, [38.6, 44.3], [40.34, 42.66])],
                    CAP, rng, lanterns=[(41.8, rafters[4]), (41.8, rafters[9])],
                    lintel=(X_HI, FX0 + 0.02, [(YN_IN, YN_OUT), (YS_IN, YS_OUT)]))
B.done("Roof", angle=50)
parts_report()
ob = join_all("ShopRoofCriadero")
report(ob)
zs = [v.co.z for v in ob.data.vertices]
print("ROOF_ZMAX %.3f ZMIN %.3f slope_deg %.1f" % (max(zs), min(zs), math.degrees(S.th)))
coplanar_report([ob], "ShopRoofCriadero", show=30)
export(ob, flags)
