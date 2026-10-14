import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

AX_Z = 0.175
DISC_X = 0.178
DISC_T = 0.05
DISC_R = 0.135
CARD_W = 0.27
CARD_T = 0.036
R0 = 0.05
R1 = 0.165


def rot_x_to(m_axis):
    return Matrix.Rotation(math.radians(90 * m_axis), 4, "Y")


def card(bm, ang, r1, w=CARD_W, cx=0.0, t=CARD_T):
    h = r1 - R0
    rbox_bm((cx, 0.0, R0 + h / 2), (w, t, h), 0.011, segs=1, bm=bm,
            matrix=None)
    return bm


def place(bm, verts, ang):
    m = Matrix.Translation((0, 0, AX_Z)) @ Matrix.Rotation(math.radians(ang), 4, "X")
    xf(bm, m, verts)


out, flags = cli()
begin()

finish("Base", soft_box((0, 0, 0.035), (0.40, 0.31, 0.07), 0.07, 0.03, seg=3, Rb=0.012), "SH_Mint", angle=50)
foot = bmesh.new()
for sx in (1, -1):
    rbox_bm((sx * DISC_X, 0.0, 0.075), (DISC_T * 0.9, 0.16, 0.06), 0.02, segs=2, bm=foot)
finish("Cradle", foot, "SH_Mint", angle=50)

prof = [(0.0, -DISC_T / 2), (DISC_R - 0.014, -DISC_T / 2), (DISC_R, -DISC_T / 2 + 0.014),
        (DISC_R, DISC_T / 2 - 0.014), (DISC_R - 0.014, DISC_T / 2), (0.0, DISC_T / 2)]
discs = bmesh.new()
for sx in (1, -1):
    lathe_bm(prof, 24, bm=discs, matrix=Matrix.Translation((sx * DISC_X, 0, AX_Z)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
finish("Discs", discs, "SH_Mint", angle=50)

kprof = [(0.0, 0.0), (0.05, 0.0), (0.05, 0.018), (0.04, 0.034), (0.0, 0.04)]
knobs = bmesh.new()
for sx in (1, -1):
    lathe_bm(kprof, 16, bm=knobs, matrix=Matrix.Translation((sx * (DISC_X + DISC_T / 2 - 0.004), 0, AX_Z)) @
             Matrix.Rotation(math.radians(90 * sx), 4, "Y"))
finish("Knobs", knobs, "SH_Coral", angle=55)

hub = bmesh.new()
lathe_bm([(0.0, -DISC_X), (0.055, -DISC_X), (0.055, DISC_X), (0.0, DISC_X)], 12, bm=hub,
         matrix=Matrix.Translation((0, 0, AX_Z)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
finish("Hub", hub, "SH_Coral", angle=50)

angles = [-70 + 14 * i for i in range(11)]
seps = {2: ("SH_Sky", -0.08), 5: ("SH_Coral", 0.0), 8: ("SH_Straw", 0.08)}
white = bmesh.new()
colored = {k: bmesh.new() for k in ("SH_Sky", "SH_Coral", "SH_Straw")}
for i, a in enumerate(angles):
    fan = 1.0 - 0.18 * (abs(a) / 70.0) ** 2
    r1 = R0 + (R1 - R0) * fan
    if i in seps:
        mat, tx = seps[i]
        bm = colored[mat]
        before = set(bm.verts)
        card(bm, a, r1 + 0.012)
        rbox_bm((tx, 0.0, r1 + 0.03), (0.085, CARD_T, 0.05), 0.012, segs=1, bm=bm)
        place(bm, [v for v in bm.verts if v not in before], a)
    else:
        before = set(white.verts)
        card(white, a, r1)
        place(white, [v for v in white.verts if v not in before], a)
finish("Cards", white, "SH_White", angle=50)
for mat, bm in colored.items():
    finish("Sep_" + mat, bm, mat, angle=50)

lab = bmesh.new()
loft(rbox_rings(0.14, 0.05, 0.012, 0.02, 0.006, seg=1), 2, cap0=False, bm=lab,
     matrix=Matrix(((1, 0, 0, 0), (0, 0, -1, -0.155 + 0.004), (0, 1, 0, 0.038), (0, 0, 0, 1))))
finish("Label", lab, "SH_White", angle=60)

ob = join_all("ShopLedger")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.72, 0.42, 0), dragon_rot=20.0, target=(-0.1, 0, 0.3), ortho=1.25)
