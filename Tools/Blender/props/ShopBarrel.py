import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

H = 0.8
R_END = 0.238
BULGE = 0.056
STAVES = 12
SEGS = STAVES * 2
HOOPS = (0.12, 0.68)


def front_matrix(x, y, z, rz=0.0, tilt=0.0):
    M = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ \
        Matrix.Rotation(math.radians(tilt), 4, "X") @ M


def fin(name, bm, mat, angle=50.0, smooth=True):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, smooth=smooth, angle=angle)


def paw_bm(M, s, t=0.014, bm=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    ellipsoid_bm((0.0, -0.28 * s, 0.0), (0.62 * s, 0.5 * s, t), useg=10, vseg=4, bm=bm)
    for a, rr, k in ((-62, 0.92, 0.9), (-21, 1.0, 1.0), (21, 1.0, 1.0), (62, 0.92, 0.9)):
        ra = math.radians(a)
        ellipsoid_bm((rr * s * math.sin(ra), -0.28 * s + rr * s * math.cos(ra) + 0.12 * s, 0.0),
                     (0.24 * s * k, 0.28 * s * k, t), useg=8, vseg=4, bm=bm)
    xf(bm, M, [v for v in bm.verts if v not in before])
    return bm


def barrel_r(z):
    return R_END + BULGE * math.sin(math.pi * min(max(z / H, 0.0), 1.0))


def build_body():
    zs = [0.035 + (H - 0.07) * i / 10 for i in range(11)]
    prof = [(0.0, 0.0), (R_END - 0.03, 0.0), (R_END - 0.006, 0.012)]
    prof += [(barrel_r(z), z) for z in zs]
    prof += [(R_END - 0.006, H - 0.012), (R_END - 0.03, H), (R_END - 0.055, H), (R_END - 0.06, H - 0.04), (0.0, H - 0.04)]
    bm = lathe_bm(prof, SEGS)
    for v in bm.verts:
        r = math.hypot(v.co.x, v.co.y)
        if r < 0.2 or v.co.z < 0.006 or v.co.z > H - 0.006:
            continue
        a = math.atan2(v.co.y, v.co.x) % (2 * math.pi)
        k = round(a / (2 * math.pi / SEGS)) % SEGS
        if k % 2 == 0:
            v.co.x *= (r - 0.014) / r
            v.co.y *= (r - 0.014) / r
    fin("Staves", bm, "SH_Honey", angle=28)


def build_lid():
    z = H - 0.04
    prof = [(R_END - 0.058, z - 0.01), (R_END - 0.062, z + 0.006), (R_END - 0.08, z + 0.018), (0.08, z + 0.026), (0.0, z + 0.028)]
    fin("Lid", lathe_bm(prof, SEGS), "SH_Oak", angle=40)
    bm = bmesh.new()
    for x in (-0.07, 0.07):
        rbox_bm((x, 0.0, z + 0.014), (0.026, 2 * (R_END - 0.07) * math.sqrt(max(0.0, 1 - (x / (R_END - 0.07)) ** 2)), 0.026),
                0.01, 1, bm=bm)
    fin("LidSeams", bm, "SH_Walnut", angle=50)
    bm = torus_bm(0.046, 0.016, 14, 6, matrix=Matrix.Translation((0, -0.02, z + 0.05)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    ellipsoid_bm((0, -0.02, z + 0.03), (0.04, 0.032, 0.022), 10, 5, bm=bm)
    fin("LidRing", bm, "SH_Gold", angle=70)


def build_hoops():
    bm = bmesh.new()
    for zc in HOOPS:
        h = 0.065
        r0 = barrel_r(zc - h / 2) - 0.004
        r1 = barrel_r(zc + h / 2) - 0.004
        prof = [(r0, zc - h / 2), (r0 + 0.016, zc - h / 2 + 0.003), (barrel_r(zc) + 0.02, zc - h / 2 + 0.014),
                (barrel_r(zc) + 0.02, zc + h / 2 - 0.014), (r1 + 0.016, zc + h / 2 - 0.003), (r1, zc + h / 2)]
        lathe_bm(prof, SEGS, bm=bm)
    fin("Hoops", bm, "SH_Gold", angle=40)
    bm = bmesh.new()
    rp = [(0.0, 0.0), (0.02, 0.0), (0.02, 0.006), (0.013, 0.016), (0.0, 0.019)]
    for zc in HOOPS:
        for a in (-32, 32, 148, 212):
            ra = math.radians(a)
            r = barrel_r(zc) + 0.018
            lathe_bm(rp, 6, bm=bm, matrix=front_matrix(r * math.sin(ra), -r * math.cos(ra), zc, rz=a))
    fin("Rivets", bm, "SH_Walnut", angle=60)


def build_paw():
    zc = 0.41
    r = barrel_r(zc) - 0.004
    fin("Paw", paw_bm(front_matrix(0.0, -r, zc), 0.088, 0.018), "SH_Walnut", angle=None)


out, flags = cli()
begin()
build_body()
build_lid()
build_hoops()
build_paw()
ob = join_all("ShopBarrel")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.0, 0.3, 0), target=(-0.4, 0.0, 0.45), ortho=2.1)
