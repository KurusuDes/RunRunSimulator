import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

W = 3.4
NSTRIPES = 9
D = 1.0
YB, YF = D / 2, -D / 2 + 0.04
DROP = 0.42
ZF = 0.34
ZB = ZF + DROP
BULGE = 0.07
PUFF = 0.03
T = 0.05
VAL = 0.1
SCAL = 0.17


def face_m(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def fin(name, bm, mat, angle=50.0):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def offset2d(pts, d):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        t = (p2 - p0).normalized()
        nin = Vector((-t.y, t.x)) * s
        out.append((p1.x + nin.x * d, p1.y + nin.y * d))
    return out


def badge_bm(outline, t, bev, steps=2, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = [(0.0, 0.0), (0.0, t - bev)]
    for j in range(1, steps + 1):
        a = math.pi / 2 * j / steps
        rings.append((bev * (1 - math.cos(a)), t - bev + bev * math.sin(a)))
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    vr = []
    for d, z in rings:
        vr.append([bm.verts.new((x, y, z)) for x, y in offset2d(outline, d)])
    n = len(outline)
    for A, B in zip(vr, vr[1:]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    c0 = bm.verts.new((cx, cy, 0.0))
    c1 = bm.verts.new((cx, cy, t))
    for k in range(n):
        bm.faces.new((vr[0][(k + 1) % n], vr[0][k], c0))
        bm.faces.new((vr[-1][k], vr[-1][(k + 1) % n], c1))
    if matrix is not None:
        xf(bm, matrix, [v for r in vr for v in r] + [c0, c1])
    return bm


def canopy_z(t):
    return ZB - DROP * t + BULGE * math.sin(math.pi * t)


def stripe_bm(x0, x1, bm=None, nt=7, nx=4):
    bm = bm or bmesh.new()
    top, bot = [], []
    for i in range(nt + 1):
        t = i / nt
        y = YB + (YF - YB) * t
        rt, rb = [], []
        for j in range(nx + 1):
            u = j / nx
            x = x0 + (x1 - x0) * u
            z = canopy_z(t) + PUFF * math.sin(math.pi * u)
            rt.append(bm.verts.new((x, y, z)))
            rb.append(bm.verts.new((x, y, z - T)))
        top.append(rt)
        bot.append(rb)
    for i in range(nt):
        for j in range(nx):
            bm.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]))
            bm.faces.new((bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j]))
    for i in range(nt):
        bm.faces.new((top[i][0], bot[i][0], bot[i + 1][0], top[i + 1][0]))
        bm.faces.new((top[i][nx], top[i + 1][nx], bot[i + 1][nx], bot[i][nx]))
    for j in range(nx):
        bm.faces.new((top[0][j], top[0][j + 1], bot[0][j + 1], bot[0][j]))
        bm.faces.new((top[nt][j], bot[nt][j], bot[nt][j + 1], top[nt][j + 1]))
    return bm


def flap_outline(w, n=8):
    hw = w / 2
    pts = [(-hw, 0.0)]
    for k in range(n + 1):
        a = math.pi + math.pi * k / n
        pts.append((hw * math.cos(a), -VAL + SCAL * math.sin(a)))
    pts.append((hw, 0.0))
    return list(reversed(pts))


def build_canopy():
    sw = W / NSTRIPES
    bms = {"SH_Sage": bmesh.new(), "SH_Parchment": bmesh.new()}
    for k in range(NSTRIPES):
        mat = "SH_Sage" if k % 2 == 0 else "SH_Parchment"
        x0 = -W / 2 + k * sw
        stripe_bm(x0 + 0.001, x0 + sw - 0.001, bm=bms[mat])
        cx = x0 + sw / 2
        zf = canopy_z(1.0) + 0.012
        badge_bm(flap_outline(sw - 0.004), 0.045, 0.016, 2, bm=bms[mat], matrix=face_m(cx, YF + 0.012, zf))
    fin("StripesCoral", bms["SH_Sage"], "SH_Sage", angle=40)
    fin("StripesCream", bms["SH_Parchment"], "SH_Parchment", angle=40)


def build_sides():
    bm = bmesh.new()
    zf = canopy_z(1.0)
    pts = [(YB - 0.02, ZB - 0.02), (YB - 0.02, ZB - 0.36), (YF + 0.22, zf - 0.08), (YF + 0.04, zf - 0.02)]
    for t in [i / 6 for i in range(1, 6)]:
        y = YB + (YF - YB) * (1 - t)
        pts.append((y, canopy_z(1 - t) - 0.02))
    outline = [(-y, z) for y, z in pts]
    for sx in (-1, 1):
        m = Matrix(((0, 0, 1, sx * (W / 2 + 0.005) - (0.04 if sx > 0 else 0.0)), (-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
        badge_bm(outline, 0.04, 0.014, 2, bm=bm, matrix=m)
    fin("Sides", bm, "SH_Sage", angle=55)


def build_frame():
    bm = tube_bm([(-W / 2 - 0.06, YB - 0.02, ZB - 0.01), (W / 2 + 0.06, YB - 0.02, ZB - 0.01)], 0.055, 10)
    for sx in (-1, 1):
        ellipsoid_bm((sx * (W / 2 + 0.08), YB - 0.02, ZB - 0.01), (0.07, 0.07, 0.07), 10, 6, bm=bm)
    zf = canopy_z(1.0)
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.12)
        tube_bm(catmull([(x, YB - 0.02, ZB - 0.42), (x, 0.0, ZB - 0.36), (x, YF + 0.1, zf - 0.05)], 3), 0.024, 6, bm=bm)
        rbox_bm((x, YB - 0.03, ZB - 0.42), (0.12, 0.06, 0.14), 0.02, bm=bm)
    fin("Frame", bm, "SH_Walnut", angle=55)


out, flags = cli()
begin()
build_canopy()
build_sides()
build_frame()
ob = join_all("ShopAwning")
zmin = min(v.co.z for v in ob.data.vertices)
ys = [v.co.y for v in ob.data.vertices]
ob.data.transform(Matrix.Translation((0, -(max(ys) + min(ys)) / 2, -zmin)))
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(2.7, -1.0, 0), target=(0.4, 0.0, 0.5), ortho=5.0)
if out and "close" in flags:
    for o in [o for o in bpy.data.objects if o.type == "MESH" and o.name not in (ob.name, "Plane")]:
        o.hide_render = True
    render(os.path.join(out, "ShopAwning_close.png"), 90, 8, (1.2, 0.0, 0.4), 2.0, res=(600, 600))
    render(os.path.join(out, "ShopAwning_close2.png"), 120, 20, (1.2, 0.0, 0.4), 2.0, res=(600, 600))
