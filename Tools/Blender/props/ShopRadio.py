import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

BW = 0.40
BD = 0.22
BH = 0.26
Z0 = 0.035
TOP = Z0 + BH
YF = -BD / 2


def front(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


out, flags = cli()
begin()

finish("Plinth", soft_box((0, 0, 0.03), (BW + 0.02, BD + 0.02, 0.06), 0.06, 0.022, seg=2, Rb=0.01), "SH_Dark", angle=50)
finish("Body", soft_box((0, 0, Z0 + BH / 2), (BW, BD, BH), 0.055, 0.035, seg=3), "SH_Straw", angle=50)
finish("TopRim", soft_box((0, 0, TOP - 0.035), (BW + 0.014, BD + 0.014, 0.04), 0.06, 0.012, seg=1, Rb=0.012), "SH_Dark", angle=50)
hpts = [(-0.055, 0.0, TOP - 0.01)] + [(-0.055 + 0.11 * (0.5 - 0.5 * math.cos(math.pi * t / 6)), 0.0,
                                       TOP + 0.075 * math.sin(math.pi * t / 6)) for t in range(1, 6)] + [(0.055, 0.0, TOP - 0.01)]
finish("Handle", tube_bm(hpts, 0.019, 8), "SH_Dark", angle=60)

zc = Z0 + BH * 0.47
spk = bmesh.new()
loft(rbox_rings(0.17, 0.165, 0.016, 0.04, 0.008, seg=2), 3, cap0=False, bm=spk, matrix=front(-0.09, YF + 0.006, zc))
finish("Speaker", spk, "SH_Dark", angle=55)
ribs = bmesh.new()
for k in range(4):
    loft(rbox_rings(0.13, 0.024, 0.016, 0.012, 0.008, seg=2), 2, cap0=False, bm=ribs,
         matrix=front(-0.09, YF - 0.006, zc - 0.054 + 0.036 * k))
finish("SpeakerRibs", ribs, "SH_Straw", angle=55)

dprof = [(0.0, 0.0), (0.064, 0.0), (0.064, 0.018), (0.056, 0.03), (0.0, 0.032)]
dial = bmesh.new()
lathe_bm(dprof, 20, bm=dial, matrix=front(0.1, YF + 0.004, zc + 0.03))
finish("Dial", dial, "SH_Cream", angle=55)
ptr = bmesh.new()
rbox_bm((0.0, 0.02, 0.034), (0.018, 0.075, 0.02), 0.008, segs=1, bm=ptr)
xf(ptr, front(0.1, YF + 0.004, zc + 0.03) @ Matrix.Rotation(math.radians(-35), 4, "Z"))
finish("DialPointer", ptr, "SH_Coral", angle=55)

kprof = [(0.0, 0.0), (0.026, 0.0), (0.026, 0.02), (0.02, 0.028), (0.0, 0.03)]
knobs = bmesh.new()
for x in (0.065, 0.135):
    lathe_bm(kprof, 12, bm=knobs, matrix=front(x, YF + 0.004, zc - 0.07))
finish("Knobs", knobs, "SH_Dark", angle=55)

bulb = bmesh.new()
lathe_bm([(0.0, 0.0), (0.05, 0.0), (0.05, 0.02), (0.0, 0.02)], 16, bm=bulb, matrix=Matrix.Translation((-0.135, 0.0, TOP - 0.004)))
finish("BulbBase", bulb, "SH_Cream", angle=50)
dome = ellipsoid_bm((-0.135, 0.0, TOP + 0.016), (0.042, 0.042, 0.05), useg=14, vseg=8)
finish("Bulb", dome, "SH_Coral", angle=None)

ax, ay = 0.13, 0.05
ant = bmesh.new()
lathe_bm([(0.0, 0.0), (0.04, 0.0), (0.04, 0.03), (0.03, 0.04), (0.0, 0.04)], 14, bm=ant, matrix=Matrix.Translation((ax, ay, TOP - 0.006)))
finish("AntennaBase", ant, "SH_Dark", angle=50)
tilt = Matrix.Translation((ax, ay, TOP)) @ Matrix.Rotation(math.radians(-9), 4, "Y")
seg = bmesh.new()
lathe_bm([(0.0, 0.0), (0.028, 0.0), (0.028, 0.065), (0.023, 0.072), (0.023, 0.105), (0.019, 0.112), (0.019, 0.145), (0.0, 0.145)],
         10, bm=seg, matrix=tilt)
finish("Antenna", seg, "SH_Dark", angle=50)
tip = ellipsoid_bm((0, 0, 0), (0.037, 0.037, 0.037), useg=12, vseg=7)
xf(tip, tilt @ Matrix.Translation((0, 0, 0.16)))
finish("AntennaTip", tip, "SH_Coral", angle=None)

ob = join_all("ShopRadio")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.72, 0.42, 0), dragon_rot=20.0, target=(-0.1, 0, 0.3), ortho=1.25)
