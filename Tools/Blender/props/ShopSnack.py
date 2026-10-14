import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

SEAM_Z = 0.232
SEAM_TOP = 0.3
SEAM_T = 0.036
SEAM_W = 0.25
TEETH = 7


def front(x, y, z):
    return Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))


def zigzag_prism(w, z0, z1, t, teeth, tooth_h):
    bm = bmesh.new()
    pts = [(-w / 2, z0), (w / 2, z0)]
    for k in range(teeth * 2 + 1):
        x = w / 2 - w * k / (teeth * 2)
        z = z1 if k % 2 == 0 else z1 - tooth_h
        pts.append((x, z))
    pts[2] = (w / 2, z1 - tooth_h * 0.5)
    pts[-1] = (-w / 2, z1 - tooth_h * 0.5)
    front_v = [bm.verts.new((x, -t / 2, z)) for x, z in pts]
    back_v = [bm.verts.new((x, t / 2, z)) for x, z in pts]
    n = len(pts)
    bm.faces.new(front_v)
    bm.faces.new(list(reversed(back_v)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front_v[j], front_v[i], back_v[i], back_v[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=1, affect="EDGES", clamp_overlap=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    return bm


out, flags = cli()
begin()

prof = [(0.0, 0.215, 0.09), (0.012, 0.242, 0.125), (0.04, 0.26, 0.15), (0.085, 0.27, 0.162), (0.135, 0.27, 0.152),
        (0.175, 0.265, 0.122), (0.205, 0.258, 0.085), (0.225, 0.252, 0.052), (SEAM_Z + 0.012, 0.248, 0.03)]
rings = [(w, d, 0.075, z) for z, w, d in prof]
finish("Bag", loft(rings, 4), "SH_Coral", angle=None)

finish("Seam", zigzag_prism(SEAM_W, SEAM_Z, SEAM_TOP, SEAM_T, TEETH, 0.022), "SH_Straw", smooth=False)

tilt = math.radians(-12)
M = front(0, -0.064, 0.115) @ Matrix.Rotation(tilt, 4, "X")
lab = bmesh.new()
lathe_bm([(0.0, 0.0), (0.078, 0.0), (0.078, 0.012), (0.068, 0.02), (0.0, 0.022)], 22, bm=lab, matrix=M)
finish("Label", lab, "SH_Cream", angle=55)

paw = bmesh.new()
ellipsoid_bm((0.0, -0.014, 0.022), (0.03, 0.024, 0.012), useg=12, vseg=5, bm=paw)
for a, rr in ((-58, 0.042), (-20, 0.046), (20, 0.046), (58, 0.042)):
    ra = math.radians(a)
    ellipsoid_bm((rr * math.sin(ra), -0.014 + rr * math.cos(ra) + 0.004, 0.022), (0.012, 0.014, 0.01), useg=10, vseg=5, bm=paw)
xf(paw, M)
finish("Paw", paw, "SH_Coral", angle=None)

ob = join_all("ShopSnack")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-0.72, 0.42, 0), dragon_rot=20.0, target=(-0.1, 0, 0.3), ortho=1.25)
