import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

HX, HY = 0.9, 0.65
PLINTH_H = 0.07
TOP_Z0, TOP_Z1 = 0.235, 0.30
BODY_INSET = 0.05
CUSH_X = 0.42
CUSH_Y = -0.08
CUSH_R = 0.335
CUSH_H = 0.105
CUSH_TOP = TOP_Z1 + CUSH_H
RX, RY_BACK = 0.80, 0.54
RY_FRONT = -0.42
CORNER_R = 0.2
POST_R = 0.046
POST_TOP = 0.665
RAIL_R = 0.034
RAIL_Z = (0.47, 0.625)


def fin(name, bm, mat, angle=50.0):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def face_m(x, y, z, rx=0.0):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rx), 4, "X") @ Matrix(
        ((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def back_m(x, y, z):
    return Matrix.Translation((x, y, z)) @ Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def star_bm(R, r, depth, bm=None, matrix=None):
    bm = bm or bmesh.new()
    prof = [(1.0, 0.0), (1.0, depth * 0.55), (0.84, depth * 0.9), (0.6, depth)]
    rings = []
    for s, d in prof:
        ring = []
        for k in range(10):
            a = math.pi / 2 + math.pi * k / 5
            rad = (R if k % 2 == 0 else r) * s
            ring.append(bm.verts.new((rad * math.cos(a), rad * math.sin(a), d)))
        rings.append(ring)
    for A, B in zip(rings, rings[1:]):
        for k in range(10):
            bm.faces.new((A[k], A[(k + 1) % 10], B[(k + 1) % 10], B[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    if matrix is not None:
        xf(bm, matrix, [v for r_ in rings for v in r_])
    return bm


def paw_bm(s, bm, matrix):
    before = set(bm.verts)
    ellipsoid_bm((0, -0.03 * s, 0), (0.07 * s, 0.058 * s, 0.022 * s), 8, 4, bm=bm)
    for ang, d in ((-58, 0.105), (-20, 0.118), (20, 0.118), (58, 0.105)):
        a = math.radians(90 + ang)
        ellipsoid_bm((d * s * math.cos(a), d * s * math.sin(a) - 0.01 * s, 0), (0.03 * s, 0.036 * s, 0.018 * s), 6, 3, bm=bm)
    xf(bm, matrix, [v for v in bm.verts if v not in before])
    return bm


def build_podium():
    rings = rbox_rings(2 * HX - 0.03, 2 * HY - 0.03, PLINTH_H, 0.2, 0.025, seg=2, Rb=0.012, segb=1)
    fin("Plinth", loft(rings, 3), "SH_Walnut")
    bw, bd = 2 * HX - 2 * BODY_INSET, 2 * HY - 2 * BODY_INSET
    fin("Body", loft([(bw, bd, 0.17, PLINTH_H - 0.01), (bw, bd, 0.17, TOP_Z0 + 0.01)], 3, cap0=False, cap1=False),
        "SH_Oak")
    rings = rbox_rings(2 * HX, 2 * HY, TOP_Z1 - TOP_Z0, 0.21, 0.032, seg=3, Rb=0.02, segb=2, z0=TOP_Z0)
    fin("TopSlab", loft(rings, 3), "SH_Walnut")
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (HX - BODY_INSET - 0.05), sy * (HY - BODY_INSET - 0.05)
            prof = [(0.062, PLINTH_H - 0.01), (0.062, TOP_Z0 + 0.01)]
            lathe_bm(prof, 8, bm=bm, matrix=Matrix.Translation((x, y, 0)))
    fin("Pilasters", bm, "SH_Walnut")


def build_cushions():
    for i, sx in enumerate((-1, 1)):
        cx = sx * CUSH_X
        prof = [(0.0, TOP_Z1 - 0.005), (CUSH_R - 0.035, TOP_Z1 - 0.005), (CUSH_R, TOP_Z1 + 0.035),
                (CUSH_R - 0.04, TOP_Z1 + 0.085), (0.15, CUSH_TOP), (0.0, CUSH_TOP - 0.012)]
        fin("Cushion%d" % i, lathe_bm(prof, 20, matrix=Matrix.Translation((cx, CUSH_Y, 0))), "SH_Sage", angle=70)
        m = Matrix.Translation((cx, CUSH_Y, TOP_Z1 + 0.035))
        bm = torus_bm(CUSH_R + 0.002, 0.021, 20, 4, matrix=m)
        fin("Piping%d" % i, bm, "SH_Gold", angle=70)


def rail_path(z, n_arc=3):
    pts = [(-RX, RY_FRONT, z), (-RX, RY_BACK - CORNER_R, z)]
    for j in range(1, n_arc):
        a = math.pi - math.pi / 2 * j / n_arc
        pts.append((-RX + CORNER_R + CORNER_R * math.cos(a), RY_BACK - CORNER_R + CORNER_R * math.sin(a), z))
    pts += [(-RX + CORNER_R, RY_BACK, z), (RX - CORNER_R, RY_BACK, z)]
    for j in range(1, n_arc):
        a = math.pi / 2 - math.pi / 2 * j / n_arc
        pts.append((RX - CORNER_R + CORNER_R * math.cos(a), RY_BACK - CORNER_R + CORNER_R * math.sin(a), z))
    pts += [(RX, RY_BACK - CORNER_R, z), (RX, RY_FRONT, z)]
    return pts


def build_rail():
    rails = bmesh.new()
    for z in RAIL_Z:
        tube_bm(rail_path(z), RAIL_R, 6, bm=rails)
    fin("Rails", rails, "SH_Oak", angle=60)
    a45 = math.radians(45)
    posts = [(-RX, RY_FRONT), (RX, RY_FRONT), (0.0, RY_BACK),
             (-RX + CORNER_R - CORNER_R * math.cos(a45), RY_BACK - CORNER_R + CORNER_R * math.sin(a45)),
             (RX - CORNER_R + CORNER_R * math.cos(a45), RY_BACK - CORNER_R + CORNER_R * math.sin(a45))]
    bm = bmesh.new()
    balls = bmesh.new()
    z0 = TOP_Z1 - 0.005
    for x, y in posts:
        r = POST_R + (0.008 if y == RY_FRONT else 0.0)
        prof = [(r + 0.024, z0), (r + 0.02, z0 + 0.04), (r, z0 + 0.07), (r, POST_TOP), (0.0, POST_TOP + 0.006)]
        lathe_bm(prof, 8, bm=bm, matrix=Matrix.Translation((x, y, 0)))
        ellipsoid_bm((x, y, POST_TOP + 0.04), (r + 0.016, r + 0.016, 0.05), 8, 4, bm=balls)
    fin("Posts", bm, "SH_Walnut", angle=40)
    fin("PostBalls", balls, "SH_Gold", angle=80)


def build_sign():
    y0, z0 = -HY + 0.13, TOP_Z1
    stake = bmesh.new()
    prof = [(0.0, z0 - 0.005), (0.05, z0 - 0.005), (0.045, z0 + 0.025), (0.026, z0 + 0.04), (0.026, z0 + 0.12),
            (0.0, z0 + 0.125)]
    lathe_bm(prof, 8, bm=stake, matrix=Matrix.Translation((0, y0 + 0.02, 0)))
    tilt = -14.0
    bz = z0 + 0.205
    frame = rbox_rings(0.4, 0.22, 0.05, 0.08, 0.018, seg=1, z0=-0.025)
    loft(frame, 3, bm=stake, matrix=face_m(0, y0, bz, tilt))
    fin("SignFrame", stake, "SH_Walnut")
    panel = rbox_rings(0.33, 0.155, 0.016, 0.05, 0.007, seg=1, z0=0.0)
    fin("SignPanel", loft(panel, 3, cap0=False, matrix=face_m(0, y0, bz, tilt) @ Matrix.Translation((0, 0, 0.024))),
        "SH_Oak", angle=55)
    st = face_m(0, y0, bz, tilt) @ Matrix.Translation((-0.085, 0.005, 0.038))
    bm = star_bm(0.072, 0.034, 0.032, matrix=st)
    coin = face_m(0, y0, bz, tilt) @ Matrix.Translation((0.075, -0.005, 0.038))
    prof = [(0.0, 0.0), (0.05, 0.0), (0.052, 0.01), (0.043, 0.02), (0.0, 0.02)]
    lathe_bm(prof, 10, bm=bm, matrix=coin)
    fin("SignGold", bm, "SH_Gold", angle=60)


def build_charms():
    bm = bmesh.new()
    zf = (PLINTH_H + TOP_Z0) / 2
    for sx in (-1, 1):
        paw_bm(0.82, bm, face_m(sx * CUSH_X, -HY + BODY_INSET + 0.006, zf + 0.005))
    star_bm(0.072, 0.034, 0.03, bm=bm, matrix=back_m(0, HY - BODY_INSET - 0.004, zf + 0.004))
    for sx in (-1, 1):
        paw_bm(0.68, bm, back_m(sx * 0.52, HY - BODY_INSET - 0.004, zf + 0.004))
    fin("Charms", bm, "SH_Gold", angle=70)


out, flags = cli()
begin()
build_podium()
build_cushions()
build_rail()
build_sign()
build_charms()
ob = join_all("ShopShowcaseWindow")
report(ob)
export(ob, flags)
if out and "empty" not in flags:
    d2 = load_dragon((CUSH_X, CUSH_Y, CUSH_TOP - 0.02), 8.0)
    bpy.context.view_layer.update()
    xs = [(o.matrix_world @ Vector(c)).x for o in d2 if o.type == "MESH" and not o.hide_render for c in o.bound_box]
    ys = [(o.matrix_world @ Vector(c)).y for o in d2 if o.type == "MESH" and not o.hide_render for c in o.bound_box]
    print("DRAGON2_X %.3f %.3f Y %.3f %.3f" % (min(xs), max(xs), min(ys), max(ys)))
preview(ob, out, dragon_loc=(-CUSH_X, CUSH_Y, CUSH_TOP - 0.02) if "empty" not in flags else (9, 9, 0), dragon_rot=-8.0, target=(0, 0, 0.55), ortho=3.0)
