import sys, random
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *

PIL_X = 0.33
PIL_W = 0.28
BASE_D = 0.60
PLINTH_H = 0.08
MANTEL_Z0 = 0.40
MANTEL_H = 0.08
DOME_Z = MANTEL_Z0 + MANTEL_H - 0.012
DOME_R = 0.41
DOME_SY = 0.68
DOME_CY = 0.05
DOME_H = 0.49
ENT_FRONT = -0.32
DOOR_HW = 0.12
DOOR_Z0 = DOME_Z + 0.01
ARCH_ZC = DOOR_Z0 + 0.14
STONE = "SH_Stone"
STONE_D = "SH_StoneDark"
WOOD = "SH_Walnut"
ACC = "SH_Gold"
PAINT = "SH_Sage"


def fin(name, bm, mat, angle=50.0):
    print("PART %-12s tris=%d" % (name, sum(len(f.verts) - 2 for f in bm.faces)))
    return finish(name, bm, mat, angle=angle)


def fillet(corners, segs=4):
    pts = []
    n = len(corners)
    for i in range(n):
        p0 = Vector(corners[i - 1][:2])
        p1 = Vector(corners[i][:2])
        p2 = Vector(corners[(i + 1) % n][:2])
        r = corners[i][2]
        if r <= 0:
            pts.append(p1)
            continue
        d1 = (p0 - p1).normalized()
        d2 = (p2 - p1).normalized()
        th = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        t = r / math.tan(th / 2)
        a = p1 + d1 * t
        b = p1 + d2 * t
        c = p1 + (d1 + d2).normalized() * (r / math.sin(th / 2))
        a0 = math.atan2(a.y - c.y, a.x - c.x)
        a1 = math.atan2(b.y - c.y, b.x - c.x)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(segs + 1):
            ang = a0 + da * k / segs
            pts.append(c + Vector((math.cos(ang), math.sin(ang))) * r)
    return pts


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


def bone_bm(length, r, flat=1.0, bm=None, matrix=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    hx = length / 2 - r * 0.9
    tube_bm([(-hx, 0, 0), (hx, 0, 0)], r * 0.62, 8, bm=bm)
    for sx in (-1, 1):
        for sz in (-1, 1):
            ellipsoid_bm((sx * hx, 0, sz * r * 0.62), (r * 0.72, r * 0.72, r * 0.72), 10, 6, bm=bm)
    new = [v for v in bm.verts if v not in before]
    m = Matrix.Diagonal((1.0, flat, 1.0, 1.0))
    if matrix is not None:
        m = matrix @ m
    xf(bm, m, new)
    return bm


def build_base():
    fin("Plinth", soft_box((0, 0, PLINTH_H / 2), (0.96, 0.66, PLINTH_H), 0.08, 0.03, Rb=0.015), STONE_D, angle=50)
    bm = bmesh.new()
    z0, z1 = PLINTH_H - 0.01, MANTEL_Z0 + 0.01
    for s in (-1, 1):
        rbox_bm((s * PIL_X, 0, (z0 + z1) / 2), (PIL_W - 0.05, BASE_D - 0.05, z1 - z0), 0.02, 1, bm=bm)
    hz0, hz1 = PLINTH_H - 0.01, MANTEL_Z0 + 0.01
    rbox_bm((0, 0.22, (hz0 + hz1) / 2), (0.44, 0.14, hz1 - hz0), 0.02, 1, bm=bm)
    fin("BaseCore", bm, STONE_D, angle=50)
    bm = bmesh.new()
    gap = 0.014
    ch = (MANTEL_Z0 - PLINTH_H + 0.01) / 3
    for s in (-1, 1):
        x0, x1 = s * PIL_X - PIL_W / 2, s * PIL_X + PIL_W / 2
        for c in range(3):
            zc = PLINTH_H + ch * (c + 0.5) - 0.004
            if c == 1:
                cells = [((x0 + x1) / 2, PIL_W, -BASE_D / 4, BASE_D / 2), ((x0 + x1) / 2, PIL_W, BASE_D / 4, BASE_D / 2)]
            else:
                sp = 0.13 if (c == 0) == (s < 0) else 0.15
                xa = x0 + sp if s < 0 else x0 + PIL_W - sp
                cells = [((x0 + xa) / 2, xa - x0, 0, BASE_D), ((xa + x1) / 2, x1 - xa, 0, BASE_D)]
            for xc, wx, yc, wy in cells:
                rbox_bm((xc, yc, zc), (wx - gap, wy - gap, ch - gap), 0.03, 1, bm=bm)
    fin("PillarBlocks", bm, STONE, angle=50)
    fin("Mantel", soft_box((0, 0, MANTEL_Z0 + MANTEL_H / 2), (0.98, 0.68, MANTEL_H), 0.07, 0.032, Rb=0.02), WOOD, angle=50)


def build_logs():
    bark = bmesh.new()
    ends = bmesh.new()
    L = 0.42
    y0 = -0.075
    for x, z, r in ((-0.093, PLINTH_H + 0.083, 0.085), (0.093, PLINTH_H + 0.083, 0.085), (0.0, PLINTH_H + 0.226, 0.08)):
        m = Matrix.Translation((x, y0, z)) @ Matrix.Rotation(math.pi / 2, 4, "X")
        prof = [(0.0, -L / 2), (r * 0.92, -L / 2), (r, -L / 2 + 0.03), (r, L / 2 - 0.03), (r * 0.92, L / 2), (0.0, L / 2)]
        lathe_bm(prof, 12, bm=bark, matrix=m)
        cap = [(0.0, L / 2 - 0.012), (r * 0.84, L / 2 - 0.012), (r * 0.8, L / 2 + 0.008), (r * 0.4, L / 2 + 0.014), (0.0, L / 2 + 0.014)]
        lathe_bm(cap, 12, bm=ends, matrix=Matrix.Translation((x, y0, z)) @ Matrix.Rotation(-math.pi / 2, 4, "X"))
    fin("Logs", bark, WOOD, angle=55)
    fin("LogEnds", ends, ACC, angle=60)


def build_dome():
    prof = [(DOME_R + 0.012, DOME_Z), (DOME_R + 0.01, DOME_Z + 0.03)]
    for k in range(1, 10):
        t = math.pi / 2 * k / 10
        prof.append((DOME_R * math.cos(t), DOME_Z + 0.02 + (DOME_H - 0.02) * math.sin(t)))
    prof.append((0.0, DOME_Z + DOME_H))
    fin("Dome", lathe_bm(prof, 26, sy=DOME_SY, matrix=Matrix.Translation((0, DOME_CY, 0))), STONE, angle=60)
    bm = bmesh.new()
    n = 16
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        x = (DOME_R + 0.004) * math.cos(a)
        y = DOME_CY + (DOME_R + 0.004) * DOME_SY * math.sin(a)
        if y < -0.1 and abs(x) < 0.27:
            continue
        nrm = Vector((math.cos(a) * DOME_SY, math.sin(a), 0)).normalized()
        rz = math.atan2(nrm.y, nrm.x)
        before = set(bm.verts)
        ellipsoid_bm((0, 0, 0), (0.03, 0.068, 0.05), 8, 4, bm=bm)
        xf(bm, Matrix.Translation((x, y, DOME_Z + 0.055)) @ Matrix.Rotation(rz, 4, "Z"),
           [v for v in bm.verts if v not in before])
    rnd = random.Random(11)
    for a_deg, el in ((235, 0.55), (305, 0.62)):
        a = math.radians(a_deg)
        ce = math.cos(el)
        p = Vector((DOME_R * ce * math.cos(a), DOME_CY + DOME_R * DOME_SY * ce * math.sin(a),
                    DOME_Z + 0.02 + (DOME_H - 0.02) * math.sin(el)))
        nrm = Vector((ce * math.cos(a) / DOME_R, ce * math.sin(a) / (DOME_R * DOME_SY),
                      math.sin(el) / (DOME_H - 0.02))).normalized()
        q = nrm.to_track_quat("Z", "Y")
        before = set(bm.verts)
        s = rnd.uniform(0.85, 1.1)
        ellipsoid_bm((0, 0, 0), (0.06 * s, 0.045 * s, 0.024), 10, 5, bm=bm)
        xf(bm, Matrix.Translation(p - nrm * 0.006) @ q.to_matrix().to_4x4(), [v for v in bm.verts if v not in before])
    fin("DomeStones", bm, STONE_D, angle=70)


def build_mouth():
    w, h = 0.46, 0.36
    pts = fillet([(-w / 2, 0.0, 0.0), (w / 2, 0.0, 0.0), (w / 2, h, w / 2 - 0.02), (-w / 2, h, w / 2 - 0.02)], 6)
    yb = -0.1
    t = yb - ENT_FRONT
    fin("Entrance", slab(pts, t, lambda u, v, ww: (u, (yb + ENT_FRONT) / 2 + ww, DOME_Z - 0.01 + v), bev=0.025),
        STONE, angle=50)
    dh = ARCH_ZC - DOOR_Z0 + DOOR_HW
    dpts = fillet([(-DOOR_HW, 0.0, 0.0), (DOOR_HW, 0.0, 0.0), (DOOR_HW, dh, DOOR_HW - 0.005),
                   (-DOOR_HW, dh, DOOR_HW - 0.005)], 6)
    fin("Door", slab(dpts, 0.034, lambda u, v, ww: (u, ENT_FRONT - 0.004 + ww, DOOR_Z0 + v), bev=0.012), PAINT,
        angle=50)
    bm = bmesh.new()
    rad = 0.168
    for k in range(7):
        a = math.pi * k / 6
        big = k == 3
        sz = (0.1 if big else 0.085, 0.06, 0.09 if big else 0.075)
        m = Matrix.Translation((rad * math.cos(a), ENT_FRONT - 0.012, ARCH_ZC + rad * math.sin(a))) @ \
            Matrix.Rotation(math.pi / 2 - a, 4, "Y")
        rbox_bm((0, 0, 0), sz, 0.024, 1, bm=bm, matrix=m)
    for s in (-1, 1):
        rbox_bm((s * rad, ENT_FRONT - 0.012, DOOR_Z0 + 0.055), (0.075, 0.06, 0.1), 0.024, 1, bm=bm)
    fin("Voussoirs", bm, STONE_D, angle=50)
    bm = bmesh.new()
    for z, wd in ((DOOR_Z0 + 0.045, 0.2), (ARCH_ZC + 0.04, 0.2)):
        rbox_bm((0, ENT_FRONT - 0.026, z), (wd, 0.02, 0.032), 0.009, 1, bm=bm)
        for s in (-1, 1):
            ellipsoid_bm((s * (wd / 2 - 0.022), ENT_FRONT - 0.038, z), (0.014, 0.01, 0.014), 6, 3, bm=bm)
    bone_bm(0.18, 0.031, 0.6, bm=bm, matrix=Matrix.Translation((0, ENT_FRONT - 0.042, (DOOR_Z0 + ARCH_ZC) / 2 + 0.012)))
    for s in (-1, 1):
        tube_bm([(s * 0.045, ENT_FRONT - 0.02, (DOOR_Z0 + ARCH_ZC) / 2 + 0.012),
                 (s * 0.045, ENT_FRONT - 0.045, (DOOR_Z0 + ARCH_ZC) / 2 + 0.012)], 0.013, 6, bm=bm)
    fin("DoorIron", bm, ACC, angle=60)


def build_chimney():
    x, y = 0.15, 0.06
    prof = [(0.0, 0.82), (0.1, 0.82), (0.098, 0.88), (0.08, 0.93), (0.074, 1.0), (0.0, 1.0)]
    fin("Chimney", lathe_bm(prof, 14, matrix=Matrix.Translation((x, y, 0))), STONE_D, angle=50)
    prof = [(0.0, 0.985), (0.106, 0.985), (0.115, 1.0), (0.11, 1.022), (0.085, 1.05), (0.045, 1.08), (0.0, 1.095)]
    fin("ChimneyCap", lathe_bm(prof, 14, matrix=Matrix.Translation((x, y, 0))), ACC, angle=55)
    bm = torus_bm(0.088, 0.018, 14, 5, matrix=Matrix.Translation((x, y, 0.95)))
    fin("ChimneyBand", bm, ACC, angle=70)


out, flags = cli()
begin()
build_base()
build_logs()
build_dome()
build_mouth()
build_chimney()
ob = join_all("ShopStove")
report(ob)
export(ob, flags)
preview(ob, out, dragon_loc=(-1.05, -0.3, 0), dragon_rot=20.0, target=(-0.3, 0, 0.55), ortho=2.5)
