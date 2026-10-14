import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

PW = 0.44
HALF = 0.23
ANG = math.radians(28)
Z0 = 0.075
H_MID = 1.445
H_SIDE = 1.33
ARCH = 0.2
FRAME_T = 0.05
FAB_T = 0.066
INSET = 0.06
YC = 0.05
LOW_TOP = 0.42


def slab(pts, thick, to3d, bev=0.02, bsegs=2, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.faces)
    A = [bm.verts.new(to3d(p.x, p.y, -thick / 2)) for p in pts]
    B = [bm.verts.new(to3d(p.x, p.y, thick / 2)) for p in pts]
    n = len(pts)
    caps = [bm.faces.new(list(reversed(A))), bm.faces.new(B)]
    for k in range(n):
        bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in before])
    edges = list({e for f in caps for e in f.edges})
    bmesh.ops.bevel(bm, geom=edges, offset=bev, offset_type="OFFSET", segments=bsegs, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    big = [f for f in bm.faces if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


def outline(w, top, ah, bot=0.0, rb=0.03, n=12):
    pts = []
    for k in range(3):
        a = -math.pi / 2 + math.pi / 2 * k / 2
        pts.append(Vector((w / 2 - rb + rb * math.cos(a), bot + rb + rb * math.sin(a))))
    for k in range(n + 1):
        t = math.pi * k / n
        pts.append(Vector((w / 2 * math.cos(t), top - ah + ah * math.sin(t))))
    for k in range(3):
        a = math.pi + math.pi / 2 * k / 2
        pts.append(Vector((-w / 2 + rb + rb * math.cos(a), bot + rb + rb * math.sin(a))))
    return pts


def panels():
    dl = Vector((math.cos(ANG), math.sin(ANG)))
    dr = Vector((math.cos(ANG), -math.sin(ANG)))
    p1 = Vector((-HALF, YC))
    p2 = Vector((HALF, YC))
    p0 = p1 - dl * PW
    p3 = p2 + dr * PW
    return [((p0 + p1) / 2, dl, H_SIDE, ANG), ((p1 + p2) / 2, Vector((1, 0)), H_MID, 0.0),
            ((p2 + p3) / 2, dr, H_SIDE, -ANG)], (p1, p2)


def to3d_factory(c, d):
    nrm = Vector((d.y, -d.x))

    def f(u, v, t):
        return (c.x + d.x * u + nrm.x * t, c.y + d.y * u + nrm.y * t, Z0 + v)
    return f


def panel_matrix(c, ang, u, v, t):
    return Matrix.Translation((c.x, c.y, Z0)) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Translation((u, -t, v))


def paw_bm(s, bm):
    ellipsoid_bm((0, 0, -0.022 * s), (0.05 * s, 0.018, 0.042 * s), 12, 6, bm=bm)
    for ang, d, rr in ((-58, 0.064, 0.019), (-20, 0.072, 0.021), (20, 0.072, 0.021), (58, 0.064, 0.019)):
        a = math.radians(90 + ang)
        ellipsoid_bm((math.cos(a) * d * s, 0, 0.01 * s + math.sin(a) * d * s * 0.85),
                     (rr * s, 0.016, rr * 1.15 * s), 10, 5, bm=bm)
    return bm


def add_xf(bm, fn, M):
    before = set(bm.verts)
    fn(bm)
    xf(bm, M, [v for v in bm.verts if v not in before])


def build():
    pans, hinges = panels()
    frame, fab, oak, low = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
    for c, d, H, ang in pans:
        f = to3d_factory(c, d)
        h = H - Z0
        slab(outline(PW - 0.012, h, ARCH, 0.0, 0.035), FRAME_T, f, bev=0.02, bm=frame)
        slab(outline(PW - 2 * INSET, h - INSET * 0.9, ARCH - 0.045, LOW_TOP + 0.07, 0.03), FAB_T, f, bev=0.024, bm=fab)
        lo = [Vector(p) for p in rrect(PW - 2 * INSET, LOW_TOP - INSET, 0.03, 3, 0.0, (LOW_TOP + INSET) / 2)]
        slab(lo, FAB_T - 0.004, f, bev=0.018, bm=low)
        ellipsoid_bm(f(0, h + 0.03, 0), (0.05, 0.05, 0.045), 10, 5, bm=oak)
        for s in (-1, 1):
            ellipsoid_bm(f(s * (PW / 2 - 0.08), 0.06 - Z0, 0), (0.07, 0.06, 0.06), 10, 5, bm=oak)
    finish("Frames", frame, "SH_Walnut", angle=45)
    finish("Fabric", fab, "SH_Sage", angle=55)
    finish("LowPanels", low, "SH_Oak", angle=55)
    for p in hinges:
        for z in (0.32, 0.95):
            prof = [(0.0, 0.0), (0.03, 0.0), (0.036, 0.012), (0.036, 0.098), (0.03, 0.11), (0.0, 0.11)]
            lathe_bm(prof, 10, bm=oak, matrix=Matrix.Translation((p.x, p.y, Z0 + z)))
    finish("Oak", oak, "SH_Oak", angle=60)

    c, d, H, ang = pans[1]
    zc = 0.96
    yf = c.y - FAB_T / 2 + 0.004
    R = 0.1
    M = Matrix(((1, 0, 0, c.x), (0, 0, -1, yf), (0, 1, 0, zc), (0, 0, 0, 1)))
    prof = [(0.0, 0.0), (R + 0.014, 0.0), (R + 0.018, 0.016), (R + 0.009, 0.03), (R, 0.028), (0.0, 0.028)]
    finish("BadgeRim", lathe_bm(prof, 28, matrix=M), "SH_Walnut", angle=55)
    prof = [(0.0, 0.0), (R - 0.004, 0.0), (R - 0.004, 0.032), (R - 0.018, 0.04), (0.0, 0.04)]
    finish("BadgeDisc", lathe_bm(prof, 28, matrix=M), "SH_White", angle=55)
    a, b = R * 1.25, R * 0.42
    bm = bmesh.new()
    rbox_bm((c.x, yf - 0.048, zc), (b, 0.034, a), 0.014, 2, bm=bm)
    rbox_bm((c.x, yf - 0.048, zc), (a, 0.034, b), 0.014, 2, bm=bm)
    finish("Cross", bm, "SH_Teal", angle=55)

    paws = bmesh.new()
    for c, d, H, ang in (pans[0], pans[2]):
        for u, v, s in ((-0.06, 0.66, 1.0), (0.07, 0.94, 1.0)):
            uu = u if ang > 0 else -u
            add_xf(paws, lambda bm, s=s: paw_bm(s, bm), panel_matrix(c, ang, uu, v, FAB_T / 2 + 0.004))
    finish("Paws", paws, "SH_White", angle=70)


out, flags = cli()
begin()
build()
ob = join_all("ShopFolderScreen")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.1, -0.4, 0), dragon_rot=25.0, target=(-0.3, 0.0, 0.7), ortho=2.7)
