import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

BW, BH, BT = 2.4, 1.1, 0.1
BZ = 1.1
PW, PH = 2.06, 0.96
POST_X = 1.04
POST_Y = 0.115
POST_R = 0.09
POST_TOP = 1.74
TAPE_W = 0.16
TAPE_T = 0.034


def face_m(x, y, z, facing=-1):
    if facing < 0:
        return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
    return Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def build_board():
    rings = rbox_rings(BW, BH, BT, 0.1, 0.03, seg=3, Rb=0.03, segb=3, z0=-BT / 2)
    finish("Board", loft(rings, 4, matrix=face_m(0, 0, BZ)), "SH_WoodDark", angle=50)
    bm = bmesh.new()
    for f in (-1, 1):
        panel = rbox_rings(PW, PH, 0.02, 0.07, 0.01, seg=2)
        loft(panel, 4, cap0=False, bm=bm, matrix=face_m(0, f * (BT / 2 - 0.006), BZ, facing=f))
    finish("Panels", bm, "SH_Cream", angle=55)


def build_posts():
    bm = bmesh.new()
    prof = [(0.0, 0.0), (POST_R + 0.05, 0.0), (POST_R + 0.055, 0.04), (POST_R + 0.03, 0.08), (POST_R + 0.004, 0.12),
            (POST_R, 0.16), (POST_R, POST_TOP - 0.04), (POST_R * 0.8, POST_TOP - 0.008), (POST_R * 0.4, POST_TOP + 0.004),
            (0.0, POST_TOP + 0.006)]
    for sx in (-1, 1):
        lathe_bm(prof, 12, bm=bm, matrix=Matrix.Translation((sx * POST_X, POST_Y, 0)))
    finish("Posts", bm, "SH_WoodDark", angle=40)
    bm = bmesh.new()
    for sx in (-1, 1):
        ellipsoid_bm((sx * POST_X, POST_Y, POST_TOP + 0.075), (0.105, 0.105, 0.09), 12, 7, bm=bm)
    finish("PostBalls", bm, "SH_Straw", angle=80)


def tape(cx, cz, ang, L, mats, w=TAPE_W):
    y = -BT / 2 - 0.012
    n = max(3, int(round(L / 0.13)))
    sl = L / n
    rot = Matrix.Rotation(-ang, 4, "Y")
    for k in range(n):
        u = -L / 2 + sl * (k + 0.5)
        m = Matrix.Translation((cx, y, cz)) @ rot @ Matrix.Translation((u, 0, 0))
        rbox_bm((0, 0, 0), (sl + 0.002, TAPE_T, w), 0.01, 1, bm=mats[k % 2], matrix=m)


def build_tape():
    yel = bmesh.new()
    blk = bmesh.new()
    d = 0.17
    for sx in (-1, 1):
        for sz in (1,):
            cx = sx * (BW / 2 - d * 0.62)
            cz = BZ + sz * (BH / 2 - d * 0.62)
            ang = math.radians(45) * (-sx * sz)
            tape(cx, cz, ang, 0.38, (yel, blk))
    tape(0, BZ - BH / 2 + 0.05, 0.0, 2.2, (yel, blk), w=0.085)
    finish("TapeY", yel, "SH_Straw", angle=50)
    finish("TapeK", blk, "SH_Dark", angle=50)


def build_lock():
    zc = BZ + BH / 2 + 0.14
    bw, bh, bd = 0.6, 0.48, 0.2
    y = -0.015
    rings = rbox_rings(bw, bh, bd, 0.15, 0.05, seg=3, Rb=0.045, segb=3, z0=-bd / 2)
    finish("LockBody", loft(rings, 4, matrix=face_m(0, y, zc)), "SH_Coral", angle=50)
    plate = rbox_rings(0.28, 0.3, 0.024, 0.1, 0.012, seg=2)
    finish("LockPlate", loft(plate, 4, cap0=False, matrix=face_m(0, y - bd / 2 + 0.008, zc - 0.01)), "SH_Straw", angle=55)
    kh = bmesh.new()
    prof = [(0.0, 0.0), (0.055, 0.0), (0.055, 0.02), (0.0, 0.02)]
    lathe_bm(prof, 12, bm=kh, matrix=face_m(0, y - bd / 2 - 0.008, zc + 0.03))
    rings = rbox_rings(0.05, 0.13, 0.02, 0.016, 0.004, seg=1)
    loft(rings, 2, bm=kh, matrix=face_m(0, y - bd / 2 - 0.008, zc - 0.045))
    finish("Keyhole", kh, "SH_Dark", angle=60)
    bm = bmesh.new()
    for sx in (-1, 1):
        for sz in (-1, 1):
            ellipsoid_bm((sx * 0.225, y - bd / 2 + 0.004, zc + sz * 0.165), (0.034, 0.022, 0.034), 8, 5, bm=bm)
    finish("Rivets", bm, "SH_Straw", angle=80)
    top = zc + bh / 2
    rr = 0.175
    pts = [(-rr, y, top - 0.04), (-rr, y, top + 0.08)]
    for k in range(1, 10):
        a = math.pi - math.pi * k / 10
        pts.append((rr * math.cos(a), y, top + 0.08 + rr * math.sin(a) * 1.05))
    pts += [(rr, y, top + 0.08), (rr, y, top - 0.04)]
    finish("Shackle", tube_bm(pts, 0.055, 10), "SH_Dark", angle=60)


def build_chain():
    a = Vector((-POST_X + POST_R * 0.6, POST_Y, 0.44))
    b = Vector((POST_X - POST_R * 0.6, POST_Y, 0.44))
    sag = 0.16
    pitch = 0.105
    L = (b - a).length
    n = int(L / pitch)
    bm = bmesh.new()
    pts = []
    for k in range(n + 1):
        t = k / n
        p = a.lerp(b, t)
        p.z -= sag * 4 * t * (1 - t)
        pts.append(p)
    for k in range(n):
        p, q = pts[k], pts[k + 1]
        c = (p + q) / 2
        d = q - p
        ang = math.atan2(d.z, d.x)
        m = Matrix.Translation(c) @ Matrix.Rotation(-ang, 4, "Y") @ Matrix.Diagonal((1.45, 1.0, 1.0, 1.0))
        if k % 2:
            m = m @ Matrix.Rotation(math.pi / 2, 4, "X")
        torus_bm(0.045, 0.017, 10, 5, bm=bm, matrix=m)
    finish("Chain", bm, "SH_Dark", angle=70)


out, flags = cli()
begin()
build_board()
build_posts()
build_tape()
build_lock()
build_chain()
ob = join_all("ShopLockedSign")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(1.75, -0.5, 0))
