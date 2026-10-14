import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

CAP_Z = 0.84
FA, FB = 0.155, 0.19
TILT = -11.0


def oval_ring(c, a, b, r, segs=20, sides=6, bm=None):
    bm = bm or bmesh.new()
    c = Vector(c)
    Y = Vector((0, 1, 0))
    rings = []
    for k in range(segs):
        t = 2 * math.pi * k / segs
        p = c + Vector((a * math.cos(t), 0, b * math.sin(t)))
        n = Vector((b * math.cos(t), 0, a * math.sin(t))).normalized()
        rings.append([bm.verts.new(p + n * math.cos(2 * math.pi * j / sides) * r + Y * math.sin(2 * math.pi * j / sides) * r)
                      for j in range(sides)])
    faces = []
    for k in range(segs):
        A, B = rings[k], rings[(k + 1) % segs]
        for j in range(sides):
            faces.append(bm.faces.new((A[j], A[(j + 1) % sides], B[(j + 1) % sides], B[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def monchi_badge(cx, cy, cz, s, gold, plum):
    hz = cz - 0.05 * s
    ellipsoid_bm((cx, cy, hz), (s, 0.026, s * 0.86), 12, 6, bm=gold)
    ellipsoid_bm((cx, cy + 0.006, hz - 1.05 * s), (s * 0.95, 0.024, s * 0.42), 10, 5, bm=gold)
    for sx in (-1, 1):
        tube_bm([(cx + sx * 0.5 * s, cy, hz + 0.6 * s), (cx + sx * 0.82 * s, cy, hz + 0.9 * s),
                 (cx + sx * 0.88 * s, cy, hz + 1.25 * s)], [0.2 * s, 0.13 * s, 0.04 * s], 6, bm=gold)
        ellipsoid_bm((cx + sx * 0.36 * s, cy - 0.024, hz + 0.02 * s), (0.15 * s, 0.012, 0.19 * s), 6, 4, bm=plum)


def build_column():
    bm = soft_box((0, 0, 0.065), (0.48, 0.48, 0.13), 0.09, 0.035, seg=2, Rb=0.012)
    finish("Plinth", bm, "SH_Walnut", angle=50)
    prof = [(0.0, 0.12), (0.17, 0.12), (0.175, 0.15), (0.15, 0.18), (0.13, 0.2), (0.12, 0.24), (0.115, 0.5),
            (0.12, 0.74), (0.13, 0.77), (0.15, 0.79), (0.155, 0.81), (0.0, 0.81)]
    finish("Column", lathe_bm(prof, 16), "SH_Honey", angle=45)
    bm = bmesh.new()
    for z in (0.2, 0.775):
        torus_bm(0.135, 0.026, 16, 6, bm=bm, matrix=Matrix.Translation((0, 0, z)))
    finish("Rings", bm, "SH_Walnut", angle=70)
    bm = soft_box((0, 0, CAP_Z - 0.03), (0.42, 0.42, 0.08), 0.08, 0.03, seg=2, Rb=0.012)
    finish("Capital", bm, "SH_Walnut", angle=50)
    bm = rbox_bm((0, -0.243, 0.065), (0.24, 0.03, 0.07), 0.013, 1)
    finish("Plaque", bm, "SH_Gold", angle=50)


def build_portrait():
    zc = CAP_Z + 0.055 + FB
    M = Matrix.Translation((0, -0.02, zc)) @ Matrix.Rotation(math.radians(TILT), 4, "X")
    frame, plum, gold = bmesh.new(), bmesh.new(), bmesh.new()
    oval_ring((0, 0, 0), FA, FB, 0.042, 22, 6, bm=frame)
    ellipsoid_bm((0, 0.02, 0), (FA + 0.005, 0.03, FB + 0.005), 14, 5, bm=plum)
    monchi_badge(0, -0.012, -0.03, FA * 0.5, gold, plum)
    for sx in (-1, 1):
        ellipsoid_bm((sx * 0.065, -0.01, FB + 0.05), (0.065, 0.032, 0.042), 10, 5, bm=plum)
        tube_bm([(sx * 0.03, -0.03, FB + 0.04), (sx * 0.075, -0.035, FB + 0.0), (sx * 0.1, -0.03, FB - 0.035)],
                [0.022, 0.02, 0.017], 5, bm=plum)
    ellipsoid_bm((0, -0.03, FB + 0.05), (0.034, 0.032, 0.034), 8, 5, bm=frame)
    for b in (frame, plum, gold):
        xf(b, M)
    finish("Frame", frame, "SH_Gold", angle=70)
    finish("Velvet", plum, "SH_Plum", angle=None)
    finish("Badge", gold, "SH_Gold", angle=None)
    bm = rbox_bm((0, -0.01, CAP_Z + 0.03), (0.3, 0.16, 0.06), 0.025, 2)
    rbox_bm((0, -0.085, CAP_Z + 0.07), (0.3, 0.05, 0.07), 0.022, 2, bm=bm)
    p0 = Vector((0, 0.05, CAP_Z + 0.04))
    p1 = M @ Vector((0, 0.05, 0.08))
    tube_bm([p0, (p0 + p1) / 2 + Vector((0, 0.025, 0)), p1], [0.03, 0.026, 0.024], 6, bm=bm)
    finish("Stand", bm, "SH_Walnut", angle=50)


out, flags = cli()
begin()
build_column()
build_portrait()
for o in PARTS:
    print("PART %-8s tris=%d" % (o.name, sum(len(f.vertices) - 2 for f in o.data.polygons)))
ob = join_all("ShopPortraitPedestal")
report(ob)
export(ob, flags)
if out:
    preview(ob, out, dragon_loc=(1.15, -0.3, 0), ortho=2.7, target=(0.5, 0, 0.65))
