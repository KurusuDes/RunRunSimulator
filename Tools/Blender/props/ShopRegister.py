import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

CW, CD, CH = 1.0, 0.8, 0.8
TOP_T = 0.075
BW, BD = 0.88, 0.66
REG_Y = 0.06
SLOPE_Y0, SLOPE_Y1 = -0.17, 0.29
BODY_H0, BODY_H1 = 0.24, 0.11


def face_m(x, y, z, facing=-1):
    if facing < 0:
        return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
    return Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def dollar_bm(cx, y, cz, s, facing=-1, r=0.012, bm=None):
    bm = bm or bmesh.new()
    S = [(0.034, 0.03), (0.014, 0.05), (-0.018, 0.048), (-0.035, 0.028), (-0.022, 0.007), (0.0, 0.0),
         (0.022, -0.007), (0.035, -0.028), (0.018, -0.048), (-0.014, -0.05), (-0.034, -0.03)]
    pts = catmull(S, 4)
    f = 1 if facing < 0 else -1
    world = [(cx + p.x * s * f, y, cz + p.y * s) for p in pts]
    tube_bm(world, r * s / 1.0, 6, bm=bm)
    tube_bm([(cx, y, cz - 0.072 * s), (cx, y, cz + 0.072 * s)], r * s * 0.85, 6, bm=bm)
    return bm


def build_counter():
    rings = rbox_rings(CW, CD, TOP_T, 0.09, 0.032, seg=3, Rb=0.02, segb=2, z0=CH - TOP_T)
    finish("Top", loft(rings, 3), "SH_WoodDark", angle=50)
    rings = rbox_rings(BW, BD, CH - TOP_T - 0.05 + 0.01, 0.06, 0.012, seg=1, z0=0.06)
    finish("Body", loft(rings, 3), "SH_Wood", angle=50)
    rings = rbox_rings(BW + 0.05, BD + 0.05, 0.085, 0.08, 0.025, seg=2, z0=0.0)
    finish("Plinth", loft(rings, 3), "SH_WoodDark", angle=50)
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (BW / 2 - 0.035), sy * (BD / 2 - 0.035)
            prof = [(0.0, 0.07), (0.058, 0.07), (0.058, CH - TOP_T + 0.005), (0.0, CH - TOP_T + 0.005)]
            lathe_bm(prof, 10, bm=bm, matrix=Matrix.Translation((x, y, 0)))
    finish("Pilasters", bm, "SH_WoodDark", angle=50)
    yf = -BD / 2
    zc = 0.4
    pw, ph = 0.6, 0.46
    panel = rbox_rings(pw, ph, 0.03, 0.06, 0.014, seg=2)
    finish("FrontPanel", loft(panel, 3, cap0=False, matrix=face_m(0, yf + 0.008, zc)), "SH_Cream", angle=55)
    prof = [(0.0, 0.0), (0.13, 0.0), (0.135, 0.02), (0.128, 0.034), (0.11, 0.036), (0.1, 0.03), (0.0, 0.03)]
    finish("Coin", lathe_bm(prof, 20, matrix=face_m(0, yf - 0.018, zc)), "SH_Coral", angle=50)
    finish("CoinSign", dollar_bm(0, yf - 0.05, zc, 1.6, r=0.012), "SH_Cream", angle=70)
    for sx in (-1, 1):
        side = rbox_rings(0.44, 0.46, 0.03, 0.06, 0.014, seg=2)
        m = Matrix.Translation((sx * (BW / 2 - 0.008), 0, zc)) @ Matrix.Rotation(sx * math.pi / 2, 4, "Y") @ \
            Matrix.Rotation(math.pi / 2, 4, "Z")
        finish("SidePanel", loft(side, 3, cap0=False, matrix=m), "SH_Cream", angle=55)
    bm = bmesh.new()
    for sx in (-1, 1):
        back = rbox_rings(0.285, ph, 0.03, 0.05, 0.014, seg=2)
        loft(back, 3, cap0=False, bm=bm, matrix=face_m(sx * 0.157, BD / 2 - 0.008, zc, facing=1))
    finish("BackDoors", bm, "SH_Cream", angle=55)
    prof = [(0.0, 0.0), (0.038, 0.0), (0.038, 0.02), (0.026, 0.034), (0.0, 0.036)]
    bm = bmesh.new()
    for sx in (-1, 1):
        lathe_bm(prof, 12, bm=bm, matrix=face_m(sx * 0.06, BD / 2 + 0.018, zc, facing=1))
    finish("BackKnobs", bm, "SH_Coral", angle=60)


def build_register():
    z0 = CH - 0.005
    soft = soft_box((0, REG_Y, z0 + 0.065), (0.6, 0.5, 0.13), 0.06, 0.035, seg=3)
    finish("Drawer", soft, "SH_Mint", angle=50)
    yb = REG_Y + 0.25
    df = rbox_rings(0.46, 0.075, 0.025, 0.03, 0.01, seg=2)
    finish("DrawerFront", loft(df, 2, cap0=False, matrix=face_m(0, yb - 0.006, z0 + 0.065, facing=1)), "SH_Cream", angle=55)
    finish("DrawerKnob", ellipsoid_bm((0, yb + 0.03, z0 + 0.065), (0.04, 0.03, 0.03), 10, 6), "SH_Coral", angle=80)

    zb = z0 + 0.12
    rings = rbox_rings(0.54, SLOPE_Y1 - SLOPE_Y0, 1.0, 0.06, 0.05, seg=3, Rb=0.0, cy=(SLOPE_Y0 + SLOPE_Y1) / 2)
    bm = loft(rings, 3)
    for v in bm.verts:
        t = (v.co.y - SLOPE_Y0) / (SLOPE_Y1 - SLOPE_Y0)
        t = min(max(t, 0.0), 1.0)
        h = BODY_H0 + (BODY_H1 - BODY_H0) * t
        v.co.z = zb - 0.01 + v.co.z * h
    finish("Body", bm, "SH_Mint", angle=45)

    theta = math.atan((BODY_H0 - BODY_H1) / (SLOPE_Y1 - SLOPE_Y0))
    rot = Matrix.Rotation(-theta, 4, "X")
    keys = bmesh.new()
    big = bmesh.new()
    pitch, size = 0.098, 0.078
    rows = (-0.06, 0.035, 0.13)
    for ri, yr in enumerate(rows):
        t = (yr + REG_Y - SLOPE_Y0) / (SLOPE_Y1 - SLOPE_Y0)
        zs = zb - 0.01 + BODY_H0 + (BODY_H1 - BODY_H0) * t
        for ci in range(4):
            x = -0.165 + ci * 0.1
            if ci == 3 and ri < 2:
                continue
            kr = rbox_rings(size, size, 0.04, 0.022, 0.016, seg=2, z0=-0.02)
            loft(kr, 2, cap0=False, bm=keys, matrix=Matrix.Translation((x, REG_Y + yr, zs)) @ rot)
        if ri == 0:
            yc = (rows[0] + rows[1]) / 2
            t = (yc + REG_Y - SLOPE_Y0) / (SLOPE_Y1 - SLOPE_Y0)
            zc = zb - 0.01 + BODY_H0 + (BODY_H1 - BODY_H0) * t
            kr = rbox_rings(size, size + pitch - 0.004, 0.045, 0.026, 0.018, seg=2, z0=-0.02)
            loft(kr, 2, cap0=False, bm=big, matrix=Matrix.Translation((0.135, REG_Y + yc, zc)) @ rot)
    finish("Keys", keys, "SH_Cream", angle=55)
    finish("BigKey", big, "SH_Coral", angle=55)

    ty = SLOPE_Y0 + 0.065
    tz = zb + BODY_H0 - 0.05
    tower = rbox_rings(0.36, 0.14, 0.13, 0.04, 0.03, seg=3, z0=tz, cy=ty)
    finish("Tower", loft(tower, 3), "SH_Mint", angle=50)
    for f, yy in ((-1, ty - 0.07), (1, ty + 0.07)):
        win = rbox_rings(0.27, 0.075, 0.02, 0.025, 0.008, seg=2)
        finish("Window", loft(win, 2, cap0=False, matrix=face_m(0, yy - f * 0.006, tz + 0.075, facing=f)), "SH_Cream", angle=55)
    fz = tz + 0.13 - 0.01
    flag = rbox_rings(0.2, 0.15, 0.04, 0.05, 0.018, seg=2)
    finish("Flag", loft(flag, 3, matrix=face_m(0, ty + 0.02, fz + 0.075)), "SH_Coral", angle=50)
    bm = dollar_bm(0, ty - 0.022, fz + 0.075, 1.15, facing=-1, r=0.013)
    dollar_bm(0, ty + 0.022, fz + 0.075, 1.15, facing=1, r=0.013, bm=bm)
    finish("FlagSign", bm, "SH_Cream", angle=70)

    hx = 0.27
    hz = zb + 0.07
    hy = REG_Y + 0.02
    prof = [(0.0, 0.0), (0.06, 0.0), (0.06, 0.025), (0.045, 0.04), (0.0, 0.042)]
    m = Matrix.Translation((hx - 0.005, hy, hz)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
    finish("CrankHub", lathe_bm(prof, 14, matrix=m), "SH_Cream", angle=55)
    arm = [(hx + 0.035, hy, hz), (hx + 0.045, hy + 0.06, hz - 0.035), (hx + 0.045, hy + 0.1, hz - 0.075)]
    bm = tube_bm(arm, 0.018, 8)
    tube_bm([(hx + 0.04, hy + 0.1, hz - 0.075), (hx + 0.12, hy + 0.1, hz - 0.075)], 0.017, 8, bm=bm)
    finish("CrankArm", bm, "SH_Cream", angle=60)
    finish("CrankKnob", ellipsoid_bm((hx + 0.14, hy + 0.1, hz - 0.075), (0.042, 0.038, 0.038), 10, 6), "SH_Coral", angle=80)


def build_bell():
    x, y, z = -0.34, -0.27, CH - 0.004
    prof = [(0.0, 0.0), (0.075, 0.0), (0.078, 0.012), (0.07, 0.024), (0.0, 0.024)]
    finish("BellBase", lathe_bm(prof, 16, matrix=Matrix.Translation((x, y, z))), "SH_Cream", angle=50)
    prof = [(0.062, 0.018), (0.064, 0.03), (0.056, 0.058), (0.04, 0.08), (0.02, 0.09), (0.0, 0.093)]
    prof = [(0.0, 0.018)] + prof
    finish("BellDome", lathe_bm(prof, 16, matrix=Matrix.Translation((x, y, z))), "SH_Coral", angle=60)
    finish("BellNub", ellipsoid_bm((x, y, z + 0.1), (0.018, 0.018, 0.016), 8, 5), "SH_Cream", angle=80)


out, flags = cli()
begin()
build_counter()
build_register()
build_bell()
ob = join_all("ShopRegister")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(1.3, -0.35, 0))
